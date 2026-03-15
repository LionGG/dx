# Portfolio Parser Skill

## 用途

自动解析股票持仓截图，提取结构化数据并存入数据库，支持对比分析。

## 安装

```bash
# 该Skill无需额外安装，直接可用
# 依赖：sqlite3（Python内置）
```

## 使用方法

### Python API

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/portfolio-parser/scripts')

from portfolio_parser import save_to_database, generate_report

# 解析后的数据结构
data = {
    'account_id': 'A',
    'trade_date': '2026-03-10',
    'total_assets': 20070000.00,
    'total_profit': 122000.00,
    'holding_profit': -1620000.00,
    'debt': 7340000.00,
    'guarantee_ratio': 273.51,
    'holdings': [
        {
            'stock_code': '300059',
            'stock_name': '东方财富',
            'position_pct': 32.0,
            'market_value': 6490000,
            'float_profit': -417000
        }
    ]
}

# 保存到数据库
save_to_database(data)

# 生成对比报告
report = generate_report('A', '2026-03-10')
print(report)
```

### 命令行

```bash
cd /root/.openclaw/workspace/skills/portfolio-parser

# 生成报告
python3 scripts/cli.py /path/to/screenshot.jpg --account A --date 2026-03-10 --report
```

## 核心功能

### 1. 数据提取
- `extract_account_info()`: 提取账户总体信息
- `extract_holdings()`: 提取个股持仓明细

### 2. 数据存储
- `save_to_database()`: 保存到SQLite数据库

### 3. 对比分析
- `compare_with_yesterday()`: 与昨日持仓对比
- `generate_report()`: 生成变化报告

## 数据库

使用 `/root/.openclaw/workspace/stock-plan/data/portfolio.db`

表结构：
- `portfolio_snapshots`: 持仓快照
- `stock_holdings`: 个股持仓明细

## 注意事项

1. 图片解析依赖AI视觉能力，需要AI读取图片内容
2. 数据提取后会自动进行正则匹配和结构化
3. 建议每日收盘后使用，保持数据连续性

## 更新日志

### v1.0.0 (2026-03-10)
- 初始版本
- 支持持仓图片解析框架
- 支持数据库存储
- 支持对比报告生成
