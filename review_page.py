import streamlit as st
import pandas as pd

st.title("✨ 成分ギャラリー(登録)")
st.write("新しい成分の特徴をデータベースに追加します。")

# 📊 カラム定義（画像なし）
GALLERY_COLS = ["成分名", "分類", "効果・特徴"]

# 入力用のフォーム構造（テキストのみ）
with st.form("gallery_reg_form"):
    new_name = st.text_input("成分名（例: CBN, リモネン など）")
    new_cat = st.selectbox("分類", ["カンナビノイド", "半合成", "テルペン", "その他"])
    new_effect = st.text_area("効果・特徴の説明（体感や香り、特徴など）")
    
    submitted = st.form_submit_button("💾 ギャラリーデータベースに登録")

# ボタンが押された時の保存処理
if submitted:
    if new_name and new_effect:
        try:
            # 💾 保存用オブジェクトの作成
            new_data = {
                "成分名": new_name,
                "分類": new_cat,
                "効果・特徴": new_effect
            }
            
            # home.pyで共通定義されている保存関数を使用
            if save_data_to_db("Gallery_Master", new_data, GALLERY_COLS):
                st.success(f"🎉 「{new_name}」のデータをギャラリーに正常に登録しました！")
                st.balloons()
        except Exception as e:
            st.error(f"❌ 登録処理中にエラーが発生しました: {e}")
    else:
        st.warning("⚠️ 必須項目（成分名 および 効果・特徴の説明）が入力されていません。")
