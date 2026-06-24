import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データをカテゴリ別に確認できます。")

# 📊 カラム定義
GALLERY_COLS = ["成分名", "分類", "効果・特徴"]

# 1. まず現在のデータベース（スプレッドシート等）からデータを読み込む
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

# 💡 データベースが完全に空の場合、Excel（data.xlsx）から元データを復元して追加する
if df_gallery.empty:
    with st.spinner("🔄 Excel(data.xlsx)から初期成分データを復元中..."):
        try:
            excel_file = "data.xlsx"
            restored_rows = []
            
            # 各シートから成分名を取得してマスタデータを作成
            # ※効果・特徴は初期値として空欄、または仮テキストを入れます
            if "半合成" in pd.ExcelFile(excel_file).sheet_names:
                df_syn = pd.read_excel(excel_file, sheet_name="半合成", header=2)
                for name in df_syn["成分名"].dropna().unique():
                    restored_rows.append({"成分名": str(name), "分類": "半合成", "効果・特徴": "Excelより自動同期"})
                    
            if "カンナビノイド" in pd.ExcelFile(excel_file).sheet_names:
                df_can = pd.read_excel(excel_file, sheet_name="カンナビノイド", header=2)
                for name in df_can["成分名"].dropna().unique():
                    restored_rows.append({"成分名": str(name), "分類": "カンナビノイド", "効果・特徴": "Excelより自動同期"})
                    
            if "テルペン" in pd.ExcelFile(excel_file).sheet_names:
                df_ter = pd.read_excel(excel_file, sheet_name="テルペン", header=2)
                for name in df_ter["成分名"].dropna().unique():
                    restored_rows.append({"成分名": str(name), "分類": "テルペン", "効果・特徴": "Excelより自動同期"})
            
            if restored_rows:
                df_restored = pd.DataFrame(restored_rows)
                # スプレッドシート（またはCSVベース）へ一括保存
                save_all_data_to_db("Gallery_Master", df_restored, GALLERY_COLS)
                # 画面表示用にデータを再読み込み
                df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)
                st.success("🎉 Excel内の全初期データをスプレッドシートに同期・追加しました！")
        except Exception as e:
            st.error(f"❌ Excelデータの読み込み中にエラーが発生しました: {e}")

# 2. データの表示処理
if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。『⚙️ マスター登録』＞『✨ 成分ギャラリー登録』から追加してください。")
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
