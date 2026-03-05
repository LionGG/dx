#!/bin/bash
# AI新闻每日抓取 - 早上8:30执行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/root/.openclaw/workspace/logs/ai_news_$(date +%Y%m%d).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始AI新闻抓取" >> "$LOG_FILE"

cd /root/.openclaw/workspace && /usr/bin/python3 scripts/fetch_ai_news.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI新闻抓取成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI新闻抓取失败" >> "$LOG_FILE"
fi
