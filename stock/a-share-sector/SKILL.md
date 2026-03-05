---
name: a-stock-analysis
description: A股收盘分析报告生成。基于a-stock-data提供的数据，生成专业分析报告并保存到墨问。
---

# A股收盘分析报告生成

## 核心职责
1. **数据依赖**：完全依赖a-stock-data skill提供的数据，不直接下载
2. **专业分析**：基于全面数据进行盘面、情绪、板块三维度分析
3. **模板输出**：严格按照用户提供的模板格式输出
4. **双份保存**：本地存档 + 墨问发布

## 执行前提
- a-stock-data skill 已完成当天数据获取
- 数据完整性检查通过

## 执行流程

### 步骤1：检查数据可用性
```python
from a_stock_data_provider import AStockDataProvider

provider = AStockDataProvider()
if not provider.check_data_ready():
    return "数据尚未准备好，请先执行a-stock-data任务或等待15:20自动获取"
```

### 步骤2：读取数据
```python
# 市场概况
market = provider.get_market_summary()

# 指数数据
indices = provider.get_index_data('all')

# 全部个股
stocks = provider.get_all_stocks()

# 情绪指标
emotion = provider.get_emotion_metrics()

# 板块数据
sectors = provider.get_sectors()
```

### 步骤3：生成分析报告

严格按照以下模板生成：

---

# A股收盘分析-{{MM/DD}}({{周几}})-Billy哥的小龙虾

## 一、盘面整体分析

### 1.1 【{{市场整体状态}}】
**行情性质**：【趋势行情/板块轮动/退潮期/混沌期】，{{核心结论}}。{{情绪周期位置及演变预期}}，{{主线板块及风险点}}。

**近5个交易日演变**：{{简述从X状态到Y状态的变化}}

### 1.2 盘面主要数据
上证指数【涨/跌】{{X}}%{{（如振幅超2%可备注：振幅X%）}}，创业板指【涨/跌】{{X}}%{{（如涨跌超2%：创业板【大涨/大跌】X%，【领涨/领跌】两市，显示【科技成长/新能源】方向【强势/承压】）}}，科创50【涨/跌】{{X}}%{{（如涨跌超3%：科创50【暴涨/暴跌】X%，【半导体/硬科技】方向【情绪高涨/资金出逃】）}}。今日两市上涨{{X}}家，下跌{{Y}}家，涨跌比{{X}}:{{Y}}{{（如涨跌比>2:1：赚钱效应较好；如<1:2：亏钱效应蔓延）}}，涨停{{X}}家，跌停{{Y}}家{{（如跌停>10家：短线情绪【明显降温/恐慌蔓延】）}}。成交额{{金额}}亿，较昨日【放量/缩量/持平】{{X}}%{{（如放量超20%：资金入场积极；如缩量超15%：市场观望情绪浓厚）}}，呈现【量价齐升/量价背离/缩量上涨/放量下跌】态势{{（如缩量上涨：上涨动能减弱，需防回调；如放量下跌：资金出逃明显，谨慎应对）}}。

### 1.3 后市观察要点
- **情绪指标**：涨停家数能否维持{{X}}家以上，跌停是否扩大
- **关键个股**：{{龙头名称}}表现（断板/补跌/加速）
- **板块动态**：主线是否分化，新题材是否持续
- **指数支撑**：关注{{点位}}支撑位/压力位

---

## 二、短线情绪分析

### 2.1 【{{情绪周期阶段}}】
{{当前情绪状态描述：如涨停家数从X家降至Y家，跌停扩大至Z家，连板高度X板但梯队断层}}。{{近3日演变：从X期→Y期→Z期}}。{{核心风险点：如中位股批量跌停、炸板率飙升、核按钮增多等}}。

### 2.2 市场风格偏好
**连板 vs 趋势**：【连板接力活跃 / 趋势抱团为主 / 均衡 / 两者皆弱】。{{具体描述：如连板高度打开但晋级率低，或趋势中军破位}}。

