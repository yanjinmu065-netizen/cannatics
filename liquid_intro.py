import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

st.title("📸 リキッド紹介 & ギャラリー")
st.write("これまでに登録した写真とレビューのまとめです。")

# 1. データベースから履歴を取得
if 'load_data_from_db' in globals():
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_logs = pd.DataFrame(columns=LOG_COLS)

if df_logs.empty:
    st.warning("記録がまだありません。")
else:
    liquid_names = df_logs["リキッド名"].dropna().unique().tolist()
    selected_liq = st.selectbox("詳細を確認するリキッドを選択", liquid_names)
    
    # 履歴を絞り込み（最新順）
    target_logs = df_logs[df_logs["リキッド名"] == selected_liq].iloc[::-1]

    # --- 📸 ギャラリー表示 ---
    st.subheader("🖼️ フォトギャラリー")
    # 画像があるものだけ抽出
    img_logs = target_logs[target_logs["画像"] != ""]
    if not img_logs.empty:
        cols = st.columns(3) # 3列で写真を表示
        for i, (_, row) in enumerate(img_logs.iterrows()):
            with cols[i % 3]:
                st.image(f"data:image/png;base64,{row['画像']}", use_column_width=True)
                st.caption(f"記録日: {row['日付']}")
    else:
        st.caption("写真はありません。")

    st.markdown("---")

    # --- 📋 レビュー履歴表 ---
    st.subheader("📋 体感レビュー履歴表")
    # 表として見やすく表示
    display_df = target_logs[["日付", "体感した効果", "体感メモ"]].copy()
    display_df.columns = ["日付", "体感・レビュー", "メモ"]
    st.table(display_df)
