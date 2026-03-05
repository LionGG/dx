# 短线情绪研判自动化流程（完整版）

## 执行时间
每日 16:00（北京时间）

---

## 第一步：数据抓取（16:00-16:05）

### 1.1 短线侠情绪数据
**脚本：** `scripts/crawler.py`
**来源：** 短线侠网站
**数据表：** `market_sentiment`
**字段：**
- date（日期）
- sentiment_index（情绪指数）
- limit_up（涨停数）
- limit_down（跌停数）
- major_pullback（大幅回撤数）
- volume（量能，单位：亿）
- consecutive_height（连板高度）
- up_count（上涨家数）
- down_count（下跌家数）
- seal_rate（封板率）
- limit_up_performance（涨停表现）
- consecutive_performance（连板表现）
- consecutive_promotion_rate（连板晋级率）

**特点：** 使用 `INSERT OR REPLACE`，支持重复执行

### 1.2 AKShare指数K线数据
**脚本：** `scripts/fetch_kline_akshare.py`
**来源：** AKShare `stock_zh_index_daily()`
**数据表：** `index_kline`
**指数：**
- 上证指数 (sh000001) → 代码 000001
- 创业板指 (sz399006) → 代码 399006

**字段：**
- date（日期）
- index_code（指数代码）
- index_name（指数名称）
- open/high/low/close（OHLC）
- volume（成交量/股数）
- ma5/ma10/ma50（移动平均线）

**注意：** AKShare指数数据只有成交量，没有成交额

---

## 第二步：AI分析（16:05-16:15）

**输入数据：**
- 当日情绪数据（market_sentiment）
- 当日K线数据（index_kline：上证/创业板收盘、MA5/MA10/MA50）
- 历史情绪指数（近5日，用于演变描述）
- 交易日历（节假日判断）

**输出内容：**
- 周期定位（如：情绪修复期/新周期启动初期）
- 操作方向（关注方向、回避方向）
- 关键信号
- 一句话总结
- 墨问笔记链接

**存储位置：**
- 主表：`market_sentiment.analysis_phase/action/summary/mowen_link`
- 报告表：`daily_reports`（phase/action/summary/mowen_link/full_content）

**注意：** 需要同时更新两个表，确保HTML生成时能读取到

---

## 第三步：生成HTML（16:15-16:20）

**脚本：** `scripts/generate_html.py`

### 数据读取

**1. 情绪数据（marketData）**
```sql
SELECT * FROM market_sentiment ORDER BY date DESC LIMIT 30
```
- 结果：倒序排列（最新日期在前）
- 用途：情绪指数图表、数据表格

**2. 分析报告（dailyReports）**
```sql
SELECT * FROM daily_reports ORDER BY date DESC LIMIT 30
```
- 结果：倒序排列
- 用途：情绪研判卡片

**3. K线数据（klineData）**
```sql
SELECT * FROM index_kline 
WHERE index_code IN ('000001', '399006')
ORDER BY date DESC LIMIT 60
```
- 结果：每个指数60天数据
- 用途：K线图

### 数据更新逻辑

| 变量 | 更新方式 | 说明 |
|------|---------|------|
| marketData | 新数据插在最前面 | 倒序排列 |
| dailyReports | 从daily_reports表读取 | 所有报告 |
| reportDates | 从marketData提取日期 | 倒序排列 |
| currentReportIndex | 设为0 | 指向最新日期 |
| klineData | 上证+创业板各60天 | 正序排列（K线图需要） |

### HTML结构（当前）

```
第一行：
  - 左侧：短线情绪图表（情绪指数折线图）
  - 右侧：情绪研判卡片
    - 日期切换器（‹ 日期 ›）
    - 情绪研判（标题）
    - 周期定位
    - 操作方向
    - 一句话总结
    - 查看完整内容链接

第二行：
  - 左侧：指数K线图（含成交量子图）
    - 指数选择器（上证/创业板）
  - 右侧：数据详情卡片
    - 上证指数数据
    - 创业板指数据
    - 情绪数据

第三行（已隐藏）：
  - 中期趋势图表（原MA50+强势股，已隐藏）
  - 板块分析卡片（已隐藏）

底部：
  - 历史数据明细表格（可展开）
```

### 日期切换器逻辑

**数组顺序：** reportDates = ["2026-02-24", "2026-02-13", "2026-02-12", ...]
- 索引0 = 最新日期（2月24日）
- 索引1 = 2月13日
- 索引2 = 2月12日
...

**按钮功能：**
- 左箭头 ‹ → 看更早日期 → 索引+1
- 右箭头 › → 看更新日期 → 索引-1

**边界处理：**
- 左箭头禁用：索引 = 数组长度-1（最旧日期）
- 右箭头禁用：索引 = 0（最新日期）

**无报告处理：**
- 周期定位、操作方向、总结 = 空字符串
- 查看链接隐藏

---

## 第四步：部署（16:20-16:25）

**步骤：**
1. 压缩HTML（可选）
2. 提交GitHub
3. 推送到GitHub Pages

**验证：**
- 网页可正常访问
- 最新日期显示正确
- 日期切换器正常工作
- 图表渲染正常

---

## 关键检查清单

### 数据抓取后
- [ ] market_sentiment 有当日记录
- [ ] index_kline 有当日K线（2个指数）
- [ ] K线数据包含MA5/MA10/MA50

### AI分析后
- [ ] market_sentiment 分析字段已更新
- [ ] daily_reports 表已插入/更新
- [ ] 墨问笔记发布成功

### HTML生成后
- [ ] marketData 包含新日期（在最前面）
- [ ] dailyReports 包含所有报告
- [ ] reportDates 包含新日期
- [ ] currentReportIndex = 0
- [ ] klineData 包含最新K线

### 部署前
- [ ] 本地打开HTML检查显示正常
- [ ] 日期切换器可正常使用
- [ ] 无报告日期显示为空

---

## 文件位置

```
/root/.openclaw/workspace/stock/a-share-dx/
├── scripts/
│   ├── crawler.py                   # 情绪数据抓取
│   ├── fetch_kline_akshare.py       # K线数据抓取（AKShare）
│   ├── analyze_sentiment.py         # AI分析（待完善）
│   └── generate_html.py             # HTML生成 ✅
├── data/
│   └── duanxian.db                  # 数据库
│       ├── market_sentiment         # 情绪数据+分析
│       ├── index_kline              # K线数据
│       └── daily_reports            # 分析报告
├── web/
│   ├── index.html                   # 主页面
│   └── backups/                     # 自动备份
└── docs/
    └── DEPLOY_WORKFLOW.md           # 本文档
```

---

## 注意事项

1. **数据库双表更新** - AI分析后需同时更新 market_sentiment 和 daily_reports
2. **日期数组倒序** - reportDates[0] 是最新日期
3. **K线图正序** - klineData.data 是正序排列（日期从小到大）
4. **成交量非成交额** - AKShare指数数据只有成交量
5. **自动备份** - generate_html.py 每次运行自动备份HTML
6. **无报告处理** - 切换日期时无报告则显示空内容

---

## 待完善

1. **analyze_sentiment.py** - 需要创建完整的AI分析脚本
2. **定时任务脚本** - 整合所有步骤的自动化脚本
3. **历史数据补充** - 批量生成之前日期的分析报告
