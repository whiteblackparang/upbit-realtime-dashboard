import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sql_queries import get_latest_snapshot, get_top_gainers, get_volume_surge
from risk_indicators import get_normalized_volatility, get_ma_deviation, flag_risk_alerts

st.set_page_config(page_title="Upbit 리스크 모니터링 대시보드", layout="wide")

st.title(" Upbit 실시간 리스크 모니터링 대시보드")
st.caption("5분 간격 수집 데이터 기반 · 데이터는 최신 스냅샷 시점 기준")

if st.button(" 새로고침"):
    st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("최신 시세 스냅샷")
    latest = get_latest_snapshot()
    latest_display = latest[['market', 'trade_price', 'signed_change_rate', 'acc_trade_volume_24h']].copy()
    latest_display['signed_change_rate'] = (latest_display['signed_change_rate'] * 100).round(2)
    latest_display.columns = ['코인', '현재가', '등락률(%)', '24h 거래량']
    st.dataframe(latest_display, use_container_width=True, hide_index=True)

with col2:
    st.subheader(" 리스크 경보 대상")
    alerts = flag_risk_alerts()
    alert_display = alerts[alerts['alert']][['market', 'cv_pct', 'deviation_pct']].copy()
    alert_display.columns = ['코인', '변동계수(CV%)', '이동평균 이격도(%)']
    if len(alert_display) > 0:
        st.dataframe(alert_display, use_container_width=True, hide_index=True)
    else:
        st.info("현재 경보 대상 코인이 없습니다.")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader(" 정규화 변동성(CV%) 순위")
    vol = get_normalized_volatility()
    st.bar_chart(vol.set_index('market')['cv_pct'])

with col4:
    st.subheader(" 24시간 거래량 상위")
    volume = get_volume_surge()
    st.bar_chart(volume.set_index('market')['acc_trade_volume_24h'])

st.divider()
st.subheader("이동평균 이격도")
ma_dev = get_ma_deviation()
st.dataframe(ma_dev, use_container_width=True, hide_index=True)