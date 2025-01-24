import streamlit as st
import pandas as pd
import altair as alt
from database import Database
from datetime import date
from pptx import Presentation
from pptx.util import Inches
import os

def save_chart_as_image(chart, filename):
    """Altairのグラフを画像として保存"""
    chart.save(filename, scale_factor=2)

def generate_pptx_with_charts(comparison_chart, monthly_chart):
    """PowerPointファイルを生成"""
    ppt = Presentation()

    # スライド1: 利益予実比較
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    title = slide.shapes.title
    title.text = "利益予実比較"
    save_chart_as_image(comparison_chart, "profit_comparison_chart.png")
    slide.shapes.add_picture("profit_comparison_chart.png", Inches(1), Inches(1.5), width=Inches(6))
    os.remove("profit_comparison_chart.png")

    # スライド2: 月毎利益
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    title = slide.shapes.title
    title.text = "月毎利益"
    save_chart_as_image(monthly_chart, "monthly_profit_chart.png")
    slide.shapes.add_picture("monthly_profit_chart.png", Inches(1), Inches(1.5), width=Inches(6))
    os.remove("monthly_profit_chart.png")

    # PowerPointファイルを保存
    ppt.save("profit_charts.pptx")
    return "profit_charts.pptx"

def profit_management_page():
    st.header("利益管理")

    # 利益データの取得
    profits_data = Database.fetch_data("SELECT revenue, cost, sg_a_cost, profit, date FROM profits")
    df = pd.DataFrame(profits_data, columns=["売上高", "原価", "販管費", "利益", "日付"])

    if not df.empty:
        st.subheader("利益データ（表形式）")
        st.dataframe(df, use_container_width=True)

        # 利益の合計を計算
        total_profit = df["利益"].sum()
        st.write(f"総利益: {total_profit:,} 千円")

        # 利益予実比較グラフの作成
        st.subheader("利益予実比較（棒グラフ）")
        planned_profit = Database.fetch_data("SELECT planned_profit FROM target_profit")[0][0]
        comparison_data = pd.DataFrame({
            "項目": ["目標利益", "実績利益"],
            "金額（千円）": [planned_profit, total_profit]
        })
        comparison_chart = alt.Chart(comparison_data).mark_bar().encode(
            x="項目:N",
            y="金額（千円）:Q"
        )
        st.altair_chart(comparison_chart, use_container_width=True)

        # 月毎利益グラフの作成
        st.subheader("月毎利益（折れ線グラフ）")
        df["月"] = pd.to_datetime(df["日付"]).dt.to_period("M")
        monthly_profit = df.groupby("月")["利益"].sum().reset_index()
        monthly_chart = alt.Chart(monthly_profit).mark_line().encode(
            x="月:T",
            y="利益:Q"
        )
        st.altair_chart(monthly_chart, use_container_width=True)

        # グラフをPowerPointにダウンロード
        st.subheader("グラフのエクスポート")
        if st.button("PowerPointファイルをダウンロード"):
            pptx_file = generate_pptx_with_charts(comparison_chart, monthly_chart)
            with open(pptx_file, "rb") as file:
                st.download_button(
                    label="PowerPointをダウンロード",
                    data=file,
                    file_name=pptx_file,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            os.remove(pptx_file)

        # SQLファイルダウンロード
        st.subheader("データエクスポート")
        if st.button("SQLファイルをダウンロード"):
            sql_file_path = "profits_data.sql"
            with open(sql_file_path, "w") as f:
                conn = Database.get_connection()
                for line in conn.iterdump():
                    f.write(f"{line}\n")
                conn.close()
            with open(sql_file_path, "rb") as file:
                st.download_button(
                    label="SQLファイルをダウンロード",
                    data=file,
                    file_name=sql_file_path,
                    mime="application/sql"
                )
            os.remove(sql_file_path)
    else:
        st.warning("利益データが登録されていません。")
