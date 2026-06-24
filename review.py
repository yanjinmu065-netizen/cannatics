import streamlit as st
import pandas as pd
import datetime

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

# 安全なCSS読み込み処理（home.py側で設定されている前提ですが、review.py単体でもすっきりさせるために追加）
st.markdown("""
<style>
/* レビュー画面全体のボタンを小さく、文字を読みやすく調整 */
.stButton>button {
    font-size: 14px !important;
    padding: 2px 10px !important;
    height: 35px !important;
    border-radius: 20px !important; /* 角丸で丸っこく */
    border: 1px solid rgba(0,0,0,0.2) !important;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    transform: scale(1.03); /* ホバー時に少し大きく */
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ★系統ボタン（小ぶりでパステル調）★ */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button[key*="sb_sat"] {
    background-color: #E3F2FD !important; /* パステルブルー */
    color: #1565C0 !important;
    font-weight: bold !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button[key*="sb_ind"] {
    background-color: #F3E5F5 !important; /* パステルパープル */
    color: #7B1FA2 !important;
    font-weight: bold !important;
}

/* ★体感ボタン（さらに小さく。文字は黒。パステル調のパレット）★ */
/* 小さく表示するためにカラム幅をさらに細かく調整（home.pyのCSSを上書き） */
div[data-testid="column"] button {
    font-size: 12px !important;
    height: 30px !important;
    border-radius: 15px !important;
    font-weight: normal !important;
    color: #000000 !important; /* 文字は黒で統一 */
    background-color: #fafafa;
}

/* 各体感ボタンの色分け（統一感のあるパステル調） */
/* 1列目: 青系 */
div[data-testid="column"]:nth-of-type(1) button { background-color: #e1f5fe !important; }
/* 2列目: 緑系 */
div[data-testid="column"]:nth-of-type(2) button { background-color: #e8f5e9 !important; }
/* 3列目: 黄系 */
div[data-testid="column"]:nth-of-type(3) button { background-color: #fffde7 !important; }
/* 4列目: オレンジ/ピンク系 */
div[data-testid="column"]:nth-of-type(4) button { background-color: #fff3e0 !important; }

/* ホバー時は少し濃く */
div[data-testid="column"] button:hover {
    background-color: rgba(0,0,0,0.05) !important;
    border: 1px solid rgba(0,0,0,0.3) !important;
}

/* 選択クリアボタンだけは赤系 */
button[key*="btn_clear_eff"] {
    background-color: #ffebee !important;
    color: #c62828 !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 リキッド紹介 & レビュー")
st.write("3つの項目をタップするだけで、簡単にレビューを記録できます。")

# 💡 複数選択された体感を一時的にキープするためのセッション変数を準備
if "selected_effects_list" not in st.session_state:
    st.session_state.selected_effects_list = []

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
    # 対象のリキッドを選択
    selected_review_liq = st.selectbox("🚬 レビューするリキッドを選択", df_master["リキッド名"].tolist(), key="sb_review_target")
    liq_detail = df_master[df_master["リキッド名"] == selected_review_liq]["配合詳細"].values[0]
    st.caption(f"現在の配合内容: {liq_detail}")
    
    st.markdown("---")

    # =========================================================
    # 項目①：サティバ or インディカ（どちらか1つをタップして保存）
    # =========================================================
    st.subheader("① 系統の選択（タップで即保存）")
    # すっきりさせるために幅を狭く
    col_sys1, col_sys2, col_sys_spacer = st.columns([1.5, 1.5, 5])
    
    selected_system = None
    with col_sys1:
        # keyに「sb_sat」を含めることでCSSを適用
        if st.button("🚀 サティバ", key="sb_sat_btn", use_container_width=True): selected_system = "サティバ"
    with col_sys2:
        # keyに「sb_ind」を含めることでCSSを適用
        if st.button("💤 インディカ", key="sb_ind_btn", use_container_width=True): selected_system = "インディカ"

    if selected_system:
        new_log_row = {
            "日付": datetime.date.today().strftime("%Y-%m-%d"),
            "リキッド名": selected_review_liq,
            "パフ数": 0,
            "配合詳細": liq_detail,
            "体感した効果": f"系統: {selected_system}",
            "体感メモ": ""
        }
        if 'save_data_to_db' in globals():
            globals()['save_data_to_db']("Attraction_Logs", new_log_row, LOG_COLS)
            st.success(f"🎉 【{selected_system}】を記録しました！")
            st.rerun()

    st.markdown("---")

    # =========================================================
    # 項目②：体感（複数選択）
    # =========================================================
    st.subheader("② 体感の選択（複数選択可能）")
    st.write("👇 ボタンを押して体感をリストに追加していってください。")
    
    # 13個の体感ボタンをさらに細かく配置（5列）して、1つ1つのボタンを小さく
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
    
    # 統一感のあるパステル調のカラーパレットをCSSで適用（文字は黒）
    with b_col1:
        if st.button("🧠 ヘッドハイ", key="ef_hh", use_container_width=True):
            if "ヘッドハイ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ヘッドハイ")
        if st.button("✨ 陶酔", key="ef_ts", use_container_width=True):
            if "陶酔" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("陶酔")
        if st.button("🍕 食欲増進", key="ef_sy", use_container_width=True):
            if "食欲増進" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("食欲増進")

    with b_col2:
        if st.button("🧍 ボディハイ", key="ef_bh", use_container_width=True):
            if "ボディハイ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ボディハイ")
        if st.button("🔥 興奮", use_container_width=True):
            if "興奮" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("興奮")
        if st.button("🟢 落ち着き", key="ef_oc", use_container_width=True):
            if "落ち着き" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("落ち着き")

    with b_col3:
        if st.button("💤 睡眠サポート", key="ef_su", use_container_width=True):
            if "睡眠サポート" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("睡眠サポート")
        if st.button("🕊️ ストレス緩和", key="ef_st", use_container_width=True):
            if "ストレス緩和" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ストレス緩和")
        if st.button("🧘‍♂️ リラックス", key="ef_rx", use_container_width=True):
            if "リラックス" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("リラックス")

    with b_col4:
        if st.button("🌈 多幸感", key="ef_tk", use_container_width=True):
            if "多幸感" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("多幸感")
        if st.button("💬 おしゃべり", key="ef_os", use_container_width=True):
            if "おしゃべり" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("おしゃべり")
        if st.button("📈 高揚感", key="ef_ky", use_container_width=True):
            if "高揚感" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("高揚感")

    with b_col5:
        if st.button("⚡ エネルギッシュ", key="ef_en", use_container_width=True):
            if "エネルギッシュ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("エネルギッシュ")

    # 選択されている体感を画面に表示
    if st.session_state.selected_effects_list:
        st.markdown(f"**【選択中】:** `{'` / `'.join(st.session_state.selected_effects_list)}`")
        
        # 保存とクリアボタンも小さく横並びに
        c_save_eff, c_clear_eff, c_spacer_eff = st.columns([2, 1.5, 4.5])
        with c_save_eff:
            # type="primary"で少し目立たせる（home.pyのCSSでパステル調になっているはず）
            if st.button("💾 この体感で保存", key="btn_save_eff", type="primary", use_container_width=True):
                all_effects_str = ", ".join(st.session_state.selected_effects_list)
                new_log_row = {
                    "日付": datetime.date.today().strftime("%Y-%m-%d"),
                    "リキッド名": selected_review_liq,
                    "パフ数": 0,
                    "配合詳細": liq_detail,
                    "体感した効果": f"体感: {all_effects_str}",
                    "体感メモ": ""
                }
                if 'save_data_to_db' in globals():
                    globals()['save_data_to_db']("Attraction_Logs", new_log_row, LOG_COLS)
                    st.success(f"🎉 体感【{all_effects_str}】をまとめて記録しました！")
                    st.session_state.selected_effects_list = []  # 保存後にリセット
                    st.rerun()
        with c_clear_eff:
            # keyに「btn_clear_eff」を含めることでCSSを適用
            if st.button("❌ クリア", key="btn_clear_eff_action", use_container_width=True):
                st.session_state.selected_effects_list = []
                st.rerun()

    st.markdown("---")

    # =========================================================
    # 項目③：1〜5での星レビュー（タップで即保存）
    # =========================================================
    st.subheader("③ 満足度レビュー（タップで即保存）")
    # すっきりさせるために幅を狭く
    star_col1, star_col2, star_col3, star_col4, star_col5, star_spacer = st.columns([0.8, 0.8, 0.8, 0.8, 0.8, 4])
    
    # 満足度ボタンはhome.pyの共通CSS（丸っこくて薄い緑）が適用されます（さらに小さく表示されるはず）
    selected_star = None
    with star_col1:
        if st.button("1", key="st1_b", use_container_width=True): selected_star = "★☆☆☆☆ (1)"
    with star_col2:
        if st.button("2", key="st2_b", use_container_width=True): selected_star = "★★☆☆☆ (2)"
    with star_col3:
        if st.button("3", key="st3_b", use_container_width=True): selected_star = "★★★☆☆ (3)"
    with star_col4:
        if st.button("4", key="st4_b", use_container_width=True): selected_star = "★★★★☆ (4)"
    with star_col5:
        if st.button("5", key="st5_b", use_container_width=True): selected_star = "★★★★★ (5)"

    if selected_star:
        new_log_row = {
            "日付": datetime.date.today().strftime("%Y-%m-%d"),
            "リキッド名": selected_review_liq,
            "パフ数": 0,
            "配合詳細": liq_detail,
            "体感した効果": f"星評価: {selected_star}",
            "体感メモ": ""
        }
        if 'save_data_to_db' in globals():
            globals()['save_data_to_db']("Attraction_Logs", new_log_row, LOG_COLS)
            st.success(f"🎉 評価【{selected_star}】を記録しました！")
            st.rerun()

    st.markdown("---")

    # === 📋 過去のレビュー履歴一覧 ===
    st.subheader("📋 これまでのレビュー・体感履歴一覧")
    if df_logs.empty:
        st.caption("まだレビューや吸引の記録はありません。")
    else:
        target_logs = df_logs[df_logs["リキッド名"] == selected_review_liq].copy()
        if target_logs.empty:
            st.caption(f"「{selected_review_liq}」に関するレビューはまだありません。")
        else:
            # 最新の記録が上にくるように並び替え
            target_logs = target_logs.iloc[::-1]
            for index, row in target_logs.iterrows():
                with st.container():
                    c_date, c_eff, c_memo = st.columns([2, 5, 3])
                    with c_date: st.markdown(f"📅 **{row['日付']}**")
                    with c_eff:
                        val = row.get('体感した効果', '')
                        if pd.isna(val) or val == '':
                            st.caption(f"吸引記録 ({row.get('パフ数', 0)} puffs)")
                        else:
                            # 履歴の体感は少し小さめに表示してすっきりさせる
                            st.markdown(f"<span style='font-size: 13px; color: #555;'>`{val}`</span>", unsafe_allow_html=True)
                    with c_memo:
                        memo_val = row.get('体感メモ', '')
                        st.write(memo_val if (pd.notna(memo_val) and memo_val != '') else "ーー")
                    st.markdown("<hr style='margin:5px 0; border:0; border-top:1px dashed #eee;'>", unsafe_allow_html=True)
