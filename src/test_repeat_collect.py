import time
from datetime import datetime
from collector import run_once

INTERVAL_SECONDS = 60   
REPEAT_COUNT = 8         

def repeat_collect(interval: int = INTERVAL_SECONDS, count: int = REPEAT_COUNT):
    for i in range(count):
        print(f"\n[{i+1}/{count}] {datetime.now().strftime('%H:%M:%S')} 수집 시작")
        run_once()
        if i < count - 1:
            time.sleep(interval)

    print("수집 완료.")

if __name__ == '__main__':
    repeat_collect()