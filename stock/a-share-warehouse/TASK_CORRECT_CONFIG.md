# A股数据仓库定时任务 - 正确配置记录
# 记录时间：2026-02-26
# 用途：明天执行时参考，避免犯错

---

## 任务1：个股数据抓取 - 16:05

### 配置
- **时间**：16:05（交易日 1-5）
- **脚本**：`sync_stock_from_mysql_v2.py`
- **数据源**：MySQL (82.156.239.131:3306)

### 执行逻辑
1. 判断今天是否为交易日（使用trading_calendar表）
2. 连接MySQL数据库
3. 检查MySQL是否有今天数据
4. 同步数据到SQLite
5. 输出结果

### 推送方式
- 飞书群：无
- 个人：OpenClaw捕获控制台输出自动推送

### 输出格式
**成功时：**
```
✅ 个股数据抓取-16:05 执行成功 - 2026-02-26

同步结果:
- 今天(2026-02-26): X条 ✅
- 昨天(2026-02-25): Y条

说明: 数据同步完成，今天数据已更新。（可能有停牌或退市的股票）
```

**无数据时：**
```
⚠️ 个股数据抓取-16:05 执行完成 - 2026-02-26

状态: 数据源暂无今天数据
MySQL最新数据日期: 2026-02-25
今天(2026-02-26)数据条数: 0

说明: 数据源尚未更新今天数据，请稍后重试或检查数据源更新机制。
```

**非交易日：**
```
⏭️ 个股数据抓取-16:05 跳过执行 - 2026-02-26

原因: 今天是非交易日（周末/节假日）
```

### 关键代码
```python
# 交易日判断
from trading_date import is_trading_date
if not is_trading_date(today):
    print("⏭️ 跳过执行，今天是非交易日")
    return 0

# 检查MySQL是否有今天数据
cursor.execute('SELECT COUNT(*) FROM stock_history WHERE trade_date = %s', (today,))
mysql_today_count = cursor.fetchone()[0]

if mysql_today_count == 0:
    print("⚠️ 数据源暂无今天数据")
    return 0
```

---

## 任务2：MA50占比计算 - 16:10

### 配置
- **时间**：16:10（交易日 1-5）
- **脚本**：`calculate_ma50_ratio.py`
- **依赖**：个股数据抓取-16:05（必须先执行）

### 执行逻辑
1. 检查今天是否有MA50数据
2. **如果没有，先计算今天的MA50**（基于stock_kline表）
3. 生成趋势图
4. 发送文字+图片到飞书群
5. 输出结果到控制台

### 推送方式
- **飞书群**：脚本调用`send-to-feishu-group.py`发送文字+图片
- **个人**：OpenClaw捕获控制台输出自动推送

### 输出格式
```
✅ MA50占比计算 - 16:10 执行成功 - 2026-02-26

📊 统计结果
━━━━━━━━━━━━━━━━━━━━━
总股票数: X只
MA50上方: Y只 (Z%) 🟢
MA50下方: W只 (V%) 🔴
━━━━━━━━━━━━━━━━━━━━━

📈 趋势对比
昨天: XX%
今天: YY%
变化: +ZZ%
```

### 关键代码
```python
# 检查今天是否有MA50数据，如果没有则计算
cursor.execute('SELECT COUNT(*) FROM stock_ma50 WHERE date = ?', (today,))
if cursor.fetchone()[0] == 0:
    # 计算今天的MA50
    for code in codes:
        df = pd.read_sql_query(f'''
            SELECT date, close FROM stock_kline 
            WHERE code = '{code}' ORDER BY date DESC LIMIT 50
        ''', conn)
        
        if len(df) >= 50:
            df['ma50'] = df['close'].rolling(window=50).mean()
            # 插入stock_ma50表

# 发送飞书群消息（文字+图片）
subprocess.run([
    'python3', '/root/.openclaw/workspace/send-to-feishu-group.py', 
    'both', group_message, image_path
])
```

---

## 执行顺序

| 时间 | 任务 | 说明 |
|------|------|------|
| 16:05 | 个股数据抓取 | 先同步今天数据 |
| 16:10 | MA50占比计算 | 基于今天数据计算MA50 |

---

## 如果明天犯错

**检查清单：**
1. 个股数据是否同步成功？
2. MA50是否计算的是今天数据？
3. 飞书群是否收到文字+图片？
4. 个人是否收到推送？

**常见错误：**
- MA50计算的是昨天数据 → 检查是否先计算今天MA50
- 飞书群没收到图片 → 检查send-to-feishu-group.py调用
- 数据源无今天数据 → 检查MySQL更新状态

---

## 关键文件

- `/root/.openclaw/workspace/stock/a-share-warehouse/scripts/sync_stock_from_mysql_v2.py`
- `/root/.openclaw/workspace/stock/a-share-warehouse/scripts/calculate_ma50_ratio.py`
- `/root/.openclaw/workspace/stock/a-share-warehouse/scripts/trading_date.py`
- `/root/.openclaw/workspace/send-to-feishu-group.py`

---

**明天执行时，先读这个文件，再执行任务。**
