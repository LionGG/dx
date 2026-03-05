#!/bin/bash
# 每日数据更新定时任务脚本
# 添加到 crontab 使用

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/daily_update_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 15:45 批次 - 基础数据
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始 15:45 批次更新" >> "$LOG_FILE"
cd "$PROJECT_DIR" && /usr/bin/python3 scripts/daily_update_v2.py 1545 >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 15:45 批次完成" >> "$LOG_FILE"
