#!/bin/bash
# 定时任务执行检查脚本
# 每天早上自动检查昨晚任务状态

echo "=== 定时任务执行检查 ==="
echo "检查时间: $(date)"
echo ""

# 检查cron-jobs状态
python3 << 'PYEOF'
import json
from datetime import datetime

with open('/root/.openclaw/workspace/cron-jobs-updated.json') as f:
    data = json.load(f)

print("📋 任务状态检查:\n")

issues = []
for job in data['jobs']:
    name = job['name']
    state = job.get('state', {})
    last_status = state.get('lastStatus', 'unknown')
    last_run = state.get('lastRunAtMs', 0)
    last_error = state.get('lastError', '')
    
    # 转换时间
    if last_run:
        last_run_time = datetime.fromtimestamp(last_run / 1000).strftime('%m-%d %H:%M')
    else:
        last_run_time = '从未执行'
    
    # 检查问题
    if last_status in ['error', 'failed', 'skipped']:
        issues.append({
            'name': name,
            'status': last_status,
            'time': last_run_time,
            'error': last_error
        })
        print(f"❌ {name}")
        print(f"   状态: {last_status}")
        print(f"   时间: {last_run_time}")
        if last_error:
            print(f"   错误: {last_error}")
        print()

if not issues:
    print("✅ 所有任务正常执行，无问题\n")
else:
    print(f"⚠️ 发现 {len(issues)} 个问题任务\n")

PYEOF

echo ""
echo "=== 检查完成 ==="
