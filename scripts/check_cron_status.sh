#!/bin/bash
# 定时任务执行检查脚本 - 实时版本
# 每天早上自动检查昨晚任务状态

echo "=== 定时任务执行检查 ==="
echo "检查时间: $(date)"
echo ""

# 获取实时任务状态
openclaw cron list --json 2>/dev/null | python3 << 'PYEOF'
import json
import sys
from datetime import datetime, timedelta

try:
    data = json.load(sys.stdin)
except:
    print("❌ 无法获取任务状态")
    sys.exit(1)

print("📋 任务状态检查:\n")

issues = []
cutoff_time = datetime.now() - timedelta(hours=48)  # 只检查48小时内的问题

for job in data.get('jobs', []):
    name = job.get('name', 'unknown')
    state = job.get('state', {})
    last_status = state.get('lastRunStatus', 'unknown')
    last_run_ms = state.get('lastRunAtMs', 0)
    last_error = state.get('lastRunError', '')
    
    # 跳过从未执行的任务
    if not last_run_ms:
        continue
    
    # 转换时间
    last_run_time = datetime.fromtimestamp(last_run_ms / 1000)
    last_run_str = last_run_time.strftime('%m-%d %H:%M')
    
    # 只检查48小时内的问题
    if last_run_time < cutoff_time:
        continue
    
    # 检查问题状态
    if last_status in ['error', 'failed', 'skipped']:
        issues.append({
            'name': name,
            'status': last_status,
            'time': last_run_str,
            'error': last_error
        })
        print(f"❌ {name}")
        print(f"   状态: {last_status}")
        print(f"   时间: {last_run_str}")
        if last_error:
            print(f"   错误: {last_error}")
        print()

if not issues:
    print("✅ 最近48小时内所有任务正常执行，无问题\n")
else:
    print(f"⚠️ 发现 {len(issues)} 个问题任务 (48小时内)\n")

PYEOF

echo ""
echo "=== 检查完成 ==="
