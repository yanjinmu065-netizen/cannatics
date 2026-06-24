import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

# 📊 Excelの成分一覧データを辞書（マスターデータ）として定義
# リキッドの配合詳細に含まれる成分を自動マッチングして、解説を引っ張ってきます
INGREDIENTS_DB = {
    # カンナビノイド
    "CBD": {"効果": "リラックス効果, 抗炎症, 睡眠の質の向上", "時間": "2〜4h", "ロケーション": "【合法】 成熟した茎や種子由来、または純粋な合成品であれば流通可能。", "タイプ": "カンナビノイド"},
    "CBG": {"効果": "すっきりとした感覚, 抗炎症, 抗菌作用", "時間": "2～6h", "ロケーション": "【合法】 精神作用がなく、広く市販製品に使用されている。", "タイプ": "カンナビノイド"},
    "CBC": {"効果": "アントラージュ効果向上", "時間": "2〜4h", "ロケーション": "【合法】 精神作用はなく、ブレンド用として流通。", "タイプ": "カンナビノイド"},
    "CBN": {"効果": "深い持続的なリラックス感, 強い抗不安作用", "時間": "3〜5h", "ロケーション": "【指定薬物】完全違法（2026年6月1日より規制対象）", "タイプ": "カンナビノイド"},
    "CBDP": {"効果": "深い持続的なリラックス感, 強い抗不安作用", "時間": "5〜8h", "ロケーション": "【合法】 CRDPなどのベースとなる天然由来のマイナー成分。", "タイプ": "カンナビノイド"},
    
    # 半合成
    "HHC": {"効果": "多幸感, リラックス感, 知覚の変化", "時間": "3〜5h", "ロケーション": "【指定薬物】完全違法（2022年3月規制）", "タイプ": "半合成"},
    "HHCP": {"効果": "ボディハイ, 陶酔感", "時間": "12〜24h", "ロケーション": "【指定薬物】完全違法（2022年春〜夏規制）", "タイプ": "半合成"},
    "THCO": {"効果": "多幸感, マンチ（時間差で押し寄せる）", "時間": "4〜8h", "ロケーション": "【指定薬物】完全違法（2023年3月規制）", "タイプ": "半合成"},
    "HHCO": {"効果": "多幸感（時間差で押し寄せる）", "時間": "4〜6h", "ロケーション": "【指定薬物】完全違法（2023年3月規制）", "タイプ": "半合成"},
    "THCH": {"効果": "ヘッドハイ, 視覚の変化, 聴覚の変容, 多幸感", "時間": "4〜8h", "ロケーション": "【指定薬物】完全違法（2023年8月規制）", "タイプ": "半合成"},
    "HHCH": {"効果": "眠気, 酩酊感（大麻グミの主成分）", "時間": "6〜12h", "ロケーション": "【指定薬物】完全違法（2023年12月規制）", "タイプ": "半合成"},
    "THCPO": {"効果": "幻覚作用, パニック, 動悸, 強烈な眠気", "時間": "24〜48h", "ロケーション": "【指定薬物】完全違法（2024年初頭規制）", "タイプ": "半合成"},
    "10-OH-HHC": {"効果": "軽いふわふわ感, 穏やかなリラックス効果", "時間": "3〜5h", "ロケーション": "【指定薬物】完全違法", "タイプ": "半合成"},
    "8-OH-HHC": {"効果": "マイルドなリラックス感", "時間": "2〜4h", "ロケーション": "【指定薬物】完全違法", "タイプ": "半合成"},
    
    # テルペン（「香り」項目付き）
    "ミルセン": {"効果": "強いリラックス効果, 鎮静作用, 筋肉の弛緩, 睡眠サポート", "時間": "2〜4h", "香り": "アース（土っぽさ）, マンゴー, ムスク", "タイプ": "テルペン"},
    "リモネン": {"効果": "気分の高揚, ストレス緩和, 抗不安, 活力を与える", "時間": "1〜3h", "香り": "柑橘類（レモン、ライム、オレンジ）", "タイプ": "テルペン"},
    "カリオフィレン": {"効果": "抗炎症作用, 鎮痛効果, 不安の軽減（CB2受容体に直接作用）", "時間": "2〜4h", "香り": "スパイシー, 黒胡椒, ウッド, ウコン", "タイプ": "テルペン"},
    "リナロール": {"効果": "強力なリラックス効果, 不安や気分の落ち込みの改善, 安眠", "時間": "2〜4h", "香り": "フローラル, ラベンダー, ほのかなスパイシー", "タイプ": "テルペン"},
    "ピネン": {"効果": "集中力の向上, 記憶力サポート, 気管支拡張, 覚醒作用", "時間": "1〜2h", "香り": "松の木, 森林の香り, ハーブ", "タイプ": "テルペン"},
    "テルピノレン": {"効果": "軽い中枢鎮静, 抗菌作用, 抗酸化作用, 気分のリフレッシュ", "時間": "2〜3h", "香り": "フレッシュ, ハーブ, ほのかな柑橘とウッド", "タイプ": "テルペン"},
    "フムレン": {"効果": "抗炎症作用, 抗菌作用, 食欲抑制（マンチを抑える）", "時間": "2〜4h", "香り": "ホップ, ウッディ, 土っぽさ", "タイプ": "テルペン"},
    "オシメン": {"効果": "抗ウイルス作用, うっ滞除去, 爽快感", "時間": "1〜2h", "香り": "甘いフローラル, トロピカルフルーツ, 木質", "タイプ": "テルペン"},
}

