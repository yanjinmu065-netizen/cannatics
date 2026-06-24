import streamlit as st
import pandas as pd
import os

# --- 🔌 Googleスプレッドシート連携用（review用独立版） ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD_REV = True
except ImportError:
    HAS_GSPREAD_REV = False

def get_spreadsheet_client_review():
    if not HAS_GSPREAD_REV:
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
    except Exception:
        return None
    return None

def load_data_for_review(sheet_name, default_cols):
    client = get_spreadsheet_client_review()
    if client:
        try:
            sh = client.open("Cannatics_Database")
            try:
                worksheet = sh.worksheet(sheet_name)
                df = pd.DataFrame(worksheet.get_all_records())
                return df if not df.empty else pd.DataFrame(columns=default_cols)
            except Exception:
                return pd.DataFrame(columns=default_cols)
        except Exception:
            pass
    
    file_name = f"{sheet_name}.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return pd.DataFrame(columns=default_cols)

# --- ✨ 表示処理 ---
st.title("📊 リキッド・成分紹介 & レビュー")

LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

df_master = load_data_for_review("Liquid_Master", LIQUID_MASTER_COLS)
df_logs = load_data_for_review("Attraction_Logs", LOG_COLS)

tab1, tab2 = st.tabs(["🧪 登録リキッドとみんなのレビュー", "📖 基礎成分カタログ(Excel)"])

with tab1:
    if df_master.empty:
        st.info("まだ登録されているリキッドがありません。")
    else:
        st.subheader("📦 登録リキッドの紹介")
        target_liq = st.selectbox("詳細を見たいリキッドを選択してください", df_master["リキッド名"].tolist())
        detail_text = df_master[df_master["リキッド名"] == target_liq]["配合詳細"].values[0]
        
        st.markdown(f"""
        <div style="background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <h4 style="margin:0; color:#15803d;">🧬 {target_liq} の配合レシピ</h4>
            <p style="margin: 8px 0 0 0; font-size: 16px; font-weight: bold; color: #000000;">{detail_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader(f"💬 {target_liq} のレビュー・吸引履歴")
        if not df_logs.empty:
            filtered_logs = df_logs[df_logs["リキッド名"] == target_liq].copy()
            if filtered_logs.empty:
                st.write("このリキッドのレビュー・吸引ログはまだありません。")
            else:
                display_logs = filtered_logs[["日付", "パフ数", "体感した効果", "体感メモ"]].sort_values(by="日付", ascending=False)
                st.dataframe(display_logs, use_container_width=True, hide_index=True)
        else:
            st.write("吸引履歴がまだ1件もありません。")

with tab2:
    st.subheader("📖 data.xlsx の成分カタログ")
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        try:
            excel_file = pd.ExcelFile(file_path)
            selected_sheet = st.selectbox("表示するシートを選択", excel_file.sheet_names)
            df_excel = pd.read_excel(file_path, sheet_name=selected_sheet, header=2).dropna(how='all')
            st.dataframe(df_excel, use_container_width=True)
        except Exception as e:
            st.error(f"Excel読み込みエラー: {e}")
    else:
        st.warning("⚠️ data.xlsx が見つかりません。")
