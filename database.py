# database.py
import sqlite3
import logging
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(message)s")

class Database:
    DB_FILE = "dashboard_data.db"
    SCHEMA_VERSION = 1

    TABLES = {
        "sales": """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                tag TEXT,
                revenue REAL NOT NULL,
                date TEXT NOT NULL
            )
        """,
        "costs": """
            CREATE TABLE IF NOT EXISTS costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                cost REAL NOT NULL,
                date TEXT NOT NULL
            )
        """,
        "sg_a_costs": """
            CREATE TABLE IF NOT EXISTS sg_a_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """,
        "cashflow": """
            CREATE TABLE IF NOT EXISTS cashflow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                inflow REAL NOT NULL,
                outflow REAL NOT NULL
            )
        """,
        "tags": """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL
            )
        """,
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """,
        "target_revenue": """
            CREATE TABLE IF NOT EXISTS target_revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL
            )
        """,
        "profits": """
            CREATE TABLE IF NOT EXISTS profits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revenue REAL NOT NULL,
                cost REAL NOT NULL,
                sg_a_cost REAL NOT NULL,
                profit REAL NOT NULL,
                date TEXT NOT NULL
            )
        """
    }

    @staticmethod
    def init_db():
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()
        try:
            # スキーマバージョンテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL
                )
            """)
            cursor.execute("SELECT MAX(version) FROM schema_version")
            current_version = cursor.fetchone()[0] or 0

            # テーブル作成または更新
            if current_version < Database.SCHEMA_VERSION:
                for create_query in Database.TABLES.values():
                    cursor.execute(create_query)

                cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (Database.SCHEMA_VERSION,))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"データベース初期化エラー: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def execute_query(query: str, params: Optional[Tuple] = None) -> None:
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"SQLエラー: {e} | クエリ: {query} | パラメータ: {params}")
            raise
        finally:
            conn.close()

    @staticmethod
    def fetch_data(query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        conn = sqlite3.connect(Database.DB_FILE)
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"SQLエラー: {e} | クエリ: {query} | パラメータ: {params}")
            raise
        finally:
            conn.close()
