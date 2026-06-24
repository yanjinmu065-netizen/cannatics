import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

st.title("📸 リキッド・成分紹介 & ギャラリー")
st.write("各リキッドに配合されている成分の詳細と、これまでの写真・レビュー履歴をまとめて確認できます。")

# 1. データベース（Excel / スプレッドシート）からデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

# 表示するリキッド名のリスト（Excelのマスターデータを優先）
if not df_master.empty:
    all_liquids = df_master["リキッド名"].dropna().unique().tolist()
elif not df_logs.empty:
    all_liquids = df_logs["リキッド名"].dropna().unique().tolist()
else:
    all_liquids = []

if not all_liquids:
    st.warning("⚠️ まだExcelにリキッドが登録されていないか、レビューの記録がありません。")
else:
    # 🚬 リキッド選択用のドロップダウン
    selected_liq = st.selectbox("🚬 詳細を確認するリキッドを選択", all_liquids)
    
    st.markdown("---")

    # =========================================================
    # 🧪 【重要】Excelから取得した成分一覧の表示セクション
    # =========================================================
    st.subheader("🧪 配合成分一覧（Excelデータ）")
    
    # 選択されたリキッドの行をExcelのマスターから探す
    liq_row = df_master[df_master["リキッド名"] == selected_liq] if not df_master.empty else pd.DataFrame()
    
    if not liq_row.empty:
        detail_str = str(liq_row["配合詳細"].values[0])
        
        # 画面に分かりやすく目立つように表示
        st.info(f"📋 **このリキッドの成分配合:**\n\n{detail_str}")
        
        # もし「CBD:30%, THC:5%」のようにカンマで区切られていれば、表形式にも直してあげる（おまけ機能）
        if "," in detail_str or ":" in detail_str:
            try:
                components = [c.strip() for c in detail_str.split(",") if c.strip()]
                comp_data = []
                for comp in components:
                    if ":" in comp:
                        name, rate = comp.split(":", 1)
                        comp_data.append({"成分名": name.strip(), "配合比率": rate.strip()})
                    else:
                        comp_data.append({"成分名": comp, "配合比率": "ー"})
                if comp_data:
                    st.markdown("**📊 成分早見表**")
                    st.table(pd.DataFrame(comp_data))
            except:
                pass
    else:
        # マスターにないが履歴にある場合
        latest_log = df_logs[df_logs["リキッド名"] == selected_liq] if not df_logs.empty else pd.DataFrame()
        if not latest_log.empty:
            st.info(f"📋 **記録時の配合詳細:** {latest_log['配合詳細'].iloc[0]}")
        else:
            st.caption("⚠️ Excelのマスターデータに配合詳細が見つかりませんでした。")

    st.markdown("---")

    # =========================================================
    # 🖼️ フォトギャラリー セクション
    # =========================================================
    st.subheader("🖼️ フォトギャラリー")
    
    target_logs = df_logs[df_logs["リキッド名"] == selected_liq].copy() if not df_logs.empty else pd.DataFrame()
    
    if not target_logs.empty:
        # 最新順に並び替え
        target_logs['sort_id'] = range(len(target_logs))
        target_logs = target_logs.sort_values(by=['日付', 'sort_id'], ascending=[False, False])
        
        # 画像がある行だけ
        img_logs = target_logs[target_logs["画像"].notna() & (target_logs["画像"] != "")]
        
        if not img_logs.empty:
            cols = st.columns(3)
            for i, (_, row) in enumerate(img_logs.iterrows()):
                with cols[i % 3]:
                    st.image(f"data:image/png;base64,{row['画像']}", use_column_width=True)
                    st.caption(f"📅 {row['日付']}")
        else:
            st.caption("📸 このリキッドに登録された写真はありません。")
    else:
        st.caption("📸 写真はありません。")

    st.markdown("---")

    # =========================================================
    # 📋 体感レビュー履歴表 セクション
    # =========================================================
    st.subheader("📋 これまでのレビュー履歴")
    
    if not target_logs.empty:
        display_rows = []
        for _, row in target_logs.iterrows():
            eff_text = row['体感した効果']
            if (pd.isna(eff_text) or eff_text == '') and pd.notna(row['パフ数']) and row['パフ数'] > 0:
                eff_text = f"🚬 吸引記録 ({row['パフ数']} puffs)"
            
            memo_text = row['体感メモ'] if pd.notna(row['体感メモ']) and row['体感メモ'] != '' else "ーー"
            
            # 💡 日付の非表示要望に合わせ、表の「中身」からは日付をあえて抜くか、もしくは表として並べる
            display_rows.append({
                "内容": eff_text,
                "メモ": memo_text
            })
        
        display_df = pd.DataFrame(display_rows)
        st.table(display_df)
    else:
        st.caption("📋 レビュー履歴はまだありません。")
