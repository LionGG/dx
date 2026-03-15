#!/bin/bash
# OpenClaw 健康检查脚本
# 执行时间: 每周日 04:30
# 特点: 不依赖 AI API，纯命令行检查

REPORT_FILE="/tmp/health_check_report.txt"
DT=$(date '+%Y-%m-%d %H:%M')

echo "🏥 OpenClaw 健康检查报告 - ${DT}" > $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 1. Gateway 状态
echo "【1. Gateway 状态】" >> $REPORT_FILE
GW_STATUS=$(openclaw gateway status 2>/dev/null | grep -E "running|active" | head -1)
if [ -n "$GW_STATUS" ]; then
    echo "✅ Gateway 运行正常" >> $REPORT_FILE
else
    echo "⚠️ Gateway 状态需关注" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 2. 系统资源
echo "【2. 系统资源】" >> $REPORT_FILE
echo "内存使用:" >> $REPORT_FILE
if command -v free >/dev/null 2>&1; then
    free -h 2>/dev/null | grep "Mem:" | while read line; do
        used=$(echo $line | awk '{print $3}')
        total=$(echo $line | awk '{print $2}')
        echo "  已用: $used / 总计: $total" >> $REPORT_FILE
    done
else
    echo "  (无法获取内存信息)" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

echo "磁盘使用:" >> $REPORT_FILE
df -h / 2>/dev/null | tail -1 | awk '{print "  根分区: " $5 " 已用 (" $3 "/" $2 ")"}' >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 3. 定时任务状态
echo "【3. 定时任务概览】" >> $REPORT_FILE
ERROR_COUNT=$(openclaw cron list 2>/dev/null | grep -c "error" || echo "0")
if [ "$ERROR_COUNT" -eq "0" ]; then
    echo "✅ 所有定时任务正常" >> $REPORT_FILE
else
    echo "⚠️ 发现 ${ERROR_COUNT} 个错误任务:" >> $REPORT_FILE
    openclaw cron list 2>/dev/null | grep "error" | head -3 | awk '{print "  - " $2}' >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 4. 会话状态
echo "【4. 会话状态】" >> $REPORT_FILE
SESSION_COUNT=$(openclaw sessions list 2>/dev/null | wc -l || echo "0")
echo "  活跃会话数: ${SESSION_COUNT}" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "---" >> $REPORT_FILE
echo "检查完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> $REPORT_FILE
echo "执行方式: 纯命令行检查 (无 AI API 调用)" >> $REPORT_FILE

# 输出报告内容
cat $REPORT_FILE

# 发送飞书消息
openclaw message send --channel feishu --target "ou_7b3b64c0a18c735401f4e1d172d4c802" --message "$(cat $REPORT_FILE)" 2>/dev/null

exit 0
