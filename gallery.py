import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データをカテゴリ別に確認できます。")

# 📊 カラム定義
GALLERY_COLS = ["成分名", "分類", "効果・特徴"]

# データの読み込み
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。ジャンルを切り替えて『✨ 成分ギャラリー登録』から追加してください。")
else:
    categories = df_gallery["分類"].unique()
    for cat in categories:
        st.subheader(f"🏷️ {cat}")
        cat_items = df_gallery[df_gallery["分類"] == cat]
        
        cols = st.columns(2)
        for i, (_, item) in enumerate(cat_items.iterrows()):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #ffffff;">
                        <h4 style="margin: 0 0 8px 0; color: #000000;">{item['成分名']}</h4>
                        <p style="margin: 0; font-size: 14px; color: #333333; line-height: 1.5;">{item['効果・特徴']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
