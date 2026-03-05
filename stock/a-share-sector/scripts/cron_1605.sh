#!/bin/bash
# A股收盘分析定时任务 - 交易日16:05执行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/analysis_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行收盘分析" >> "$LOG_FILE"

# 执行分析脚本
cd "$PROJECT_DIR" && /usr/bin/python3 scripts/generate_report.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 分析完成" >> "$LOG_FILE"
