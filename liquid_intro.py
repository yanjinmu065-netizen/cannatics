import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

st.title("📸 リキッド・成分紹介 & ギャラリー")
st.write("各リキッドに配合されている成分の詳細と、これまでの写真・レビュー履歴をまとめて確認できます。")

# 1. データベースからマスターデータと履歴データを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

# 表示するリキッド名のリストを作成（マスター登録されているもの、または履歴にあるもの）
master_liquids = df_master["リキッド名"].dropna().unique().tolist() if not df_master.empty else []
log_liquids = df_logs["リキッド名"].dropna().unique().tolist() if not df_logs.empty else []
all_liquids = list(set(master_liquids + log_liquids))

if not all_liquids:
    st.warning("⚠️ まだリキッド登録やレビューの記録がありません。")
else:
    # 🚬 リキッド選択用のドロップダウン
    selected_liq = st.selectbox("🚬 詳細を確認するリキッドを選択", all_liquids)
    
    st.markdown("---")

    # =========================================================
    # 🧪 【復活・強化】成分紹介セクション
    # =========================================================
    st.subheader("🧪 配合成分の紹介")
    
    # 選択されたリキッドの配合詳細をマスターから取得
    liq_row = df_master[df_master["リキッド名"] == selected_liq]
    
    if not liq_row.empty:
        detail_str = liq_row["配合詳細"].values[0]
        
        # 「CBD: 30%, THCH: 5%」のようなカンマ区切りの文字列を、見やすい表形式に分解する処理
        try:
            components = [c.strip() for c in detail_str.split(",") if c.strip()]
            comp_data = []
            for comp in components:
                if ":" in comp:
                    name, rate = comp.split(":", 1)
                    comp_data.append({"成分名": name.strip(), "配合比率": rate.strip()})
                elif " " in comp: # スペース区切りにも対応
                    name, rate = comp.rsplit(" ", 1)
                    comp_data.append({"成分名": name.strip(), "配合比率": rate.strip()})
                else:
                    comp_data.append({"成分名": comp, "配合比率": "確認中"})
            
            if comp_data:
                df_comp = pd.DataFrame(comp_data)
                # オシャレな成分表を表示
                st.table(df_comp)
            else:
                st.info(f" 配合詳細: {detail_str}")
        except Exception:
            # 万が一分解に失敗した場合はそのまま文字列として綺麗に表示
            st.info(f" 配合詳細: {detail_str}")
    else:
        # マスターにないが履歴にある場合
        latest_log = df_logs[df_logs["リキッド名"] == selected_liq]
        if not latest_log.empty:
            st.info(f" 記録時の配合: {latest_log['配合詳細'].iloc[0]}")
        else:
            st.caption("配合詳細データがありません。")

    st.markdown("---")

    # =========================================================
    # 🖼️ フォトギャラリー セクション
    # =========================================================
    st.subheader("🖼️ フォトギャラリー")
    
    # このリキッドに関する記録だけを絞り込み（最新順に並び替え）
    target_logs = df_logs[df_logs["リキッド名"] == selected_liq].copy()
    if not target_logs.empty:
        target_logs['sort_id'] = range(len(target_logs))
        target_logs = target_logs.sort_values(by=['日付', 'sort_id'], ascending=[False, False])
        
        # 画像が保存されている行だけを抽出
        img_logs = target_logs[target_logs["画像"].notna() & (target_logs["画像"] != "")]
        
        if not img_logs.empty:
            cols = st.columns(3) # 画面を3列に分割して写真を並べる
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
    st.subheader("📋 体感レビュー履歴表")
    
    if not target_logs.empty:
        # 吸引記録（パフ数があるもの）とレビューボタンからの入力をきれいに整理
        display_rows = []
        for _, row in target_logs.iterrows():
            # 体感した効果が空で、パフ数がある場合は「吸引記録」にする
            eff_text = row['体感した効果']
            if (pd.isna(eff_text) or eff_text == '') and pd.notna(row['パフ数']) and row['パフ数'] > 0:
                eff_text = f"🚬 吸引記録 ({row['パフ数']} puffs)"
            
            memo_text = row['体感メモ'] if pd.notna(row['体感メモ']) and row['体感メモ'] != '' else "ーー"
            
            display_rows.append({
                "日付": row['日付'],
                "体感・レビュー内容": eff_text,
                "メモ": memo_text
            })
        
        display_df = pd.DataFrame(display_rows)
        # レビュー履歴を表形式で表示
        st.table(display_df)
    else:
        st.caption("📋 レビュー履歴はまだありません。")
