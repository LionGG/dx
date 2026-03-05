# 短线情绪研判任务 - 完整流程（最终版）
# 记录时间：2026-02-26
# 执行时间：交易日 16:20
# 版本：FINAL v1.0（今天讨论确定，禁止修改）

---

## 任务概览

**任务名称**：短线情绪研判  
**执行时间**：16:20（交易日）  
**项目目录**：`/root/.openclaw/workspace/stock/dx/`  
**总步骤**：8步

---

## 详细步骤

### 步骤1：抓取短线侠情绪数据
**脚本**：`python3 scripts/crawler.py`

**功能**：
- 调用短线侠API获取情绪数据
- 获取字段：情绪指数、涨停数、跌停数、上涨数、下跌数、连板高度、封板率等

**输出**：数据保存到 `duanxian.db` 的 `market_sentiment` 表

**成功标志**：输出 "✅ 更新 2026-02-26: 12 个字段"

---

### 步骤2：抓取AKShare K线数据
**脚本**：`python3 scripts/fetch_kline_akshare.py`

**功能**：
- 获取上证指数(sh000001)和创业板指(sz399006)的K线数据
- 计算MA5、MA10、MA50

**注意**：
- 使用 `stock_zh_index_daily` 方法（已验证可行）
- 确保计算最近50天的MA50

**输出**：数据保存到 `duanxian.db` 的 `index_kline` 表

**成功标志**：输出 "✓ 新增 X 条, 更新 Y 条"

---

### 步骤3：同步MA50占比数据
**脚本**：`python3 scripts/sync_ma50_ratio.py`

**功能**：
- 从 `a-share-warehouse/data/akshare_full.db` 读取今天的MA50占比
- 写入 `duanxian.db` 的 `market_sentiment` 表

**注意**：不复用MA50计算，只读取已计算好的数据

**成功标志**：输出 "已写入duanxian.db: 2026-02-26 = XX.XX%"

---

### 步骤4：AI分析
**执行方式**：AI大脑直接分析（不调用API）

**输入数据**：
- 最近5个交易日数据（从duanxian.db读取）
- 包括：情绪指数、涨停跌停数、涨跌家数、连板高度、MA50占比等

**分析格式**：使用 `prompt.md` 确认好的三部分结构

```
# A股短线情绪研判 - YYYY/MM/DD(周X) - Billy's Claw

---

## 一、当日盘面解读

**指数与量能：** [上证指数收盘及涨跌幅]；[创业板指涨跌幅]。全市上涨家数[xx]家，下跌家数[xx]家，涨跌比约[x:x]。成交额[xx]亿，较前一日[放量/缩量][x]%，[资金情绪描述]。

**短线情绪：** [情绪状态描述]。情绪指数[xx]，涨停[xx]家，跌停[xx]家，连板晋级率[xx]%，封板率[xx]%。

---

## 二、周期定位与演变

**当前阶段：[周期阶段判断]**

周期特征：[概括描述近几日演变，不每天列出]

信号判断：[关键信号及后续可能走势]

---

## 三、后市策略应对

**操作方向：**
- **关注方向：** [具体方向1]、[具体方向2]
- **回避方向：** [回避方向1]、[回避方向2]

**关键信号：** [信号1]、[信号2]

**一句话：** [核心策略总结]
```

**输出**：完整分析报告（保存到变量）

---

### 步骤5：发布到墨问
**脚本**：`python3 scripts/publish_to_mowen.py`

**功能**：
- 将AI分析的完整报告发布到墨问笔记
- 使用墨问API创建笔记

**成功标志**：返回墨问链接，如 `https://note.mowen.cn/detail/xxxxx`

**输出**：墨问链接

---

### 步骤6：生成HTML
**脚本**：`python3 scripts/update_html_data.py`

**功能**：
- 从数据库读取最新数据
- 更新HTML中的 `marketData` 和 `dailyReports`
- 注意字段索引对应（row[14-17]对应analysis_phase/action/summary/mowen_link）

**注意**：
- 日历切换组件在"情绪研判"标题上方
- 确保创业板指MA50数据已计算

**成功标志**：输出 "✅ HTML已更新"

---

### 步骤7：部署到GitHub
**脚本**：`python3 scripts/deploy.py`

**功能**：
- 将更新后的 `index.html` 推送到GitHub Pages
- 只推送index.html，其他文件不动

**成功标志**：输出 "✓ 部署成功: [commit_id]"

---

### 步骤8：截图情绪图表
**执行方式**：Python脚本

**功能**：
- 使用Playwright截取情绪图表
- 等待5秒确保图表完全渲染

**代码**：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('file:///root/.openclaw/workspace/stock/dx/web/index.html')
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(5000)  # 等待图表渲染
    
    chart_container = page.locator('.row').first.locator('.chart-container').first
    chart_container.screenshot(path='sentiment_chart.png')
    browser.close()
```

**成功标志**：生成 `sentiment_chart.png`

---

### 步骤9：发送飞书群通知
**执行方式**：调用 `send-to-feishu-group.py`

**内容**：
```
📊 短线情绪研判 - [日期]

周期定位：[analysis_phase]

查看完整分析：[墨问链接]
```
+ 图片：sentiment_chart.png

**注意**：
- 只发送文字，暂时不发图片（HTML截图工具待解决）
- 使用 `send_to_feishu_group.py` 的 `send_to_group` 函数

**成功标志**：输出 "✅ 文字发送成功"

---

## 关键检查点

| 检查项 | 标准 |
|--------|------|
| 个股数据 | 今天数据已同步（5000+条） |
| MA50占比 | 已计算并同步（约70%） |
| 创业板指MA50 | 不为None |
| AI分析 | 使用确认好的prompt格式 |
| 墨问链接 | 有效可访问 |
| HTML字段 | 周期定位/操作方向/一句话/链接 不错位 |
| 日历位置 | 在"情绪研判"标题上方 |

---

## 禁用项（不要执行）

- ❌ 调用Kimi API（已废弃）
- ❌ 发送图片（HTML截图工具待解决）
- ❌ 使用archive目录下的旧脚本
- ❌ 自己发明新格式或新方法

---

## 明天执行口诀

1. 先读文档确认流程
2. 一步一步执行，不跳步
3. 每步检查输出结果
4. 有问题立即停下，不擅自修改
5. 全部完成再发送通知

---

**记录时间**：2026-02-26 18:45  
**执行日期**：2026-02-27开始  
**版本**：FINAL v1.0（禁止修改）
