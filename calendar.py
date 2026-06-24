import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import calendar

st.title("📅 シフトボード風・履歴カレンダー")

# 現在の年月を取得
now = datetime.date.today()
year = now.year
month = now.month

st.subheader(f"📅 {year}年 {month}月")

# カレンダーのグリッドデータを作成
cal = calendar.monthcalendar(year, month)
days_df = []

# 登録されているログの日付一覧を取得
saved_dates = st.session_state.get("history_logs", {}).keys()

# シフトボード風のマス目データを構築
for week in cal:
    row = []
    for day in week:
        if day == 0:
            row.append("")
        else:
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in saved_dates:
                row.append(f"{day}日🌿\n(ログあり)")
            else:
                row.append(f"{day}日")
    days_df.append(row)

# 7列（月〜日）のデータフレームにしてオシャレな表として全画面表示
cols = ["月", "火", "水", "木", "金", "土", "日"]
cal_table = pd.DataFrame(days_df, columns=cols)
st.table(cal_table)

st.markdown("---")

# 閲覧したい日付の選択
st.subheader("🔍 ログの詳細確認")
if saved_dates:
    selected_date = st.selectbox("確認したい日付ログを選択してください", sorted(list(saved_dates), reverse=True))
    
    data = st.session_state.history_logs[selected_date]
    
    # 1. 成分比率
    st.markdown("### 📊 成分比率内訳")
    chart_df = pd.DataFrame(list(data["liquid_data"].items()), columns=["成分", "比率(%)"])
    fig_pie = px.pie(chart_df, values='比率(%)', names='成分', hole=0.5,
                     color_discrete_sequence=['#3b82f6', '#ec4899', '#f97316', '#eab308', '#a855f7'])
    st.plotly_chart(fig_pie, use_container_width=True)

    # 2. レーダーチャート
    st.markdown("### 📈 精神活性チャート")
    categories = ['パワー', '時間', 'ヘッドハイ', 'スリーブ', 'サイコアティブ', 'ユーフィリア', 'ボディハイ', 'アブノーマル']
    v = [min(5, int(data["g1_total"]/15 + data["puffs"]/2)), min(5, int(data["g1_total"]/12 + 1)), 3, 3, 4, 3, 2, 1]
    v += v[:1]
    categories += categories[:1]
    
    fig_radar = go.Figure(go.Scatterpolar(r=v, theta=categories, fill='toself', fillcolor='rgba(234, 179, 8, 0.3)', line=dict(color='#eab308', width=2)))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
    st.plotly_chart(fig_radar, use_container_width=True)

    # 3. 体感レビュー
    st.markdown("### 💬 レビュー体感")
    c_pos, c_neg = st.columns(2)
    with c_pos:
        st.write("**🟢 ポジティブ要素**")
        fig_pos = px.pie(pd.DataFrame({"要素": ["睡眠サポート", "陶酔", "リラックス"], "値": [30, 40, 30]}), values='値', names='要素', color_discrete_sequence=px.colors.sequential.YlOrRd_r)
        st.plotly_chart(fig_pos, use_container_width=True)
    with c_neg:
        st.write("**🔴 ネガティブ要素**")
        fig_neg = px.pie(pd.DataFrame({"要素": ["頭痛", "パラノイア", "翌日残存"], "値": [20, 30, 50]}), values='値', names='要素', color_discrete_sequence=px.colors.sequential.Purples_r)
        st.plotly_chart(fig_neg, use_container_width=True)
        
    st.info(f"**📝 吸った回数:** {data['puffs']} パフ\n\n**📝 体感メモ:** {data['memo']}")

else:
    st.info("カレンダーに保存されたログはまだありません。『配合電卓』で数値を入力して保存ボタンを押してください。")