import requests
import sqlite3
from datetime import datetime, timezone

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
DB_PATH = os.path.join(BASE_DIR, 'data', 'upbit_realtime.db')

TARGET_MARKETS = [
    'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
    'KRW-ADA', 'KRW-AVAX', 'KRW-TRX', 'KRW-LINK', 'KRW-DOT'
]

TICKER_URL = 'https://api.upbit.com/v1/ticker'

def fetch_ticker(markets: list[str]):
    params = {'markets': ','.join(markets)}
    response = requests.get(TICKER_URL, params=params, headers={'Accept': 'application/json'})
    response.raise_for_status()
    return response.json()

def save_ticks(ticker_data: list[dict], db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    collected_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    rows = [
        (
            item['market'],
            item['trade_price'],
            item['trade_volume'],
            item['acc_trade_volume_24h'],
            item['signed_change_rate'],
            item['high_price'],
            item['low_price'],
            collected_at
        )
        for item in ticker_data
    ]

    cursor.executemany("""
        INSERT INTO ticks (
            market, trade_price, trade_volume, acc_trade_volume_24h,
            signed_change_rate, high_price, low_price, collected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()
    print(f"{len(rows)}건 적재 완료 ({collected_at})")

def run_once():
    data = fetch_ticker(TARGET_MARKETS)
    save_ticks(data)

if __name__ == '__main__':
    run_once()