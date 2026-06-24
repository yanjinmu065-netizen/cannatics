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

    # 💡 セッション変数の初期化
    if "m_g1" not in st.session_state: st.session_state.m_g1 = 1
    if "m_g2" not in st.session_state: st.session_state.m_g2 = 1
    if "m_g3" not in st.session_state: st.session_state.m_g3 = 1
    if "edit_target" not in st.session_state: st.session_state.edit_target = None

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

    def save_all_data_to_db(sheet_name, df, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                sh = client.open("Cannatics_Database")
                try:
                    worksheet = sh.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    # シートが無ければ自動で作る
                    worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
                worksheet.clear()
                worksheet.append_row(default_cols)
                if not df.empty:
                    worksheet.append_rows(df[default_cols].astype(str).values.tolist())
                return True
            except Exception: pass
        df.to_csv(f"{sheet_name}.csv", index=False)
        return True

    def save_data_to_db(sheet_name, new_row_dict, default_cols):
        client = get_spreadsheet_client()
        if client:
            try:
                sh = client.open("Cannatics_Database")
                try:
                    worksheet = sh.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
                    worksheet.append_row(default_cols)
                row_to_append = [str(new_row_dict.get(col, "")) for col in default_cols]
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
            df_synthetic = pd.read_excel("data.xlsx", sheet_name="半合成", header=2)
            df_cannabinoid = pd.read_excel("data.xlsx", sheet_name="カンナビノイド", header=2)
            df_terpene = pd.read_excel("data.xlsx", sheet_name="テルペン", header=2)
            g1 = [str(r["成分名"]) for _, r in df_synthetic.dropna(subset=["成分名"]).iterrows()]
            g2 = [str(r["成分名"]) for _, r in df_cannabinoid.dropna(subset=["成分名"]).iterrows()]
            g3 = list(df_terpene["成分名"].dropna().unique())
            return g1, g2, g3
        except Exception: return ["CRDP", "THA"], ["CBD", "CBG"], ["ミルセン", "リモネン"]

    # 💡 永久保存用のカラム定義
    COMP_MASTER_COLS = ["成分名", "分類"]

    # ドロップダウンの初期化とシートからの同期
    if 'g1_presets' not in st.session_state or 'g2_presets' not in st.session_state or 'g3_presets' not in st.session_state:
        g1_init, g2_init, g3_init = load_excel_presets()
        st.session_state['g1_presets'] = g1_init
        st.session_state['g2_presets'] = g2_init
        st.session_state['g3_presets'] = g3_init
        
        # 💡 アプリ起動時に、スプレッドシートに永久保存されている追加成分を自動で読み込んで合流させる
        df_saved_comps = load_data_from_db("Components_Master", COMP_MASTER_COLS)
        if not df_saved_comps.empty:
            for _, r in df_saved_comps.iterrows():
                c_name = str(r["成分名"])
                c_group = str(r["分類"])
                if c_group == "主要成分" and c_name not in st.session_state['g1_presets']:
                    st.session_state['g1_presets'].append(c_name)
                elif "ベース" in c_group and c_name not in st.session_state['g2_presets']:
                    st.session_state['g2_presets'].append(c_name)
                elif "テルペン" in c_group and c_name not in st.session_state['g3_presets']:
                    st.session_state['g3_presets'].append(c_name)

    g1_presets = st.session_state['g1_presets']
    g2_presets = st.session_state['g2_presets']
    g3_presets = st.session_state['g3_presets']

    # --- 🎨 背景画像処理 ---
    bg_style_raw = "linear-gradient(135deg, #130021 0%, #3a0066 100%)"
    if os.path.exists("title_bg.png"):
        try:
            with open("title_bg.png", "rb") as f: encoded = base64.b64encode(f.read()).decode()
            bg_style_raw = f"url(data:image/png;base64,{encoded}) center/cover"
        except Exception: pass

    css_code = """
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        h1, h2, h3, h4, p, label { color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }
        .stButton>button { 
            background-color: #98FB98 !important; color: #000000 !important; font-weight: bold; border-radius: 8px; border: 1px solid #000000; width: 100%; height: 45px;
        }
        .group-container { border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fafafa; }
        .custom-title-banner { background: BACKGROUND_PLACEHOLDER; padding: 40px 20px; border-radius: 12px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .custom-title-banner h1 { color: #ffffff !important; font-size: 34px !important; font-weight: 800 !important; text-shadow: 0 0 10px #00ff00 !important; margin: 0 !important; }
        .custom-title-banner p { color: #ff00ff !important; font-size: 18px !important; font-weight: bold !important; text-shadow: 0 0 8px #ff00ff !important; margin-top: 10px !important; }
        [data-testid="stSidebar"] { background: BACKGROUND_PLACEHOLDER; border-right: 2px solid #ff00ff; }
        [data-testid="stSidebar"] .stRadio > label div p { color: #ffffff !important; font-weight: 900 !important; font-size: 18px !important; text-shadow: 0 0 5px #00ff00 !important; margin-bottom: 10px; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span p,
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div p,
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #ffffff !important; font-weight: bold !important; font-size: 14px !important; }
        [data-testid="stSidebar"] div[data-baseweb="radio"] div { border-color: #00ff00 !important; background-color: rgba(0, 0, 0, 0.4) !important; }
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] span p,
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] div p { color: #ff00ff !important; text-shadow: 0 0 8px #ff00ff !important; }
        [data-testid="stSidebar"] div[data-baseweb="radio"][aria-checked="true"] div div { background-color: #ff00ff !important; }
        </style>
    """.replace("BACKGROUND_PLACEHOLDER", bg_style_raw)

    st.markdown(css_code, unsafe_allow_html=True)

    page = st.sidebar.radio("メニューを選択", ["📝 ワンタップ吸引記録", "🧪 リキッドマスター登録", "🌐 新成分マスター登録", "📅 履歴カレンダー", "📊 成分紹介"])

    banner_titles = {
        "📝 ワンタップ吸引記録": "ワンタップ吸引記録",
        "🧪 リキッドマスター登録": "リキッドマスター設定",
        "🌐 新成分マスター登録": "新成分の追加登録",
        "📅 履歴カレンダー": "使用履歴カレンダー",
        "📊 成分紹介": "リキッド紹介 & レビュー"
    }
    current_title = banner_titles.get(page, "Cannatics")
    st.markdown(f"""<div class="custom-title-banner"><h1>🌿 Cannatics</h1><p>{current_title}</p></div>""", unsafe_allow_html=True)

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
        df_master = load_data_from_db("Liquid_Master", LIQUID_MASTER_COLS)
        
        st.subheader("📦 登録済みのリキッド一覧・編集・削除")
        if df_master.empty:
            st.caption("現在登録されているリキッドはありません。")
        else:
            for index, row in df_master.iterrows():
                col_name, col_detail, col_btn1, col_btn2 = st.columns([2, 4, 1, 1])
                with col_name: st.markdown(f"**{row['リキッド名']}**")
                with col_detail: st.caption(row['配合詳細'])
                with col_btn1:
                    if st.button("📝 編集", key=f"edit_btn_{index}"):
                        st.session_state.edit_target = row['リキッド名']
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 削除", key=f"del_btn_{index}"):
                        df_updated = df_master.drop(index)
                        save_all_data_to_db("Liquid_Master", df_updated, LIQUID_MASTER_COLS)
                        st.success(f"「{row['リキッド名']}」を削除しました。")
                        st.rerun()

        st.markdown("---")
        
        if st.session_state.edit_target:
            st.subheader("🧪 登録内容の編集・上書き")
            new_liq_name = st.text_input(f"📦 修正後のリキッド名 (元の名前: {st.session_state.edit_target})", value=st.session_state.edit_target, key="master_target_liquid_name_edit")
        else:
            st.subheader("🧪 新規リキッドの登録")
            new_liq_name = st.text_input("📦 新しいリキッド名", value="", key="master_target_liquid_name_new")
            
        st.write("配合割合を入力してください。")
        
        g1_total = 0.0
        g2_total = 0.0
        g3_total = 0.0
        
        g1_data = []
        for i in range(st.session_state.m_g1):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"主要成分 {i+1}", g1_presets, key=f"g1_n_{i}")
            with c2: pct = st.number_input(f"比率%##{i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key=f"g1_p_{i}")
            g1_data.append((name, pct))
            g1_total += pct
        if st.button("➕ 主要成分を追加", key="btn_add_g1"):
            st.session_state.m_g1 += 1
            st.rerun()
            
        g2_data = []
        for i in range(st.session_state.m_g2):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"天然成分 {i+1}", g2_presets, key=f"g2_n_{i}")
            with c2: pct = st.number_input(f"比率% (天然)##{i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key=f"g2_p_{i}")
            g2_data.append((name, pct))
            g2_total += pct
        if st.button("➕ カンナビノイド成分を追加", key="btn_add_g2"):
            st.session_state.m_g2 += 1
            st.rerun()

        g3_data = []
        for i in range(st.session_state.m_g3):
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"テルペン {i+1}", g3_presets, key=f"g3_n_{i}")
            with c2: pct = st.number_input(f"比率% (テルペン)##{i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key=f"g3_p_{i}")
            g3_data.append((name, pct))
            g3_total += pct
        if st.button("➕ テルペン成分を追加", key="btn_add_g3"):
            st.session_state.m_g3 += 1
            st.rerun()

        total_all = g1_total + g2_total + g3_total
        st.markdown("---")
        st.markdown("### 📊 現在の配合比率（リアルタイム計算）")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("🧬 主要成分 合計", f"{g1_total:.1f} %")
        col_m2.metric("🌿 天然成分 合計", f"{g2_total:.1f} %")
        col_m3.metric("🍋 テルペン 合計", f"{g3_total:.1f} %")
        
        if total_all > 100.0:
            st.error(f"🚨 **総合合計が100%を超えています！ ({total_all:.1f} %)**")
        else:
            col_m4.metric("🏆 総合合計", f"{total_all:.1f} %")
        st.markdown("---")

        btn_label = "💾 編集内容を上書き保存" if st.session_state.edit_target else "💾 マスターに登録"
        
        if st.session_state.edit_target:
            c_save, c_cancel = st.columns(2)
            with c_save: save_clicked = st.button(btn_label, key="btn_save_master")
            with c_cancel:
                if st.button("❌ 編集をキャンセル"):
                    st.session_state.edit_target = None
                    st.rerun()
        else:
            save_clicked = st.button(btn_label, key="btn_save_master")

        if save_clicked:
            if not new_liq_name:
                st.error("リキッド名を入力してください")
            else:
                parts = []
                for n, p in g1_data + g2_data + g3_data:
                    if p > 0.0: 
                        p_str = f"{int(p)}" if p.is_integer() else f"{p:.1f}"
                        parts.append(f"{n}:{p_str}%")
                if not parts:
                    st.error("比率が0.1%以上の成分を1つ以上入力してください")
                else:
                    detail_str = ", ".join(parts)
                    
                    if st.session_state.edit_target:
                        df_master = df_master[df_master["リキッド名"] != st.session_state.edit_target]
                        new_row = pd.DataFrame([{"リキッド名": new_liq_name, "配合詳細": detail_str}])
                        df_updated = pd.concat([df_master, new_row], ignore_index=True)
                        save_all_data_to_db("Liquid_Master", df_updated, LIQUID_MASTER_COLS)
                        st.success(f"🎉 「{new_liq_name}」に編集内容を上書き保存しました！")
                        st.session_state.edit_target = None
                    else:
                        save_data_to_db("Liquid_Master", {"リキッド名": new_liq_name, "配合詳細": detail_str}, LIQUID_MASTER_COLS)
                        st.success(f"🎉 「{new_liq_name}」を新規登録しました！")
                    st.rerun()

    elif page == "📊 成分紹介":
        try:
            with open("review.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception as e: st.error(f"読み込みエラー: {e}")

    elif page == "🌐 新成分マスター登録":
        try:
            with open("seibunn.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception as e: st.error(f"⚠️ 新成分マスターの読み込みに失敗しました: {e}")
        
    elif page == "📅 履歴カレンダー":
        try:
            with open("calendar.py", encoding="utf-8") as f: exec(f.read(), globals())
        except Exception as e: st.error(f"⚠️ 履歴カレンダーの読み込みに失敗しました: {e}")
