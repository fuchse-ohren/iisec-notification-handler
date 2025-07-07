#!/usr/bin/env python3

import time,signal,sys,logging,subprocess
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 停止フラグ
running = True

def signal_handler(signum, frame):
    global running
    logging.info(f"{signum}シグナルを受け取ったためプログラムを停止します")
    running = False
    exit()

# シグナルの設定
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# 次の00分までの秒数を返す
def seconds_until_next_hour():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    delta = (next_hour - now).total_seconds()
    return delta

def main_loop():
    logging.info("デーモンを開始しました")

    # ここにメインの処理を書く
    while running:
        logging.info("iisec.py を実行します")
        
        # iisec.pyを実行する
        start_time = datetime.now()
        result = subprocess.run(["python","iisec.py"])
        elapsed = (datetime.now() - start_time).total_seconds()
        logging.info(f"iisec.pyの実行が完了しました．返値:{result.returncode}, 実行時間: {elapsed}秒")
        
        # 次の00分まで待機
        wait_seconds = seconds_until_next_hour()
        logging.info(f"{int(wait_seconds)}秒間待機します")
        time.sleep(wait_seconds)

    logging.info("デーモンが停止しました")

if __name__ == "__main__":
    main_loop()
