#!/bin/bash
# 每周自动复盘脚本
# 执行时间: 每周日 03:30 (Gateway重启后)

LOG_FILE="/root/.openclaw/logs/weekly_review.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
WEEK_START=$(date -d '7 days ago' '+%Y-%m-%d')

echo "========== 每周复盘报告 - $DATE ==========" > $LOG_FILE
echo "统计周期: $WEEK_START 至 $(date '+%Y-%m-%d')" >> $LOG_FILE
echo "" >> $LOG_FILE

# 1. 任务执行情况
echo "📊 一、任务执行情况" >> $LOG_FILE
echo "-------------------" >> $LOG_FILE

# 检查定时任务状态
echo "定时任务状态:" >> $LOG_FILE
openclaw cron list 2>&1 | grep -E "(ok|failed|error)" >> $LOG_FILE || echo "  无法获取状态" >> $LOG_FILE

echo "" >> $LOG_FILE

# 2. 用户反馈统计
echo "⭐ 二、用户反馈统计" >> $LOG_FILE
echo "-------------------" >> $LOG_FILE

if [ -f "/root/.openclaw/workspace/memory/task_feedback.json" ]; then
    python3 << 'EOF' >> $LOG_FILE
import json
with open('/root/.openclaw/workspace/memory/task_feedback.json', 'r') as f:
    data = json.load(f)

if data['stats']:
    total_score = sum(s['total_score'] for s in data['stats'].values())
    total_count = sum(s['count'] for s in data['stats'].values())
    avg = total_score / total_count if total_count > 0 else 0
    print(f"整体评分: {avg:.2f}/5分 (共{total_count}次评价)")
    print()
    print("各任务表现:")
    for task, stats in data['stats'].items():
        bar = '█' * int(stats['avg_score']) + '░' * (5 - int(stats['avg_score']))
        print(f"  {bar} {task}: {stats['avg_score']}/5分")
else:
    print("本周暂无反馈记录")
EOF
else
    echo "暂无反馈记录" >> $LOG_FILE
fi

echo "" >> $LOG_FILE

# 3. 错误分析
echo "⚠️ 三、错误与问题分析" >> $LOG_FILE
echo "-------------------" >> $LOG_FILE

if [ -f "/root/.openclaw/workspace/memory/ERROR_PREVENTION.md" ]; then
    echo "已记录的错误模式:" >> $LOG_FILE
    grep "^###" /root/.openclaw/workspace/memory/ERROR_PREVENTION.md | head -5 | sed 's/### /  - /' >> $LOG_FILE
else
    echo "暂无错误记录" >> $LOG_FILE
fi

echo "" >> $LOG_FILE

# 4. 改进建议
echo "💡 四、改进建议" >> $LOG_FILE
echo "-------------------" >> $LOG_FILE

# 根据反馈生成建议
python3 << 'EOF' >> $LOG_FILE
import json
import os

suggestions = []

# 检查反馈分数
if os.path.exists('/root/.openclaw/workspace/memory/task_feedback.json'):
    with open('/root/.openclaw/workspace/memory/task_feedback.json', 'r') as f:
        data = json.load(f)
    
    for task, stats in data['stats'].items():
        if stats['avg_score'] < 3:
            suggestions.append(f"⚠️ {task} 评分较低({stats['avg_score']}/5)，需要重点改进")
        elif stats['avg_score'] >= 4.5:
            suggestions.append(f"✅ {task} 表现优秀({stats['avg_score']}/5)，保持")

# 检查错误记录
if os.path.exists('/root/.openclaw/workspace/memory/ERROR_PREVENTION.md'):
    with open('/root/.openclaw/workspace/memory/ERROR_PREVENTION.md', 'r') as f:
        content = f.read()
    if 'Gateway' in content:
        suggestions.append("📌 注意: 有Gateway重启相关错误记录，避免频繁重启")

if not suggestions:
    print("本周表现良好，暂无特别建议")
else:
    for s in suggestions:
        print(s)
EOF

echo "" >> $LOG_FILE

# 5. 下周计划
echo "📅 五、下周重点" >> $LOG_FILE
echo "-------------------" >> $LOG_FILE
echo "- 继续监控定时任务执行情况" >> $LOG_FILE
echo "- 根据反馈持续优化" >> $LOG_FILE
echo "- 周日 03:00 Gateway 自动重启" >> $LOG_FILE

echo "" >> $LOG_FILE
echo "========== 复盘结束 ==========" >> $LOG_FILE

# 发送报告（可选）
# cat $LOG_FILE | head -50

echo "✅ 每周复盘完成，报告保存至: $LOG_FILE"
