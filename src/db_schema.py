import sqlite3
import os

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DB_PATH = os.path.join(BASE_DIR, 'data', 'upbit_realtime.db')

TARGET_MARKETS = [
    'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
    'KRW-ADA', 'KRW-AVAX', 'KRW-TRX', 'KRW-LINK', 'KRW-DOT'
]

def init_db(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            trade_price REAL NOT NULL,
            trade_volume REAL,
            acc_trade_volume_24h REAL,
            signed_change_rate REAL,
            high_price REAL,
            low_price REAL,
            collected_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_time
        ON ticks (market, collected_at)
    """)

    conn.commit()
    conn.close()
    print(f"DB 초기화 완료: {db_path}")


if __name__ == '__main__':
    init_db()