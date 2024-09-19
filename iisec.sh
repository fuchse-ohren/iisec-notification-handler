#!/bin/bash
cd $(dirname "$0")
export IISEC_ID=""
export IISEC_PW=""
export GROQ_API_KEY=""
export DISCORD_WEBHOOK=""
set | /usr/bin/python3 iisec.py | tee -a log.txt