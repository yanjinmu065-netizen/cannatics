import streamlit as st
import pandas as pd
import os

# 1. ページ設定とカスタムCSS（指定のデザインのみ適用）
st.set_page_config(page_title="Cannatics", layout="wide")

st.markdown("""
<style>
    /* サイドバーのリンク文字色を白にする */
    [data-testid="stSidebarNav"] ul li a span {
        color: white !important;
    }
    /* 枠を追加・枠を削除ボタンの色を #98FB98 にする */
    div.stButton > button {
        background-color: #98FB98 !important;
        color: #000000 !important; /* 文字色は見やすいように黒に */
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 簡易的なログイン管理
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ログイン - Cannatics")
    password_input = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        # ここにご自身の元のパスワードを設定してください
        if password_input == "your_password":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
else:
    # 3. メニュー切り替え
    page = st.sidebar.radio("メニューを選択", ["配合電卓・分析", "新成分マスター登録", "履歴カレンダー", "成分紹介"])

    # --- 配合電卓・分析（元の状態を完全キープ） ---
    if page == "配合電卓・分析":
        st.title("🌿 Cannatics (カンナティクス)")
        st.subheader("🧪 グループ別・配合電卓")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("＋ 枠を追加")
        with col2:
            st.button("－ 枠を削除")
            
        st.caption("🔥 1. 主要精神活性成分（半合成等）")
        
        st.selectbox("活性成分 1", ["H4CBH ⚠️", "CRDP"])
        st.number_input("比率 1 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.01)
        
        st.selectbox("活性成分 2", ["CRDP", "H4CBH ⚠️"], index=0)
        st.number_input("比率 2 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.01)
        
        st.write("活性成分 合計値")
        st.markdown("## 50.0 %")

    # --- 新成分マスター登録（元の状態） ---
    elif page == "新成分マスター登録":
        st.title("🌐 新成分マスター登録")
        st.write("ここに新しい成分の登録画面を作成します。")

    # --- 履歴カレンダー（元の状態） ---
    elif page == "履歴カレンダー":
        st.title("📅 履歴カレンダー")
        st.write("ここに配合履歴のカレンダーを表示します。")

    # --- 成分紹介（シート切り替え対応・見栄え修正版） ---
    elif page == "成分紹介":
        st.title("📊 成分紹介ページ")
        st.write("`data.xlsx` に登録されている成分の一覧表です。")
        
        file_path = "data.xlsx"
        
        if os.path.exists(file_path):
            try:
                # Excelファイルのすべてのシート名を取得
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                # サイドバーまたは画面上にシート選択のドロップダウンを表示
                selected_sheet = st.selectbox("表示するシートを選択してください", sheet_names)
                
                # 選択されたシートを読み込む（1行目のズレを自動調整）
                df = pd.read_excel(file_path, sheet_name=selected_sheet)
                
                # もし最初の行が空欄だらけで、2行目に項目名があるような場合の簡易クリーンアップ
                if "Unnamed:" in "".join([str(col) for col in df.columns]):
                    # 最初の行を項目名として仕切り直す
                    df = pd.read_excel(file_path, sheet_name=selected_sheet, header=1)
                
                # 完全に空の行や列を非表示にする調整をして表示
                df = df.dropna(how='all')
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"【{selected_sheet}】シートの中にはデータが入っていません。")
                    
            except Exception as e:
                st.error(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
        else:
            st.warning("`data.xlsx` が見つかりませんでした。")
