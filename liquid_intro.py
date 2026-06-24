import streamlit as st
import pandas as pd

# --- カラム構造の定義 ---
LIQUID_MASTER_COLS = ["リキッド名", "配合詳細"]
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ", "画像"]

st.title("📸 リキッド・成分紹介 & ギャラリー")
st.write("Excelの全成分マスター一覧と、各リキッドの写真・レビュー履歴をまとめて確認できます。")

# 1. データベース（Excel / スプレッドシート）からデータを取得
if 'load_data_from_db' in globals():
    df_master = globals()['load_data_from_db']("Liquid_Master", LIQUID_MASTER_COLS)
    df_logs = globals()['load_data_from_db']("Attraction_Logs", LOG_COLS)
else:
    df_master = pd.DataFrame(columns=LIQUID_MASTER_COLS)
    df_logs = pd.DataFrame(columns=LOG_COLS)

# =========================================================
# 📊 【最優先】Excelの成分一覧表（効果、効果時間、ロケーション、香りを網羅）
# =========================================================
st.markdown("---")
st.header("📋 成分マスター一覧（Excelデータ）")
st.write("アップロードされたExcelシートごとの全成分リストです。タブで切り替えて確認できます。")

# 3つのシート（カンナビノイド、半合成、テルペン）をタブ形式で綺麗に整理
tab1, tab2, tab3 = st.tabs(["🧪 カンナビノイド", "🧬 半合成", "🌿 テルペン"])

with tab1:
    st.subheader("🧪 カンナビノイド一覧")
    cannabinoid_data = [
        {"成分名": "CBD", "効果": "リラックス効果, 抗炎症, 睡眠の質の向上", "効果時間": "2〜4h", "ロケーション": "【合法】 成熟した茎や種子由来、または純粋な合成品であれば流通可能。"},
        {"成分名": "CBG", "効果": "すっきりとした感覚, 抗炎症, 抗菌作用", "効果時間": "2～6h", "ロケーション": "【合法】 精神作用がなく、広く市販製品に使用されている。"},
        {"成分名": "CBC", "効果": "アントラージュ効果向上", "効果時間": "2〜4h", "ロケーション": "【合法】 精神作用はなく、ブレンド用として流通。"},
        {"成分名": "CBN", "効果": "深い持続的なリラックス感, 強い抗不安作用", "効果時間": "3〜5h", "ロケーション": "【指定薬物】完全違法（2026年6月1日より規制対象）"},
        {"成分名": "CBDP", "効果": "深い持続的なリラックス感, 強い抗不安作用", "効果時間": "5〜8h", "ロケーション": "【合法】 CRDPなどのベースとなる天然由来のマイナー成分。"}
    ]
    st.table(pd.DataFrame(cannabinoid_data))

with tab2:
    st.subheader("🧬 半合成カンナビノイド一覧")
    semi_synthetic_data = [
        {"成分名": "HHC", "効果": "多幸感, リラックス感, 知覚の変化", "効果時間": "3〜5h", "ロケーション": "【指定薬物】完全違法（2022年3月規制）"},
        {"成分名": "HHCP", "効果": "ボディハイ, 陶酔感", "効果時間": "12〜24h", "ロケーション": "【指定薬物】完全違法（2022年春〜夏規制）"},
        {"成分名": "THCO", "効果": "多幸感, マンチ（時間差で押し寄せる）", "効果時間": "4〜8h", "ロケーション": "【指定薬物】完全違法（2023年3月規制）"},
        {"成分名": "HHCO", "効果": "多幸感（時間差で押し寄せる）", "効果時間": "4〜6h", "ロケーション": "【指定薬物】完全違法（2023年3月規制）"},
        {"成分名": "THCH", "効果": "ヘッドハイ, 視覚の変化, 聴覚の変容, 多幸感", "効果時間": "4〜8h", "ロケーション": "【指定薬物】完全違法（2023年8月規制）"},
        {"成分名": "HHCH", "効果": "眠気, 酩酊感（大麻グミの主成分）", "効果時間": "6〜12h", "ロケーション": "【指定薬物】完全違法（2023年12月規制）"},
        {"成分名": "THCPO", "効果": "幻覚作用, パニック, 動悸, 強烈な眠気", "効果時間": "24〜48h", "ロケーション": "【指定薬物】完全違法（2024年初頭規制）"},
        {"成分名": "10-OH-HHC", "効果": "軽いふわふわ感, 穏やかなリラックス効果", "効果時間": "3〜5h", "ロケーション": "【指定薬物】完全違法"},
        {"成分名": "8-OH-HHC", "効果": "マイルドなリラックス感", "効果時間": "2〜4h", "ロケーション": "【指定薬物】完全違法"},
        {"成分名": "10-OH-HHCP", "効果": "超強力な効果、ヘッド・ボディハイ", "効果時間": "12〜24h", "ロケーション": "【指定薬物】完全違法"}
    ]
    st.table(pd.DataFrame(semi_synthetic_data))