**10cm vs 20cm**：【10cm主导 / 20cm套利活跃 / 均衡】。{{如20cm涨停多且有大号连板，说明资金偏好弹性；如10cm独强，说明主板接力意愿强}}。

**资金面**：龙虎榜显示{{游资/机构}}{{活跃/观望}}，{{大买/大卖}}{{板块方向}}{{（如游资大买AI算力：短线资金聚焦主线；如机构大卖高股息：防御资金撤离）}}。

### 2.3 短线操作策略
{{仓位建议：如空仓/轻仓/半仓}}，{{操作风格：如防守观望/去弱留强/高低切换}}。{{具体方向：如只做低位首板/空仓等待/聚焦核心龙头}}，{{风险提示：如回避中位股、警惕核按钮等}}。

---

## 三、主流板块分析

### 3.1 主升期板块（核心战场）

#### 3.1.1 {{板块A名称}}
**板块表现**：板块指数{{涨跌幅}}，涨停{{X}}家，占全市涨停{{X}}%
**龙头梯队**：
- **总龙头**：{{股名}} {{X}}板（逻辑：{{核心驱动}}，状态：{{加速/分歧}}）
- **中军**：{{股名}}（{{趋势状态}}，成交额{{X}}亿）
- **补涨龙**：{{股名}} {{X}}板
**驱动因素**：{{政策/产业趋势/订单/事件}}
**持续性判断**：{{主升加速，预计明日分化/强上强}}
**参与策略**：{{去弱留强，只盯龙头分歧机会}}
**风险预警**：{{一致性过高/监管风险/大面股信号}}

#### 3.1.2 {{板块B名称}}（如有）
（同上结构）

---

### 3.2 发酵期板块（观察晋级）

#### 3.2.1 {{板块名称}}
**状态**：启动第{{X}}日，涨停{{X}}家，最高{{X}}板
**催化**：{{新消息/分支延伸}}
**晋升潜力**：【可能晋升主线/支线轮动】，观察{{明日是否出现板块性涨停潮}}
**关注标的**：{{潜在龙头}}

#### 3.2.2 {{板块名称}}（如有）
（同上简述）

---

### 3.3 高位震荡板块（只卖不买）

#### 3.3.1 {{板块A名称}}
**板块状态**：{{龙头名称}}高位横盘/{{滞涨}}，补涨{{活跃/随机}}，{{成交量萎缩}}
**策略**：{{等待二波信号或彻底退潮}}
**风险**：{{假突破/补跌风险}}

#### 3.3.2 {{板块B名称}}（如有）
（同上结构）

---

### 3.4 退潮期板块（坚决回避）

#### 3.4.1 {{板块A名称}}
**板块状态**：{{龙头名称}}跌停/{{A杀}}，{{核按钮}}频发
**风险**：{{反弹即是卖点}}
**策略**：{{坚决不抄底}}

#### 3.4.2 {{板块B名称}}（如有）
（同上结构）

---

### 3.5 混沌期板块（随机轮动）

#### 3.5.1 {{板块A名称}}
**板块状态**：{{快速轮动/一日游}}，无明确龙头
**策略**：{{暂不参与，等待明确}}

#### 3.5.2 {{板块B名称}}（如有）
（同上结构）

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。

---

## 分析逻辑说明

### 1.1 行情性质判断
基于以下数据综合判断：
- 四大指数涨跌幅（上证、深证、创业板、科创50）
- 涨跌家数比例
- 涨停跌停家数对比
- 成交额变化（较昨日）
- 近期均线位置

**判断标准**：
- **趋势行情**：主要指数涨跌幅>1%，涨跌比>2:1，涨停>50家
- **板块轮动**：指数震荡，板块分化，无明显主线
- **退潮期**：涨停数下降，跌停数上升，高标断板
- **混沌期**：无明显主线，快速轮动

### 2.1 情绪周期定位
基于情绪指标数据：
- 涨停家数及变化趋势
- 连板高度及梯队完整性
- 跌停家数（是否>10家）
- 炸板率

