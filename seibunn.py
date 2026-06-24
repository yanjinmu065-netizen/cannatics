import streamlit as st

st.title("🌐 新成分のマスター登録")
st.write("インターネットで見つけた新しい成分を、配合ドロップダウンメニューへ追加できます。")

new_comp_name = st.text_input("新成分名を入力 (例: THCH, CBDP)")
new_comp_group = st.radio("成分の分類（割り当てるグループ）", ["主要精神活性（強い）", "ベース（CBD/CBG等）", "テルペン・その他"])

if st.button("成分マスターに登録・同期"):
    if new_comp_name:
        g_key = '活性' if "精神活性" in new_comp_group else ('ベース' if "ベース" in new_comp_group else 'テルペン')
        st.session_state.custom_components.append({"name": new_comp_name, "group": g_key})
        st.success(f"「{new_comp_name}」を選択肢に正常追加しました！")
    else:
        st.error("成分名を入力してください。")