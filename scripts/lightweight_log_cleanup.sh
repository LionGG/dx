#!/bin/bash
# 轻量级日志清理 - 每天00:27执行
# 只清理日志文件，不动业务数据

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/lightweight_cleanup.log"

mkdir -p $(dirname $LOG_FILE)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始轻量级日志清理" >> $LOG_FILE

# 1. 清理OpenClaw日志（保留最近3天）
find /tmp/openclaw -name "openclaw-*.log" -mtime +3 -delete 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理OpenClaw旧日志（>3天）" >> $LOG_FILE

# 2. 清理Python缓存
find $WORKSPACE -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find $WORKSPACE -name "*.pyc" -delete 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理Python缓存" >> $LOG_FILE

# 3. 清理临时下载文件
find $WORKSPACE/temp -type f -mtime +1 -delete 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理临时文件（>1天）" >> $LOG_FILE

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 轻量级清理完成" >> $LOG_FILE
