#!/bin/bash
# A-Share Warehouse 数据获取 - 17:50 龙虎榜和资金流向
# 获取龙虎榜、板块资金流向、板块资金排名

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/fetch_lhb_fund_$(date +%Y%m%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取龙虎榜和资金流向数据" >> "$LOG_FILE"

cd "$PROJECT_DIR" && /usr/bin/python3 scripts/fetch_lhb_fund_v2.py >> "$LOG_FILE" 2>&1

exit $?
