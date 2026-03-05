# 短线情绪研判项目 - 关键细节说明

## 1. 数据源单位转换

### 新浪财经 (主数据源)
- **成交量单位**: "手"（1手 = 100股）
- **处理方式**: 获取后必须乘以100转换为"股"
- **成交额单位**: 元（无需转换）
- **优点**: 数据实时，有成交额
- **缺点**: 只有当日数据，无历史数据

### AKShare (备用数据源)
- **成交量单位**: "股"（无需转换）
- **成交额**: 历史数据无成交额
- **优点**: 有历史数据
- **缺点**: 数据有延迟

## 2. 定时任务时间安排

| 时间 | 任务 | 说明 |
|------|------|------|
| 16:20 | 短线情绪-数据抓取 | 抓取情绪数据、指数K线 |
| 16:15 | MA50占比计算 | 保持原有 |
| 16:25 | 短线情绪研判 | AI分析生成报告 |
| 16:30 | 短线情绪-部署通知 | 更新HTML、部署、发送通知 |

## 3. HTML页面指标显示

### K线图下方指标
- **显示**: 成交量（volume）
- **不显示**: 成交额（amount）
- **原因**: 历史数据缺失成交额，保持一致性

### 数据表格
- 显示成交量（volume）
- 单位：亿股

## 4. 数据库字段说明

### index_kline表
| 字段 | 说明 | 单位 |
|------|------|------|
| volume | 成交量 | 股 |
| amount | 成交额 | 元（可能为NULL） |

### market_sentiment表
| 字段 | 说明 | 单位 |
|------|------|------|
| volume | 量能 | 亿 |

## 5. 常见错误及处理

### 错误1: 成交量数据异常（如8亿 vs 800亿）
**原因**: 单位未转换（手→股）
**解决**: 检查脚本中是否乘以100

### 错误2: AI分析报告未生成
**原因**: analyze_sentiment.py设计为输出prompt，需要外部AI介入
**解决**: 定时任务直接触发AI（我）生成报告

### 错误3: 消息推送失败
**原因**: 多通道配置（钉钉+飞书），未指定channel
**解决**: 所有message调用必须加 `channel: "feishu"`

## 6. 文件位置

- 数据脚本: `/root/.openclaw/workspace/stock/dx/scripts/`
- 数据库: `/root/.openclaw/workspace/stock/dx/data/duanxian.db`
- HTML: `/root/.openclaw/workspace/stock/dx/web/index.html`
- Prompt模板: `/root/.openclaw/workspace/stock/dx/prompt.md`

## 7. 部署流程

```
1. 数据抓取 (crawler.py + fetch_kline_sina.py)
2. MA50计算 (calculate_ma50_ratio.py)
3. AI分析 (我生成报告)
4. 保存数据库
5. 更新HTML (update_html_data.py)
6. 部署GitHub (deploy.py)
7. 发送飞书通知
```

## 8. 重要提醒

- **成交量单位**: 新浪财经是"手"，必须转换
- **消息推送**: 必须使用 `channel: "feishu"`
- **AI分析**: 严格按照prompt.md格式生成报告
- **墨问发布**: 报告需发布到墨问，链接保存到数据库
- **K线指标**: 显示成交量，不显示成交额

## 9. 墨问发布流程

### 发布步骤
1. 调用 `publish_to_mowen(date, content)` 函数
2. 获取返回的 note_id 和 url
3. 保存到数据库两个表：
   - `market_sentiment.mowen_link`
   - `daily_reports.mowen_link`
4. 更新HTML时，链接会自动嵌入

### 函数位置
- `/root/.openclaw/workspace/stock/dx/scripts/publish_to_mowen.py`

### 调用示例
```python
from publish_to_mowen import publish_to_mowen

result = publish_to_mowen('2026-03-02', report_content)
# result: {'success': True, 'note_id': 'xxx', 'url': 'https://note.mowen.cn/detail/xxx'}
```

### 数据库更新
```python
# 更新market_sentiment表
cursor.execute('UPDATE market_sentiment SET mowen_link = ? WHERE date = ?', (url, date))

# 更新daily_reports表
cursor.execute('UPDATE daily_reports SET mowen_link = ? WHERE date = ?', (url, date))
```
