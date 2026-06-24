import streamlit as st
import pandas as pd

# ページ設定とカスタムCSS（デザイン修正）
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

# 簡易的なログイン管理
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ログイン - Cannatics")
    password_input = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        # ここにご自身のパスワードを設定してください（例: "your_password"）
        if password_input == "your_password":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
else:
    # ログイン成功後のメインメニュー（サイドバーで切り替え）
    page = st.sidebar.radio("メニューを選択", ["配合電卓・分析", "新成分マスター登録", "履歴カレンダー", "成分紹介"])

    if page == "配合電卓・分析":
        st.title("🌿 Cannatics (カンナティクス)")
        st.subheader("🧪 グループ別・配合電卓")
        
        # ボタンの配置と枠の追加/削除のモック
        col1, col2 = st.columns(2)
        with col1:
            st.button("＋ 枠を追加")
        with col2:
            st.button("－ 枠を削除")
            
        st.caption("🔥 1. 主要精神活性成分（半合成等）")
        
        # 活性成分1
        st.selectbox("活性成分 1", ["H4CBH ⚠️", "CRDP"])
        st.number_input("比率 1 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.01)
        
        # 活性成分2
        st.selectbox("活性成分 2", ["CRDP", "H4CBH ⚠️"], index=0)
        st.number_input("比率 2 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.01)
        
        st.write("活性成分 合計値")
        st.markdown("## 50.0 %")

    elif page == "新成分マスター登録":
        st.title("🌐 新成分マスター登録")
        st.write("ここに新しい成分の登録画面を作成します。")

    elif page == "履歴カレンダー":
        st.title("📅 履歴カレンダー")
        st.write("ここに配合履歴のカレンダーを表示します。")

    elif page == "成分紹介":
        st.title("📊 成分紹介ページ")
        st.write("`data.xlsx` に登録されている成分の一覧表です。")
        
        # Excelファイルの読み込みと表示
        try:
            df = pd.read_excel("data.xlsx")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning("data.xlsx を読み込めませんでした。ファイルがリポジトリに存在するか確認してください。")
                }
                st.success(f"🎉 {date_str} のログを保存しました！『📅 履歴カレンダー』を確認してください。")
    else:
        pg.run()
