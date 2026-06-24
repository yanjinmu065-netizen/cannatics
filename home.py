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
            background-color: #98FB98 !important; color: #000000 !important; font-weight: bold
