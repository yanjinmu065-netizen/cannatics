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

    # --- 🔗 データベース接続・読み書き関数 (home.py/review.py共用) ---
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

    # --- 🎨 背景画像と共通CSS ---
    bg_image_file = "title_bg.png"  
    bg_css_style = "background: linear-gradient(135deg, #130021 0%, #3a0066 100%);" 
    if os.path.exists(bg_image_file):
        try:
            with open(bg_image_file, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode()
            bg_css_style = f"background-image: url(data:image/png;base64,{encoded_string}); background-size: cover; background-position: center;"
        except Exception: pass

    st.markdown(f"""
        <style>
        /* メイン画面のスタイル */
        .stApp {{ background-color: #ffffff; color: #000000; }}
        h1, h2, h3, h4, p, label {{ color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }}
        .stButton>button {{ 
            background-color: #98FB9
