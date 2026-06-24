import streamlit as st
import pandas as pd
import os

# 1. ページ設定とカスタムCSS（デザイン修正：指定箇所のみ適用）
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

# 2. 簡易的なログイン管理（元々のログイン画面の仕組み）
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ログイン - Cannatics")
    password_input = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        # ここにご自身の元のパスワードを設定してください（例: "your_password"）
        if password_input == "your_password":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
else:
    # 3. メニュー切り替え（元のメニュー ＋「成分紹介」を追加）
    page = st.sidebar.radio("メニューを選択", ["配合電卓・分析", "新成分マスター登録", "履歴カレンダー", "成分紹介"])

    # --- 配合電卓・分析（修正前の元のコードの状態に戻しています） ---
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

    # --- 成分紹介（Excel表示の改善版） ---
    elif page == "成分紹介":
        st.title("📊 成分紹介ページ")
        st.write("`data.xlsx` に登録されている成分の一覧表です。")
        
        file_path = "data.xlsx"
        
        if os.path.exists(file_path):
            try:
                # Excelファイルを読み込み
                df = pd.read_excel(file_path)
                
                # データが空っぽでなければ表として綺麗に表示
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Excelファイルの中にデータが入っていません（空のファイルです）。")
            except Exception as e:
                st.error(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
                st.info("※ openpyxl がインストールされていないか、ファイルが破損している可能性があります。")
        else:
            st.warning("`data.xlsx` が見つかりませんでした。GitHubの `main` ブランチにファイルが正しくアップロードされているか確認してください。")
