import streamlit as st
import pandas as pd

st.title("✨ 成分ギャラリー(登録)")
st.write("新しい成分の特徴をデータベースに追加します。")

# 📊 カラム定義
GALLERY_COLS = ["成分名", "分類", "効果・特徴"]

# フォームの作成
with st.form(key="gallery_input_form_final"):
    new_name = st.text_input("成分名（例: CBN, リモネン など）")
    new_cat = st.selectbox("分類", ["カンナビノイド", "半合成", "テルペン", "その他"])
    new_effect = st.text_area("効果・特徴の説明（体感や香り、特徴など）")
    
    # 💡 正しい送信ボタンの関数
    submitted = st.form_submit_button(label="💾 ギャラリーデータベースに登録")

# 送信後の保存処理
if submitted:
    if new_name and new_effect:
        try:
            new_data = {
                "成分名": new_name,
                "分類": new_cat,
                "効果・特徴": new_effect
            }
            # home.pyの共通保存関数を使用
            if save_data_to_db("Gallery_Master", new_data, GALLERY_COLS):
                st.success(f"🎉 「{new_name}」のデータをギャラリーに登録しました！")
                st.balloons()
        except Exception as e:
            st.error(f"❌ 登録エラー: {e}")
    else:
        st.warning("⚠️ 成分名と効果・特徴の説明を入力してください。")
