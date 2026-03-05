#!/bin/bash
# 美股收盘推送 - 每天7:40执行
# 获取昨晚美股收盘数据并推送到飞书

cd /root/.openclaw/workspace

# 使用OpenClaw的定时任务机制触发agent执行
# 配置在cron-jobs.json中

echo "美股推送任务触发: $(date)"
