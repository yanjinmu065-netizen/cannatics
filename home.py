import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import calendar
import os

# まん丸のオシャレなバッジUIボタン（画像スタイル再現CSS）
st.markdown("""
    <style>
    .badge-effect {
        background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1;
        padding: 6px 14px; border-radius: 20px; display: inline-block; margin: 4px; font-weight: bold; font-size: 14px;
    }
    .badge-terpene {
        background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a;
        padding: 6px 14px; border-radius: 20px; display: inline-block; margin: 4px; font-weight: bold; font-size: 14px;
    }
    /* サイドバーのリンク文字色を白にする（リクエスト追加） */
    [data-testid="stSidebarNav"] ul li a span {
        color: white !important;
    }
    /* 枠を追加・枠を削除ボタンの色を #98FB98 にする（リクエスト追加） */
    div.stButton > button {
        background-color: #98FB98 !important;
        color: #000000 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Cannatics 履歴ダッシュボード")

now = datetime.date.today()
year, month = now.year, now.month
saved_dates = st.session_state.get("history_logs", {}).keys()

cal = calendar.monthcalendar(year, month)
days_df = []
for week in cal:
    row = []
    for day in week:
        if day == 0: row.append("")
        else:
            date_str = f"{year}-{month:02d}-{day:02d}"
            row.append(f"{day}日🌿" if date_str in saved_dates else f"{day}日")
    days_df.append(row)

st.table(pd.DataFrame(days_df, columns=["月", "火", "水", "木", "金", "土", "日"]))

st.markdown("---")
if saved_dates:
    selected_date = st.selectbox("確認したい日付ログを選択", sorted(list(saved_dates), reverse=True))
    data = st.session_state.history_logs[selected_date]
    
    st.markdown("### 📊 成分比率内訳")
    chart_df = pd.DataFrame(list(data["liquid_data"].items()), columns=["成分", "比率(%)"])
    st.plotly_chart(px.pie(chart_df, values='比率(%)', names='成分', hole=0.5), use_container_width=True)

    st.markdown("### 📈 精神活性チャート")
    categories = ['パワー', '時間', 'ヘッドハイ', 'スリーブ', 'サイコアティブ', 'ユーフィリア', 'ボディハイ', 'アブノーマル']
    v = [min(5, int(data["g1_total"]/15 + data["puffs"]/2)), min(5, int(data["g1_total"]/12 + 1)), 3, 3, 4, 3, 2, 1]
    v += v[:1]; categories += categories[:1]
    fig_radar = go.Figure(go.Scatterpolar(r=v, theta=categories, fill='toself', fillcolor='rgba(234, 179, 8, 0.3)', line=dict(color='#eab308', width=2)))
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("### 💬 選択された体感・効果")
    if data["effects"]:
        html_str = "".join([f"<span class='badge-effect'>{eff}</span>" for eff in data["effects"]])
        st.markdown(html_str, unsafe_allow_html=True)
    else:
        st.caption("選択された体感効果はありません。")

    st.markdown("#### 🧪 今回配合したテルペンの香りと特徴")
    try:
        df_terpene = pd.read_excel("data.xlsx", sheet_name="テルペン", header=2)
        t_html = ""
        found_any = False
        
        for comp_name
