import streamlit as st
from sales_management import sales_management_page
from cost_management import cost_management_page
from sg_a_costs import sg_a_costs_page
from profit_management import profit_management_page
from cashflow_management import cashflow_management_page
from tags_and_target import tags_and_target_page
from database import Database

# ページ設定
st.set_page_config(page_title="経営ダッシュボード", layout="wide")

# データベース初期化
Database.init_db()

# ログイン認証状態管理
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "ログイン"  # 初期ページ設定

# ログインページ
def login_page():
    st.title("ログイン")
    username = st.text_input("ユーザー名", key="login_username")
    password = st.text_input("パスワード", type="password", key="login_password")
    if st.button("ログイン", key="login_button"):
        user = Database.fetch_data(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
        )
        if user:
            st.success("ログイン成功！")
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["current_page"] = "初期設定登録"  # ログイン後の遷移先
        else:
            st.error("ユーザー名またはパスワードが間違っています。")
    if st.button("ユーザー登録はこちら", key="to_register"):
        st.session_state["current_page"] = "ユーザー登録"

# ユーザー登録ページ
def registration_page():
    st.title("ユーザー登録")
    username = st.text_input("ユーザー名", key="register_username")
    password = st.text_input("パスワード", type="password", key="register_password")
    if st.button("登録", key="register_button"):
        try:
            Database.execute_query(
                "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
            )
            st.success("ユーザー登録が完了しました！ログインしてください。")
            st.session_state["current_page"] = "ログイン"  # 登録後にログイン画面に戻る
        except Exception as e:
            st.error(f"ユーザー登録に失敗しました: {e}")
    if st.button("ログイン画面に戻る", key="to_login"):
        st.session_state["current_page"] = "ログイン"

# メインページ
def main_page():
    # サイドバー
    st.sidebar.header(f"メニュー - ようこそ、{st.session_state['username']} さん！")
    menu = st.sidebar.radio("ページを選択してください", [
        "初期設定登録",
        "売上管理",
        "原価管理",
        "販管費管理",
        "利益管理",
        "資金管理",
        "ログアウト"
    ])

    # ページ分岐
    if menu == "初期設定登録":
        st.session_state["current_page"] = "初期設定登録"
        tags_and_target_page()
    elif menu == "売上管理":
        st.session_state["current_page"] = "売上管理"
        sales_management_page()
    elif menu == "原価管理":
        st.session_state["current_page"] = "原価管理"
        cost_management_page()
    elif menu == "販管費管理":
        st.session_state["current_page"] = "販管費管理"
        sg_a_costs_page()
    elif menu == "利益管理":
        st.session_state["current_page"] = "利益管理"
        profit_management_page()
    elif menu == "資金管理":
        st.session_state["current_page"] = "資金管理"
        cashflow_management_page()
    elif menu == "ログアウト":
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["current_page"] = "ログイン"  # ログアウト後はログイン画面に戻る

# ページ管理
if not st.session_state["authenticated"]:
    if st.session_state["current_page"] == "ログイン":
        login_page()
    elif st.session_state["current_page"] == "ユーザー登録":
        registration_page()
else:
    main_page()
