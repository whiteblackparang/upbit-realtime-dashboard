import sqlite3
import pandas as pd

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
DB_PATH = os.path.join(BASE_DIR, 'data', 'upbit_realtime.db')

def get_latest_snapshot(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = """
    SELECT t.*
    FROM ticks t
    INNER JOIN (
        SELECT market, MAX(collected_at) AS max_time
        FROM ticks
        GROUP BY market
    ) latest
    ON t.market = latest.market AND t.collected_at = latest.max_time
    ORDER BY t.signed_change_rate DESC
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


def get_top_gainers(hours: int = 1, top_n: int = 5, db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = f"""
    WITH windowed AS (
        SELECT *
        FROM ticks
        WHERE collected_at >= datetime('now', '-{hours} hours')
    ),
    first_last AS (
        SELECT
            market,
            FIRST_VALUE(trade_price) OVER (PARTITION BY market ORDER BY collected_at) AS start_price,
            LAST_VALUE(trade_price) OVER (
                PARTITION BY market ORDER BY collected_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS end_price,
            collected_at
        FROM windowed
    )
    SELECT DISTINCT
        market,
        start_price,
        end_price,
        ROUND((end_price - start_price) * 100.0 / start_price, 2) AS change_pct
    FROM first_last
    ORDER BY change_pct DESC
    LIMIT {top_n}
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


def get_volatility_ranking(hours: int = 1, db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT
        market,
        AVG(trade_price) AS avg_price,
        (
            AVG(trade_price * trade_price) - AVG(trade_price) * AVG(trade_price)
        ) AS variance_proxy,
        COUNT(*) AS n_snapshots
    FROM ticks
    WHERE collected_at >= datetime('now', '-{hours} hours')
    GROUP BY market
    HAVING n_snapshots >= 2
    ORDER BY variance_proxy DESC
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


def get_volume_surge(top_n: int = 5, db_path: str = DB_PATH) -> pd.DataFrame:
    latest = get_latest_snapshot(db_path)
    return latest.sort_values('acc_trade_volume_24h', ascending=False).head(top_n)[
        ['market', 'trade_price', 'acc_trade_volume_24h', 'signed_change_rate']
    ]


if __name__ == '__main__':
    print(" 최신 스냅샷 (등락률순) ")
    print(get_latest_snapshot().to_string(index=False))

    print(" 최근 1시간 상승률 상위 ")
    print(get_top_gainers(hours=1).to_string(index=False))

    print(" 최근 1시간 변동성 순위 ")
    print(get_volatility_ranking(hours=1).to_string(index=False))

    print(" 24시간 거래량 상위 ")
    print(get_volume_surge().to_string(index=False))