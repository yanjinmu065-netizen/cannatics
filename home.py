import streamlit as st
import pandas as pd
import datetime
import os

# --- ページ設定とパスワード保護 ---
st.set_page_config(page_title="Cannatics", layout="centered")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 ログイン - Cannatics")
    password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == "0602": # パスワード
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False

if check_password():
    # --- Excelデータから成分と効果を賢く自動抽出・整理 ---
    @st.cache_data
    def load_excel_and_extract_tags():
        try:
            # 【対策】header=2 を指定して、Excelの3行目をヘッダー（列名）として正しく認識させます
            df_cannabinoid = pd.read_excel("data.xlsx", sheet_name="カンナビノイド", header=2)
            df_synthetic = pd.read_excel("data.xlsx", sheet_name="半合成", header=2)
            df_terpene = pd.read_excel("data.xlsx", sheet_name="テルペン", header=2)
            
            # --- 1. 成分リストの抽出 ---
            g1_list = []
            if "成分名" in df_synthetic.columns:
                for _, row in df_synthetic.dropna(subset=["成分名"]).iterrows():
                    loc = str(row.get("ロケーション", ""))
                    status = " ⚠️" if "違法" in loc or "規制" in loc else ""
                    g1_list.append(f"{row['成分名']}{status}")
                
            g2_list = []
            if "成分名" in df_cannabinoid.columns:
                for _, row in df_cannabinoid.dropna(subset=["成分名"]).iterrows():
                    loc = str(row.get("ロケーション", ""))
                    status = " ⚠️" if "違法" in loc or "規制" in loc else ""
                    g2_list.append(f"{row['成分名']}{status}")
                
            g3_list = []
            if "成分名" in df_terpene.columns:
                g3_list = list(df_terpene["成分名"].dropna().unique())
            
            # --- 2. 効果（体感ボタン用タグ）の自動分解・抽出 ---
            all_effects = set()
            for df in [df_cannabinoid, df_synthetic, df_terpene]:
                if "効果" in df.columns:
                    for eff_str in df["効果"].dropna():
                        # 全角・半角カンマ、読点で区切られている体感を綺麗に分解
                        for e in str(eff_str).replace("、", ",").split(","):
                            clean_e = e.strip()
                            if clean_e:
                                all_effects.add(clean_e)
                                
            return g1_list, g2_list, g3_list, sorted(list(all_effects))
        except Exception as e:
            # 最悪読み込めなかった場合のセーフティ
            return ["CRDP", "THA"], ["CBD", "CBG"], ["ミルセン", "リモネン"], ["リラックス", "多幸感", "眠気"]

    g1_presets, g2_presets, g3_presets, extracted_effects = load_excel_and_extract_tags()

    # カスタムCSS（リクエストのデザイン修正を追加）
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        h1, h2, h3, h4, p, label, .stMarkdown { color: #000000 !important; font-family: 'Noto Sans JP', sans-serif; }
        
        /* ➕枠を追加・➖枠を削除ボタンの色を #98FB98 (淡い緑) に変更 */
        .stButton>button { 
            background-color: #98FB98 !important; 
            color: #000000 !important; 
            font-weight: bold; 
            border_radius: 8px; 
            border: 1px solid #000000; 
            width: 100%; 
            height: 45px;
        }
        .group-container {
            border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fafafa;
        }
        .group-title {
            font-weight: bold; font-size: 16px; border-left: 4px solid #00ffff; padding-left: 10px; margin-bottom: 15px;
        }
        
        /* サイドバーのリンク文字色を「白」にする */
        [data-testid="stSidebarNav"] ul li a span {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if "custom_components" not in st.session_state: st.session_state.custom_components = []
    if "group1_rows" not in st.session_state: st.session_state.group1_rows = 1
    if "group2_rows" not in st.session_state: st.session_state.group2_rows = 1
    if "group3_rows" not in st.session_state: st.session_state.group3_rows = 1
    if "history_logs" not in st.session_state: st.session_state.history_logs = {}

    pg_home = st.Page("home.py", title="📝 配合電卓・分析", icon="📝")
    pg_seibunn = st.Page("seibunn.py", title="🌐 新成分マスター登録", icon="🌐")
    pg_calendar = st.Page("calendar.py", title="📅 履歴カレンダー", icon="📅")
    
    # 🌟 【修正箇所】ナビゲーションに「成分紹介」のダミーページを紐付け
    pg_intro = st.Page("home.py", title="📊 成分紹介", icon="📊")
    
    pg = st.navigation([pg_home, pg_seibunn, pg_calendar, pg_intro], position="sidebar")

    if pg == pg_home:
        st.title("🌿 Cannatics (カンナティクス)")
        st.subheader("🧪 グループ別・配合電卓")

        all_g1 = g1_presets + [c["name"] for c in st.session_state.custom_components if c['group'] == '活性']
        all_g2 = g2_presets + [c["name"] for c in st.session_state.custom_components if c['group'] == 'ベース']
        all_g3 = g3_presets + [c["name"] for c in st.session_state.custom_components if c['group'] == 'テルペン']

        liquid_data = {}

        # --- 1. 主要精神活性成分 ---
        st.markdown('<div class="group-container"><div class="group-title">🔥 1. 主要精神活性成分（半合成等）</div>', unsafe_allow_html=True)
        c_add, c_del = st.columns(2)
        with c_add:
            if st.button("➕ 枠を追加", key="add_g1"): st.session_state.group1_rows += 1; st.rerun()
        with c_del:
            if st.button("➖ 枠を削除", key="del_g1"):
                if st.session_state.group1_rows > 0: st.session_state.group1_rows -= 1; st.rerun()

        g1_total = 0.0
        for i in range(st.session_state.group1_rows):
            if not all_g1: break
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"活性成分 {i+1}", all_g1, key=f"g1_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key=f"g1_p_{i}")
            if pct > 0: liquid_data[name] = pct; g1_total += pct
        st.metric("活性成分 合計値", f"{g1_total} %")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 2. ベース成分 ---
        st.markdown('<div class="group-container"><div class="group-title">🌿 2. ベース成分（天然カンナビノイド等）</div>', unsafe_allow_html=True)
        c_add2, c_del2 = st.columns(2)
        with c_add2:
            if st.button("➕ 枠を追加", key="add_g2"): st.session_state.group2_rows += 1; st.rerun()
        with c_del2:
            if st.button("➖ 枠を削除", key="del_g2"):
                if st.session_state.group2_rows > 0: st.session_state.group2_rows -= 1; st.rerun()

        g2_total = 0.0
        for i in range(st.session_state.group2_rows):
            if not all_g2: break
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"ベース成分 {i+1}", all_g2, key=f"g2_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key=f"g2_p_{i}")
            if pct > 0: liquid_data[name] = pct; g2_total += pct
        st.metric("ベース成分 合計値", f"{g2_total} %")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 3. テルペン・その他 ---
        st.markdown('<div class="group-container"><div class="group-title">🧪 3. テルペン・その他添加剤</div>', unsafe_allow_html=True)
        c_add3, c_del3 = st.columns(2)
        with c_add3:
            if st.button("➕ 枠を追加", key="add_g3"): st.session_state.group3_rows += 1; st.rerun()
        with c_del3:
            if st.button("➖ 枠を削除", key="del_g3"):
                if st.session_state.group3_rows > 0: st.session_state.group3_rows -= 1; st.rerun()

        g3_total = 0.0
        for i in range(st.session_state.group3_rows):
            if not all_g3: break
            c1, c2 = st.columns([2, 1])
            with c1: name = st.selectbox(f"添加成分 {i+1}", all_g3, key=f"g3_n_{i}")
            with c2: pct = st.number_input(f"比率 {i+1} (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"g3_p_{i}")
            if pct > 0: liquid_data[name] = pct; g3_total += pct
        st.metric("テルペン・その他 合計値", f"{g3_total} %")
        st.markdown('</div>', unsafe_allow_html=True)

        grand_total = g1_total + g2_total + g3_total
        st.subheader(f"🧮 総合計配合比率: {grand_total} %")

        st.markdown("---")
        st.subheader("3. 吸引ログと体感レビューの選択")
        puffs = st.slider("今回の摂取量 (パフ数)", 1, 10, 3)
        
        selected_effects = st.multiselect("🟢 🔴 体感した効果・副反応を選択", extracted_effects)
        
        user_memo = st.text_area("体感メモ（自由記述）")
        log_date = st.date_input("記録する日付", datetime.date.today())

        if st.button("📊 チャートを生成して履歴に保存"):
            if grand_total == 0:
                st.error("数値を入力してください。")
            else:
                date_str = log_date.strftime("%Y-%m-%d")
                st.session_state.history_logs[date_str] = {
                    "liquid_data": liquid_data, "puffs": puffs, "memo": user_memo,
                    "g1_total": g1_total, "g2_total": g2_total,
                    "effects": selected_effects
                }
                st.success(f"🎉 {date_str} のログを保存しました！『📅 履歴カレンダー』を確認してください。")

    # 🌟 【ここから末尾に新規付け足し】成分紹介メニューが選ばれたときの表示処理
    elif pg == pg_intro:
        st.title("📊 カンナティクス 成分紹介")
        st.write("`data.xlsx` に登録されている、すべてのシートの成分データを切り替えて確認できます。")

        file_path = "data.xlsx"

        if os.path.exists(file_path):
            try:
                # Excelを開いてシート名を全部自動取得
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                # ユーザーがシートを切り替えられる選択ボックスを設置
                selected_sheet = st.selectbox("確認したいシートを選択してください", sheet_names)
                
                # あなたのExcelに合わせて、3行目(header=2)を項目名（成分名・効果・時間など）として正確に読み込む
                df = pd.read_excel(file_path, sheet_name=selected_sheet, header=2)
                
                # 完全に空白のゴミ行や列をきれいに掃除
                df = df.dropna(how='all')
                
                # データが存在すれば一覧表として綺麗に表示
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"【{selected_sheet}】シートの中には表示できるデータがありません。")
                    
            except Exception as e:
                st.error(f"Excelシートの読み込み中に予期せぬエラーが起きました: {e}")
        else:
            st.warning("`data.xlsx` が見つかりませんでした。GitHubにファイルがあるか確認してください。")

    else:
        pg.run()
