#!/bin/bash
# A-Share Warehouse 数据获取 - 周六02:00 板块与个股关系
# 获取板块与个股的对应关系（增量更新）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/fetch_sector_stocks_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取板块与个股关系数据" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/fetch_sector_stocks_v2.py >> "$LOG_FILE" 2>&1

exit $?
