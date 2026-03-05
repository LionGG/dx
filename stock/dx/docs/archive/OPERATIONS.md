# A股短线情绪数据 - 自动化流程文档

**最后更新**: 2026-02-24  
**定时任务**: 每日 16:00 (北京时间)  
**执行目录**: `/root/.openclaw/workspace/stock/a-share-dx`

---

## 核心原则

1. **只推送 index.html** - 部署时仅更新单个文件，其他文件不动
2. **关键步骤失败即停** - 数据抓取/分析/生成失败则停止，部署失败可继续
3. **幂等执行** - 重复执行不会导致重复数据

---

## 完整流程

```
16:00 定时触发
    │
    ▼
┌─────────────────┐
│ 1. 抓取短线侠情绪 │ ← 关键步骤，失败则停
│    crawler.py   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 抓取AKShare K线│ ← 关键步骤，失败则停
│ fetch_kline_akshare.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. AI分析+墨问   │ ← 关键步骤，失败则停
│ analyze_sentiment.py
│ - 生成分析报告
│ - 发布到墨问
│ - 存储到数据库
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 生成HTML      │ ← 关键步骤，失败则停
│ generate_html.py
│ - 自动备份旧版本
│ - 验证数据完整性
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 部署到GitHub  │ ← 非关键，失败只告警
│ deploy.py
│ - 只推送 index.html
│ - 其他文件完全不动
└─────────────────┘
```

---

## 定时任务配置

```bash
# 查看当前任务
crontab -l | grep a-share-dx

# 任务ID: 6ff81a4c-90cf-4127-b9d3-f2a3abc9ca53
# 执行时间: 每天 16:00
# 命令:
0 16 * * * cd /root/.openclaw/workspace/stock/a-share-dx && python3 scripts/daily_pipeline.py >> logs/daily_$(date +\%Y\%m\%d).log 2>&1
```

---

## 各脚本职责

### crawler.py
- **输入**: 无（从短线侠网站抓取）
- **输出**: `data/duanxian.db` - `market_sentiment` 表
- **超时**: 120秒
- **失败处理**: 停止整个流程

### fetch_kline_akshare.py
- **输入**: 无（从AKShare获取）
- **输出**: `data/duanxian.db` - `index_kline` 表
- **数据**: 上证指数(000001)、创业板指(399006)的K线+MA5/MA10/MA50
- **超时**: 120秒
- **失败处理**: 停止整个流程

### analyze_sentiment.py
- **输入**: 当日情绪数据 + K线数据
- **输出**: 
  - 墨问笔记（公开发布）
  - `market_sentiment` 表（analysis_phase, action, summary, mowen_link）
  - `daily_reports` 表（完整报告，用于HTML展示）
- **超时**: 300秒
- **失败处理**: 停止整个流程

### generate_html.py
- **输入**: `market_sentiment` 表 + `daily_reports` 表 + `index_kline` 表
- **输出**: `web/index.html`
- **特性**:
  - 自动备份旧版本到 `web/backup/index.html.{timestamp}`
  - 验证数据完整性（日期连续性检查）
  - 包含：情绪走势图、K线图、AI研判、数据表格
- **超时**: 60秒
- **失败处理**: 停止整个流程

### deploy.py
- **输入**: `web/index.html`
- **输出**: GitHub 仓库的 `index.html`
- **方式**: GitHub API 直接上传（避免git超时）
- **原则**: **只操作 index.html，其他文件完全不动**
- **超时**: 60秒
- **失败处理**: 记录日志，不阻断流程

---

## 依赖检查清单

执行前确认以下依赖正常：

| 依赖 | 检查方式 | 状态 |
|------|---------|------|
| SQLite数据库 | `ls data/duanxian.db` | ✅ |
| 墨问API Token | 硬编码在脚本中 | ✅ |
| GitHub Token | 硬编码在deploy.py | ✅ |
| AKShare | `python3 -c "import akshare"` | ✅ |
| 网络连接 | `curl -I https://duanxianxia.com` | ✅ |

---

## 故障处理

### 场景1: 数据抓取失败
```bash
# 手动重试
python3 scripts/crawler.py

# 检查网络
curl -I https://duanxianxia.com/short/
```

### 场景2: AI分析失败
```bash
# 检查API额度
# 检查prompt.md是否存在
ls -la prompt.md
```

### 场景3: 部署失败
```bash
# 手动部署
python3 scripts/deploy.py

# 检查GitHub API状态
# 如持续失败，检查token是否过期
```

### 场景4: 需要补录历史数据
```bash
# 1. 手动抓取指定日期（修改crawler.py中的日期）
# 2. 手动执行分析
python3 scripts/analyze_sentiment.py
# 3. 重新生成HTML
python3 scripts/generate_html.py
# 4. 部署
python3 scripts/deploy.py
```

---

## 文件清单

```
a-share-dx/
├── data/
│   └── duanxian.db              # SQLite数据库（核心数据）
├── web/
│   ├── index.html               # 生成的网页（唯一部署文件）
│   └── backup/                  # 自动备份目录
├── scripts/
│   ├── crawler.py               # 短线侠数据抓取
│   ├── fetch_kline_akshare.py   # AKShare K线抓取
│   ├── analyze_sentiment.py     # AI分析+墨问发布
│   ├── generate_html.py         # HTML生成
│   ├── deploy.py                # GitHub部署（只推index.html）
│   └── daily_pipeline.py        # 完整流程编排
├── prompt.md                    # AI分析Prompt模板
└── OPERATIONS.md                # 本文件
```

---

## 数据库表结构

### market_sentiment（情绪数据+分析）
```sql
CREATE TABLE market_sentiment (
    date TEXT PRIMARY KEY,
    sentiment_index INTEGER,      -- 情绪指数
    limit_up INTEGER,             -- 涨停数
    limit_down INTEGER,           -- 跌停数
    volume REAL,                  -- 量能(亿)
    consecutive_height INTEGER,   -- 连板高度
    -- ... 其他字段
    analysis_phase TEXT,          -- 周期阶段
    analysis_action TEXT,         -- 操作策略
    analysis_summary TEXT,        -- 一句话总结
    mowen_link TEXT               -- 墨问链接
);
```

### index_kline（K线数据）
```sql
CREATE TABLE index_kline (
    date TEXT,
    index_code TEXT,              -- 000001=上证, 399006=创业板
    open REAL, high REAL, low REAL, close REAL,
    volume REAL,                  -- 成交量
    ma5 REAL, ma10 REAL, ma50 REAL,
    PRIMARY KEY (date, index_code)
);
```

### daily_reports（完整报告）
```sql
CREATE TABLE daily_reports (
    date TEXT PRIMARY KEY,
    full_report TEXT              -- HTML格式完整报告
);
```

---

## 验证检查点

每天执行后，验证以下检查点：

- [ ] `market_sentiment` 表有今日数据
- [ ] `index_kline` 表有今日数据（2条记录：上证+创业板）
- [ ] `daily_reports` 表有今日报告
- [ ] 墨问笔记发布成功（有返回链接）
- [ ] `web/index.html` 文件更新（时间戳最新）
- [ ] GitHub 上的 `index.html` 已更新

---

## 联系方式

如有问题，检查日志：
```bash
tail -f /root/.openclaw/workspace/stock/a-share-dx/logs/daily_$(date +%Y%m%d).log
```
