---
name: a-share-dx
description: A股短线情绪数据服务。从短线侠API抓取市场情绪数据，生成可视化网页并部署到GitHub Pages。触发词：a股短线情绪、短线侠数据、情绪走势图。
---

# A股短线情绪

## 功能

抓取13项指标 → 生成网页 → 部署GitHub Pages

## 指标

情绪、涨停/跌停、上涨/下跌、量能、大幅回撤、连板高度、封板率、涨停/连板表现、连板晋级率

## 使用

```bash
# 完整流程
python3 /root/.openclaw/workspace/skills/a-share-dx/scripts/auto_update.py

# 单独步骤
python3 /root/.openclaw/workspace/skills/a-share-dx/scripts/crawler.py          # 抓取
python3 /root/.openclaw/workspace/skills/a-share-dx/scripts/generate_html.py    # 生成网页
/root/.openclaw/workspace/skills/a-share-dx/scripts/deploy.sh                   # 部署
```

## 定时任务

每个交易日15:01自动执行（任务ID: 9d7ced29-c010-4289-b4a9-b0db174104b1）

## 配置

- 数据库：`/root/.openclaw/workspace/duanxianxia_data.db`
- 网站：https://liongg.github.io/dx/
