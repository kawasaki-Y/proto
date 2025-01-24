import sqlite3


class Database:
    DB_FILE = "dashboard_data.db"

    @staticmethod
    def init_db():
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()

        # 売上テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                tag TEXT,
                revenue REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)

        # 原価テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                cost REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)

        # 販管費テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sg_a_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)

        # 利益テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revenue REAL NOT NULL,
                cost REAL NOT NULL,
                sg_a_cost REAL NOT NULL,
                profit REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)

        # 資金管理テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cashflow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                inflow REAL NOT NULL,
                outflow REAL NOT NULL
            )
        """)

        # 目標売上テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS target_revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL
            )
        """)

        # タグテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL
            )
        """)

        # ユーザーテーブル (ログイン用)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def execute_query(query, params=None):
        """SQLクエリを実行"""
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLエラー: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def fetch_data(query, params=None):
        """データを取得するクエリを実行"""
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            data = cursor.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"SQLエラー: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_connection():
        """データベース接続を返す"""
        return sqlite3.connect(Database.DB_FILE)
