import streamlit as st

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

# 入力欄の識別キーを綺麗に分離
new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)", key="sb_new_comp_name_input")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要精神活性（強い）", "ベース（CBD/CBG等）", "テルペン・その他", "主要成分"], key="sb_new_comp_group_radio")

if st.button("成分マスターに登録・同期", key="sb_btn_submit_component"):
    if new_comp_name:
        clean_name = new_comp_name.strip()
        
        # グループキーの割り当て
        if "主要精神活性" in new_comp_group or "主要成分" in new_comp_group:
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
        
        # 2. home.py 側で表示しているセレクトボックスの選択肢（リスト）へ直接追加して同期
        if g_key == '活性':
            if 'g1_presets' in st.session_state:
                if clean_name not in st.session_state['g1_presets']:
                    st.session_state['g1_presets'].append(clean_name)
            elif 'g1_presets' in globals() and clean_name not in globals()['g1_presets']:
                globals()['g1_presets'].append(clean_name)
                
        elif g_key == 'ベース':
            if 'g2_presets' in st.session_state:
                if clean_name not in st.session_state['g2_presets']:
                    st.session_state['g2_presets'].append(clean_name)
            elif 'g2_presets' in globals() and clean_name not in globals()['g2_presets']:
                globals()['g2_presets'].append(clean_name)
                
        elif g_key == 'テルペン':
            if 'g3_presets' in st.session_state:
                if clean_name not in st.session_state['g3_presets']:
                    st.session_state['g3_presets'].append(clean_name)
            elif 'g3_presets' in globals() and clean_name not in globals()['g3_presets']:
                globals()['g3_presets'].append(clean_name)
                
        st.success(f"🎉「{clean_name}」を選択肢に追加しました！メニューを切り替えるとリキッド登録画面に反映されます。")
    else:
        st.error("成分名を入力してください。")
