#!/bin/bash
REPORT_FILE="/tmp/daily_status_report.txt"
DT=$(date +%Y%m%d_%H%M)
DT_FULL=$(date +%Y-%m-%d_%H:%M:%S)

echo "========================================" > $REPORT_FILE
echo "📊 每日状态报告 - $DT" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "【时间信息】" >> $REPORT_FILE
echo "  当前时间: $DT_FULL" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "【定时任务状态】" >> $REPORT_FILE
openclaw cron list 2>/dev/null | grep -E "(error|failed)" | head -3 >> $REPORT_FILE || echo "  ✅ 所有任务正常" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "【Gateway 状态】" >> $REPORT_FILE
openclaw gateway status 2>/dev/null | grep -E "running" | head -1 >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "【磁盘使用】" >> $REPORT_FILE
df -h / | tail -1 | awk "{print \"  使用率: \"\$5}" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "---" >> $REPORT_FILE
echo "报告生成时间: $DT_FULL" >> $REPORT_FILE
echo "生成方式: 直接命令执行（不依赖 AI API）" >> $REPORT_FILE

cat $REPORT_FILE
