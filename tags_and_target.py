# tags_and_target.py
import streamlit as st
from database import Database

def tags_and_target_page():
    st.header("タグと目標売上の登録")

    # タグ登録フォーム
    st.subheader("タグ登録")
    with st.form("tag_form"):
        new_tag = st.text_input("新しいタグを登録")
        submitted_tag = st.form_submit_button("登録")
        if submitted_tag and new_tag:
            Database.execute_query("INSERT INTO tags (tag_name) VALUES (?)", (new_tag,))
            st.success(f"タグ '{new_tag}' を登録しました！")

    # 登録済みタグの表示と管理
    tags_data = Database.fetch_data("SELECT id, tag_name FROM tags")
    if tags_data:
        st.subheader("登録済みタグ")
        for tag_id, tag_name in tags_data:
            col1, col2, col3 = st.columns([6, 1, 1])
            col1.text(tag_name)

            # タグ削除ボタン
            if col2.button("削除", key=f"delete_{tag_id}"):
                Database.execute_query("DELETE FROM tags WHERE id = ?", (tag_id,))
                st.success(f"タグ '{tag_name}' を削除しました！")
                st.experimental_rerun()

            # タグ編集機能
            if col3.button("編集", key=f"edit_{tag_id}"):
                new_name = st.text_input(f"タグ '{tag_name}' の新しい名前を入力", value=tag_name, key=f"edit_name_{tag_id}")
                if st.button("変更を保存", key=f"save_{tag_id}"):
                    Database.execute_query("UPDATE tags SET tag_name = ? WHERE id = ?", (new_name, tag_id))
                    st.success(f"タグ '{tag_name}' を '{new_name}' に変更しました！")
                    st.experimental_rerun()
    else:
        st.info("まだタグが登録されていません。")

    # 目標売上登録フォーム
    st.subheader("目標売上登録")
    with st.form("target_form"):
        target_revenue = st.number_input("年間目標売上高（円）", min_value=0, step=1000)
        submitted_target = st.form_submit_button("登録")
        if submitted_target:
            Database.execute_query("DELETE FROM target_revenue")
            Database.execute_query("INSERT INTO target_revenue (amount) VALUES (?)", (target_revenue,))
            st.success(f"年間目標売上高を {target_revenue:,} 円に設定しました！")

    # 登録済み目標売上の表示
    target_data = Database.fetch_data("SELECT amount FROM target_revenue")
    if target_data:
        st.subheader("登録済み目標売上")
        st.write(f"{target_data[0][0]:,} 円")
    else:
        st.info("まだ目標売上が登録されていません。")
