import sqlite3
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'upbit_realtime.db')


def get_normalized_volatility(hours: int = 1, db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT
        market,
        trade_price,
        collected_at
    FROM ticks
    WHERE collected_at >= datetime('now', '-{hours} hours')
    ORDER BY market, collected_at
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    result = (
        df.groupby('market')['trade_price']
        .agg(avg_price='mean', std_price='std', n_snapshots='count')
        .reset_index()
    )
    result = result[result['n_snapshots'] >= 2]
    result['cv_pct'] = (result['std_price'] / result['avg_price']) * 100
    return result.sort_values('cv_pct', ascending=False)


def get_ma_deviation(short_window: int = 3, db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = """
    SELECT market, trade_price, collected_at
    FROM ticks
    ORDER BY market, collected_at
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    results = []
    for market, group in df.groupby('market'):
        group = group.sort_values('collected_at')
        if len(group) < short_window:
            continue
        ma = group['trade_price'].tail(short_window).mean()
        current = group['trade_price'].iloc[-1]
        deviation_pct = (current - ma) / ma * 100
        results.append({
            'market': market,
            'current_price': current,
            f'ma_{short_window}': ma,
            'deviation_pct': round(deviation_pct, 3)
        })

    return pd.DataFrame(results).sort_values('deviation_pct', ascending=False)


def flag_risk_alerts(cv_threshold: float = 0.5, deviation_threshold: float = 1.0, db_path: str = DB_PATH) -> pd.DataFrame:
    vol = get_normalized_volatility(db_path=db_path)
    ma_dev = get_ma_deviation(db_path=db_path)

    merged = vol.merge(ma_dev[['market', 'deviation_pct']], on='market', how='left')
    merged['alert'] = (
        (merged['cv_pct'] > cv_threshold) | (merged['deviation_pct'].abs() > deviation_threshold)
    )
    return merged.sort_values('alert', ascending=False)


if __name__ == '__main__':
    print(" 정규화된 변동성(CV%) 순위 ")
    print(get_normalized_volatility().to_string(index=False))

    print(" 이동평균 이격도 ")
    print(get_ma_deviation().to_string(index=False))

    print(" 리스크 경보 대상 ")
    print(flag_risk_alerts().to_string(index=False))