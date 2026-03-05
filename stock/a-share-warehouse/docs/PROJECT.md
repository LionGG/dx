# A-Share Warehouse A股数据仓库

## 项目目标

建立并维护一个**完整、准确、实时**的A股全量数据库，为量化分析、情绪研判、策略回测提供可靠的数据基础。

### 核心目标
1. **数据完整性** - 覆盖全部A股股票、板块、指数的日线数据
2. **数据准确性** - 与交易所官方数据保持一致，每日核对
3. **实时更新** - 每个交易日自动抓取收盘数据，无遗漏
4. **历史可追溯** - 建立从2026年起完整的全量数据集

### 数据范围
- **个股**: 全部A股（约5500只）的日线K线、基本面数据
- **板块**: 全部行业、概念板块的日线数据及成分股
- **指数**: 主要宽基指数（上证、深证、创业板、科创50等）
- **市场情绪**: 涨停/跌停池、资金流向、龙虎榜等短线数据

---

## 项目概述

基于 AKShare 的 A股全量数据仓库，每日自动更新，为分析和可视化提供数据支持。

**核心数据库**: `data/akshare_full.db` (52MB, 11个表)  
**更新频率**: 每个交易日  
**数据来源**: AKShare  
**数据起始**: 2026-01-05

---

## 数据完整性检查

### 2026年交易日历
- **总交易日**: 约 240 天
- **已下载**: 从 2026-01-05 至 2026-02-13，共 24 个交易日
- **缺失**: 待检查

### 检查方法
```bash
# 检查数据库最新日期
cd /root/.openclaw/workspace/stock/a-share-warehouse
python3 -c "
import sqlite3
db = sqlite3.connect('data/akshare_full.db')
cursor = db.cursor()
cursor.execute('SELECT MAX(date) FROM stock_kline')
print('个股K线最新日期:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(DISTINCT date) FROM stock_kline WHERE date >= \"2026-01-01\"')
print('2026年交易日数:', cursor.fetchone()[0])
db.close()
"
```

---

## 数据库表结构

| 表名 | 说明 | 更新频率 |
|------|------|----------|
| index_kline | 指数K线 | 每日 |
| sector_kline | 板块K线 | 每日 |
| sector_stocks | 板块成分股 | 每日 |
| stock_kline | 个股K线 | 每日 |
| sector_fund_flow | 板块资金流向 | 每日 |
| zt_pool | 涨停池 | 每日 |
| dt_pool | 跌停池 | 每日 |
| zbgc_pool | 炸板股池 | 每日 |
| strong_pool | 强势股池 | 每日 |
| sector_fund_flow_rank | 板块资金流向排名 | 每日 |
| lhb_daily | 龙虎榜 | 每日 |

---

## 定时任务

| 时间 | 内容 | 脚本 |
|------|------|------|
| 15:45 | 指数、板块、个股K线、涨停板生态 | `cron_1545.sh` |
| 18:00 | 资金流向、龙虎榜 | `cron_1800.sh` |

### Crontab 配置

```bash
# 编辑 crontab
crontab -e

# 添加以下行
45 15 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1545.sh
0 18 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1800.sh
```

---

## 项目结构

```
a-share-warehouse/
├── docs/
│   ├── PROJECT.md          # 本文件
│   ├── CRONTAB.md          # 定时任务配置
│   └── AKShare_API_Reference.md
├── scripts/
│   ├── daily_update_v2.py  # 每日更新主脚本
│   ├── trading_date.py     # 交易日判断
│   ├── cron_1545.sh        # 15:45定时脚本
│   └── cron_1800.sh        # 18:00定时脚本
├── data/
│   └── akshare_full.db     # 主数据库
└── web/                    # 可视化（待开发）
```

---

## 手动执行更新

```bash
cd /root/.openclaw/workspace/stock/a-share-warehouse

# 15:45批次
python3 scripts/daily_update_v2.py 1545

# 18:00批次
python3 scripts/daily_update_v2.py 1800
```

---

## 数据最新状态

- **最新日期**: 2026-02-13
- **个股K线**: 5474只股票
- **板块K线**: 964个板块
- **指数K线**: 9个指数
- **2026年已下载交易日**: 24天

---

## 相关项目

- `a-share-dx/` - 短线情绪研判（基于本仓库数据）


| 表名 | 说明 | 更新频率 |
|------|------|----------|
| index_kline | 指数K线 | 每日 |
| sector_kline | 板块K线 | 每日 |
| sector_stocks | 板块成分股 | 每日 |
| stock_kline | 个股K线 | 每日 |
| sector_fund_flow | 板块资金流向 | 每日 |
| zt_pool | 涨停池 | 每日 |
| dt_pool | 跌停池 | 每日 |
| zbgc_pool | 炸板股池 | 每日 |
| strong_pool | 强势股池 | 每日 |
| sector_fund_flow_rank | 板块资金流向排名 | 每日 |
| lhb_daily | 龙虎榜 | 每日 |

---

## 定时任务

| 时间 | 内容 | 脚本 |
|------|------|------|
| 15:45 | 指数、板块、个股K线、涨停板生态 | `cron_1545.sh` |
| 18:00 | 资金流向、龙虎榜 | `cron_1800.sh` |

### Crontab 配置

```bash
# 编辑 crontab
crontab -e

# 添加以下行
45 15 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1545.sh
0 18 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1800.sh
```

---

## 项目结构

```
a-share-warehouse/
├── docs/
│   ├── PROJECT.md          # 本文件
│   ├── CRONTAB.md          # 定时任务配置
│   └── AKShare_API_Reference.md
├── scripts/
│   ├── daily_update_v2.py  # 每日更新主脚本
│   ├── trading_date.py     # 交易日判断
│   ├── cron_1545.sh        # 15:45定时脚本
│   └── cron_1800.sh        # 18:00定时脚本
├── data/
│   └── akshare_full.db     # 主数据库
└── web/                    # 可视化（待开发）
```

---

## 手动执行更新

```bash
cd /root/.openclaw/workspace/stock/a-share-warehouse

# 15:45批次
python3 scripts/daily_update_v2.py 1545

# 18:00批次
python3 scripts/daily_update_v2.py 1800
```

---

## 数据最新状态

- **最新日期**: 2026-02-13
- **个股K线**: 5474只股票
- **板块K线**: 964个板块
- **指数K线**: 9个指数

---

## 相关项目

- `a-share-dx/` - 短线情绪研判（基于本仓库数据）
