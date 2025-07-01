#!/usr/bin/env python3

import time
import signal
import sys
import logging
import subprocess

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
    logging.info(f"Received signal {signum}, shutting down...")
    running = False
    exit()

# シグナルの設定
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main_loop():
    logging.info("Daemon started.")

    # ここにメインの処理を書く
    while running:
        subprocess.run(["python","iisec.py"])
        time.sleep(3600)

    logging.info("Daemon stopped.")

if __name__ == "__main__":
    main_loop()
