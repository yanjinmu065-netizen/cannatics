import streamlit as st
import pandas as pd
import datetime

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

# 🎨 ご指定のカラーコードをCSSに完全反映
st.markdown("""
<style>
/* レビュー画面全体のボタン基本スタイル */
.stButton>button {
    font-size: 13px !important;
    padding: 2px 8px !important;
    height: 32px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

/* ★★★ 初期状態（選択されていない時）は一律で薄いグレー ★★★ */
div[data-testid="column"] button, 
div[data-testid="stHorizontalBlock"] button {
    background-color: #fefefe !important;
    color: #999999 !important;
    border: 1px solid #eeeeee !important;
}

/* 満足度（星）ボタンだけはデフォルトの見た目を維持 */
div[key^="st"] button {
    background-color: #fafafa !important;
    color: #000000 !important;
}

/* クリアボタンは赤文字で固定 */
button[key*="btn_clear_eff"] {
    background-color: #ffebee !important;
    color: #c62828 !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 リキッド紹介 & レビュー")
st.write("3つの項目をタップするだけで、簡単にレビューを記録できます。")

# 💡 選択状態を管理するセッション変数
if "selected_effects_list" not in st.session_state:
    st.session_state.selected_effects_list = []

# 1. データベースから現在のデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)

if df_master.empty:
    st.warning("⚠️ まだリキッドが登録されていません。「リキッドマスター登録」から登録してください。")
else:
    # 対象のリキッドを選択
    selected_review_liq = st.selectbox("🚬 レビューするリキッドを選択", df_master["リキッド名"].tolist(), key="sb_review_target")
    liq_detail = df_master[df_master["リキッド名"] == selected_review_liq]["配合詳細"].values[0]
    st.caption(f"現在の配合内容: {liq_detail}")
    
    st.markdown("---")

    # =========================================================
    # 項目①：サティバ / インディカ / ハイブリッド（タップで即保存）
    # =========================================================
    st.subheader("① 系統の選択（タップで即保存）")
    # ハイブリッド追加に伴い、3列に拡張
    col_sys1, col_sys2, col_sys3, col_sys_spacer = st.columns([1.5, 1.5, 1.5, 3.5])
    
    # 選択時に指定の色をパッと出すためのCSS（文字は見やすいように調整しています）
    st.markdown("""
    <style>
    /* 系統がホバーされたときの色指定 */
    div[data-testid="column"] button[key*="sb_sat_btn"]:hover { background-color: #ff0000 !important; color: #ffffff !important; }
    div[data-testid="column"] button[key*="sb_ind_btn"]:hover { background-color: #00ffff !important; color: #000000 !important; }
    div[data-testid="column"] button[key*="sb_hyb_btn"]:hover { background-color: #ffff00 !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

    selected_system = None
    with col_sys1:
        if st.button("🚀 サティバ", key="sb_sat_btn", use_container_width=True): selected_system = "サティバ"
    with col_sys2:
        if st.button("💤 インディカ", key="sb_ind_btn", use_container_width=True): selected_system = "インディカ"
    with col_sys3:
        if st.button("🧬 ハイブリッド", key="sb_hyb_btn", use_container_width=True): selected_system = "ハイブリッド"

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
            st.session_state.selected_effects_list = []
            st.rerun()

    st.markdown("---")

    # =========================================================
    # 項目②：体感（複数選択）※ご指定のカラーコードを動的適用
    # =========================================================
    st.subheader("② 体感の選択（複数選択可能）")
    st.write("👇 ボタンを押して体感をリストに追加していってください。")

    # === 🎨 選択されたボタンをご指定のカラーコードに戻す処理 ===
    dynamic_css = "<style>"
    for effect_name in st.session_state.selected_effects_list:
        # 文字が見えづらくならないよう、背景が黄色やシアンの時は黒文字、赤の時は白文字に自動調整しています
        if effect_name == "ヘッドハイ": dynamic_css += "button[key*='ef_hh'] { background-color: #ff0000 !important; color: #ffffff !important; border: 1px solid #ff0000 !important; font-weight: bold !important; }"
        elif effect_name == "ボディハイ": dynamic_css += "button[key*='ef_bh'] { background-color: #00ffff !important; color: #000000 !important; border: 1px solid #00ffff !important; font-weight: bold !important; }"
        elif effect_name == "睡眠サポート": dynamic_css += "button[key*='ef_su'] { background-color: #00ffff !important; color: #000000 !important; border: 1px solid #00ffff !important; font-weight: bold !important; }"
        elif effect_name == "多幸感": dynamic_css += "button[key*='ef_tk'] { background-color: #ffff00 !important; color: #000000 !important; border: 1px solid #ffff00 !important; font-weight: bold !important; }"
        elif effect_name == "陶酔": dynamic_css += "button[key*='ef_ts'] { background-color: #ffc0cb !important; color: #000000 !important; border: 1px solid #ffc0cb !important; font-weight: bold !important; }"
        elif effect_name == "興奮": dynamic_css += "button[key*='ef_ko'] { background-color: #ff0000 !important; color: #ffffff !important; border: 1px solid #ff0000 !important; font-weight: bold !important; }"
        elif effect_name == "ストレス緩和": dynamic_css += "button[key*='ef_st'] { background-color: #3cb371 !important; color: #ffffff !important; border: 1px solid #3cb371 !important; font-weight: bold !important; }"
        elif effect_name == "おしゃべり": dynamic_css += "button[key*='ef_os'] { background-color: #ffff00 !important; color: #000000 !important; border: 1px solid #ffff00 !important; font-weight: bold !important; }"
        elif effect_name == "食欲増進": dynamic_css += "button[key*='ef_sy'] { background-color: #ffff00 !important; color: #000000 !important; border: 1px solid #ffff00 !important; font-weight: bold !important; }"
        elif effect_name == "落ち着き": dynamic_css += "button[key*='ef_oc'] { background-color: #3cb371 !important; color: #ffffff !important; border: 1px solid #3cb371 !important; font-weight: bold !important; }"
        elif effect_name == "リラックス": dynamic_css += "button[key*='ef_rx'] { background-color: #3cb371 !important; color: #ffffff !important; border: 1px solid #3cb371 !important; font-weight: bold !important; }"
        elif effect_name == "エネルギッシュ": dynamic_css += "button[key*='ef_en'] { background-color: #ffff00 !important; color: #000000 !important; border: 1px solid #ffff00 !important; font-weight: bold !important; }"
        elif effect_name == "高揚感": dynamic_css += "button[key*='ef_ky'] { background-color: #ff0000 !important; color: #ffffff !important; border: 1px solid #ff0000 !important; font-weight: bold !important; }"
    dynamic_css += "</style>"
    st.markdown(dynamic_css, unsafe_allow_html=True)

    # 13個のボタンを5列に綺麗に配置
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
    
    with b_col1:
        if st.button("🧠 ヘッドハイ", key="ef_hh", use_container_width=True):
            if "ヘッドハイ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ヘッドハイ")
            else: st.session_state.selected_effects_list.remove("ヘッドハイ")
            st.rerun()
        if st.button("✨ 陶酔", key="ef_ts", use_container_width=True):
            if "陶酔" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("陶酔")
            else: st.session_state.selected_effects_list.remove("陶酔")
            st.rerun()
        if st.button("🍕 食欲増進", key="ef_sy", use_container_width=True):
            if "食欲増進" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("食欲増進")
            else: st.session_state.selected_effects_list.remove("食欲増進")
            st.rerun()

    with b_col2:
        if st.button("🧍 ボディハイ", key="ef_bh", use_container_width=True):
            if "ボディハイ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ボディハイ")
            else: st.session_state.selected_effects_list.remove("ボディハイ")
            st.rerun()
        if st.button("🔥 興奮", key="ef_ko", use_container_width=True):
            if "興奮" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("興奮")
            else: st.session_state.selected_effects_list.remove("興奮")
            st.rerun()
        if st.button("🟢 落ち着き", key="ef_oc", use_container_width=True):
            if "落ち着き" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("落ち着き")
            else: st.session_state.selected_effects_list.remove("落ち着き")
            st.rerun()

    with b_col3:
        if st.button("💤 睡眠サポート", key="ef_su", use_container_width=True):
            if "睡眠サポート" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("睡眠サポート")
            else: st.session_state.selected_effects_list.remove("睡眠サポート")
            st.rerun()
        if st.button("🕊️ ストレス緩和", key="ef_st", use_container_width=True):
            if "ストレス緩和" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("ストレス緩和")
            else: st.session_state.selected_effects_list.remove("ストレス緩和")
            st.rerun()
        if st.button("🧘‍♂️ リラックス", key="ef_rx", use_container_width=True):
            if "リラックス" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("リラックス")
            else: st.session_state.selected_effects_list.remove("リラックス")
            st.rerun()

    with b_col4:
        if st.button("🌈 多幸感", key="ef_tk", use_container_width=True):
            if "多幸感" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("多幸感")
            else: st.session_state.selected_effects_list.remove("多幸感")
            st.rerun()
        if st.button("💬 おしゃべり", key="ef_os", use_container_width=True):
            if "おしゃべり" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("おしゃべり")
            else: st.session_state.selected_effects_list.remove("おしゃべり")
            st.rerun()
        if st.button("📈 高揚感", key="ef_ky", use_container_width=True):
            if "高揚感" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("高揚感")
            else: st.session_state.selected_effects_list.remove("高揚感")
            st.rerun()

    with b_col5:
        if st.button("⚡ エネルギッシュ", key="ef_en", use_container_width=True):
            if "エネルギッシュ" not in st.session_state.selected_effects_list: st.session_state.selected_effects_list.append("エネルギッシュ")
            else: st.session_state.selected_effects_list.remove("エネルギッシュ")
            st.rerun()

    # 選択されている体感を画面に表示
    if st.session_state.selected_effects_list:
        st.markdown(f"**【選択中】:** `{'` / `'.join(st.session_state.selected_effects_list)}`")
        
        c_save_eff, c_clear_eff, c_spacer_eff = st.columns([2, 1.5, 4.5])
        with c_save_eff:
            if st.button("💾 この体感で保存", key="btn_save_eff_action", type="primary", use_container_width=True):
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
                    st.session_state.selected_effects_list = []
                    st.rerun()
        with c_clear_eff:
            if st.button("❌ クリア", key="btn_clear_eff_action", use_container_width=True):
                st.session_state.selected_effects_list = []
                st.rerun()

    st.markdown("---")

    # =========================================================
    # 項目③：1〜5での星レビュー（タップで即保存）
    # =========================================================
    st.subheader("③ 満足度レビュー（タップで即保存）")
    star_col1, star_col2, star_col3, star_col4, star_col5, star_spacer = st.columns([0.8, 0.8, 0.8, 0.8, 0.8, 4])
    
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
            st.session_state.selected_effects_list = []
            st.rerun()

    st.markdown("---")
    st.info("💡 過去のレビュー履歴は「リキッド紹介」画面で確認できます。")
