#!/bin/bash
# A-Share Warehouse 数据获取 - 15:05 指数数据
# 获取9个指数的日K线数据

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/fetch_index_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取指数数据" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/fetch_index_kline_v2.py >> "$LOG_FILE" 2>&1

exit $?

