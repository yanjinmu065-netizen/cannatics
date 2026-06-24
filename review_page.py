import streamlit as st
import pandas as pd
import datetime

# 📊 ログ（履歴）のカラム定義
LOG_COLS = ["日付", "リキッド名", "パフ数", "配合詳細", "体感した効果", "体感メモ"]

# home.pyで選択されているページ（メニュー項目）に応じて表示を切り替えます
if page == "✍️ 体感レビュー入力":
    st.subheader("✍️ 吸引したリキッドの体感レビューを記録")
    
    # 履歴データベースから、まだレビューが未入力のログや直近のログを取得
    df_logs = load_data_from_db("Attraction_Logs", LOG_COLS)
    
    if df_logs.empty:
        st.info("💡 まずは『📝 ワンタップ吸引記録』から吸引データを記録してください。")
    else:
        # 日付とリキッド名の選択肢を作成（直近の記録をレビューしやすくするため逆順に）
        log_options = []
        for idx, row in df_logs.iterrows():
            log_options.append(f"{row['日付']} - {row['リキッド名']} ({row['パフ数']}パフ)")
            
        selected_log_str = st.selectbox("レビューする吸引記録を選んでください", log_options[::-1])
        
        # 選択されたログの元のインデックスを特定
        selected_idx = len(df_logs) - 1 - log_options[::-1].index(selected_log_str)
        target_row = df_logs.iloc[selected_idx]
        
        st.markdown(f"**現在の配合詳細:** `{target_row['配合詳細']}`")
        
        # レビュー入力フォーム
        with st.form(key="review_input_form"):
            effect = st.multiselect(
                "体感した効果（複数選択可）",
                ["リラックス", "ハッピー・多幸感", "サティバ系（活気・集中）", "インディカ系（深い眠り・ボディハイ）", "マンチ（食欲増進）", "ヘッドハイ（頭が冴える）", "その他"]
            )
            memo = st.text_area("体感メモ・具体的な感想（味、香り、ピーク時間など）")
            
            submitted_review = st.form_submit_button("💾 レビューを確定して保存")
            
        if submitted_review:
            # 選択された行のデータを更新
            df_logs.at[selected_idx, "体感した効果"] = ", ".join(effect)
            df_logs.at[selected_idx, "体感メモ"] = memo
            
            # データベース全体を上書き保存
            if save_all_data_to_db("Attraction_Logs", df_logs, LOG_COLS):
                st.success("🎉 体感レビューを正常に記録しました！")
                st.balloons()
                st.rerun()

elif page == "📊 レビュー":
    st.subheader("📊 過去の体感レビュー・統計一覧")
    
    df_logs = load_data_from_db("Attraction_Logs", LOG_COLS)
    
    # レビュー（体感した効果またはメモ）が書かれているデータのみに絞り込む
    df_reviews = df_logs[(df_logs["体感した効果"] != "") | (df_logs["体感メモ"] != "")].copy()
    
    if df_reviews.empty:
        st.info("まだレビューが登録されていません。『✍️ 体感レビュー入力』から感想を書き込んでください。")
    else:
        # 登録されているレビューをカード型で綺麗に表示
        for idx, row in df_reviews.iterrows():
            st.markdown(
                f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #333;">📅 {row['日付']}</span>
                        <span style="background-color: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #555;">💨 {row['パフ数']} Puff</span>
                    </div>
                    <h4 style="margin: 0 0 5px 0; color: #000000;">📦 {row['リキッド名']}</h4>
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #666;">🧪 配合: {row['配合詳細']}</p>
                    <div style="margin-bottom: 8px;">
                        <span style="background-color: #98FB98; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: #000;">✨ 体感: {row['体感した効果'] if row['体感した効果'] else '未選択'}</span>
                    </div>
                    <p style="margin: 0; font-size: 14px; color: #222; line-height: 1.5; background: #fafafa; padding: 10px; border-radius: 6px;">📝 {row['体感メモ'] if row['体感メモ'] else 'メモなし'}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
