#!/bin/bash
# Memory 和 ERROR_PREVENTION 归档脚本

WORKSPACE="/root/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/archive/memory"
DATE_STR=$(date +%Y%m%d)
LOG_FILE="$WORKSPACE/logs/archive_memory.log"

mkdir -p $ARCHIVE_DIR
mkdir -p $(dirname $LOG_FILE)

echo "========================================" >> $LOG_FILE
echo "[$(date)] Memory 归档开始" >> $LOG_FILE

# 1. 归档 7 天前的 memory 文件
find $WORKSPACE/memory -name "*.md" -mtime +7 -type f | while read file; do
    filename=$(basename "$file")
    echo "  归档: $filename" >> $LOG_FILE
    gzip -c "$file" > "$ARCHIVE_DIR/${filename}.gz"
    rm "$file"
done

# 2. 检查 ERROR_PREVENTION.md 大小
ERROR_FILE="$WORKSPACE/ERROR_PREVENTION.md"
ERROR_SIZE=$(wc -c < "$ERROR_FILE")
if [ $ERROR_SIZE -gt 5000 ]; then
    cp "$ERROR_FILE" "$ARCHIVE_DIR/ERROR_PREVENTION_${DATE_STR}.md"
    gzip "$ARCHIVE_DIR/ERROR_PREVENTION_${DATE_STR}.md"
    echo "  ERROR_PREVENTION.md 已归档 ($ERROR_SIZE 字节)" >> $LOG_FILE
fi

echo "[$(date)] 归档完成" >> $LOG_FILE
