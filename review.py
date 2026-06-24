import streamlit as st
import pandas as pd
import datetime

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

st.title("📊 リキッド紹介 & レビュー")
st.write("リキッドの体感レビューを、ボタンをポンと押すだけで素早く記録・確認できます。")

# 1. データベースから現在のデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

if df_master.empty:
    st.warning("⚠️ まだリキッドが登録されていません。「リキッドマスター登録」から登録してください。")
else:
    # === ✍️ ワンタップでレビューを書き込むセクション ===
    st.subheader("✍️ 最新の体感をワンタップ入力")
    
    # 対象のリキッドを選択
    selected_review_liq = st.selectbox("🚬 レビューするリキッドを選択", df_master["リキッド名"].tolist(), key="sb_review_target")
    liq_detail = df_master[df_master["リキッド名"] == selected_review_liq]["配合詳細"].values[0]
    st.caption(f"現在の配合内容: {liq_detail}")
    
    # テキストの自由入力欄（メモを残したい時だけ使う。空欄でもOK）
    review_memo = st.text_input("📝 詳しい体感メモ（あれば入力、無くてもOK）", value="", key="ti_review_memo")
    
    # --- 🎛️ プルダウンなし！押すだけで即保存される「体感効果」ボタン ---
    st.write("👇 **今の体感に一番近いボタンを1タップしてください（押すと即保存されます）**")
    
    # 横並びにボタンを配置
    eff_col1, eff_col2, eff_col3, eff_col4, eff_col5 = st.columns(5)
    
    selected_effect = None
    with eff_col1:
        if st.button("🔥 アゲアゲ/高揚"): selected_effect = "高揚・アゲアゲ"
    with eff_col2:
        if st.button("🧘‍♂️ チル/まったり"): selected_effect = "チル・まったり"
    with eff_col3:
        if st.button("💤 サティバ/眠気"): selected_effect = "眠気・サティバ"
    with eff_col4:
        if st.button("🧠 集中/クリア"): selected_effect = "集中・サティバ"
    with eff_col5:
        if st.button("🌈 音楽/マンチ"): selected_effect = "音楽・マンチ"

    # ボタンが押されたら即座に記録
    if selected_effect:
        new_log_row = {
            "日付": datetime.date.today().strftime("%Y-%m-%d"),
            "リキッド名": selected_review_liq,
            "パフ数": 0, # レビュー入力時はパフ数0として記録
            "配合詳細": liq_detail,
            "体感した効果": selected_effect,
            "体感メモ": review_memo
        }
        if 'save_data_to_db' in globals():
            globals()['save_data_to_db']("Attraction_Logs", new_log_row, LOG_COLS)
            st.success(f"🎉 「{selected_review_liq}」に【{selected_effect}】のレビューを記録しました！")
            st.rerun()

    st.markdown("---")
    
    # --- ⭐ 満足度（星評価）も1タップで残せるボタン ---
    st.write("👇 **このリキッドの満足度を星ボタンで1タップ（押すと即保存されます）**")
    star_col1, star_col2, star_col3, star_col4, star_col5 = st.columns(5)
    
    selected_star = None
    with star_col1:
        if st.button("⭐ (不満)"): selected_star = "★☆☆☆☆"
    with star_col2:
        if st.button("⭐⭐ (普通)"): selected_star = "★★☆☆☆"
    with star_col3:
        if st.button("⭐⭐⭐ (良い)"): selected_star = "★★★☆☆"
    with star_col4:
        if st.button("⭐⭐⭐⭐ (最高)"): selected_star = "★★★★☆"
    with star_col5:
        if st.button("⭐⭐⭐⭐⭐ (神)"): selected_star = "★★★★★"

    if selected_star:
        new_log_row = {
            "日付": datetime.date.today().strftime("%Y-%m-%d"),
            "リキッド名": selected_review_liq,
            "パフ数": 0,
            "配合詳細": liq_detail,
            "体感した効果": f"満足度: {selected_star}",
            "体感メモ": review_memo
        }
        if 'save_data_to_db' in globals():
            globals()['save_data_to_db']("Attraction_Logs", new_log_row, LOG_COLS)
            st.success(f"🎉 「{selected_review_liq}」に評価【{selected_star}】を記録しました！")
            st.rerun()

    st.markdown("---")

    # === 📋 過去のレビュー履歴一覧セクション ===
    st.subheader("📋 これまでのレビュー・体感履歴一覧")
    
    if df_logs.empty:
        st.caption("まだレビューや吸引の記録はありません。")
    else:
        # このリキッドに関する記録だけを絞り込んで新しい順に表示
        target_logs = df_logs[df_logs["リキッド名"] == selected_review_liq].copy()
        
        if target_logs.empty:
            st.caption(f"「{selected_review_liq}」に関するレビューはまだありません。")
        else:
            # 日付の新しい順に並び替え
            target_logs = target_logs.iloc[::-1]
            
            for index, row in target_logs.iterrows():
                # 吸引記録（パフ数があるもの）と、レビューボタンからの入力を区別して見やすく表示
                with st.container():
                    c_date, c_eff, c_memo = st.columns([2, 3, 5])
                    with c_date:
                        st.markdown(f"📅 **{row['日付']}**")
                    with c_eff:
                        if row['体感した効果']:
                            st.markdown(f"`{row['体感した効果']}`")
                        else:
                            st.caption(f"吸引記録 ({row['パフ数']} puffs)")
                    with c_memo:
                        if row['体感メモ']:
                            st.write(row['体感メモ'])
                        else:
                            st.caption("ーー")
                    st.markdown("<hr style='margin:5px 0; border:0; border-top:1px dashed #eee;'>", unsafe_allow_html=True)
