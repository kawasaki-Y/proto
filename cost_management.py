import streamlit as st
import pandas as pd
import altair as alt
from database import Database

def cost_management_page():
    st.header("原価管理")

    # 原価登録フォーム
    with st.form("cost_form"):
        project_names = ["仕入", "労務費", "外注費", "サーバー代", "直接経費", "減価償却費"]
        project = st.selectbox("費目名", options=project_names)
        cost = st.number_input("原価（円）", min_value=0, step=1000)
        date = st.date_input("日付")
        submitted = st.form_submit_button("登録")
        if submitted:
            Database.execute_query(
                "INSERT INTO costs (project, cost, date) VALUES (?, ?, ?)",
                (project, cost, str(date))
            )
            st.success("原価を登録しました！")

    # データ表示
    data = Database.fetch_data("SELECT project, cost, date FROM costs")
    df = pd.DataFrame(data, columns=["案件名", "原価", "日付"])
    if not df.empty:
        st.dataframe(df)

        selected_row = st.selectbox("編集・削除するデータを選択", options=df.to_dict(orient="records"), format_func=lambda x: f"{x['案件名']} - {x['原価']}円 - {x['日付']}")
        if st.button("データを編集"):
            new_project = st.text_input("新しい案件名", value=selected_row["案件名"])
            new_cost = st.number_input("新しい原価（円）", value=selected_row["原価"], min_value=0, step=1000)
            new_date = st.date_input("新しい日付", value=pd.to_datetime(selected_row["日付"]))
            if st.button("更新"):
                Database.execute_query(
                    "UPDATE costs SET project = ?, cost = ?, date = ? WHERE project = ? AND cost = ? AND date = ?",
                    (new_project, new_cost, str(new_date), selected_row["案件名"], selected_row["原価"], selected_row["日付"]),
                )
                st.success("データを更新しました！")

        if st.button("データを削除"):
            Database.execute_query(
                "DELETE FROM costs WHERE project = ? AND cost = ? AND date = ?",
                (selected_row["案件名"], selected_row["原価"], selected_row["日付"]),
            )
            st.success("データを削除しました！")

        # グラフ表示
        chart = alt.Chart(df).mark_bar(color="#ff7f7f").encode(
            x="案件名:N",
            y="原価:Q",
            tooltip=["案件名", "原価", "日付"]
        )
        st.altair_chart(chart, use_container_width=True)

        line_chart = alt.Chart(df).mark_line().encode(
            x="日付:T",
            y="原価:Q",
            color="案件名:N",
            tooltip=["案件名", "原価", "日付"]
        )
        st.altair_chart(line_chart, use_container_width=True)

        pie_chart = alt.Chart(df).mark_arc().encode(
            theta="sum(原価):Q",
            color="案件名:N",
            tooltip=["案件名", "sum(原価):Q"]
        )
        st.altair_chart(pie_chart, use_container_width=True)

        # 集計
        total_cost = df["原価"].sum()
        st.metric("総原価", f"{total_cost}円")

    # SQLダウンロード
    if st.button("SQLファイルをダウンロード"):
        with open("cost_data.sql", "w") as f:
            for line in Database.fetch_data("SELECT * FROM costs"):
                f.write(str(line) + "\n")
        st.success("SQLファイルをダウンロードしました！")
