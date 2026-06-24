import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データを分類別・詳細項目別に確認できます。")

# 📊 アプリ側の共通カラム定義
GALLERY_COLS = ["成分名", "分類", "効果", "効果時間", "ロケーション", "香り"]

# 1. データベース（スプレッドシートやCSV）から最新データを読み込む
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

# 💡 データベースが完全に空の場合のみ、Excel(data.xlsx)から初期データを復元・同期する
if df_gallery.empty:
    with st.spinner("🔄 データベースが空のため、Excelから初期データを抽出中..."):
        try:
            excel_file = "data.xlsx"
            restored_rows = []
            xl = pd.ExcelFile(excel_file)
            sheets = xl.sheet_names
            
            categories_map = {
                "半合成": "半合成",
                "カンナビノイド": "カンナビノイド",
                "テルペン": "テルペン"
            }
            
            for sheet_name, cat_label in categories_map.items():
                if sheet_name in sheets:
                    df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
                    df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                    
                    if "成分名" not in df_sheet.columns:
                        for idx, row in df_sheet.iterrows():
                            if "成分名" in row.values:
                                df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=idx+1)
                                df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                                break
                    
                    for _, row in df_sheet.iterrows():
                        name = row.get("成分名")
                        if pd.isna(name) or str(name).strip() == "成分名" or str(name).strip() == "" or str(name).strip() == "nan":
                            continue
                        
                        eff_val = row.get("効果")
                        dur_val = row.get("時間")
                        
                        if cat_label == "テルペン":
                            loc_val = "-"
                            scent_val = row.get("香り")
                        else:
                            loc_val = row.get("ロケーション")
                            scent_val = "-"
                        
                        def clean_val(v):
                            return str(v).strip() if not pd.isna(v) and str(v).strip() != "nan" and str(v).strip() != "" else "-"
                        
                        restored_rows.append({
                            "成分名": str(name).strip(), 
                            "分類": cat_label, 
                            "効果": clean_val(eff_val), 
                            "効果時間": clean_val(dur_val), 
                            "ロケーション": clean_val(loc_val),
                            "香り": clean_val(scent_val)
                        })
            
            if restored_rows:
                df_restored = pd.DataFrame(restored_rows)
                save_all_data_to_db("Gallery_Master", df_restored, GALLERY_COLS)
                df_gallery = df_restored
                st.success("🎉 成分表Excelからデータを初期同期しました！")
        except Exception as e:
            st.error(f"❌ Excel自動抽出エラー: {e}")

# 2. 分類ごとの振り分け表示処理（新しく登録されたデータもここで自動追加されます）
if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。『✨ 成分ギャラリー登録』から追加してください。")
else:
    # 💡 登録フォームで選択できるすべての分類に対応
    target_categories = ["カンナビノイド", "半合成", "テルペン", "その他"]
    
    for cat in target_categories:
        cat_items = df_gallery[df_gallery["分類"] == cat]
        if cat_items.empty:
            continue
            
        st.subheader(f"🏷️ {cat}")
        cols = st.columns(2)
        
        for i, (_, item) in enumerate(cat_items.iterrows()):
            if str(item['成分名']).strip() == "成分名":
                continue
                
            eff = item.get("効果", "-")
            dur = item.get("効果時間", "-")
            loc = item.get("ロケーション", "-")
            scent = item.get("香り", "-")
            
            # テルペンなら香り、それ以外ならロケーションを動的に表示
            if cat == "テルペン":
                sub_info_html = f'<div style="margin-top:4px;">🍋 <b>香り:</b> {scent}</div>'
            else:
                sub_info_html = f'<div style="margin-top:4px;">📍 <b>ロケーション:</b> {loc}</div>'
            
            card_html = (
                f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:15px;margin-bottom:15px;background-color:#ffffff;box-shadow:0 2px 4px rgba(0,0,0,0.05);">'
                f'<h4 style="margin:0 0 10px 0;color:#000000;border-bottom:2px solid #98FB98;padding-bottom:4px;">{item["成分名"]}</h4>'
                f'<div style="font-size:14px;color:#333333;line-height:1.6;">'
                f'<div>✨ <b>効果:</b> {eff}</div>'
                f'<div style="margin-top:4px;">⏳ <b>効果時間:</b> {dur}</div>'
                f'{sub_info_html}'
                f'</div>'
                f'</div>'
            )
            
            with cols[i % 2]:
                st.markdown(card_html, unsafe_allow_html=True)
