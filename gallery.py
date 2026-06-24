import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データを詳細項目別に確認できます。")

# 📊 カラム定義
GALLERY_COLS = ["成分名", "分類", "効果", "効果時間", "ロケーション", "香り"]

# 1. データベースからデータを読み込む
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

# 💡 データベースが完全に空の場合、Excel(data.xlsx)から初期データを復元
if df_gallery.empty:
    with st.spinner("🔄 Excel(data.xlsx)から効果・特徴も含めてデータを抽出中..."):
        try:
            excel_file = "data.xlsx"
            restored_rows = []
            sheets = pd.ExcelFile(excel_file).sheet_names
            
            categories_map = {
                "半合成": "半合成",
                "カンナビノイド": "カンナビノイド",
                "テルペン": "テルペン"
            }
            
            for sheet_name, cat_label in categories_map.items():
                if sheet_name in sheets:
                    # header=2（3行目が見出し）として読み込み
                    df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=2)
                    
                    # 💡 Excel内の列名をきれいにする（前後の空白を削除）
                    df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                    
                    for _, row in df_sheet.iterrows():
                        name = row.get("成分名")
                        if pd.isna(name) or str(name).strip() == "成分名" or str(name).strip() == "":
                            continue
                        
                        # 💡 Excel内から該当しそうな列のデータを取得（なければ「-」にする）
                        eff_val = row.get("効果") if not pd.isna(row.get("効果")) else row.get("効果・特徴", "-")
                        dur_val = row.get("効果時間", "-") if not pd.isna(row.get("効果時間")) else "-"
                        loc_val = row.get("ロケーション", "-") if not pd.isna(row.get("ロケーション")) else "-"
                        scent_val = row.get("香り", "-") if not pd.isna(row.get("香り")) else "-"
                        
                        restored_rows.append({
                            "成分名": str(name).strip(), 
                            "分類": cat_label, 
                            "効果": str(eff_val).strip(), 
                            "効果時間": str(dur_val).strip(), 
                            "ロケーション": str(loc_val).strip(),
                            "香り": str(scent_val).strip() if cat_label == "テルペン" else ""
                        })
            
            if restored_rows:
                df_restored = pd.DataFrame(restored_rows)
                save_all_data_to_db("Gallery_Master", df_restored, GALLERY_COLS)
                df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)
                st.success("🎉 Excelから全ての詳細データをスプレッドシートに同期しました！")
        except Exception as e:
            st.error(f"❌ Excel読み込み・抽出エラー: {e}")

# 2. データの表示処理
if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。ジャンルを切り替えて『✨ 成分ギャラリー登録』から追加してください。")
else:
    categories = df_gallery["分類"].unique()
    for cat in categories:
        st.subheader(f"🏷️ {cat}")
        cat_items = df_gallery[df_gallery["分類"] == cat]
        
        cols = st.columns(2)
        for i, (_, item) in enumerate(cat_items.iterrows()):
            if str(item['成分名']).strip() == "成分名":
                continue
                
            eff = item.get("効果", "-") if str(item.get("効果", "")) != "nan" else "-"
            dur = item.get("効果時間", "-") if str(item.get("効果時間", "")) != "nan" else "-"
            loc = item.get("ロケーション", "-") if str(item.get("ロケーション", "")) != "nan" else "-"
            scent = item.get("香り", "-") if str(item.get("香り", "")) != "nan" else "-"
            
            # テルペンだけの「香り」表示
            scent_html = f'<div style="margin-top:4px;">🍋 <b>香り:</b> {scent}</div>' if cat == "テルペン" else ""
            
            card_html = (
                f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:15px;margin-bottom:15px;background-color:#ffffff;box-shadow:0 2px 4px rgba(0,0,0,0.05);">'
                f'<h4 style="margin:0 0 10px 0;color:#000000;border-bottom:2px solid #98FB98;padding-bottom:4px;">{item["成分名"]}</h4>'
                f'<div style="font-size:14px;color:#333333;line-height:1.6;">'
                f'<div>✨ <b>効果:</b> {eff}</div>'
                f'<div style="margin-top:4px;">⏳ <b>効果時間:</b> {dur}</div>'
                f'<div style="margin-top:4px;">📍 <b>ロケーション:</b> {loc}</div>'
                f'{scent_html}'
                f'</div>'
                f'</div>'
            )
            
            with cols[i % 2]:
                st.markdown(card_html, unsafe_allow_html=True)
