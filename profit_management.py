# profit_management.py
import streamlit as st
import pandas as pd
import altair as alt
from database import Database
from pptx import Presentation
from pptx.util import Inches
import os

def generate_profit_pptx(comparison_chart, monthly_chart):
    """PowerPointファイルを生成"""
    ppt = Presentation()

    # スライド1: 利益予実比較
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "利益予実比較"
    slide.shapes.add_picture(comparison_chart, Inches(1), Inches(1.5), width=Inches(6))

    # スライド2: 月毎利益
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "月毎利益"
    slide.shapes.add_picture(monthly_chart, Inches(1), Inches(1.5), width=Inches(6))

    pptx_file = "profit_report.pptx"
    ppt.save(pptx_file)
    return pptx_file

def profit_management_page():
    st.header("利益管理")

    # 売上、原価、販管費データを取得
    sales_total = Database.fetch_data("SELECT SUM(revenue) FROM sales")[0][0] or 0
    cost_total = Database.fetch_data("SELECT SUM(cost) FROM costs")[0][0] or 0
    sg_a_cost_total = Database.fetch_data("SELECT SUM(amount) FROM sg_a_costs")[0][0] or 0

    # 営業利益を計算
    total_profit = sales_total - cost_total - sg_a_cost_total

    # 利益情報を表示
    st.metric("総売上", f"{sales_total:,} 円")
    st.metric("総原価", f"{cost_total:,} 円")
    st.metric("総販管費", f"{sg_a_cost_total:,} 円")
    st.metric("営業利益", f"{total_profit:,} 円")

    # グラフ作成
    st.subheader("月毎の営業利益")
    monthly_profit_chart = alt.Chart(pd.DataFrame({
        "月": ["2023-01", "2023-02"],  # 例
        "利益": [total_profit, total_profit * 0.8]  # 仮データ
    })).mark_line().encode(
        x="月",
        y="利益"
    )
    st.altair_chart(monthly_profit_chart, use_container_width=True)

    # PowerPointエクスポート
    st.subheader("PowerPointエクスポート")
    if st.button("PowerPointファイルをダウンロード"):
        pptx_file = generate_profit_pptx(monthly_profit_chart, monthly_profit_chart)
        with open(pptx_file, "rb") as file:
            st.download_button(
                label="PowerPointをダウンロード",
                data=file,
                file_name=pptx_file,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
