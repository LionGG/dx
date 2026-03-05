#!/bin/bash
# A-Share Warehouse 数据获取 - 16:01 板块数据
# 获取板块K线数据

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/fetch_sector_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取板块数据" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/fetch_sector_kline_v2.py >> "$LOG_FILE" 2>&1

exit $?
