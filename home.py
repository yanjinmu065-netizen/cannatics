import streamlit as st
import pandas as pd
import datetime
import os
import base64
import json

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
        if username == "0602" and password == "admin": 
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
            # StreamlitのSecrets（環境変数）またはローカルのjsonファイルから認証
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

    # --- 💾 データの読み込み・保存処理（スプレッドシートまたはローカルCSVでの代替） ---
    def load_data_from_db(sheet_name, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                # 「Cannatics_Database」という名前のスプレッドシートを開く
                sh = client.open("Cannatics_Database")
                try:
                    worksheet = sh.worksheet(sheet_name)
                    df = pd.DataFrame(worksheet.get_all_records())
                    return df if not df.empty else pd.DataFrame(columns=default_cols)
                except gspread.exceptions.WorksheetNotFound:
                    # シートがなければ自動作成
                    worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols=str(len(default_cols)))
                    worksheet.append_row(default_cols)
                    return pd.DataFrame(columns=default_cols)
            except Exception as e:
                st.sidebar.warning(f"スプレッドシート読み込み失敗（CSVで代替します）: {e}")
        
        # 予備：ローカルファイル保存
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
                # 辞書の並び順を列名に合わせる
                row_to_append = [new_row_dict.get(col, "") for col in default_cols]
                worksheet.append_row(row_to_append)
                saved_via_gs = True
            except Exception as e:
                st.sidebar.error(f"スプレッドシート保存失敗: {e}")
        
        # 常にローカルCSVにもバックアップ保存
        file_name = f"{sheet_name}.csv"
        df = load_data_from_db(sheet_name, default_cols)
        df = pd.concat([df, pd.DataFrame([new_row_dict])], ignore_index=True)
        df.to_csv(file_name, index=False)
        return saved_via_gs

    # --- Excelデータから成分と効果を自動抽出 ---
    @st.cache_data
    def load_excel_and_extract_tags():
        try:
            df_cannabinoid = pd.read_excel("data.xlsx", sheet_name="カンナビノイド", header=2)
            df_synthetic = pd.read_excel("data.xlsx", sheet_name="半合成", header=2)
            df_terpene = pd.read_excel("data.xlsx", sheet_name="テルペン", header=2)
            
            g1_list, g2_list, g3_list = [], [], []
            if "成分名" in df_synthetic.columns:
                g1_list = [f"{r['成分名']}" for _, r in df_synthetic.dropna(subset=["成分名"]).iterrows()]
            if "成分名" in df_cannabinoid.columns:
                g2_list = [f"{r['成分名']}" for _, r in df_cannabinoid.dropna(subset=["成分名"]).iterrows()]
            if "成分名" in df_terpene.columns:
                g3_list = list(df_terpene["成分名"].dropna().unique())
            
            all_effects = set()
            for df in [df_cannabinoid, df_synthetic, df_terpene]:
                if "効果" in df.columns:
                    for eff_str in df["効果"].dropna():
                        for e in str(eff_str).replace("、", ",").split(","):
                            if e.strip(): all_effects.add(e.strip())
                                
            return g1_list, g2_list, g3_list, sorted(list(all_effects))
        except Exception:
            return ["CRDP", "THA"], ["CBD", "CBG"], ["ミルセン", "リモネン"], ["リラックス", "多幸感", "眠気"]

    g1_presets, g2_presets, g3_presets, extracted_effects = load_excel_and_extract_tags()

    # --- 背景画像処理 ---
    bg_image_file = "title_bg.png"  
    bg_css_style = "background: linear-gradient(135deg, #130021 0%, #3a0066 100%);" 
    if os.path.exists(bg_image_file):
        try:
            with open(bg_image_file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            bg_css_style = f"background-image: url(data:image/png;base64,{encoded_string}); background-size: cover; background-position: center;"
        except Exception: pass

    # カスタムCSS
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

    # データベースの列定義
    LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
    LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

    # サイドバーメニュー
    page = st.sidebar.radio("メニューを選択", ["📝 ワンタップ吸引記録", "🧪 リキッドマスター登録", "🌐 新成分マスター登録", "📅 履歴カレンダー", "📊 成分紹介"])

    # -------------------------------------------------------------------------
    # 🧪 新機能：リキッドマスター登録（事前にお気に入りの配合と名前を決めておく）
    # -------------------------------------------------------------------------
    if page == "🧪 リキッドマスター登録":
        st.title("🧪 リキッド名と配合の事前登録")
        st.write("毎回成分を入力する手間を省くため、ここにリキッドの名前と配合比率を登録しておきましょう！")
        
        new_liquid_name = st.text_input("📦 登録するリキッド名（例: 特製ミックスA, プレミアムCRDP）")
        
        st.markdown("👇 このリキッドに含まれる成分と比率を入力してください")
        c1, c2, c3 = st.columns(3)
        with c1:
            g1_sel = st.multiselect("主要活性成分", g1_presets)
            g1_p = {name: st.number_input(f"{name} 比率(%)", 0.0, 100.0, step=5.0, key=f"m_g1_{name}") for name in g1_sel}
        with c2:
            g2_sel = st.multiselect("ベース成分", g2_presets)
            g2_p = {name: st.number_input(f"{name} 比率(%)", 0.0, 100.0, step=5.0, key=f"m_g2_{name}") for name in g2_sel}
        with c3:
            g3_sel = st.multiselect("テルペン", g3_presets)
            g3_p = {name: st.number_input(f"{name} 比率(%)", 0.0, 100.0, step=1.0, key=f"m_g3_{name}") for name in g3_sel}
            
        if st.button("💾 このリキッドをマスターに登録"):
            if not new_liquid_name:
                st.error("リキッド名を入力してください。")
            else:
                # 配合データを1つの文字列にまとめる (例: CRDP:40%/CBD:30%)
                all_p = {**g1_p, **g2_p, **g3_p}
                details_str = " / ".join([f"{k}:{v}%" for k, v in all_p.items() if v > 0])
                
                new_master_row = {"リキッド名": new_liquid_name, "配合詳細": details_str}
                success = save_data_to_db("Liquid_Master", new_master_row, LIQUID_MASTER_COLS)
                
                if success:
                    st.success(f"🎉 「{new_liquid_name}」をGoogleスプレッドシートに登録しました！")
                else:
                    st.success(f"🎉 「{new_liquid_name}」を一時保存しました（スプレッドシート未連携）。")

        st.markdown("---")
        st.subheader("📋 現在登録されているリキッド一覧")
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        st.dataframe(df_master, use_container_width=True)

    # -------------------------------------------------------------------------
    # 📝 修正・強化機能：ワンタップ吸引記録（名前を選ぶだけで一発保存）
    # -------------------------------------------------------------------------
    elif page == "📝 ワンタップ吸引記録":
        st.markdown("""<div class="custom-title-banner"><h1>🌿 Cannatics (カンナティクス)</h1><p>ワンタップ吸引記録 & ログ</p></div>""", unsafe_allow_html=True)
        
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        
        if df_master.empty:
            st.warning("⚠️ まだリキッドが登録されていません。先に「🧪 リキッドマスター登録」から登録してください。")
        else:
            st.subheader("⚡ リキッドを選んで記録")
            
            # 1. 登録されたリキッド名を選ぶだけで中身が自動決定！
            selected_liq = st.selectbox("🚬 吸うリキッドを選択してください", df_master["リキッド名"].tolist())
            liq_detail = df_master[df_master["リキッド名"] == selected_liq]["配合詳細"].values[0]
            st.info(f"📋 選択中の配合: {liq_detail}")
            
            # 2. パフ数と日付を選ぶ
            puffs = st.slider("今回の摂取量 (パフ数)", 1, 10, 3)
            log_date = st.date_input("記録する日付", datetime.date.today())
            
            st.markdown("---")
            st.subheader("🟢 体感レビュー（あとからスプレッドシートで書く場合は空欄でOK！）")
            selected_effects = st.multiselect("体感した効果・副反応", extracted_effects)
            user_memo = st.text_area("体感メモ（自由記述）")
            
            if st.button("📊 スプレッドシートへ保存"):
                date_str = log_date.strftime("%Y-%m-%d")
                effects_str = ", ".join(selected_effects)
                
                new_log_row = {
                    "日付": date_str,
                    "リキッド名": selected_liq,
                    "パフ数": puffs,
                    "配合詳細": liq_detail,
                    "体感した効果": effects_str,
                    "体感メモ": user_memo
                }
                
                success = save_data_to_db("Attraction_Logs", new_log_row, LOG_COLS)
                if success:
                    st.success(f"🎉 {date_str} のログをGoogleスプレッドシートへ完全に保存しました！")
                else:
                    st.success(f"🎉 ログを端末内にローカル保存しました。")

    # --- その他の既存ページ（エラー回避のため残し） ---
    elif page == "🌐 新成分マスター登録":
        try:
            with open("seibunn.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.title("🌐 新成分マスター登録"); st.write("ファイルを確認してください。")
    elif page == "📅 履歴カレンダー":
        try:
            with open("calendar.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception: st.title("📅 履歴カレンダー"); st.write("ファイルを確認してください。")
    elif page == "📊 成分紹介":
        st.title("📊 カンナティクス 成分紹介")
        file_path = "data.xlsx"
        if os.path.exists(file_path):
            try:
                excel_file = pd.ExcelFile(file_path)
                selected_sheet = st.selectbox("シートを選択", excel_file.sheet_names)
                df = pd.read_excel(file_path, sheet_name=selected_sheet, header=2).dropna(how='all')
                st.dataframe(df, use_container_width=True)
            except Exception as e: st.error(f"エラー: {e}")
