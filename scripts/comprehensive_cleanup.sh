#!/bin/bash
# 综合清理归档脚本 - 每天01:27执行
# 第一阶段：轻量级日志清理
# 第二阶段：全量归档清理

WORKSPACE="/root/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/archive/$(date +%Y%m%d)"
LOG_FILE="$WORKSPACE/logs/comprehensive_cleanup.log"

mkdir -p $(dirname $LOG_FILE)
mkdir -p $ARCHIVE_DIR

echo "========================================" >> $LOG_FILE
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 综合清理归档启动" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# ========== 第一阶段：轻量级日志清理 ==========
echo "" >> $LOG_FILE
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 【阶段1】轻量级日志清理..." >> $LOG_FILE

# 1.1 清理OpenClaw日志（保留最近3天）
find /tmp/openclaw -name "openclaw-*.log" -mtime +3 -delete 2>/dev/null
COUNT=$(find /tmp/openclaw -name "openclaw-*.log" 2>/dev/null | wc -l)
echo "  ✓ OpenClaw日志清理完成（保留3天，当前剩余: $COUNT）" >> $LOG_FILE

# 1.2 清理Python缓存
find $WORKSPACE -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find $WORKSPACE -name "*.pyc" -delete 2>/dev/null
echo "  ✓ Python缓存清理完成" >> $LOG_FILE

# 1.3 清理临时下载文件
if [ -d "$WORKSPACE/temp" ]; then
    TEMP_COUNT=$(find $WORKSPACE/temp -type f -mtime +1 2>/dev/null | wc -l)
    find $WORKSPACE/temp -type f -mtime +1 -delete 2>/dev/null
    echo "  ✓ 临时文件清理完成（删除: $TEMP_COUNT）" >> $LOG_FILE
fi

# ========== 第二阶段：全量归档清理 ==========
echo "" >> $LOG_FILE
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 【阶段2】全量归档清理..." >> $LOG_FILE

# 2.1 归档stock/dx/temp/下的中间文件
if [ -d "$WORKSPACE/stock/dx/temp" ]; then
    TEMP_COUNT=$(ls -1 $WORKSPACE/stock/dx/temp/*.md 2>/dev/null | wc -l)
    if [ $TEMP_COUNT -gt 0 ]; then
        tar -czf "$ARCHIVE_DIR/dx_temp_$(date +%Y%m%d).tar.gz" -C $WORKSPACE/stock/dx/temp . 2>/dev/null
        rm -f $WORKSPACE/stock/dx/temp/*.md
        echo "  ✓ stock/dx/temp 归档完成（$TEMP_COUNT 个文件）" >> $LOG_FILE
    else
        echo "  - stock/dx/temp 无文件需要归档" >> $LOG_FILE
    fi
fi

# 2.2 归档memory/temp/下的文件
if [ -d "$WORKSPACE/memory/temp" ]; then
    TEMP_COUNT=$(ls -1 $WORKSPACE/memory/temp/* 2>/dev/null | wc -l)
    if [ $TEMP_COUNT -gt 0 ]; then
        tar -czf "$ARCHIVE_DIR/memory_temp_$(date +%Y%m%d).tar.gz" -C $WORKSPACE/memory/temp . 2>/dev/null
        rm -rf $WORKSPACE/memory/temp/*
        echo "  ✓ memory/temp 归档完成（$TEMP_COUNT 个文件）" >> $LOG_FILE
    else
        echo "  - memory/temp 无文件需要归档" >> $LOG_FILE
    fi
fi

# 2.3 清理skills下的备份文件(超过3天)
BACKUP_COUNT=$(find $WORKSPACE/skills -name "*-backup.md" -mtime +3 2>/dev/null | wc -l)
find $WORKSPACE/skills -name "*-backup.md" -mtime +3 -exec mv {} $ARCHIVE_DIR/ \; 2>/dev/null
find $WORKSPACE/skills -name "*-draft.md" -mtime +3 -exec mv {} $ARCHIVE_DIR/ \; 2>/dev/null
echo "  ✓ Skills备份文件归档完成（$BACKUP_COUNT 个文件）" >> $LOG_FILE

# 2.4 清理Python/JSON备份文件
find $WORKSPACE -name "*.py.bak" -mtime +1 -delete 2>/dev/null
find $WORKSPACE -name "*.json.bak" -mtime +1 -delete 2>/dev/null
echo "  ✓ 备份文件清理完成" >> $LOG_FILE

# ========== 执行总结 ==========
echo "" >> $LOG_FILE
ARCHIVE_COUNT=$(ls -1 $ARCHIVE_DIR/ 2>/dev/null | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理归档完成" >> $LOG_FILE
echo "  - 归档目录: $ARCHIVE_DIR" >> $LOG_FILE
echo "  - 归档文件数: $ARCHIVE_COUNT" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
echo "" >> $LOG_FILE
