# AKShare 数据下载 API 参考文档

本文档记录所有成功下载的数据源及其API参数，用于每日增量更新。

---

## 1. 个股K线数据

### API
```python
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260101", end_date="20260213", adjust="")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 股票代码，格式：6位数字，如 "000001" |
| `period` | str | 周期，可选："daily", "weekly", "monthly" |
| `start_date` | str | 开始日期，格式：YYYYMMDD |
| `end_date` | str | 结束日期，格式：YYYYMMDD |
| `adjust` | str | 复权类型，""=不复权，"qfq"=前复权，"hfq"=后复权 |

### 返回字段
日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率

### 数据库表
`stock_kline`

---

## 2. 指数K线数据

### API
```python
ak.stock_zh_index_daily(symbol="sh000001")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 指数代码，格式：市场前缀+代码，如 "sh000001" |

### 常用指数代码
| 指数名称 | 代码 |
|---------|------|
| 上证指数 | sh000001 |
| 上证50 | sh000016 |
| 沪深300 | sh000300 |
| 中证500 | sh000905 |
| 中证1000 | sh000852 |
| 深证成指 | sz399001 |
| 创业板指 | sz399006 |
| 创业板50 | sz399673 |
| 科创50 | sh000688 |

### 返回字段
日期、开盘、收盘、最高、最低、成交量、成交额

### 注意
- 涨跌幅和振幅需要手动计算
- 返回数据包含历史全部数据，需要按日期筛选

### 数据库表
`index_kline`

---

## 3. 板块K线数据

### 3.1 概念板块
```python
ak.stock_board_concept_hist_em(symbol="人工智能", period="daily", start_date="20260101", end_date="20260213", adjust="")
```

### 3.2 行业板块
```python
ak.stock_board_industry_hist_em(symbol="半导体", period="日k", start_date="20260101", end_date="20260213", adjust="")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 板块名称（不是代码！） |
| `period` | str | 概念板块用 "daily"，行业板块用 "日k" |
| `start_date` | str | 开始日期，格式：YYYYMMDD |
| `end_date` | str | 结束日期，格式：YYYYMMDD |

### 重要提示
- **概念板块** period 参数用英文 `"daily"`
- **行业板块** period 参数用中文 `"日k"`（小写k）
- `symbol` 是板块名称，不是代码！

### 返回字段
日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率

### 数据库表
`sector_kline`

---

## 4. 板块成分股数据

### 4.1 概念板块成分股
```python
ak.stock_board_concept_cons_em(symbol="人工智能")
```

### 4.2 行业板块成分股
```python
ak.stock_board_industry_cons_em(symbol="半导体")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 板块名称（不是代码！） |

### 返回字段
代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、振幅、最高、最低、今开、昨收、量比、换手率、市盈率-动态、市净率

### 数据库表
`sector_stocks`

---

## 5. 板块资金流向数据

### 5.1 概念板块资金流向
```python
ak.stock_concept_fund_flow_hist(symbol="人工智能")
```

### 5.2 行业板块资金流向
```python
ak.stock_sector_fund_flow_hist(symbol="半导体")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 板块名称（不是代码！） |

### 返回字段
日期、主力净流入-净额、主力净流入-净占比、超大单净流入-净额、超大单净流入-净占比、大单净流入-净额、大单净流入-净占比、中单净流入-净额、中单净流入-净占比、小单净流入-净额、小单净流入-净占比

### 数据库表
`sector_fund_flow`

### 注意
- 部分细分行业板块可能不支持此API
- 返回约120个交易日数据，需要按日期筛选

---

## 6. 涨停板生态数据

### 6.1 涨停池
```python
ak.stock_zt_pool_em(date="20260213")
```

### 6.2 跌停池
```python
ak.stock_zt_pool_dtgc_em(date="20260213")
```

### 6.3 炸板池
```python
ak.stock_zt_pool_zbgc_em(date="20260213")
```

### 6.4 强势股池
```python
ak.stock_zt_pool_strong_em(date="20260213")
```

### 6.5 次新股池
```python
ak.stock_zt_pool_sub_new_em(date="20260213")
```

### 6.6 昨日涨停池
```python
ak.stock_zt_pool_previous_em(date="20260213")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `date` | str | 日期，格式：YYYYMMDD |

### 返回字段（涨停池示例）
代码、名称、涨跌幅、最新价、成交额、流通市值、总市值、换手率、封板资金、首次封板时间、最后封板时间、炸板次数、涨停统计、连板数、所属行业

### 数据库表
- `zt_pool` - 涨停池
- `dt_pool` - 跌停池
- `zbgc_pool` - 炸板池
- `strong_pool` - 强势股池

### 重要限制
- **API只提供最近14天数据**，无法获取更早历史数据
- 节假日无数据

---

## 7. 龙虎榜数据

