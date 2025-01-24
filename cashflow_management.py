# cashflow_management.py
import streamlit as st
import pandas as pd
import altair as alt
from database import Database

def cashflow_management_page():
    st.header("資金管理")

    # 資金データ登録フォーム
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

    # 資金データ表示
    data = Database.fetch_data("SELECT month, inflow, outflow FROM cashflow")
    df = pd.DataFrame(data, columns=["月", "収入", "支出"])
    if not df.empty:
        st.dataframe(df)
        total_inflow = df["収入"].sum()
        total_outflow = df["支出"].sum()
        st.metric("収入合計", f"{total_inflow:,} 円")
        st.metric("支出合計", f"{total_outflow:,} 円")
        st.metric("収支", f"{total_inflow - total_outflow:,} 円")
