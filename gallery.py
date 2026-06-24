import streamlit as st
import pandas as pd

st.title("📖 成分ギャラリー(閲覧)")
st.write("登録済みの成分データを詳細項目別に確認できます。")

# 📊 アプリ側の共通カラム定義
GALLERY_COLS = ["成分名", "分類", "効果", "効果時間", "ロケーション", "香り"]

# 💡 【重要】古い「未登録」のデータを強制的にリセットしてExcelから読み直すための設定
# ※一度正しく読み込まれた後は、このフラグをTrueのままにしておけば何度もリセットされません。
FORCE_RESET = True 

# 1. データベースからデータを読み込む
df_gallery = load_data_from_db("Gallery_Master", GALLERY_COLS)

# 💡 データベースが空、または強制リセットが有効な場合、Excelから再抽出する
if df_gallery.empty or FORCE_RESET:
    with st.spinner("🔄 Excelの成分表から効果や時間を100%抽出中..."):
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
                    # 💡 スキャン開始位置を調整（0行目から読み込み、後から見出し行を探す最も安全な方法）
                    df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
                    
                    # すべての文字を文字列にして前後の空白を削除
                    df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                    
                    # もし最初の読み込みでズレていたら、データ行の中から「成分名」がある行を探して見出しに再設定
                    if "成分名" not in df_sheet.columns:
                        for idx, row in df_sheet.iterrows():
                            if "成分名" in row.values:
                                df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=idx+1)
                                df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
                                break
                    
                    # データの抽出ループ
                    for _, row in df_sheet.iterrows():
                        name = row.get("成分名")
                        if pd.isna(name) or str(name).strip() == "成分名" or str(name).strip() == "" or str(name).strip() == "nan":
                            continue
                        
                        # 💡 実際のExcelの列名に完全一致させて抽出
                        eff_val = row.get("効果")
                        dur_val = row.get("時間")  # カンナビノイド/半合成/テルペン共通の「時間」列
                        
                        # 分類によって取得する列を分ける
                        if cat_label == "テルペン":
                            loc_val = "-"
                            scent_val = row.get("香り")
                        else:
                            loc_val = row.get("ロケーション")
                            scent_val = "-"
                        
                        # nan（空欄）の文字を「-」に綺麗に整える関数
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
                # データベース（スプレッドシート）を完全に新しい正しいデータで上書き！
                save_all_data_to_db("Gallery_Master", df_restored, GALLERY_COLS)
                df_gallery = df_restored
                st.success("🎉 成分表のExcelから「効果」「時間」「ロケーション」「香り」を100%完全に同期しました！")
        except Exception as e:
            st.error(f"❌ Excel自動抽出エラー: {e}")

# 2. データの画面表示処理
if df_gallery.empty:
    st.info("まだギャラリーにデータがありません。")
else:
    # 表示する順番を固定
    categories = ["カンナビノイド", "半合成", "テルペン"]
    
    for cat in categories:
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
            
            # テルペンなら「香り」、それ以外なら「ロケーション」をカードの下部に表示
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
