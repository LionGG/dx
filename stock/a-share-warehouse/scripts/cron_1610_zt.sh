#!/bin/bash
# A-Share Warehouse 数据获取 - 16:10 涨停板生态数据
# 获取涨停池、跌停池、炸板池、强势股池

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/fetch_zt_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取涨停板生态数据" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/fetch_zt_pool_v2.py >> "$LOG_FILE" 2>&1

exit $?
