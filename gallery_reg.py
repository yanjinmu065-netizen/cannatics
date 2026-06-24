import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image

st.title("✨ 成分ギャラリー(登録)")
st.write("新しい成分の画像と特徴をデータベースに追加します。")

# 📊 カラム定義
GALLERY_COLS = ["成分名", "分類", "効果・特徴", "画像"]

# 入力用のフォーム構造
with st.form("gallery_reg_form"):
    new_name = st.text_input("成分名（例: CBN, リモネン など）")
    new_cat = st.selectbox("分類", ["カンナビノイド", "半合成", "テルペン", "その他"])
    new_effect = st.text_area("効果・特徴の説明（体感や香り、特徴など）")
    uploaded_file = st.file_uploader("成分の画像を選択（PNG / JPG）", type=['png', 'jpg', 'jpeg'])
    
    submitted = st.form_submit_with_button("💾 ギャラリーデータベースに登録")

# ボタンが押された時の処理
if submitted:
    if new_name and uploaded_file:
        try:
            # 🖼️ アップロードされた画像を読み込んでリサイズ＆Base64テキストへ変換
            image = Image.open(uploaded_file)
            
            # データベースを逼迫させないよう、幅800pxに自動リサイズ（比率維持）
            image.thumbnail((800, 800))
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # 💾 保存用オブジェクトの作成
            new_data = {
                "成分名": new_name,
                "分類": new_cat,
                "効果・特徴": new_effect,
                "画像": img_str
            }
            
            # home.pyで共通定義されている保存関数を使用
            if save_data_to_db("Gallery_Master", new_data, GALLERY_COLS):
                st.success(f"🎉 「{new_name}」の画像とデータをギャラリーに正常に登録しました！")
                st.balloons()
        except Exception as e:
            st.error(f"❌ 登録処理中にエラーが発生しました: {e}")
    else:
        st.warning("⚠️ 必須項目（成分名 および 画像）が入力されていません。")
