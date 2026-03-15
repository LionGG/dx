# WAL Details Log
# Proactive Agent - Write-Ahead Logging

---

## 2026-03-06 - market_sentiment表结构

**Detail:** 字段索引映射
- [0] date
- [1] sentiment_index（情绪指数）
- [2] limit_up（涨停数）
- [3] limit_down（跌停数）
- [5] volume（成交额）
- [6] consecutive_height（连板高度）
- [7] up_count（上涨家数）
- [8] down_count（下跌家数）
- [9] seal_rate（封板率）

**Source:** PRAGMA table_info(market_sentiment)

---

## 2026-03-06 - 定时任务正确配置

**Detail:** 必须参数
```bash
openclaw cron add \
  --name "任务名" \
  --cron "0 22 * * *" \
  --tz "Asia/Shanghai" \
  --system-event "任务说明" \
  --session main \
  --agent main  # 必须加！
```

**Reference:** TASK_ADD_GUIDE.md

---

## 2026-03-06 - Claw Hub平台状态

**Detail:** 
- URL: https://clawhub.com
- 已安装Skill数: 12个
- 平台热门列表: 空（No skills yet）
- 状态: 平台较新，暂无使用统计数据

**已安装列表:**
- proactive-agent 3.1.0
- self-improving-agent 1.0.11
- memory-setup 1.0.0
- automation-workflows 0.1.0
- browse 2.0.2
- desearch-web-search 1.0.1
- ai-web-automation 1.0.0
- web-pilot 1.0.0
- web 1.0.0
- web-claude 1.1.0
- mupeng-web-claude 1.0.0
- status-web 1.0.0

---

## 2026-03-06 - 短线情绪研判定时任务

**Detail:** 已设置的任务
- MA50占比计算: 16:10
- 数据抓取: 16:20
- 短线情绪研判: 16:25
- 部署通知: 16:30
- 交易截图提醒: 19:00
- ClawHub搜索: 22:00
- 趋势分样本: 09:00（明天）

---

## 2026-03-06 - Proactive Agent配置路径

**Detail:** 文件位置
- Skill文档: ~/.openclaw/workspace/skills/proactive-agent/SKILL.md
- WAL目录: ~/.openclaw/workspace/.wal/
- Working Buffer: ~/.openclaw/workspace/memory/working-buffer.md
- Session State: ~/.openclaw/workspace/SESSION-STATE.md
