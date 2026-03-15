# Portfolio Image Parser Skill

自动解析股票持仓截图，提取结构化数据并存入数据库。

## 功能

1. 接收持仓截图（图片路径）
2. 使用 AI 视觉解析图片中的持仓数据
3. 提取结构化信息（总资产、个股、仓位、盈亏等）
4. 存入 SQLite 数据库
5. 对比昨日生成变化报告

## 使用方法

```python
from portfolio_parser import parse_portfolio_image

# 解析持仓图片
result = parse_portfolio_image(
    image_path='/path/to/screenshot.jpg',
    account_id='A',  # A/B/C
    trade_date='2026-03-10'
)

# 返回解析结果
print(result)
```

## 数据结构

解析后的数据结构：
```json
{
  "account_id": "A",
  "trade_date": "2026-03-10",
  "total_assets": 20070000.00,
  "total_profit": 122000.00,
  "holding_profit": -1620000.00,
  "debt": 7340000.00,
  "guarantee_ratio": 273.51,
  "holdings": [
    {
      "stock_code": "300059",
      "stock_name": "东方财富",
      "position_pct": 32.0,
      "market_value": 6490000,
      "float_profit": -417000
    }
  ]
}
```

## 依赖

- Python 3.8+
- sqlite3
- 无需外部 OCR 库（使用 AI 视觉能力）

## 数据库表结构

使用 stock-plan/data/portfolio.db 数据库：
- portfolio_snapshots: 持仓快照
- stock_holdings: 个股持仓明细
