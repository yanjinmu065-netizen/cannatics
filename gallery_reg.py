import streamlit as st
import pandas as pd

st.title("✨ 成分ギャラリー(登録)")
st.write("各項目を分けてデータベースに新規登録します。")

# 📊 共通カラム定義
GALLERY_COLS = ["成分名", "分類", "効果", "効果時間", "ロケーション", "香り"]

# フォームの作成
with st.form(key="gallery_input_form_v4"):
    new_name = st.text_input("成分名（例: CBD, リモネン など）")
    new_cat = st.selectbox("分類", ["カンナビノイド", "半合成", "テルペン", "その他"])
    
    # 💡 項目ごとに個別に入力欄を設置
    new_effect = st.text_area("✨ 効果（体感や特徴など）")
    new_duration = st.text_input("⏳ 効果時間（例: 2〜4h、1〜3h など）")
    new_location = st.text_input("📍 ロケーション（例: 【合法】〜、就寝前 など）")
    new_scent = st.text_input("🍋 香り（※テルペンの場合のみ入力、例: 柑橘類、ウッディ など）")
    
    submitted = st.form_submit_button(label="💾 ギャラリーデータベースに登録")

# 送信後の保存処理
if submitted:
    if new_name and new_effect:
        try:
            # テルペン以外の場合は香りを「-」にする
            final_scent = new_scent if new_cat == "テルペン" else "-"
            # テルペンの場合はロケーションを「-」にする
            final_location = new_location if new_cat != "テルペン" else "-"
            
            new_data = {
                "成分名": new_name.strip(),
                "分類": new_cat,
                "効果": new_effect.strip(),
                "効果時間": new_duration.strip() if new_duration else "-",
                "ロケーション": final_location.strip() if final_location else "-",
                "香り": final_scent.strip() if final_scent else "-"
            }
            
            # home.py側の共通保存関数を呼び出し
            if save_data_to_db("Gallery_Master", new_data, GALLERY_COLS):
                st.success(f"🎉 「{new_name}」のデータを項目別にギャラリーへ登録しました！")
                st.balloons()
                st.rerun()
        except Exception as e:
            st.error(f"❌ 登録処理中にエラーが発生しました: {e}")
    else:
        st.warning("⚠️ 必須項目（成分名 および 効果）が入力されていません。")
