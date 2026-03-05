#!/bin/bash
# Gateway 重启脚本（带自我修复）
# 执行时间: 每周日 03:00

LOG_FILE="/root/.openclaw/logs/gateway_restart.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
MAX_RETRY=3
RETRY_COUNT=0

# 确保日志目录存在
mkdir -p /root/.openclaw/logs

log() {
    echo "[$DATE] $1" | tee -a $LOG_FILE
}

log "========== Gateway 重启开始 =========="

# 函数: 检查 Gateway 状态
check_gateway() {
    local pid=$(pgrep -f "openclaw-gateway" | head -1)
    if [ -n "$pid" ]; then
        # 检查端口
        if ss -tuln | grep -q ":18789"; then
            echo "running:$pid"
            return 0
        fi
    fi
    echo "stopped"
    return 1
}

# 函数: 重启 Gateway
restart_gateway() {
    log "尝试重启 Gateway (第 $1 次)..."
    
    # 优雅停止
    openclaw gateway stop 2>/dev/null || true
    sleep 2
    
    # 强制停止（如果还在运行）
    local pid=$(pgrep -f "openclaw-gateway" | head -1)
    if [ -n "$pid" ]; then
        log "强制停止旧进程 PID=$pid"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
    
    # 启动 Gateway
    openclaw gateway start 2>&1 &
    
    # 等待启动
    sleep 5
    
    # 检查是否成功
    local status=$(check_gateway)
    if [[ "$status" == running:* ]]; then
        local new_pid=${status#running:}
        log "✅ Gateway 重启成功，新 PID=$new_pid"
        return 0
    else
        log "❌ Gateway 重启失败"
        return 1
    fi
}

# 函数: 自我修复
self_heal() {
    log "开始自我修复..."
    
    # 1. 检查配置文件
    if ! python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))" 2>/dev/null; then
        log "⚠️ 配置文件损坏，尝试恢复备份"
        local latest_backup=$(ls -t /root/.openclaw/openclaw.json.bak.* 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            cp "$latest_backup" /root/.openclaw/openclaw.json
            log "✅ 已恢复备份: $latest_backup"
        else
            log "❌ 无可用备份"
        fi
    fi
    
    # 2. 清理锁文件
    find /root/.openclaw -name "*.lock" -type f -mmin +60 -delete 2>/dev/null || true
    log "✅ 已清理旧锁文件"
    
    # 3. 检查端口占用
    local port_pid=$(ss -tulnp 2>/dev/null | grep ":18789" | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2 | head -1)
    if [ -n "$port_pid" ] && [ "$port_pid" != "*" ]; then
        log "⚠️ 端口 18789 被 PID=$port_pid 占用，尝试释放"
        kill -9 $port_pid 2>/dev/null || true
        sleep 1
    fi
    
    return 0
}

# 主逻辑
while [ $RETRY_COUNT -lt $MAX_RETRY ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    # 尝试重启
    if restart_gateway $RETRY_COUNT; then
        # 验证服务
        sleep 3
        final_status=$(check_gateway)
        if [[ "$final_status" == running:* ]]; then
            final_pid=${final_status#running:}
            log "✅ Gateway 运行正常，PID=$final_pid"
            
            # 发送成功通知（可选）
            # curl -s -X POST -H "Content-Type: application/json" \
            #   -d '{"msg_type": "text", "content": {"text": "✅ Gateway 重启成功"}}' \
            #   YOUR_WEBHOOK_URL 2>/dev/null || true
            
            log "========== Gateway 重启完成 =========="
            exit 0
        fi
    fi
    
    # 重启失败，尝试自我修复
    if [ $RETRY_COUNT -lt $MAX_RETRY ]; then
        log "等待 10 秒后尝试自我修复并重试..."
        sleep 10
        self_heal
    fi
done

# 所有重试失败
log "❌ Gateway 重启失败，已尝试 $MAX_RETRY 次"

# 发送失败通知（可选）
# curl -s -X POST -H "Content-Type: application/json" \
#   -d '{"msg_type": "text", "content": {"text": "❌ Gateway 重启失败，请手动检查"}}' \
#   YOUR_WEBHOOK_URL 2>/dev/null || true

log "========== Gateway 重启失败 =========="
exit 1
