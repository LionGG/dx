#!/bin/bash
# EvoMap Capsule 继承重试脚本

LOG_FILE="/root/.openclaw/logs/evomap_inherit.log"
NODE_ID="node_ebf2bf543e3ad0dd"

echo "[$(date)] 开始 EvoMap Capsule 继承重试" >> $LOG_FILE

# Capsule 1
CAPSULE1_ID="sha256:3788de88cc227ec0e34d8212dccb9e5d333b3ee7ef626c06017db9ef52386baa"

# 尝试继承，最多 5 次
for i in 1 2 3 4 5; do
    echo "[$(date)] 尝试继承 Capsule 1 (第 $i 次)..." >> $LOG_FILE
    
    RESPONSE=$(curl -s -X POST https://evomap.ai/a2a/fetch \
        -H "Content-Type: application/json" \
        -d "{
            \"protocol\": \"gep-a2a\",
            \"protocol_version\": \"1.0.0\",
            \"message_type\": \"fetch\",
            \"message_id\": \"msg_$(date +%s)_$(openssl rand -hex 4)\",
            \"sender_id\": \"$NODE_ID\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
            \"payload\": {
                \"asset_type\": \"Capsule\",
                \"asset_id\": \"$CAPSULE1_ID\"
            }
        }" 2>&1)
    
    if echo "$RESPONSE" | grep -q "payload.*assets"; then
        echo "$RESPONSE" > /root/.openclaw/workspace/evomap_capsule_1.json
        echo "[$(date)] ✅ Capsule 1 继承成功" >> $LOG_FILE
        break
    else
        echo "[$(date)] ❌ 失败，等待 10 秒后重试..." >> $LOG_FILE
        sleep 10
    fi
done

# Capsule 2
CAPSULE2_ID="sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec"

for i in 1 2 3 4 5; do
    echo "[$(date)] 尝试继承 Capsule 2 (第 $i 次)..." >> $LOG_FILE
    
    RESPONSE=$(curl -s -X POST https://evomap.ai/a2a/fetch \
        -H "Content-Type: application/json" \
        -d "{
            \"protocol\": \"gep-a2a\",
            \"protocol_version\": \"1.0.0\",
            \"message_type\": \"fetch\",
            \"message_id\": \"msg_$(date +%s)_$(openssl rand -hex 4)\",
            \"sender_id\": \"$NODE_ID\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
            \"payload\": {
                \"asset_type\": \"Capsule\",
                \"asset_id\": \"$CAPSULE2_ID\"
            }
        }" 2>&1)
    
    if echo "$RESPONSE" | grep -q "payload.*assets"; then
        echo "$RESPONSE" > /root/.openclaw/workspace/evomap_capsule_2.json
        echo "[$(date)] ✅ Capsule 2 继承成功" >> $LOG_FILE
        break
    else
        echo "[$(date)] ❌ 失败，等待 10 秒后重试..." >> $LOG_FILE
        sleep 10
    fi
done

echo "[$(date)] 继承重试完成" >> $LOG_FILE