st.title("📸 リキッド・成分紹介 & ギャラリー")
st.write("各リキッドに配合されている成分の詳細と、これまでの写真・レビュー履歴をまとめて確認できます。")

# 1. データベース（Excel / スプレッドシート）からデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

# 表示するリキッド名のリスト
if not df_master.empty:
    all_liquids = df_master["リキッド名"].dropna().unique().tolist()
elif not df_logs.empty:
    all_liquids = df_logs["リキッド名"].dropna().unique().tolist()
else:
    all_liquids = []

if not all_liquids:
    st.warning("⚠️ まだExcelにリキッドが登録されていないか、レビューの記録がありません。")
else:
    # 🚬 リキッド選択用のドロップダウン
    selected_liq = st.selectbox("🚬 詳細を確認するリキッドを選択", all_liquids)
    
    st.markdown("---")

    # =========================================================
    # 🧪 Excelの成分配合から各成分の詳細（効果・時間・規制・香り）を自動表示
    # =========================================================
    st.subheader("🧪 配合成分の詳しい効果・情報")
    
    # 選択されたリキッドの配合詳細を取得
    liq_row = df_master[df_master["リキッド名"] == selected_liq] if not df_master.empty else pd.DataFrame()
    detail_str = ""
    if not liq_row.empty:
        detail_str = str(liq_row["配合詳細"].values[0])
    else:
        latest_log = df_logs[df_logs["リキッド名"] == selected_liq] if not df_logs.empty else pd.DataFrame()
        if not latest_log.empty:
            detail_str = str(latest_log['配合詳細'].iloc[0])
            
    if detail_str:
        st.info(f"📋 **現在の配合:** {detail_str}")
        
        # 配合詳細文字列（例: "CBD:30%, ミルセン:5%"）から成分名を抽出してマッチング
        matched_components = []
        for ing_name, ing_info in INGREDIENTS_DB.items():
            if ing_name.lower() in detail_str.lower():
                # 画面表示用の行データを作成
                row_data = {
                    "成分名": f"{'🌿' if ing_info['type'] == 'テルペン' else '🧪'} {ing_name}",
                    "効果・効能": ing_info["効果"],
                    "効果時間": ing_info["時間"],
                    "ロケーション (規制状況)": ing_info["ロケーション"],
                    "香り (テルペンのみ)": ing_info.get("香り", "ーー") # テルペン以外は「ーー」
                }
                matched_components.append(row_data)
                
        if matched_components:
            df_comp_display = pd.DataFrame(matched_components)
            # 綺麗で読みやすい詳細表をドカンと表示！
            st.table(df_comp_display)
        else:
            st.caption("⚠️ 配合詳細に含まれる成分の解説データがマスターに見つかりませんでした。")
    else:
        st.caption("⚠️ 配合詳細データが登録されていません。")

    st.markdown("---")

    # =========================================================
    # 🖼️ フォトギャラリー セクション
    # =========================================================
    st.subheader("🖼️ フォトギャラリー")
    
    target_logs = df_logs[df_logs["リキッド名"] == selected_liq].copy() if not df_logs.empty else pd.DataFrame()
    
    if not target_logs.empty:
        target_logs['sort_id'] = range(len(target_logs))
        target_logs = target_logs.sort_values(by=['日付', 'sort_id'], ascending=[False, False])
        
        img_logs = target_logs[target_logs["画像"].notna() & (target_logs["画像"] != "")]
        
        if not img_logs.empty:
            cols = st.columns(3)
            for i, (_, row) in enumerate(img_logs.iterrows()):
                with cols[i % 3]:
                    st.image(f"data:image/png;base64,{row['画像']}", use_column_width=True)
                    st.caption(f"📅 {row['日付']}")
        else:
            st.caption("📸 このリキッドに登録された写真はありません。")
    else:
        st.caption("📸 写真はありません。")

    st.markdown("---")

    # =========================================================
    # 📋 体感レビュー履歴表 セクション（日付なし）
    # =========================================================
    st.subheader("📋 これまでのレビュー履歴")
    
    if not target_logs.empty:
        display_rows = []
        for _, row in target_logs.iterrows():
            eff_text = row['体感した効果']
            if (pd.isna(eff_text) or eff_text == '') and pd.notna(row['パフ数']) and row['パフ数'] > 0:
                eff_text = f"🚬 吸引記録 ({row['パフ数']} puffs)"
            
            memo_text = row['体感メモ'] if pd.notna(row['体感メモ']) and row['体感メモ'] != '' else "ーー"
            
            display_rows.append({
                "内容": eff_text,
                "メモ": memo_text
            })
        
        display_df = pd.DataFrame(display_rows)
        st.table(display_df)
    else:
        st.caption("📋 レビュー履歴はまだありません。")
