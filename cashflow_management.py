import streamlit as st
import pandas as pd
import altair as alt
from database import Database

def cashflow_management_page():
    st.header("資金管理")

    # 資金登録フォーム
    with st.form("cashflow_form"):
        month = st.text_input("月（例: 2023-01）")
        inflow = st.number_input("収入（円）", min_value=0, step=1000)
        outflow = st.number_input("支出（円）", min_value=0, step=1000)
        submitted = st.form_submit_button("登録")
        if submitted:
            Database.execute_query(
                "INSERT INTO cashflow (month, inflow, outflow) VALUES (?, ?, ?)",
                (month, inflow, outflow)
            )
            st.success("資金データを登録しました！")

    # データ表示
    data = Database.fetch_data("SELECT month, inflow, outflow FROM cashflow")
    df = pd.DataFrame(data, columns=["月", "収入", "支出"])
    if not df.empty:
        st.dataframe(df)

        # グラフ表示
        chart = alt.Chart(df).mark_bar().encode(
            x="月:N",
            y="収入:Q",
            tooltip=["月", "収入", "支出"]
        )
        st.altair_chart(chart, use_container_width=True)

        # 集計
        total_inflow = df["収入"].sum()
        total_outflow = df["支出"].sum()
        st.metric("収入合計", f"{total_inflow}円")
        st.metric("支出合計", f"{total_outflow}円")
        st.metric("収支バランス", f"{total_inflow - total_outflow}円")

    # SQLダウンロード
    if st.button("SQLファイルをダウンロード"):
        with open("cashflow_data.sql", "w") as f:
            for line in Database.fetch_data("SELECT * FROM cashflow"):
                f.write(str(line) + "\n")
        st.success("SQLファイルをダウンロードしました！")
