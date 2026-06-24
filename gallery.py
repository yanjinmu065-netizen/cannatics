import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データを詳細項目別に確認できます。")

# 📊 アプリ側の共通カラム定義
GALLERY_COLS = ["成分名", "分類", "効果", "効果時間", "ロケーション", "香り"]

# 1. データベースからデータを読み込む
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

# 💡 データベースが完全に空の場合、Excel(data.xlsx)から初期データを復元
if df_gallery.empty:
    with st.spinner("🔄 Excel(data.xlsx)の成分表からデータを完全に抽出中..."):
        try:
            excel_file = "data.xlsx"
            restored_rows = []
            sheets = pd.ExcelFile(excel_file).sheet_names
            
            # 各シートの名前と分類の対応
            categories_map = {
                "半合成": "半合成",
                "カンナビノイド": "カンナビノイド",
                "テルペン": "テルペン"
            }
            
            for sheet_name, cat_label in categories_map.items():
                if sheet_name in sheets:
                    # 💡 実際の構造（3行飛ばして4行目がヘッダー）に合わせて読み込み
                    df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=2)
                    
                    # 列名の前後の空白を削除
                    df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                    
                    for _, row in df_sheet.iterrows():
                        name = row.get("成分名")
                        # 空白行や見出し行のダブりを徹底除外
                        if pd.isna(name) or str(name).strip() == "成分名" or str(name).strip() == "" or str(name).strip() == "nan":
                            continue
                        
                        # 💡 Excelの実際の列名からデータを抽出
                        eff_val = row.get("効果", "-")
                        dur_val = row.get("時間", "-")          # Excelでは「時間」
                        loc_val = row.get("ロケーション", "-")  # カンナビノイド・半合成用
                        scent_val = row.get("香り", "-")        # テルペン用
                        
                        # nan（空欄）の対策
                        eff_val = str(eff_val).strip() if not pd.isna(eff_val) and str(eff_val).strip() != "nan" else "-"
                        dur_val = str(dur_val).strip() if not pd.isna(dur_val) and str(dur_val).strip() != "nan" else "-"
                        loc_val = str(loc_val).strip() if not pd.isna(loc_val) and str(loc_val).strip() != "nan" else "-"
                        scent_val = str(scent_val).strip() if not pd.isna(scent_val) and str(scent_val).strip() != "nan" else "-"
                        
                        restored_rows.append({
                            "成分名": str(name).strip(), 
                            "分類": cat_label, 
                            "効果": eff_val, 
                            "効果時間": dur_val, 
                            "ロケーション": loc_val if cat_label != "テルペン" else "-",
                            "香り": scent_val if cat_label == "テルペン" else "-"
                        })
            
            if restored_rows:
                df_restored = pd.DataFrame(restored_rows)
                # スプレッドシート（またはCSV）へ一括保存
                save_all_data_to_db("Gallery_Master", df_restored, GALLERY_COLS)
                # 画面表示用に再読み込み
                df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)
                st.success("🎉 成分表Excelから「効果」「時間」「ロケーション」「香り」をすべて同期しました！")
        except Exception as e:
            st.error(f"❌ Excel読み込み・抽出エラー: {e}")

# 2. データの表示処理
if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。ジャンルを切り替えて『✨ 成分ギャラリー登録』から追加してください。")
else:
    categories = ["カンナビノイド", "半合成", "テルペン"]
    
    for cat in categories:
        cat_items = df_gallery[df_gallery["分類"] == cat]
        if cat_items.empty:
            continue
            
        st.subheader(f"🏷️ {cat}")
        cols = st.columns(2)
        
        for i, (_, item) in enumerate(cat_items.iterrows():
            if str(item['成分名']).strip() == "成分名":
                continue
                
            eff = item.get("効果", "-")
            dur = item.get("効果時間", "-")
            loc = item.get("ロケーション", "-")
            scent = item.get("香り", "-")
            
            # テルペンだけ「香り」を表示、それ以外は「ロケーション」を表示
            sub_info_html = f'<div style="margin-top:4px;">🍋 <b>香り:</b> {scent}</div>' if cat == "テルペン" else f'<div style="margin-top:4px;">📍 <b>ロケーション:</b> {loc}</div>'
            
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
