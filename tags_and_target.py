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
            st.session_state["page_updated"] = True  # ページの更新フラグをセット

    # 登録済みタグ表示、削除、および編集機能
    tags_data = Database.fetch_data("SELECT id, tag_name FROM tags")
    if tags_data:
        st.subheader("登録済みタグ")
        for tag_id, tag_name in tags_data:
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                st.text(tag_name)
            with col2:
                if st.button("削除", key=f"delete_{tag_id}"):
                    Database.execute_query("DELETE FROM tags WHERE id = ?", (tag_id,))
                    st.success(f"タグ '{tag_name}' を削除しました！")
                    st.session_state["page_updated"] = True  # ページの更新フラグをセット
            with col3:
                if st.button("編集", key=f"edit_{tag_id}"):
                    st.session_state[f"edit_tag_{tag_id}"] = True  # 編集モードを有効化

            # 編集モード
            if st.session_state.get(f"edit_tag_{tag_id}", False):
                new_name = st.text_input(f"タグ '{tag_name}' の新しい名前を入力", key=f"edit_name_{tag_id}")
                if st.button("変更を保存", key=f"save_{tag_id}"):
                    if new_name:
                        Database.execute_query("UPDATE tags SET tag_name = ? WHERE id = ?", (new_name, tag_id))
                        st.success(f"タグ '{tag_name}' を '{new_name}' に変更しました！")
                        st.session_state[f"edit_tag_{tag_id}"] = False  # 編集モードを無効化
                        st.session_state["page_updated"] = True  # ページの更新フラグをセット
                    else:
                        st.error("タグ名は空にできません。")
    else:
        st.info("まだタグが登録されていません。")

    # 目標売上登録フォーム
    st.subheader("目標売上登録")
    with st.form("target_form"):
        target_revenue = st.number_input("年間目標売上高（千円単位）", min_value=0, step=100)
        submitted_target = st.form_submit_button("登録")
        if submitted_target:
            Database.execute_query("DELETE FROM target_revenue")
            Database.execute_query("INSERT INTO target_revenue (amount) VALUES (?)", (target_revenue,))
            st.success(f"年間目標売上高を {target_revenue:,} 千円に設定しました！")
            st.session_state["page_updated"] = True  # ページの更新フラグをセット

    # 登録済み目標売上表示
    target_data = Database.fetch_data("SELECT amount FROM target_revenue")
    if target_data:
        st.subheader("登録済み目標売上")
        st.write(f"{target_data[0][0]:,} 千円")
    else:
        st.info("まだ目標売上が登録されていません。")

# ページの更新を反映
if "page_updated" in st.session_state and st.session_state["page_updated"]:
    st.session_state["page_updated"] = False  # フラグをリセット
    st.experimental_set_query_params(dummy=1)  # クエリパラメータでリロードをトリガー
