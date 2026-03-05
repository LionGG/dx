#!/bin/bash
# MA50占比每日计算 - 定时任务脚本
# 交易日 15:10 执行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/ma50_ratio_$(date +%Y%m%d).log"
CHART_PATH="$PROJECT_DIR/data/ma50_ratio_daily.png"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始MA50占比计算" >> "$LOG_FILE"

# 1. 执行Python脚本计算并写入数据库
cd "$PROJECT_DIR" && /usr/bin/python3 scripts/calculate_ma50_ratio.py >> "$LOG_FILE" 2>&1

exit $?

