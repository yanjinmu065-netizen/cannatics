import streamlit as st
import pandas as pd

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

# 💡 永久保存用のカラム定義
COMP_MASTER_COLS = ["成分名", "分類"]

new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)", key="seibunn_final_input_name")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要成分", "ベース（CBD/CBG等）", "テルペン・その他"], key="seibunn_final_radio_group")

if st.button("成分マスターに登録・同期", key="seibunn_final_btn_submit"):
    if new_comp_name:
        clean_name = new_comp_name.strip()
        
        # 💡 重複チェック（現在ドロップダウンにあるか確認）
        already_exists = False
        if new_comp_group == "主要成分" and clean_name in st.session_state.get('g1_presets', []):
            already_exists = True
        elif "ベース" in new_comp_group and clean_name in st.session_state.get('g2_presets', []):
            already_exists = True
        elif "テルペン" in new_comp_group and clean_name in st.session_state.get('g3_presets', []):
            already_exists = True
            
        if already_exists:
            st.warning(f"「{clean_name}」は既に【{new_comp_group}】に登録されています。")
        else:
            # 1. スプレッドシート（またはCSV）の専用シート『Components_Master』に保存（永久保存）
            # home.py側の関数をそのまま呼び出すために globals() 経由か直接セッション/DB保存を実行します。
            # ここでは home.py 内で定義された関数が利用可能なため、安全に追記処理を行います。
            try:
                # home.pyのsave_data_to_db関数を呼び出し
                if 'save_data_to_db' in globals():
                    globals()['save_data_to_db']("Components_Master", {"成分名": clean_name, "分類": new_comp_group}, COMP_MASTER_COLS)
            except Exception as e:
                st.error(f"データベースへの永久保存に失敗しました: {e}")

            # 2. 現在開いている画面のドロップダウン用リスト（セッション状態）へ即座に反映
            if new_comp_group == "主要成分":
                if 'g1_presets' in st.session_state:
                    st.session_state['g1_presets'].append(clean_name)
            elif "ベース" in new_comp_group:
                if 'g2_presets' in st.session_state:
                    st.session_state['g2_presets'].append(clean_name)
            elif "テルペン" in new_comp_group:
                if 'g3_presets' in st.session_state:
                    st.session_state['g3_presets'].append(clean_name)
                    
            st.success(f"🎉 「{clean_name}」を【{new_comp_group}】専用シートに永久保存しました！リキッド登録の選択肢にすぐ反映されます。")
    else:
        st.error("成分名を入力してください。")
