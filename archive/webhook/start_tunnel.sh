#!/bin/bash
# 启动 webhook 服务 + localtunnel 内网穿透

echo "================================"
echo "启动 Webhook 内网穿透服务"
echo "================================"

# 检查 webhook 服务
if ! curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "启动 webhook 服务..."
    cd /root/.openclaw/workspace
    ./webhook.sh start
    sleep 2
fi

echo ""
echo "启动 localtunnel (需要等待 10-20 秒)..."
echo ""

# 启动 localtunnel 并捕获输出
npx localtunnel --port 8080 &
LT_PID=$!

# 等待获取 URL
sleep 8

# 尝试获取公网 URL
TUNNEL_URL=$(curl -s http://localhost:8080/ 2>/dev/null | grep -o 'https://[^"]*' || echo "")

if [ -z "$TUNNEL_URL" ]; then
    # 从进程输出中获取
    TUNNEL_URL=$(ps aux | grep localtunnel | grep -o 'https://[^[:space:]]*' | head -1)
fi

echo ""
echo "================================"
if [ -n "$TUNNEL_URL" ]; then
    echo "公网地址: $TUNNEL_URL"
    echo ""
    echo "接口地址:"
    echo "  健康检查: $TUNNEL_URL/"
    echo "  交易通知: $TUNNEL_URL/webhook/trade"
    echo "  通用通知: $TUNNEL_URL/webhook/feishu"
else
    echo "正在获取公网地址，请稍等..."
    echo "可以手动运行: npx localtunnel --port 8080"
fi
echo "================================"
echo ""
echo "按 Ctrl+C 停止"

# 等待
trap "kill $LT_PID 2>/dev/null; exit" INT
wait $LT_PID