with tab3:
    st.subheader("🌿 テルペン一覧（香りデータ付き）")
    terpene_data = [
        {"成分名": "ミルセン", "効果": "強いリラックス効果, 鎮静作用, 筋肉の弛緩, 睡眠サポート", "効果時間": "2〜4h", "香り": "アース（土っぽさ）, マンゴー, ムスク"},
        {"成分名": "リモネン", "効果": "気分の高揚, ストレス緩和, 抗不安, 活力を与える", "効果時間": "1〜3h", "香り": "柑橘類（レモン、ライム、オレンジ）"},
        {"成分名": "カリオフィレン", "効果": "抗炎症作用, 鎮痛効果, 不安の軽減（CB2受容体に直接作用）", "効果時間": "2〜4h", "香り": "スパイシー, 黒胡椒, ウッド, ウコン"},
        {"成分名": "リナロール", "効果": "強力なリラックス効果, 不安や気分の落ち込みの改善, 安眠", "効果時間": "2〜4h", "香り": "フローラル, ラベンダー, ほのかなスパイシー"},
        {"成分名": "ピネン", "効果": "集中力の向上, 記憶力サポート, 気管支拡張, 覚醒作用", "効果時間": "1〜2h", "香り": "松の木, 森林の香り, ハーブ"},
        {"成分名": "テルピノレン", "効果": "軽い中枢鎮静, 抗菌作用, 抗酸化作用, 気分のリフレッシュ", "効果時間": "2〜3h", "香り": "フレッシュ, ハーブ, ほのかな柑橘とウッド"},
        {"成分名": "フムレン", "効果": "抗炎症作用, 抗菌作用, 食欲抑制（マンチを抑える）", "効果時間": "2〜4h", "香り": "ホップ, ウッディ, 土っぽさ"},
        {"成分名": "オシメン", "効果": "抗ウイルス作用, うっ滞除去, 爽快感", "効果時間": "1〜2h", "香り": "甘いフローラル, トロピカルフルーツ, 木質"}
    ]
    st.table(pd.DataFrame(terpene_data))

st.markdown("---")

# =========================================================
# 🚬 ここから各リキッドの個別詳細・レビュー履歴
# =========================================================
st.header("🚬 各リキッドのギャラリー＆レビュー履歴")

if not df_master.empty:
    all_liquids = df_master["リキッド名"].dropna().unique().tolist()
elif not df_logs.empty:
    all_liquids = df_logs["リキッド名"].dropna().unique().tolist()
else:
    all_liquids = []

if not all_liquids:
    st.caption("現在、登録されているリキッドやレビュー履歴はありません。")
else:
    selected_liq = st.selectbox("詳細を確認するリキッドを選択", all_liquids)
    
    # 選択リキッドの配合内容を表示
    liq_row = df_master[df_master["リキッド名"] == selected_liq] if not df_master.empty else pd.DataFrame()
    if not liq_row.empty:
        st.info(f"📋 **このリキッドの現在の配合詳細:** {liq_row['配合詳細'].values[0]}")

    # 📸 フォトギャラリー
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

    # 📋 これまでのレビュー履歴（ご要望に合わせて日付のカラムは非表示）
    st.subheader("📋 これまでのレビュー履歴")
    if not target_logs.empty:
        display_rows = []
        for _, row in target_logs.iterrows():
            eff_text = row['体感した効果']
            if (pd.isna(eff_text) or eff_text == '') and pd.notna(row['パフ数']) and row['パフ数'] > 0:
                eff_text = f"🚬 吸引記録 ({row['パフ数']} puffs)"
            memo_text = row['体感メモ'] if pd.notna(row['体感メモ']) and row['体感メモ'] != '' else "ーー"
            display_rows.append({"内容": eff_text, "メモ": memo_text})
        
        st.table(pd.DataFrame(display_rows))
    else:
        st.caption("📋 レビュー履歴はまだありません。")