**情绪阶段**：主升期/震荡期/退潮期/冰点期/修复期

### 3.x 板块分类
基于板块数据和龙头股状态：
- **主升期**：板块指数持续上涨，龙头连板
- **发酵期**：启动1-2日，涨停数增加
- **高位震荡**：龙头横盘，补涨随机
- **退潮期**：龙头跌停或A杀
- **混沌期**：快速轮动，一日游

## 步骤4：保存报告

### 4.1 保存到本地
```python
import os
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
report_dir = f"/root/.openclaw/workspace/a_stock_data/reports/"
os.makedirs(report_dir, exist_ok=True)

report_path = f"{report_dir}/A股收盘分析-{today}.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)
```

### 4.2 发布到墨问
```python
import requests
import json

# 转换markdown为墨问doc格式
def convert_to_mowen_doc(markdown_content):
    # 简单转换：按段落分割
    paragraphs = markdown_content.split('\n\n')
    content = []
    
    for para in paragraphs:
        if para.startswith('# '):
            content.append({
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": para[2:]}]
            })
        elif para.startswith('## '):
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": para[3:]}]
            })
        elif para.startswith('### '):
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": para[4:]}]
            })
        elif para.startswith('- '):
            # 列表项
            items = para.split('\n')
            for item in items:
                if item.startswith('- '):
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": item[2:]}]
                    })
        elif para.strip():
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": para}]
            })
    
    return content

# 发布到墨问
url = "https://open.mowen.cn/api/open/api/v1/note/create"
headers = {
    "Authorization": "Bearer ijbrCOAwgLnp9Vu5kdZhw59hUfX72ba8",
    "Content-Type": "application/json"
}

doc_content = convert_to_mowen_doc(report_content)

payload = {
    "body": {
        "type": "doc",
        "content": doc_content
    },
    "settings": {
        "autoPublish": True,  # 公开文章
        "tags": ["A股收盘分析"]
    }
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

if result.get('code') == 200:
    note_id = result['data']['note']['id']
    note_url = f"https://mowen.cn/note/{note_id}"
else:
    note_url = "发布失败"
```

## 步骤5：返回结果
```python
return f"""
A股收盘分析完成！

**核心结论**：{核心结论}

**关键数据**：
- 上证指数：{涨跌幅}%
- 创业板指：{涨跌幅}%
- 科创50：{涨跌幅}%
- 涨跌比：{up}:{down}
- 涨停/跌停：{limit_up}/{limit_down}
- 成交额：{amount}亿

**情绪判断**：{情绪周期}

**本地保存**：{report_path}
**墨问发布**：{note_url}
"""
```

## 定时任务配置

```json
{
  "name": "A股收盘分析-交易日15:30",
  "schedule": {
    "kind": "cron",
    "expr": "30 15 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ A股收盘分析任务触发 - 基于已获取的数据生成分析报告"
  }
}
```

## 重要原则

### 1. 数据真实性（零容忍）
- **只使用a-stock-data提供的数据**，绝不编造
- 所有数字必须来自存档文件
- 不确定就报错，不猜测

### 2. 分析逻辑严谨
- 每个判断必须有数据支撑
- 不说"我觉得"，只说"数据显示"
- 近5日演变基于真实交易日数据

### 3. 格式规范
- 严格按照模板结构
- 动态内容填充{{}}占位符
- 条件注释根据数据决定是否保留

### 4. 错误处理
- 数据未准备好：明确告知用户
- 关键数据缺失：标注"数据待补充"
- 分析失败：返回错误信息，不生成半成品

## 依赖声明

本skill依赖以下资源：
1. **a-stock-data skill** - 提供原始数据
2. **数据存档目录** - `/root/.openclaw/workspace/a_stock_data/`
3. **墨问API** - 发布分析报告

执行前必须确认：
- [ ] a-stock-data已完成当天数据获取
- [ ] 数据文件存在且完整
- [ ] 墨问API可用
