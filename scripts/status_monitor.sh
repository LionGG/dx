#!/bin/bash
# Status Web 异常监控脚本

API_URL="http://localhost:8888/api/status"
FEISHU_WEBHOOK="${FEISHU_WEBHOOK:-}"

# 获取状态
curl -s $API_URL > /tmp/status_check.json 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ 无法连接到status-web服务"
    exit 1
fi

# 解析状态
HEALTH_STATUS=$(cat /tmp/status_check.json | jq -r '.health_status.status')
CPU_LOAD=$(cat /tmp/status_check.json | jq -r '.health_status.cpu_load' | tr -d '%')
MEMORY_AVAILABLE=$(cat /tmp/status_check.json | jq -r '.health_status.memory_available' | grep -o '[0-9.]*')
OPENCLAW_CONNECTED=$(cat /tmp/status_check.json | jq -r '.health_status.openclaw_connected')

# 检查异常
ALERTS=""

if [ "$HEALTH_STATUS" != "healthy" ]; then
    ALERTS="${ALERTS}系统状态异常: $HEALTH_STATUS\n"
fi

if [ "${CPU_LOAD%.*}" -gt 80 ]; then
    ALERTS="${ALERTS}CPU负载过高: ${CPU_LOAD}%\n"
fi

if [ "${MEMORY_AVAILABLE%.*}" -lt 1 ]; then
    ALERTS="${ALERTS}内存不足: ${MEMORY_AVAILABLE}GB\n"
fi

if [ "$OPENCLAW_CONNECTED" != "true" ]; then
    ALERTS="${ALERTS}OpenClaw连接断开\n"
fi

# 如果有异常，发送通知
if [ -n "$ALERTS" ]; then
    echo "⚠️ 检测到异常："
    echo -e "$ALERTS"
    # 这里可以添加飞书通知逻辑
else
    echo "✅ 系统正常"
fi
