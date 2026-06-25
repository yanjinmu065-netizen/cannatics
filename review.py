import streamlit as st
import pandas as pd

# 📊 ログ（履歴）のカラム定義
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

# -------------------------------------------------------------
# ✍️ パターンA：体感レビュー入力（マスター登録メニュー側）
# -------------------------------------------------------------
if page == "✍️ 体感レビュー入力":
    st.write("過去の吸引記録に対して、体感した効果やメモを登録・編集します。")
    
    # 履歴データベースからログを取得
    df_logs = load_data_from_db("Attraction_Logs", LOG_COLS)
    
    if df_logs.empty:
        st.info("💡 まずは『📝 ワンタップ吸引記録』から吸引データを記録してください。")
    else:
        # 🛠️ 型の安全性を確保するための前処理
        df_logs["体感した効果"] = df_logs["体感した効果"].fillna("").astype(str)
        df_logs["体感メモ"] = df_logs["体感メモ"].fillna("").astype(str)
        
        # プルダウンでリキッド名と日付の組み合わせを選択させる
        log_options = []
        for idx, row in df_logs.iterrows():
            log_options.append(f"{row['日付']} - {row['リキッド名']} ({row['パフ数']}パフ)")
            
        selected_log_str = st.selectbox("レビューを記入・変更する記録を選んでください", log_options[::-1])
        
        # 選択されたログの元のインデックスを特定
        selected_idx = len(df_logs) - 1 - log_options[::-1].index(selected_log_str)
        target_row = df_logs.iloc[selected_idx]
        
        st.markdown(f"**現在の配合詳細:** `{target_row['配合詳細']}`")
        
        # 既存の入力値がある場合はそれを初期値にする（編集対応）
        current_effects = [e.strip() for e in str(target_row.get("体感した効果", "")).split(",") if e.strip() and e.strip() != "nan"]
        current_memo = str(target_row.get("体感メモ", "")) if str(target_row.get("体感メモ", "")) != "nan" else ""
        
        # 💡 レビュー入力フォーム（まとめて保存）
        with st.form(key="review_edit_form"):
            effect = st.multiselect(
                "体感した効果（複数選択可）",
                ["リラックス", "ハッピー・多幸感", "サティバ系（活気・集中）", "インディカ系（深い眠り・ボディハイ）", "マンチ（食欲増進）", "ヘッドハイ（頭が冴える）", "その他"],
                default=current_effects
            )
            memo = st.text_area("体感メモ・具体的な感想", value=current_memo)
            
            # まとめて確定するボタン
            submitted_review = st.form_submit_button("💾 レビュー内容をまとめて確定・保存")
            
        if submitted_review:
            # 選択された行のデータを書き換え・更新
            df_logs.at[selected_idx, "体感した効果"] = ", ".join(effect)
            df_logs.at[selected_idx, "体感メモ"] = memo
            
            # データベース全体を上書き保存
            if save_all_data_to_db("Attraction_Logs", df_logs, LOG_COLS):
                st.success("🎉 体感レビューを保存しました！『📊 レビュー』メニューに閲覧用として反映されます。")
                st.rerun()

# -------------------------------------------------------------
# 📊 パターンB：レビュー閲覧・削除（メイン機能・閲覧ページ側）
# -------------------------------------------------------------
elif page == "📊 レビュー":
    st.write("これまでに記録したリキッドの体感メモを確認・管理できます。")
    
    df_logs = load_data_from_db("Attraction_Logs", LOG_COLS)
    
    # 🛠️ 修正ポイント：読み込んだ直後に、型のエラーを防ぐため文字列に強制変換
    df_logs["体感した効果"] = df_logs["体感した効果"].fillna("").astype(str).str.strip()
    df_logs["体感メモ"] = df_logs["体感メモ"].fillna("").astype(str).str.strip()
    
    # レビュー（効果またはメモ）が書かれているデータのみに自動で絞り込み
    df_reviews = df_logs[
        (df_logs["体感した効果"] != "") & (df_logs["体感した効果"] != "nan") |
        (df_logs["体感メモ"] != "") & (df_logs["体感メモ"] != "nan")
    ].copy()
    
    if df_reviews.empty:
        st.info("まだレビューが登録されていません。『⚙️ マスター登録・管理画面』＞『✍️ 体感レビュー入力』から感想を書き込んでください。")
    else:
        # 登録されているレビューを一覧表示
        for idx, row in df_reviews.iterrows():
            eff_text = row['体感した効果'] if row['体感した効果'] else '未選択'
            memo_text = row['体感メモ'] if row['体感メモ'] else 'メモなし'
            
            with st.container():
                card_html = (
                    f'<div style="border:1px solid #e2e8f0;border-radius:10px 10px 0 0;padding:15px;background-color:#ffffff;box-shadow:0 2px 4px rgba(0,0,0,0.05);margin-bottom:0;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
                    f'<span style="font-weight:bold;color:#333;">📅 {row["日付"]}</span>'
                    f'<span style="background-color:#e2e8f0;padding:2px 8px;border-radius:4px;font-size:12px;color:#555;">💨 {row["パフ数"]} Puff</span>'
                    f'</div>'
                    f'<h4 style="margin:0 0 5px 0;color:#000000;">📦 {row["リキッド名"]}</h4>'
                    f'<p style="margin:0 0 10px 0;font-size:12px;color:#666;">🧪 配合: {row["配合詳細"]}</p>'
                    f'<div style="margin-bottom:8px;">'
                    f'<span style="background-color:#98FB98;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:bold;color:#000;">✨ 体感: {eff_text}</span>'
                    f'</div>'
                    f'<p style="margin:0;font-size:14px;color:#222;line-height:1.5;background:#fafafa;padding:10px;border-radius:6px;">📝 {memo_text}</p>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                
                c_space, c_del = st.columns([5, 1.5])
                with c_del:
                    if st.button("🗑️ レビューを削除", key=f"del_rev_btn_{idx}"):
                        # 該当する吸引記録のレビュー内容だけをリセット
                        df_logs.at[idx, "体感した効果"] = ""
                        df_logs.at[idx, "体感メモ"] = ""
                        
                        # 全体データベースに上書き保存
                        if save_all_data_to_db("Attraction_Logs", df_logs, LOG_COLS):
                            st.rerun()
                
                st.markdown('<div style="margin-bottom:20px; border-bottom:1px dashed #e2e8f0;"></div>', unsafe_allow_html=True)
