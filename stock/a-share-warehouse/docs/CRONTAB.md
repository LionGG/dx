# 定时任务配置

## Crontab 配置

编辑 crontab：
```bash
crontab -e
```

添加以下行：

```cron
# AKShare 每日数据更新 - 15:45 基础数据（指数、板块、个股、涨停板生态）
45 15 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1545.sh

# AKShare 每日数据更新 - 18:00 资金流向与龙虎榜
0 18 * * 1-5 /root/.openclaw/workspace/stock/a-share-warehouse/scripts/cron_1800.sh
```

## 说明

| 时间 | 内容 | 脚本 |
|------|------|------|
| 15:45 | 指数、板块、个股K线、涨停板生态 | `scripts/cron_1545.sh` |
| 18:00 | 资金流向、龙虎榜 | `scripts/cron_1800.sh` |

## 工作日限制

- `1-5` 表示周一到周五（交易日）
- 周末和节假日不会执行

## 手动执行

```bash
cd /root/.openclaw/workspace/stock/a-share-warehouse

# 15:45 批次
python3 scripts/daily_update_v2.py 1545

# 18:00 批次
python3 scripts/daily_update_v2.py 1800
```

## 日志查看

```bash
# 查看最新日志
tail -f logs/daily_update_$(date +%Y%m%d).log

# 查看所有日志
ls -la logs/
```

## 交易日判断

使用 `scripts/trading_date.py` 判断是否为交易日：

```python
from scripts.trading_date import is_trading_date, get_today_trading_date

# 判断某天是否为交易日
is_trading_date('2026-02-13')  # True
is_trading_date('2026-02-14')  # False (周六)

# 获取今天对应的交易日（周末返回最近交易日）
get_today_trading_date()  # '2026-02-13'
```
