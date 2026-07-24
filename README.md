# Upbit 실시간 리스크 모니터링 대시보드
Upbit Real-time Data Pipeline & Risk Monitoring Dashboard

## 프로젝트 배경
블록스퀘어서울 "알고리즘 데이터분석 및 디지털 자산 트레이더" 채용공고 대응.
[변동성 돌파 백테스팅 프로젝트](../crypto-volatility-breakout)가 "과거 데이터 기반 전략 검증"이었다면,
이 프로젝트는 "현재 시장을 실시간으로 수집·분석·경보"하는 운영 관점의 데이터 파이프라인입니다.

## 아키텍처

GitHub Actions (5분 주기 스케줄)
│
▼
Upbit Ticker API (무료, 인증 불필요)
│
▼
SQLite (ticks 테이블, append-only 누적)
│
▼
SQL 분석 쿼리 (급등/변동성/거래량 랭킹)
│
▼
Streamlit 대시보드 (실시간 조회 화면)

## 모니터링 대상
업비트 원화마켓 주요 10개 코인: BTC, ETH, XRP, SOL, DOGE, ADA, AVAX, TRX, LINK, DOT

## 구성
| 파일 | 역할 | 자격요건 매핑 |
|---|---|---|
| `db_schema.py` | SQLite 스키마 초기화 | 데이터 정제 |
| `collector.py` | Upbit API 호출 → DB 적재 | 데이터 수집 |
| `sql_queries.py` | 급등/변동성/거래량 추출 SQL | SQL 추출 |
| `risk_indicators.py` | 변동계수(CV), 이동평균 이격도, 리스크 경보 | 리스크 지표 산출 |
| `dashboard.py` | Streamlit 실시간 대시보드 | 모니터링 |
| `.github/workflows/collect_data.yml` | 5분 주기 자동 수집 | 클라우드 환경 활용 |

## 핵심 설계 포인트

**1. 절대가격 스케일 정규화**
BTC(9천만원대)와 XRP(1천원대)처럼 코인마다 가격 단위가 크게 다르기 때문에,
단순 표준편차로 변동성을 비교하면 항상 BTC가 1위로 왜곡됩니다.
이를 해결하기 위해 변동계수(CV = 표준편차/평균)로 정규화하여 코인 간 공정 비교가 가능하도록 설계했습니다.

**2. 타임스탬프 포맷 트러블슈팅**
초기 구현에서 Python `datetime.isoformat()`(예: `2026-07-24T03:56:04+00:00`)과
SQLite `datetime('now')`(예: `2026-07-24 03:56:04`) 간 포맷 불일치로 SQL 날짜 비교 쿼리가
제대로 매칭되지 않는 문제가 있었습니다. `strftime('%Y-%m-%d %H:%M:%S')`로 저장 포맷을
SQLite 네이티브 포맷에 맞춰 해결했습니다.

**3. 경로 이식성**
스크립트 실행 위치(프로젝트 루트 vs `src/` 폴더)에 관계없이 항상 같은 DB 파일을 찾도록
`__file__` 기준 절대경로로 DB 경로를 계산하도록 구현했습니다.

## 실행 방법

로컬에서 1회 수집 + 대시보드 확인:
```bash
pip install -r requirements.txt
python src/db_schema.py
python src/collector.py
streamlit run src/dashboard.py
```

자동 수집은 GitHub Actions가 5분 주기로 처리합니다 (저장소 Settings → Actions → Workflow permissions를 "Read and write"로 설정 필요).

## 한계 및 향후 개선 방향
- GitHub Actions 무료 스케줄은 정확히 5분 정각에 실행되지 않고 지연될 수 있음
- 현재는 DB를 저장소에 직접 커밋 — 데이터가 누적될수록 저장소 용량 증가, 향후 별도 아카이빙 로직 필요
- 대시보드 자동 새로고침 미구현 (현재 수동 버튼 방식)
- 리스크 경보 임계값(CV 0.5%, 이격도 1%)은 초기 설정값 — 데이터가 더 쌓이면 실제 분포 기반으로 재조정 필요

## 기술 스택
Python (pandas, numpy, requests), SQLite, SQL (윈도우 함수, 서브쿼리), Streamlit, GitHub Actions