### 7.1 龙虎榜每日详情
```python
ak.stock_lhb_detail_daily_sina(date="20260213")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `date` | str | 日期，格式：YYYYMMDD |

### 返回字段
股票代码、股票名称、收盘价、对应值、成交量、成交额、指标（上榜原因）

### 数据库表
`lhb_daily`

### 注意
- 一只股票一天可能有多个上榜原因（主键：date+code+indicator）
- 可回溯约30天数据

---

## 8. 板块资金流向排名

### API
```python
ak.stock_sector_fund_flow_rank()
```

### 返回字段
序号、名称、今日涨跌幅、今日主力净流入-净额、今日主力净流入-净占比、今日超大单净流入-净额、今日超大单净流入-净占比、今日大单净流入-净额、今日大单净流入-净占比、今日中单净流入-净额、今日中单净流入-净占比、今日小单净流入-净额、今日小单净流入-净占比、今日主力净流入最大股

### 数据库表
`sector_fund_flow_rank`

---

## 9. 个股资金流向

### API
```python
ak.stock_individual_fund_flow(stock="000001", market="sh")
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| `stock` | str | 股票代码（6位数字） |
| `market` | str | 市场："sh"=上海，"sz"=深圳，"bj"=北京 |

### 返回字段
日期、收盘价、涨跌幅、主力净流入-净额、主力净流入-净占比、超大单净流入-净额、超大单净流入-净占比、大单净流入-净额、大单净流入-净占比、中单净流入-净额、中单净流入-净占比、小单净流入-净额、小单净流入-净占比

### 注意
- 返回约120个交易日数据
- 参数是 `stock` 和 `market`，不是 `symbol`

---

## 10. 每日增量更新脚本

### 更新逻辑
1. **K线数据**：使用 `start_date` 和 `end_date` 参数下载当日数据
2. **涨停板生态**：下载当日数据（date=YYYYMMDD）
3. **龙虎榜**：下载当日数据（date=YYYYMMDD）
4. **资金流向**：下载全部历史，筛选当日数据插入

### 代码格式标准
- **股票代码**：必须格式化为6位数字，不足补前导零
  - ✅ 正确：`000001`, `001896`
  - ❌ 错误：`1`, `1896`

### 增量更新示例
```python
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
today_dash = datetime.now().strftime('%Y-%m-%d')

# 个股K线增量
df = ak.stock_zh_a_hist(symbol="000001", period="daily", 
                        start_date=today, end_date=today)

# 涨停板生态增量
df = ak.stock_zt_pool_em(date=today)

# 龙虎榜增量
df = ak.stock_lhb_detail_daily_sina(date=today)
```

---

## 附录：数据库表结构

### stock_kline
```sql
CREATE TABLE stock_kline (
    date TEXT, code TEXT, name TEXT,
    open REAL, close REAL, high REAL, low REAL,
    volume REAL, amount REAL, amplitude REAL,
    change_pct REAL, change_amount REAL, turnover REAL,
    PRIMARY KEY (date, code)
);
```

### index_kline
```sql
CREATE TABLE index_kline (
    date TEXT, code TEXT, name TEXT,
    open REAL, close REAL, high REAL, low REAL,
    volume REAL, amount REAL, amplitude REAL,
    change_pct REAL, change_amount REAL, turnover REAL,
    PRIMARY KEY (date, code)
);
```

### sector_kline
```sql
CREATE TABLE sector_kline (
    date TEXT, code TEXT, name TEXT, sector_type TEXT,
    open REAL, close REAL, high REAL, low REAL,
    volume REAL, amount REAL, amplitude REAL,
    change_pct REAL, change_amount REAL, turnover REAL,
    PRIMARY KEY (date, code)
);
```

### sector_stocks
```sql
CREATE TABLE sector_stocks (
    sector_code TEXT, sector_name TEXT, sector_type TEXT,
    stock_code TEXT, stock_name TEXT,
    close REAL, change_pct REAL, volume REAL, amount REAL,
    turnover REAL, pe_ratio REAL, pb_ratio REAL,
    PRIMARY KEY (sector_code, stock_code)
);
```

### sector_fund_flow
```sql
CREATE TABLE sector_fund_flow (
    date TEXT, sector_code TEXT, sector_name TEXT, sector_type TEXT,
    main_net_inflow REAL, main_net_inflow_pct REAL,
    super_large_net_inflow REAL, super_large_net_inflow_pct REAL,
    large_net_inflow REAL, large_net_inflow_pct REAL,
    medium_net_inflow REAL, medium_net_inflow_pct REAL,
    small_net_inflow REAL, small_net_inflow_pct REAL,
    PRIMARY KEY (date, sector_code)
);
```

### zt_pool / dt_pool / zbgc_pool / strong_pool
```sql
-- 各表结构详见 download_limit_up_ecology.py
```

### lhb_daily
```sql
CREATE TABLE lhb_daily (
    date TEXT, code TEXT, name TEXT,
    close REAL, indicator_value REAL,
    volume REAL, amount REAL, indicator TEXT,
    PRIMARY KEY (date, code, indicator)
);
```

---

**文档版本**: 2026-02-23  
**AKShare版本**: 1.16.30  
**数据范围**: 2026-01-05 至 2026-02-13
