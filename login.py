import streamlit as st
from database import Database

def login_page():
    st.title("ログイン")

    # ユーザーの入力
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    login_button = st.button("ログイン")

    # ログイン処理
    if login_button:
        user_data = Database.fetch_data(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
        )
        if user_data:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("ログイン成功！")
            st.experimental_rerun()  # 状態を更新して画面遷移
        else:
            st.error("ユーザー名またはパスワードが正しくありません。")
