import streamlit as st
import pandas as pd
import altair as alt
from database import Database
import math
from pptx import Presentation
from pptx.util import Inches


def generate_sales_pptx(bar_chart_img, line_chart_img, pie_chart_img, total_sales, sales_difference):
    """PowerPointファイルを生成"""
    ppt = Presentation()

    # スライド1: 棒グラフ
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "売上データ（棒グラフ）"
    slide.shapes.add_picture(bar_chart_img, Inches(1), Inches(1.5), width=Inches(6))

    # スライド2: 折れ線グラフ
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "売上データ（折れ線グラフ）"
    slide.shapes.add_picture(line_chart_img, Inches(1), Inches(1.5), width=Inches(6))

    # スライド3: 円グラフ
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "売上データ（円グラフ）"
    slide.shapes.add_picture(pie_chart_img, Inches(1), Inches(1.5), width=Inches(6))

    # スライド4: 総売上と目標差分
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])
    slide.shapes.title.text = "総売上と目標差分"
    textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
    textbox.text = f"総売上: {total_sales:,} 千円\n目標との差分: {sales_difference:+,} 千円"

    pptx_file = "sales_report.pptx"
    ppt.save(pptx_file)
    return pptx_file


def sales_management_page():
    st.header("売上管理")

    # 登録済みタグを取得
    tags_data = Database.fetch_data("SELECT tag_name FROM tags")
    tags = [tag[0] for tag in tags_data]

    # 売上データ登録フォーム
    with st.form("sales_form"):
        project = st.text_input("案件名")
        tag = st.selectbox("タグ", options=tags if tags else ["タグなし"])
        revenue = st.number_input("売上金額（千円単位）", min_value=0, step=1)  # 千円単位で入力
        date = st.date_input("日付")
        submitted = st.form_submit_button("登録")
        if submitted:
            Database.execute_query(
                "INSERT INTO sales (project, tag, revenue, date) VALUES (?, ?, ?, ?)",
                (project, tag, revenue, str(date))
            )
            st.success("売上データを登録しました！")
            st.experimental_set_query_params(updated="true")

    # 売上データ取得
    data = Database.fetch_data("SELECT id, project, tag, revenue, date FROM sales")
    df = pd.DataFrame(data, columns=["ID", "案件名", "タグ", "売上金額", "日付"])
    df["売上金額"] = df["売上金額"].apply(lambda x: math.floor(x))  # 小数点以下を切り捨て
    df.insert(0, "番号", range(1, len(df) + 1))  # 行番号を1から開始

    if not df.empty:
        st.subheader("売上データ一覧")
        st.dataframe(df[["番号", "案件名", "タグ", "売上金額", "日付"]], use_container_width=True)

        # 目標売上の取得
        target_revenue_data = Database.fetch_data("SELECT amount FROM target_revenue")
        target_revenue = math.floor(target_revenue_data[0][0]) if target_revenue_data else 0

        # 総売上の計算
        total_sales = df["売上金額"].sum()
        sales_difference = total_sales - target_revenue

        # 目標売上と差分を表示
        st.metric("目標売上", f"{target_revenue:,} 千円")
        st.metric("総売上", f"{total_sales:,} 千円")
        st.metric("目標との差分", f"{sales_difference:+,} 千円")

        # データ編集と削除
        st.subheader("データ編集・削除")
        selected_row = st.selectbox(
            "編集・削除するデータを選択",
            options=df.to_dict(orient="records"),
            format_func=lambda x: f"{x['案件名']} - {x['売上金額']}千円 - {x['日付']}"
        )
        edit_project = st.text_input("新しい案件名", value=selected_row["案件名"], key="edit_project")
        edit_revenue = st.number_input("新しい売上金額（千円単位）", value=selected_row["売上金額"], min_value=0, step=1, key="edit_revenue")
        edit_date = st.date_input("新しい日付", value=pd.to_datetime(selected_row["日付"]), key="edit_date")

        if st.button("変更を保存"):
            Database.execute_query(
                "UPDATE sales SET project = ?, revenue = ?, date = ? WHERE id = ?",
                (edit_project, edit_revenue, str(edit_date), selected_row["ID"])
            )
            st.success("データを更新しました！")
            st.experimental_set_query_params(updated="true")

        if st.button("データを削除"):
            Database.execute_query("DELETE FROM sales WHERE id = ?", (selected_row["ID"],))
            st.success("データを削除しました！")
            st.experimental_set_query_params(updated="true")

        # グラフ作成
        st.subheader("売上データのグラフ")

        # 月単位のデータに変換
        df["月"] = pd.to_datetime(df["日付"]).dt.strftime("%Y年%m月")

        # 棒グラフ
        bar_chart = alt.Chart(df).mark_bar().encode(
            x="案件名:N",
            y="売上金額:Q",
            color=alt.Color("タグ:N", scale=alt.Scale(scheme="blues")),
            tooltip=["案件名", "タグ", "売上金額", "日付"]
        ).properties(width=700, height=400)
        st.altair_chart(bar_chart, use_container_width=True)

        # 折れ線グラフ
        line_chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("月:O", title="月"),
            y=alt.Y("売上金額:Q", title="売上金額（千円）"),
            color=alt.Color("タグ:N", title="タグ"),
            tooltip=["案件名", "売上金額", "月"]
        ).properties(width=700, height=400)
        st.altair_chart(line_chart, use_container_width=True)

        # 円グラフ
        pie_chart = alt.Chart(df).mark_arc().encode(
            theta="売上金額:Q",
            color=alt.Color("タグ:N", scale=alt.Scale(scheme="blues")),
            tooltip=["タグ", "売上金額"]
        ).properties(width=700, height=400)
        st.altair_chart(pie_chart, use_container_width=True)

        # PowerPointエクスポート
        st.subheader("PowerPointエクスポート")
        if st.button("PowerPointファイルをダウンロード"):
            pptx_file = generate_sales_pptx("bar_chart.png", "line_chart.png", "pie_chart.png", total_sales, sales_difference)
            with open(pptx_file, "rb") as file:
                st.download_button(
                    label="PowerPointをダウンロード",
                    data=file,
                    file_name=pptx_file,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
