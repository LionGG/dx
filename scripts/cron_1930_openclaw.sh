#!/bin/bash
# OpenClaw最佳实践抓取 - 晚上19:30执行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/root/.openclaw/workspace/logs/openclaw_practices_$(date +%Y%m%d).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始OpenClaw最佳实践抓取" >> "$LOG_FILE"

cd /root/.openclaw/workspace && /usr/bin/python3 scripts/fetch_openclaw_practices.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] OpenClaw最佳实践抓取成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] OpenClaw最佳实践抓取失败" >> "$LOG_FILE"
fi
