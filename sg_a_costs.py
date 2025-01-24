import streamlit as st
import pandas as pd
import altair as alt
from database import Database

def sg_a_costs_page():
    st.header("販管費管理")

    # 販管費登録フォーム
    with st.form("sg_a_costs_form"):
        category = st.text_input("カテゴリ（例: 広告費、交通費）")
        amount = st.number_input("金額（円）", min_value=0, step=1000)
        date = st.date_input("日付")
        submitted = st.form_submit_button("登録")
        if submitted:
            Database.execute_query(
                "INSERT INTO sg_a_costs (category, amount, date) VALUES (?, ?, ?)",
                (category, amount, str(date))
            )
            st.success("販管費を登録しました！")

    # データ表示
    data = Database.fetch_data("SELECT category, amount, date FROM sg_a_costs")
    df = pd.DataFrame(data, columns=["カテゴリ", "金額", "日付"])
    if not df.empty:
        st.dataframe(df)

        # グラフ表示
        chart = alt.Chart(df).mark_bar(color="#ff7f7f").encode(
            x="カテゴリ:N",
            y="金額:Q",
            tooltip=["カテゴリ", "金額", "日付"]
        )
        st.altair_chart(chart, use_container_width=True)

        # 集計
        total_amount = df["金額"].sum()
        st.metric("販管費合計", f"{total_amount}円")

    # SQLダウンロード
    if st.button("SQLファイルをダウンロード"):
        with open("sg_a_costs_data.sql", "w") as f:
            for line in Database.fetch_data("SELECT * FROM sg_a_costs"):
                f.write(str(line) + "\n")
        st.success("SQLファイルをダウンロードしました！")
