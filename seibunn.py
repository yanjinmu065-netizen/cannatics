import streamlit as st

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

# 💡 key="unique_new_comp_name" を追加して、リキッド名など他の入力欄との重複を絶対に防ぎます！
new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)", key="unique_new_comp_name")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要精神活性（強い）", "ベース（CBD/CBG等）", "テルペン・その他"], key="unique_new_comp_group")

if st.button("成分マスターに登録・同期", key="unique_btn_sync_comp"):
    if new_comp_name:
        # 入力された文字の前後にある余計なスペースを削除
        clean_name = new_comp_name.strip()
        
        # グループ判定
        if "主要精神活性" in new_comp_group:
            g_key = '活性'
        elif "ベース" in new_comp_group:
            g_key = 'ベース'
        else:
            g_key = 'テルペン'
            
        # セッションに新成分を追加
        if "custom_components" not in st.session_state:
            st.session_state.custom_components = []
            
        st.session_state.custom_components.append({"name": clean_name, "group": g_key})
        
        # 💡 home.py 側のプリセットリスト（ドロップダウン用）にもその場で直接追加して即時反映させます！
        if g_key == '活性':
            if 'g1_presets' in globals() and clean_name not in globals()['g1_presets']:
                globals()['g1_presets'].append(clean_name)
        elif g_key == 'ベース':
            if 'g2_presets' in globals() and clean_name not in globals()['g2_presets']:
                globals()['g2_presets'].append(clean_name)
        elif g_key == 'テルペン':
            if 'g3_presets' in globals() and clean_name not in globals()['g3_presets']:
                globals()['g3_presets'].append(clean_name)
                
        st.success(f"🎉「{clean_name}」をマスターに登録し、選択肢に正常追加しました！")
        
        # 画面を再起動してドロップダウン側を更新
        st.rerun()
    else:
        st.error("成分名を入力してください。")
