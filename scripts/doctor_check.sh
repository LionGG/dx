#!/bin/bash
# OpenClaw Doctor 定期检查脚本
# 建议添加到 cron: 0 9 * * 1 /root/.openclaw/workspace/scripts/doctor_check.sh

LOG_FILE="/root/.openclaw/logs/doctor_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 确保日志目录存在
mkdir -p /root/.openclaw/logs

echo "========== OpenClaw Doctor Check - $DATE ==========" >> $LOG_FILE

# 运行 Doctor 检查
openclaw doctor 2>&1 >> $LOG_FILE

# 检查关键指标
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Doctor check passed" >> $LOG_FILE
else
    echo "⚠️ Doctor check found issues (exit code: $EXIT_CODE)" >> $LOG_FILE
    
    # 发送通知（如果配置了飞书）
    # curl -s -X POST -H "Content-Type: application/json" \
    #   -d '{"msg_type": "text", "content": {"text": "⚠️ OpenClaw Doctor 检查发现异常，请查看日志"}}' \
    #   YOUR_WEBHOOK_URL 2>/dev/null || true
fi

echo "" >> $LOG_FILE

# 保留最近 30 天的日志
find /root/.openclaw/logs -name "doctor_check.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
