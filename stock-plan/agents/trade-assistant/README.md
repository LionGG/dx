# 交易助手子代理

## 概述

交易助手子代理是专门为处理交易相关任务而创建的AI代理。

**人设**: 严谨、数据驱动、不闲聊
**工作目录**: `/root/.openclaw/workspace/stock-plan`

## 职责

1. **记录交易计划** - 解析语音/文字输入，结构化存储
2. **识别持仓截图** - OCR提取持仓数据
3. **对比计划与执行** - 生成偏差分析报告
4. **分析交易模式** - 统计胜率，识别重复偏差

## 文件结构

```
agents/trade-assistant/
├── subagent_config.md   # 本文件 - 子代理配置
├── persona.md           # 人设定义
├── schema.sql           # 数据库结构
├── core.py              # 核心功能模块
├── cli.py               # 命令行接口
├── parser.py            # 交易计划解析器
├── save_plan.py         # 计划存储脚本
└── trade_notes.db       # SQLite数据库
```

## 使用方式

### 记录交易计划
```python
from agents.trade_assistant.core import get_assistant
from agents.trade_assistant.parser import TradePlanParser

parser = TradePlanParser()
plan_data = parser.parse("北方华创突破500就进，2成仓")

assistant = get_assistant()
plan_id = assistant.save_plan(plan_data)
```

### CLI命令
```bash
cd /root/.openclaw/workspace/stock-plan/agents/trade-assistant

# 记录计划
python3 cli.py record_plan "北方华创突破500就进，2成仓"

# 列出今日计划
python3 cli.py list_plans

# 对比计划与执行
python3 cli.py compare

# 分析交易模式
python3 cli.py analyze 30

# 生成日报
python3 cli.py daily_summary

# 保存复盘
python3 cli.py save_review "今天冲动交易了" anxious plan_xxx
```

## 数据库表

- **trade_plans**: 交易计划
- **position_screenshots**: 持仓截图
- **trade_executions**: 执行记录
- **trade_reviews**: 复盘记录
- **daily_summaries**: 每日汇总

## 输出格式

### 计划确认
```
━━━━━━━━━━━━━━━━━━━━
✓ 交易计划已记录

标的: 北方华创 (002371.SZ)
操作: buy
条件: 突破 500.0
仓位: 20%
止损: 480.0

状态: active
━━━━━━━━━━━━━━━━━━━━
```

### 持仓对比
```
━━━━━━━━━━━━━━━━━━━━
✓ 持仓识别完成

当前持仓:
| 标的 | 市值 | 盈亏 |
|------|------|------|
| 中国中免 | 378万 | +90.5万 |

计划对比:
| 计划 | 实际 | 偏差 |
|------|------|------|
| 买入东财 | 未执行 | 遗漏 |

偏差: 1处需说明
━━━━━━━━━━━━━━━━━━━━
```

## 集成方式

主代理可通过以下方式调用交易助手:

1. **直接导入**: `from agents.trade_assistant.core import get_assistant`
2. **CLI调用**: `python3 cli.py <command>`
3. **子代理会话**: 创建独立会话处理交易任务

## 状态

✅ 数据库结构 - 完成
✅ 计划解析器 - 完成
✅ 核心功能模块 - 完成
✅ CLI接口 - 完成
⏳ 持仓截图OCR - 待实现
⏳ 飞书机器人集成 - 待配置
