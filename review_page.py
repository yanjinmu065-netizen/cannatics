import streamlit as st
import pandas as pd
import base64
import os

# --- カラム構造の定義（home.py側で定義されている共通構造を使用） ---
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

# CSSスタイル（home.pyの stApps背景色を上書きして白ベースに、履歴を見やすく）
st.markdown("""
<style>
/* リキッド紹介画面専用のクリーンなスタイル */
[data-testid="stApp"] { background-color: #ffffff !important; }
h1, h2, h3, h4, p, label { color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }

/* 統一バナーデザイン（白基調） */
.review-title-banner {
    background-color: #f8f9fa;
    padding: 30px 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #e0e0e0;
}
.review-title-banner h1 {
    color: #333333 !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
.review-title-banner p {
    color: #666666 !important;
    font-size: 15px !important;
    font-weight: bold !important;
    margin-top: 8px !important;
}

/* 履歴の一覧（コンテナ）を見やすく */
.history-container {
    background-color: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* 履歴内の体感ラベル（少し小さくしてすっきり） */
.stMarkdown span {
    font-size: 13px !important;
    color: #555 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 成分紹介")
st.write("各リキッドの成分と、これまでの体感レビュー履歴をまとめて確認できます。")

# 1. データベースから履歴データを取得
if 'load_data_from_db' in globals():
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_logs = pd.DataFrame(columns=LOG_COLS)

if df_logs.empty:
    st.warning("⚠️ まだレビューや吸引の記録はありません。")
else:
    # 現在登録されているリキッド名の一覧を取得
    liquid_names = df_logs["リキッド名"].dropna().unique().tolist()
    
    if not liquid_names:
        st.warning("⚠️ まだレビューや吸引の記録はありません。")
    else:
        # リキッド選択用のドロップダウン
        selected_liq = st.selectbox("🚬 詳細を確認するリキッドを選択", liquid_names)
        
        # 選択されたリキッドの最新の配合詳細を取得して表示
        latest_detail = df_logs[df_logs["リキッド名"] == selected_liq]["配合詳細"].values[0]
        st.caption(f"現在の配合詳細: {latest_detail}")
        
        st.markdown("---")

        # === 📋 過去のレビュー履歴一覧 ===
        st.subheader("📋 これまでのレビュー・体感履歴一覧")
        
        # このリキッドに関する記録だけを絞り込んで表示
        target_logs = df_logs[df_logs["リキッド名"] == selected_liq].copy()
        
        if target_logs.empty:
            st.caption(f"「{selected_liq}」に関するレビューはまだありません。")
        else:
            # 最新の記録が上にくるように並び替え（日付順、同じ日付なら登録が新しい順）
            target_logs['sort_id'] = range(len(target_logs))
            target_logs = target_logs.sort_values(by=['日付', 'sort_id'], ascending=[False, False])
            
            for _, row in target_logs.iterrows():
                with st.container():
                    st.markdown('<div class="history-container">', unsafe_allow_html=True)
                    
                    # 📅 日付カラムを削除し、体感とメモの2カラム構成（比率 6:4）にしてすっきりさせました
                    c_eff, c_memo = st.columns([6, 4])
                    
                    with c_eff:
                        # 吸引記録（パフ数があるもの）と、レビューボタンからの入力を区別
                        if pd.notna(row['体感した効果']) and row['体感した効果'] != '':
                            st.markdown(f"`{row['体感した効果']}`")
                        else:
                            st.caption(f"吸引記録 ({row['パフ数']} puffs)")
                            
                    with c_memo:
                        # 体感メモがある場合は表示
                        if pd.notna(row['体感メモ']) and row['体感メモ'] != '':
                            st.write(row['体感メモ'])
                        else:
                            st.caption("ーー")
                    
                    # 履歴の下に配合詳細を小さく表示
                    st.caption(f"保存時の配合: {row['配合詳細']}")
                    st.markdown('</div>', unsafe_allow_html=True)
