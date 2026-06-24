import streamlit as st

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

# 💡 キーと選択肢の文字列を完全に「主要成分」に統一して連動させます！
new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)", key="seibunn_final_input_name")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要成分", "ベース（CBD/CBG等）", "テルペン・その他"], key="seibunn_final_radio_group")

if st.button("成分マスターに登録・同期", key="seibunn_final_btn_submit"):
    if new_comp_name:
        clean_name = new_comp_name.strip()
        
        # 💡 主要成分としてセッションデータに格納します
        if "custom_components" not in st.session_state:
            st.session_state.custom_components = []
            
        if not any(c['name'] == clean_name for c in st.session_state.custom_components):
            st.session_state.custom_components.append({"name": clean_name, "group": new_comp_group})
        
        # 💡 home.py 側のドロップダウンリストへ直接データを流し込みます
        if new_comp_group == "主要成分":
            if 'g1_presets' in st.session_state and clean_name not in st.session_state['g1_presets']:
                st.session_state['g1_presets'].append(clean_name)
                    
        elif "ベース" in new_comp_group:
            if 'g2_presets' in st.session_state and clean_name not in st.session_state['g2_presets']:
                st.session_state['g2_presets'].append(clean_name)
                    
        elif "テルペン" in new_comp_group:
            if 'g3_presets' in st.session_state and clean_name not in st.session_state['g3_presets']:
                st.session_state['g3_presets'].append(clean_name)
                
        st.success(f"🎉 「{clean_name}」を【{new_comp_group}】に追加しました！「リキッドマスター登録」画面の主要成分などに即座に反映されます。")
    else:
        st.error("成分名を入力してください。")
