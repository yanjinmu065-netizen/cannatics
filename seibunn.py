import streamlit as st

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

# 💡 他のファイルと絶対に衝突しないように完全に一意の識別キーを割り当てました
new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)", key="seibunn_page_input_name_v2")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要成分", "ベース（CBD/CBG等）", "テルペン・その他"], key="seibunn_page_radio_group_v2")

if st.button("成分マスターに登録・同期", key="seibunn_page_btn_submit_v2"):
    if new_comp_name:
        clean_name = new_comp_name.strip()
        
        # グループキーの割り当て
        if "主要成分" in new_comp_group:
            g_key = '活性'
        elif "ベース" in new_comp_group:
            g_key = 'ベース'
        else:
            g_key = 'テルペン'
            
        # 1. セッションのマスター配列に安全に追加
        if "custom_components" not in st.session_state:
            st.session_state.custom_components = []
            
        # 重複チェックをしてから追加
        if not any(c['name'] == clean_name for c in st.session_state.custom_components):
            st.session_state.custom_components.append({"name": clean_name, "group": g_key})
        
        # 2. home.py 側のドロップダウンリスト（st.session_state）へダイレクトに注入
        if g_key == '活性':
            if 'g1_presets' in st.session_state:
                if clean_name not in st.session_state['g1_presets']:
                    st.session_state['g1_presets'].append(clean_name)
                    
        elif g_key == 'ベース':
            if 'g2_presets' in st.session_state:
                if clean_name not in st.session_state['g2_presets']:
                    st.session_state['g2_presets'].append(clean_name)
                    
        elif g_key == 'テルペン':
            if 'g3_presets' in st.session_state:
                if clean_name not in st.session_state['g3_presets']:
                    st.session_state['g3_presets'].append(clean_name)
                
        st.success(f"🎉 「{clean_name}」を【{new_comp_group}】に追加しました！「リキッドマスター登録」画面の選択肢にすぐ反映されます。")
    else:
        st.error("成分名を入力してください。")
