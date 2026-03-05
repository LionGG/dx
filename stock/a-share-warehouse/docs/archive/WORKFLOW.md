# A-Share Warehouse 工作流程文档

## 1. 个股数据导入流程

### 1.1 从 MySQL 导入到 SQLite

**连接信息**：
- 主机: 82.156.239.131
- 端口: 3306
- 用户名: root
- 密码: 1q2w#E$R
- 数据库: choose_stock

**表结构**：
- MySQL: `stock_history` (trade_date, stock_code, open_price, close_price, high_price, low_price, volume, amount, amplitude, pct_chg, price_chg, turnover_rate)
- SQLite: `stock_kline` (date, code, open, close, high, low, volume, amount, amplitude, change_pct, change_amount, turnover)

**导入方法**（按股票+月份分批）：
```python
import pymysql
import sqlite3

# 连接
mysql_conn = pymysql.connect(host='82.156.239.131', port=3306, user='root', password='1q2w#E$R', database='choose_stock')
sqlite_conn = sqlite3.connect('data/akshare_full.db')

# 获取SQLite中已有股票代码
codes = [row[0] for row in sqlite_conn.execute("SELECT DISTINCT code FROM stock_kline")]

# 逐只导入（按月份分批）
for code in codes:
    for month in ['2025-06', '2025-07', '2025-08', '2025-09']:
        # 查询MySQL
        cursor.execute(f"SELECT * FROM stock_history WHERE stock_code='{code}' AND trade_date LIKE '{month}%'")
        rows = cursor.fetchall()
        # 插入SQLite
        for row in rows:
            converted = [row[0], row[1]] + [float(v) if v is not None else None for v in row[2:]]
            sqlite_conn.execute('INSERT OR IGNORE INTO stock_kline VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', converted)
```

**关键经验**：
- 按股票+月份分批，避免一次性查询大量数据
- 使用 `INSERT OR IGNORE` 避免重复数据报错
- Decimal类型需要转换为float

---

## 2. MA50计算与存储

### 2.1 创建MA50表
```sql
CREATE TABLE IF NOT EXISTS stock_ma50 (
    date TEXT,
    code TEXT,
    close REAL,
    ma50 REAL,
    deviation REAL,
    PRIMARY KEY (date, code)
);
```

### 2.2 计算并存储MA50
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/akshare_full.db')

# 获取所有股票代码
codes = pd.read_sql_query("SELECT DISTINCT code FROM stock_kline WHERE date >= '2025-09-01'", conn)['code'].tolist()

for code in codes:
    # 获取该股票数据（至少50天历史）
    df = pd.read_sql_query(f"SELECT date, close FROM stock_kline WHERE code='{code}' AND date >= '2025-09-01' ORDER BY date", conn)
    
    if len(df) >= 50:
        df['ma50'] = df['close'].rolling(window=50).mean()
        df['deviation'] = (df['close'] - df['ma50']) / df['ma50'] * 100
        
        # 筛选2026年以来的数据
        df_2026 = df[df['date'] >= '2026-01-01'].dropna()
        
        # 插入数据库
        for _, row in df_2026.iterrows():
            cursor.execute('INSERT INTO stock_ma50 VALUES (?,?,?,?,?)', 
                          (row['date'], code, row['close'], row['ma50'], row['deviation']))
```

**关键经验**：
- 需要至少50天历史数据才能计算MA50
- 使用pandas的rolling函数计算均线
- 偏离度 = (收盘价 - MA50) / MA50 * 100

---

## 3. MA50占比统计

### 3.1 单日统计
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN deviation >= 0 THEN 1 ELSE 0 END) as above,
    AVG(deviation) as avg_dev
FROM stock_ma50 
WHERE date = '2026-02-24'
```

### 3.2 多日趋势统计
```sql
SELECT 
    date,
    COUNT(*) as total,
    SUM(CASE WHEN deviation >= 0 THEN 1 ELSE 0 END) as above,
    AVG(deviation) as avg_dev
FROM stock_ma50 
WHERE date >= '2026-01-01'
GROUP BY date
ORDER BY date
```

---

## 4. 数据可视化

### 4.1 生成趋势图
```python
import matplotlib.pyplot as plt

# 获取数据
df = pd.read_sql_query("SELECT date, COUNT(*) as total, SUM(CASE WHEN deviation >= 0 THEN 1 ELSE 0 END) as above FROM stock_ma50 WHERE date >= '2026-01-01' GROUP BY date", conn)
df['ratio'] = df['above'] / df['total'] * 100

# 使用序号作为x轴（跳过非交易日）
x = range(len(df))

plt.figure(figsize=(14, 6))
plt.plot(x, df['ratio'], marker='o', linewidth=2, color='#2E86AB')
plt.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Line')

# 只显示部分日期标签
step = max(1, len(df) // 10)
plt.xticks(x[::step], df['date'].iloc[::step], rotation=45)

plt.title('Stock Price Above MA50 Ratio Trend', fontsize=14)
plt.xlabel('Trading Day')
plt.ylabel('Ratio (%)')
plt.ylim(40, 90)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('ma50_ratio_trend.png', dpi=150)
```

**关键经验**：
- 横轴使用序号而非日期，跳过周末节假日
- 只显示部分日期标签避免拥挤
- 添加50%参考线作为多空分界

### 4.2 发送图片到飞书
```python
# 确保飞书机器人有 im:file:send 权限
message.send(filePath='ma50_ratio_trend.png', caption='图表说明')
```

---

## 5. 数据库索引优化

```sql
-- 给常用查询字段加索引
CREATE INDEX idx_stock_code ON stock_kline(code);
CREATE INDEX idx_stock_date ON stock_kline(date);
CREATE INDEX idx_stock_code_date ON stock_kline(code, date);
```

---

## 6. 当前数据状态

| 时间段 | 记录数 | 状态 |
|--------|--------|------|
| 2025年1-5月 | 470,000 | ✅ 已导入 |
| 2025年6-9月 | 0 | ❌ 待导入 |
| 2025年10-12月 | 309,272 | ✅ 已导入 |
| 2026年 | 已有 | ✅ 已导入 |
| **总计** | **约78万条** | |

**MA50数据**：159,686条（2026年以来）
