#!/bin/bash
# A-Share Warehouse 数据获取 - 15:02 个股数据同步
# 从MySQL同步当日个股数据

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/sync_stock_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始个股数据同步" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/sync_stock_from_mysql_v2.py >> "$LOG_FILE" 2>&1

exit $?

