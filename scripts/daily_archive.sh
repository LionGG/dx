#!/bin/bash
# 每日归档清理脚本 - 防止使用过时中间文件
# 运行时间：每天03:00

WORKSPACE="/root/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/archive/$(date +%Y%m%d)"
LOG_FILE="$WORKSPACE/logs/daily_archive.log"

# 创建日志目录
mkdir -p $(dirname $LOG_FILE)
mkdir -p $ARCHIVE_DIR

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始每日归档清理" >> $LOG_FILE

# 1. 归档stock/dx/temp/下的中间文件
if [ -d "$WORKSPACE/stock/dx/temp" ]; then
    TEMP_COUNT=$(ls -1 $WORKSPACE/stock/dx/temp/*.md 2>/dev/null | wc -l)
    if [ $TEMP_COUNT -gt 0 ]; then
        tar -czf "$ARCHIVE_DIR/dx_temp_$(date +%Y%m%d).tar.gz" -C $WORKSPACE/stock/dx/temp .
        rm -f $WORKSPACE/stock/dx/temp/*.md
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 归档dx/temp: $TEMP_COUNT 个文件" >> $LOG_FILE
    fi
fi

# 2. 归档memory/temp/下的文件
if [ -d "$WORKSPACE/memory/temp" ]; then
    TEMP_COUNT=$(ls -1 $WORKSPACE/memory/temp/* 2>/dev/null | wc -l)
    if [ $TEMP_COUNT -gt 0 ]; then
        tar -czf "$ARCHIVE_DIR/memory_temp_$(date +%Y%m%d).tar.gz" -C $WORKSPACE/memory/temp .
        rm -rf $WORKSPACE/memory/temp/*
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 归档memory/temp: $TEMP_COUNT 个文件" >> $LOG_FILE
    fi
fi

# 3. 清理skills下的备份文件(超过3天)
find $WORKSPACE/skills -name "*-backup.md" -mtime +3 -exec mv {} $ARCHIVE_DIR/ \; 2>/dev/null
find $WORKSPACE/skills -name "*-draft.md" -mtime +3 -exec mv {} $ARCHIVE_DIR/ \; 2>/dev/null

# 4. 清理Python备份文件
find $WORKSPACE -name "*.py.bak" -mtime +1 -delete 2>/dev/null
find $WORKSPACE -name "*.json.bak" -mtime +1 -delete 2>/dev/null

# 5. 记录归档结果
ARCHIVE_COUNT=$(ls -1 $ARCHIVE_DIR/ 2>/dev/null | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 归档完成: $ARCHIVE_COUNT 个文件归档到 $ARCHIVE_DIR" >> $LOG_FILE

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日归档清理结束" >> $LOG_FILE
