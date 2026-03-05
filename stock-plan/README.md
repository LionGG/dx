# Stock Plan 项目

## 项目概述
AI驱动的交易笔记与复盘系统

## 目录结构

```
stock-plan/
├── agents/              # Agent配置
│   └── trade-assistant/ # 交易助手Agent
│       ├── persona.md   # 人设定义
│       ├── schema.sql   # 数据库结构
│       ├── parser.py    # 交易计划解析
│       ├── save_plan.py # 计划存储
│       └── trade_notes.db # SQLite数据库
├── skills/              # 技能模块
├── memory/              # 记忆/用户档案
│   └── user_profile.md  # Billy哥持仓档案
├── docs/                # 文档
├── scripts/             # 脚本工具
└── data/                # 数据文件
```

## 核心功能

1. **交易计划记录** - 语音/文字输入，结构化存储
2. **持仓截图识别** - OCR提取，自动对比
3. **执行复盘分析** - 计划vs实际，偏差分析
4. **交易风格画像** - 长期积累，模式识别

## 使用方式

通过飞书机器人"交易助手"交互：
- 语音说交易计划
- 发送持仓截图
- 文字复盘总结

## 状态

开发中，等待飞书机器人配置完成
