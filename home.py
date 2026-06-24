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
    username = st.text_input("ログインIDを入力してください", key="login_username")
    password = st.text_input("パスワードを入力してください", type="password", key="login_password")
    
    if st.button("ログイン"):
        if username == "0602" and password == "admin123": 
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います")
    return False

if check_password():

    # --- 🔗 Googleスプレッドシート接続関数 ---
    def get_spreadsheet_client():
        if not HAS_GSPREAD:
            return None
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
        except Exception as e:
            st.sidebar.error(f"Google接続エラー: {e}")
        return None

    # --- 💾 データの読み込み・保存処理 ---
    def load_data_from_db(sheet_name, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                sh = client.open("Cannatics_Database")
                try:
                    worksheet = sh.worksheet(sheet_name)
                    df = pd.DataFrame(worksheet.get_all_records())
                    return df if not df.empty else pd.DataFrame(columns=default_cols)
                except gspread.exceptions.WorksheetNotFound:
                    worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols=str(len(default_cols)))
                    worksheet.append_row(default_cols)
                    return pd.DataFrame(columns=default_cols)
            except Exception as e:
                st.sidebar.warning(f"スプレッドシート読み込み失敗: {e}")
        
        file_name = f"{sheet_name}.csv"
        if os.path.exists(file_name):
            return pd.read_csv(file_name)
        return pd.DataFrame(columns=default_cols)

    def save_data_to_db(sheet_name, new_row_dict, default_cols):
        client = get_spreadsheet_client()
        saved_via_gs = False
        if client:
            try:
                sh = client.open("Cannatics_Database")
                worksheet = sh.worksheet(sheet_name)
                row_to_append = [new_row_dict.get(col, "") for col in default_cols]
                worksheet.append_row(row_to_append)
                saved_via_gs = True
            except Exception as e:
                st.sidebar.error(f"スプレッドシート保存失敗: {e}")
        
        file_name = f"{sheet_name}.csv"
        df = load_data_from_db(sheet_name, default_cols)
        df = pd.concat([df, pd.DataFrame([new_row_dict])], ignore_index=True)
        df.to_csv(file_name, index=False)
        return saved_via_gs

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
        except Exception:
            return ["CRDP", "THA"], ["CBD", "CBG"], ["ミルセン", "リモネン"]

    g1_presets, g2_presets, g3_presets = load_excel_presets()

    # --- 背景画像処理 ---
    bg_image_file = "title_bg.png"  
    bg_css_style = "background: linear-gradient(135deg, #130021 0%, #3a0066 100%);" 
    if os.path.exists(bg_image_file):
        try:
            with open(bg_image_file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            bg_css_style = f"background-image: url(data:image/png;base64,{encoded_string}); background-size: cover; background-position: center;"
        except Exception: pass

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #ffffff; color: #000000; }}
        h1, h2, h3, h4, p, label, .stMarkdown {{ color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }}
        .stButton>button {{ 
            background-color: #98FB98 !important; color: #000000 !important; font-weight: bold; border-radius: 8px; border: 1px solid #000000; width: 100%; height: 45px;
        }}
        .group-container {{ border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fafafa; }}
        .group-title {{ font-weight: bold; font-size: 16px; border-left: 4px solid #00ffff; padding-left: 10px; margin-bottom: 15px; }}
        [data-testid="stSidebar"] .stRadio > label div p {{ color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span p {{ color: #ffffff !important; }}
        [data-testid="stSidebar"] div[data-baseweb="radio"] div {{ border-color: rgba(255, 255, 255, 0.6) !important; }}
        .custom-title-banner {{ {bg_css_style} padding: 40px 20px; border-radius: 12px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
        .custom-title-banner h1 {{ color: #ffffff !important; font-size: 32px !important; font-weight: 800 !important; text-shadow: 0 0 10px #00ff00 !important; margin: 0 !important; }}
        .custom-title-banner p {{ color: #ff00ff !important; font-size: 18px !important; font-weight: bold !important; text-shadow: 0 0 8px #ff00ff !important; margin-top: 10px !important; }}
        </style>
        """, unsafe_allow_html=True)

    if "master_g1_rows" not in st.session_state: st.session_state.master_g1_rows = 1
    if "master_g2_rows" not in st.session_state: st.session_state.master_g2_rows = 1
    if "master_g3_rows" not in st.session_state: st.session_state.master_g3_rows = 1

    LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
    LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

    # 📌 サイドバーメニュー
    page = st.sidebar.radio("メニューを選択", ["📝 ワンタップ吸引記録", "🧪 リキッドマスター登録", "🌐 新成分マスター登録", "📅 履歴カレンダー", "📊 成分紹介"])

    # -------------------------------------------------------------------------
    # 📝 ワンタップ吸引記録
    # -------------------------------------------------------------------------
    if page == "📝 ワンタップ吸引記録":
        st.markdown("""<div class="custom-title-banner"><h1>🌿 Cannatics</h1><p>ワンタップ吸引記録</p></div>""", unsafe_allow_html=True)
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        
        if df_master.empty:
            st.warning("⚠️ まだリキッドが登録されていません。先に「🧪 リキッドマスター登録」画面でリキッドを追加してください。")
        else:
            st.subheader("⚡ 選択して即記録")
            selected_liq = st.selectbox("🚬 吸うリキッドを選択", df_master["リキッド名"].tolist())
            liq_detail = df_master[df_master["リキッド名"] == selected_liq]["配合詳細"].values[0]
            st.caption(f"現在の配合: {liq_detail}")
            
            puffs = st.slider("摂取量 (パフ数)", 1, 15, 3)
            log_date = st.date_input("日付を選択", datetime.date.today())
            
            st.markdown(" ")
            if st.button("📊 スプレッドシートへワンタップ記録！"):
                date_str = log_date.strftime("%Y-%m-%d")
                new_log_row = {
                    "日付": date_str, "リキッド名": selected_liq, "パフ数": puffs,
                    "配合詳細": liq_detail, "体感した効果": "", "体感メモ": ""
                }
                success = save_data_to_db("Attraction_Logs", new_log_row, LOG_COLS)
                if success:
                    st.success(f"🎉 {selected_liq} を {puffs}パフ 記録しました！")
                else:
                    st.success(f"🎉 ローカルに保存しました。")

    # -------------------------------------------------------------------------
    # 🧪 リキッドマスター登録
    # -------------------------------------------------------------------------
    elif page == "🧪 リキッドマスター登録":
        st.title("🧪 リキッド名と配合の事前登録")
        new_liquid_name = st.text_input("📦 登録するリキッド名（例: 特製ミックスA）")
        liquid_components = {}

        st.markdown('<div class="group-container"><div class="group-title">🔥 1. 主要精神活性成分</div>', unsafe_allow_html=True)
        if st.button("➕ 活性成分の枠を追加", key="m_add_g1"): st.session_state.master_g1_rows += 1; st.rerun()
        for i in range(st.session_state.master_g1_rows):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"活性成分 {i+1}", g1_presets, key=f"m_g1_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", 0.0, 100.0, step=5.0, key=f"m_g1_p_{i}")
            if pct > 0: liquid_components[name] = pct
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="group-container"><div class="group-title">🌿 2. ベース成分</div>', unsafe_allow_html=True)
        if st.button("➕ ベース成分の枠を追加", key="m_add_g2"): st.session_state.master_g2_rows += 1; st.rerun()
        for i in range(st.session_state.master_g2_rows):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"ベース成分 {i+1}", g2_presets, key=f"m_g2_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", 0.0, 100.0, step=5.0, key=f"m_g2_p_{i}")
            if pct > 0: liquid_components[name] = pct
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="group-container"><div class="group-title">🧪 3. テルペン・その他</div>', unsafe_allow_html=True)
        if st.button("➕ テルペンの枠を追加", key="m_add_g3"): st.session_state.master_g3_rows += 1; st.rerun()
        for i in range(st.session_state.master_g3_rows):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"添加成分 {i+1}", g3_presets, key=f"m_g3_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", 0.0, 100.0, step=1.0, key=f"m_g3_p_{i}")
            if pct > 0: liquid_components[name] = pct
        st.markdown('</div>', unsafe_allow_html=True)
            
        if st.button("💾 このリキッドをマスターに登録"):
            if not new_liquid_name: st.error("リキッド名を入力してください。")
            elif not liquid_components: st.error("成分を入力してください。")
            else:
                details_str = " / ".join([f"{k}:{v}%" for k, v in liquid_components.items()])
                new_master_row = {"リキッド名": new_liquid_name, "配合詳細": details_str}
                save_data_to_db("Liquid_Master", new_master_row, LIQUID_MASTER_COLS)
                st.success(f"🎉 「{new_liquid_name}」を登録しました！")
                st.rerun()

        st.subheader("📋 現在登録されているリキッド一覧")
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        st.dataframe(df_master, use_container_width=True)

    # --- その他の外部ファイル呼び出し ---
    elif page == "🌐 新成分マスター登録":
        try:
            with open("seibunn.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.write("ファイルを確認してください。")
    elif page == "📅 履歴カレンダー":
        try:
            with open("calendar.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.write("ファイルを確認してください。")
    elif page == "📊 成分紹介":
        # 📌 ここで新設する review.py をクリーンに実行
        try:
            with open("review.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception as e: st.error(f"review.pyの読み込みエラー: {e}")
