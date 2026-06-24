import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

st.title("📸 リキッド紹介 & ギャラリー")
st.write("各リキッドの写真と、これまでの体感レビュー履歴をまとめて確認できます。")

# 1. データベース（Excel / スプレッドシート）からデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

if not df_master.empty:
    all_liquids = df_master["リキッド名"].dropna().unique().tolist()
elif not df_logs.empty:
    all_liquids = df_logs["リキッド名"].dropna().unique().tolist()
else:
    all_liquids = []

if not all_liquids:
    st.warning("⚠️ 現在、登録されているリキッドやレビュー履歴はありません。")
else:
    # 🚬 リキッド選択用のドロップダウン
    selected_liq = st.selectbox("🚬 詳細を確認するリキッドを選択", all_liquids)
    
    # 選択リキッドの配合内容を表示
    liq_row = df_master[df_master["リキッド名"] == selected_liq] if not df_master.empty else pd.DataFrame()
    if not liq_row.empty:
        st.info(f"📋 **このリキッドの現在の配合詳細:** {liq_row['配合詳細'].values[0]}")

    # 📸 フォトギャラリー
    st.subheader("🖼️ フォトギャラリー")
    target_logs = df_logs[df_logs["リキッド名"] == selected_liq].copy() if not df_logs.empty else pd.DataFrame()
    
    if not target_logs.empty:
        target_logs['sort_id'] = range(len(target_logs))
        target_logs = target_logs.sort_values(by=['日付', 'sort_id'], ascending=[False, False])
        img_logs = target_logs[target_logs["画像"].notna() & (target_logs["画像"] != "")]
        
        if not img_logs.empty:
            cols = st.columns(3)
            for i, (_, row) in enumerate(img_logs.iterrows()):
                with cols[i % 3]:
                    img_str = str(row["画像"]).strip()
                    if not img_str.startswith("data:image"):
                        img_str = f"data:image/png;base64,{img_str}"
                    
                    st.markdown(f'<img src="{img_str}" style="width:100%; border-radius:5px; margin-bottom:5px;">', unsafe_allow_html=True)
                    st.caption(f"📅 {row['日付']}")
        else:
            st.caption("📸 このリキッドに登録された写真はありません。")
    else:
        st.caption("📸 写真はありません。")

    st.markdown("---")

    # 📋 これまでのレビュー履歴（日付なし）
    st.subheader("📋 これまでのレビュー履歴")
    if not target_logs.empty:
        display_rows = []
        for _, row in target_logs.iterrows():
            eff_text = row['体感した効果']
            if (pd.isna(eff_text) or eff_text == '') and pd.notna(row['パフ数']) and row['パフ数'] > 0:
                eff_text = f"🚬 吸引記録 ({row['パフ数']} puffs)"
            memo_text = row['体感メモ'] if pd.notna(row['体感メモ']) and row['体感メモ'] != '' else "ーー"
            display_rows.append({"内容": eff_text, "メモ": memo_text})
        
        st.table(pd.DataFrame(display_rows))
    else:
        st.caption("📋 レビュー履歴はまだありません。")
