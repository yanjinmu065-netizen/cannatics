import streamlit as st
import pandas as pd
import datetime
import os
import base64

# --- 🔌 Googleスプレッドシート連携用ライブラリ ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# --- ページ設定とパスワード保護 ---
st.set_page_config(page_title="Cannatics", layout="centered")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 ログイン - Cannatics")
    username = st.text_input("ログインID", key="login_username")
    password = st.text_input("パスワード", type="password", key="login_password")
    
    if st.button("ログイン"):
        if username == "0602" and password == "admin123": 
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います")
    return False

if check_password():

    # --- 🔗 データベース接続・読み書き関数 ---
    def get_spreadsheet_client():
        if not HAS_GSPREAD: return None
        try:
            if "gcp_service_account" in st.secrets:
                creds_dict = dict(st.secrets["gcp_service_account"])
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                return gspread.authorize(creds)
            elif os.path.exists("secrets.json"):
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_file("secrets.json", scopes=scopes)
                return gspread.authorize(creds)
        except Exception: return None
        return None

    def load_data_from_db(sheet_name, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                sh = client.open("Cannatics_Database")
                worksheet = sh.worksheet(sheet_name)
                df = pd.DataFrame(worksheet.get_all_records())
                return df if not df.empty else pd.DataFrame(columns=default_cols)
            except Exception: pass
        file_name = f"{sheet_name}.csv"
        if os.path.exists(file_name): return pd.read_csv(file_name)
        return pd.DataFrame(columns=default_cols)

    def save_data_to_db(sheet_name, new_row_dict, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                sh = client.open("Cannatics_Database")
                worksheet = sh.worksheet(sheet_name)
                row_to_append = [new_row_dict.get(col, "") for col in default_cols]
                worksheet.append_row(row_to_append)
                return True
            except Exception: pass
        df = load_data_from_db(sheet_name, default_cols)
        df = pd.concat([df, pd.DataFrame([new_row_dict])], ignore_index=True)
        df.to_csv(f"{sheet_name}.csv", index=False)
        return True

    @st.cache_data
    def load_excel_presets():
        try:
            df_cannabinoid = pd.read_excel("data.xlsx", sheet_name="カンナビノイド", header=2)
            df_synthetic = pd.read_excel("data.xlsx", sheet_name="半合成", header=2)
            df_terpene = pd.read_excel("data.xlsx", sheet_name="テルペン", header=2)
            g1 = [str(r["成分名"]) for _, r in df_synthetic.dropna(subset=["成分名"]).iterrows()]
            g2 = [str(r["成分名"]) for _, r in df_cannabinoid.dropna(subset=["成分名"]).iterrows()]
            g3 = list(df_terpene["成分名"].dropna().unique())
            return g1, g2, g3
        except Exception: return ["CRDP", "THA"], ["CBD", "CBG"], ["ミルセン", "リモネン"]

    g1_presets, g2_presets, g3_presets = load_excel_presets()

    # --- 🎨 背景画像処理 ---
    bg_style_raw = "linear-gradient(135deg, #130021 0%, #3a0066 100%)"
    if os.path.exists("title_bg.png"):
        try:
            with open("title_bg.png", "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            bg_style_raw = f"url(data:image/png;base64,{encoded}) center/cover"
        except Exception: pass

    # 💡 エラーの原因だった波括弧のバッティングを防ぐため、文字列を分けて安全に結合します
    css_code = """
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        h1, h2, h3, h4, p, label { color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }
        .stButton>button { 
            background-color: #98FB98 !important; color: #000000 !important; font-weight: bold; border-radius: 8px; border: 1px solid #000000; width: 100%; height: 45px;
        }
        .group-container { border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fafafa; }
        
        /* 統一バナーデザイン */
        .custom-title-banner { 
            background: BACKGROUND_PLACEHOLDER;
            padding: 40px 20px; border-radius: 12px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
        }
        .custom-title-banner h1 { color: #ffffff !important; font-size: 34px !important; font-weight: 800 !important; text-shadow: 0 0 10px #00ff00 !important; margin: 0 !important; }
        .custom-title-banner p { color: #ff00ff !important; font-size: 18px !important; font-weight: bold !important; text-shadow: 0 0 8px #ff00ff !important; margin-top: 10px !important; }
        
        /* サイドバーおしゃれ化（白文字徹底統一デザイン） */
        [data-testid="stSidebar"] { 
            background: BACKGROUND_PLACEHOLDER;
            border-right: 2px solid #ff00ff;
        }
        [data-testid="stSidebar"] .stRadio > label div p { 
            color: #ffffff !important; font-weight: 900 !important; font-size: 18px !important; text-shadow: 0 0 5px #00ff00 !important; margin-bottom: 10px;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span p,
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div p,
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { 
            color: #ffffff !important; font-weight: bold !important; font-size: 14px !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="radio"] div { 
            border-color: #00ff00 !important; background-color: rgba(0, 0, 0, 0.4) !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] span p,
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] div p {
            color: #ff00ff !important; text-shadow: 0 0 8px #ff00ff !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] div div {
            background-color: #ff00ff !important;
        }
        </style>
    """.replace("BACKGROUND_PLACEHOLDER", bg_style_raw)

    st.markdown(css_code, unsafe_allow_html=True)

    # 📌 サイドバーメニュー
    page = st.sidebar.radio("メニューを選択", ["📝 ワンタップ吸引記録", "🧪 リキッドマスター登録", "🌐 新成分マスター登録", "📅 履歴カレンダー", "📊 成分紹介"])

    # --- ✨ 共通おしゃれバナー表示 ---
    banner_titles = {
        "📝 ワンタップ吸引記録": "ワンタップ吸引記録",
        "🧪 リキッドマスター登録": "リキッドマスター設定",
        "🌐 新成分マスター登録": "新成分の追加登録",
        "📅 履歴カレンダー": "使用履歴カレンダー",
        "📊 成分紹介": "リキッド紹介 & レビュー"
    }
    current_title = banner_titles.get(page, "Cannatics")
    st.markdown(f"""<div class="custom-title-banner"><h1>🌿 Cannatics</h1><p>{current_title}</p></div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 各ページの内容
    # -------------------------------------------------------------------------
    LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
    LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

    if page == "📝 ワンタップ吸引記録":
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        if df_master.empty:
            st.warning("⚠️ まだリキッドが登録されていません。")
        else:
            selected_liq = st.selectbox("🚬 リキッドを選択", df_master["リキッド名"].tolist())
            liq_detail = df_master[df_master["リキッド名"] == selected_liq]["配合詳細"].values[0]
            st.caption(f"配合: {liq_detail}")
            puffs = st.slider("パフ数", 1, 15, 3)
            log_date = st.date_input("日付", datetime.date.today())
            if st.button("📊 ワンタップで記録完了！"):
                new_log_row = {"日付": log_date.strftime("%Y-%m-%d"), "リキッド名": selected_liq, "パフ数": puffs, "配合詳細": liq_detail, "体感した効果": "", "体感メモ": ""}
                if save_data_to_db("Attraction_Logs", new_log_row, LOG_COLS):
                    st.success(f"🎉 {selected_liq} を記録しました！")

    elif page == "🧪 リキッドマスター登録":
        if "m_g1" not in st.session_state: st.session_state.m_g1 = 1
        if "m_g2" not in st.session_state: st.session_state.m_g2 = 1
        if "m_g3" not in st.session_state: st.session_state.m_g3 = 0
        
        new_liq_name = st.text_input("📦 新しいリキッド名")
        st.subheader("🧪 配合割合の入力")
        
        # --- 「＋ 成分を追加」ボタン式の追加システム ---
        g1_data = []
        for i in range(st.session_state.m_g1):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"半合成 {i+1}", g1_presets, key=f"g1_n_{i}")
            with c2: pct = st.number_input(f"比率%##{i}", 0, 100, 0, key=f"g1_p_{i}")
            g1_data.append((name, pct))
        if st.button("➕ 半合成成分を追加"):
            st.session_state.m_g1 += 1
            st.rerun()
            
        g2_data = []
        for i in range(st.session_state.m_g2):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"天然成分 {i+1}", g2_presets, key=f"g2_n_{i}")
            with c2: pct = st.number_input(f"比率% (天然)##{i}", 0, 100, 0, key=f"g2_p_{i}")
            g2_data.append((name, pct))
        if st.button("➕ カンナビノイド成分を追加"):
            st.session_state.m_g2 += 1
            st.rerun()

        g3_data = []
        for i in range(st.session_state.m_g3):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"テルペン {i+1}", g3_presets, key=f"g3_n_{i}")
            with c2: pct = st.number_input(f"比率% (テルペン)##{i}", 0, 100, 0, key=f"g3_p_{i}")
            g3_data.append((name, pct))
        if st.button("➕ テルペン成分を追加"):
            st.session_state.m_g3 += 1
            st.rerun()

        if st.button("💾 マスターに登録"):
            if not new_liq_name:
                st.error("リキッド名を入力してください")
            else:
                parts = []
                for n, p in g1_data + g2_data + g3_data:
                    if p > 0: parts.append(f"{n}:{p}%")
                
                if not parts:
                    st.error("比率が1%以上の成分を1つ以上入力してください")
                else:
                    detail_str = ", ".join(parts)
                    save_data_to_db("Liquid_Master", {"リキッド名": new_liq_name, "配合詳細": detail_str}, LIQUID_MASTER_COLS)
                    st.success(f"🎉 「{new_liq_name}」を登録しました！")

    elif page == "📊 成分紹介":
        try:
            with open("review.py", encoding="utf-8") as f:
                exec(f.read(), globals())
        except Exception as e: st.error(f"読み込みエラー: {e}")

    elif page == "🌐 新成分マスター登録":
        try:
            with open("seibunn.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.warning("⚠️ 新成分マスターの連携ファイルを確認してください。")
        
    elif page == "📅 履歴カレンダー":
        try:
            with open("calendar.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.warning("⚠️ 履歴カレンダーの連携ファイルを確認してください。")
