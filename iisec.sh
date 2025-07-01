#!/bin/bash
cd $(dirname "$0")
export IISEC_ID=""
export IISEC_PW=""
export MODEL_PATH="./model/tinyswallow-1.5b-instruct-q8_0.gguf"
export DISCORD_WEBHOOK=""
export SLACK_WEBHOOK=""
set | /usr/bin/python3 iisec.py | tee -a log.txt
