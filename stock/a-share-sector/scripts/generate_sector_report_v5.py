#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师版V5）
- 四节结构：主线/发酵/风险/混沌
- 放宽筛选条件
- 详细分析每个板块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

# ============ 数据预处理模块 ============

# 主流板块定义（放宽）
MAINSTREAM_KEYWORDS = [
    # 大产业
    '白酒', '食品', '饮料', '家电', '医药', '医疗', '汽车', '零售', '旅游', '消费',
    '半导体', '芯片', '计算机', '软件', '通信', '电子', '人工智能', 'AI', '科技',
    '银行', '证券', '保险', '地产', '金融',
    '有色', '煤炭', '钢铁', '化工', '石油', '建材', '周期',
    '军工', '机械', '电力', '设备', '制造', '新能源', '光伏', '风电', '锂电',
    # 大概念
    'ChatGPT', 'AIGC', '算力', '大模型', '储能', '氢能源',
    '5G', '数据中心', '特高压', '充电桩', '新基建',
    '国企改革', '央企', '中字头',
]

def preprocess_data(date_str):
    """数据预处理"""
    # 读取数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    
    raw_sectors = sectors['sectors']
    fund_flow = sectors['fund_flow']
    fund_map = {f['name']: f for f in fund_flow}
    zt_stocks = emotion.get('zt_stocks', [])
    
    # 筛选主流板块（放宽条件：关键词匹配或有大涨股）
    mainstream = []
    for s in raw_sectors:
        is_mainstream = any(kw in s['name'] for kw in MAINSTREAM_KEYWORDS)
        fund = fund_map.get(s['name'], {})
        
        if is_mainstream or s['change_pct'] > 2 or s['change_pct'] < -2:
            s['fund_inflow_pct'] = fund.get('net_inflow_pct', 0)
            s['amount'] = abs(fund.get('net_inflow', 0)) / 1e8
            
            # 匹配涨停股
            sector_zt = match_zt_stocks(s['name'], zt_stocks)
            s['zt_count'] = len(sector_zt)
            s['zt_stocks'] = sector_zt
            s['dragons'] = sector_zt[:3]  # 前3个龙头
            
            # 计算影响力
            s['influence'] = min(100, int(
                len(sector_zt) * 15 + 
                abs(s['change_pct']) * 5 +
                s['fund_inflow_pct'] * 2
            ))
            
            mainstream.append(s)
    
    # 分类（放宽条件）
    result = {
        'main': [],      # 主线板块
        'ferment': [],   # 发酵板块
        'risk': [],      # 风险板块
        'chaos': [],     # 混沌板块
    }
    
    for s in mainstream:
        change = s['change_pct']
        zt = s['zt_count']
        
        if zt >= 2 or (zt >= 1 and change > 3):
            result['main'].append(s)
        elif zt >= 1 or change > 2:
            result['ferment'].append(s)
        elif change < -2:
            result['risk'].append(s)
        else:
            result['chaos'].append(s)
    
    # 排序
    for key in result:
        result[key].sort(key=lambda x: x['influence'], reverse=True)
    
    return result, emotion

def match_zt_stocks(sector_name, zt_stocks):
    """匹配涨停股"""
    matched = []
    for z in zt_stocks:
        if z.get('industry') and (z['industry'] in sector_name or sector_name in z['industry']):
            matched.append(z)
    matched.sort(key=lambda x: x.get('boards', 0), reverse=True)
    return matched

# ============ 报告生成 ============

def generate_report_v5(date_str):
    """生成报告V5"""
    data, emotion = preprocess_data(date_str)
    
    report = f"""# A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主线板块（当前核心战场）

**判定标准**：涨停≥2家，或涨停1家+涨幅>3%，板块处于主升期

{generate_main_section(data['main'])}

---

## 二、发酵板块（明日潜在主线）

**判定标准**：涨停1家，或涨幅>2%，处于发酵期，需判断持续性

{generate_ferment_section(data['ferment'])}

---

## 三、风险板块（坚决回避）

**判定标准**：跌幅>2%，处于退潮期或高位震荡诱多

{generate_risk_section(data['risk'])}

---

## 四、混沌板块（观察等待）

**判定标准**：方向不明，表现平庸，暂无参与价值

{generate_chaos_section(data['chaos'])}

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    return report

def generate_main_section(sectors):
    """主线板块"""
    if not sectors:
        return "当前无明显主线板块。"
    
    result = ""
    for i, s in enumerate(sectors[:3], 1):
        dragons = s.get('dragons', [])
        
        # 判断阶段
        stage = judge_main_stage(s, dragons)
        
        # 龙头列表
        dragon_list = '、'.join([f"{d['name']} {d['boards']}板" for d in dragons[:2]]) if dragons else '待识别'
        
        # 策略
        strategy = get_main_strategy(stage, len(dragons))
        
        # 风险
        risk = get_main_risk(s, dragons)
        
        result += f"""### 1.{i} {s['name']}（影响力{s['influence']}/100）

**所处阶段**：{stage}

**板块表现**：板块指数{s['change_pct']:+.2f}%，涨停{s['zt_count']}家

**核心标的**：
- 龙头：{dragon_list}
- 中军：待识别（需成交额数据）

**明日策略**：{strategy}

**风险点**：{risk}

---

"""
    return result

def generate_ferment_section(sectors):
    """发酵板块"""
    if not sectors:
        return "当前无明显发酵板块。"
    
    result = ""
    for i, s in enumerate(sectors[:3], 1):
        dragons = s.get('dragons', [])
        
        # 一日游判断
        yiriyou, reason = judge_yiriyou(s, dragons)
        
        # 晋升可能性
        promote = judge_promote(s, yiriyou)
        
        # 上车条件
        condition = get_shangche_condition(s, dragons)
        
        result += f"""### 2.{i} {s['name']}（影响力{s['influence']}/100）

**板块表现**：板块指数{s['change_pct']:+.2f}%，涨停{s['zt_count']}家

**一日游风险**：{yiriyou}（{reason}）

**晋升主线可能性**：{promote}

**明日上车条件**：{condition}

---

"""
    return result

def generate_risk_section(sectors):
    """风险板块"""
    if not sectors:
        return "当前无明显风险板块。"
    
    result = ""
    for i, s in enumerate(sectors[:3], 1):
        # 判断风险类型
        risk_type = judge_risk_type(s)
        
        result += f"""### 3.{i} {s['name']}（影响力{s['influence']}/100）

**当下特征**：{risk_type}

**板块表现**：板块指数{s['change_pct']:+.2f}%

**策略**：坚决回避，不抄底，不抢反弹

---

"""
    return result

def generate_chaos_section(sectors):
    """混沌板块"""
    if len(sectors) <= 5:
        return "当前无明显混沌板块。"
    
    names = '、'.join([s['name'] for s in sectors[:5]])
    return f"""当前有{len(sectors)}个板块处于混沌状态（{names}等）。

这些板块方向不明，表现平庸，暂时不用考虑参与。若提前埋伏可能时间过久，资金效率低下。建议等待明确的启动信号或发酵迹象后再考虑介入。
"""

# ============ 辅助判断函数 ============

def judge_main_stage(sector, dragons):
    """判断主线阶段"""
    change = sector['change_pct']
    max_boards = max([d.get('boards', 0) for d in dragons], default=0)
    
    if max_boards >= 5 and change > 5:
        return "主升加速（高风险，只卖不买）"
    elif max_boards >= 3:
        return "主升初期（可参与，盯龙头）"
    else:
        return "休整接人（分歧低吸机会）"

def get_main_strategy(stage, dragon_count):
    """主线策略"""
    if "加速" in stage:
        return "只卖不买，持股者逢高减仓，未参与者观望"
    elif "初期" in stage:
        return "早盘分歧买龙，打板最强龙头，或低吸中军"
    else:
        return "持股待涨，或分歧时加仓龙头"

def get_main_risk(sector, dragons):
    """主线风险"""
    risks = []
    if sector['change_pct'] > 6:
        risks.append("一致性过高")
    if max([d.get('boards', 0) for d in dragons], default=0) >= 6:
        risks.append("监管风险")
    if sector['zt_count'] > 10:
        risks.append("板块过热")
    return '、'.join(risks) if risks else "注意分化风险"

def judge_yiriyou(sector, dragons):
    """判断一日游"""
    reasons = []
    
    # 启动即高潮
    if sector['zt_count'] > 8:
        reasons.append("首日涨停过多")
    
    # 无中军（简化判断）
    if not any(d.get('amount', 0) > 5e8 for d in dragons):
        reasons.append("大中军缺席")
    
    # 板块容量小
    if sector.get('amount', 0) < 10:
        reasons.append("板块容量小")
    
    if reasons:
        return "【可能一日游】", "、".join(reasons) + " → 策略：不参与"
    else:
        return "【真发酵】", "有逻辑、中军跟进、情绪共振 → 策略：明日竞价上车"

def judge_promote(sector, yiriyou):
    """判断晋升可能性"""
    if "真发酵" in yiriyou:
        return "高"
    elif sector['zt_count'] >= 2:
        return "中"
    else:
        return "低"

def get_shangche_condition(sector, dragons):
    """上车条件"""
    if not dragons:
        return "待观察"
    return f"明日早盘若有{min(3, len(dragons)+1)}只股快速上板，则打板最强龙头"

def judge_risk_type(sector):
    """判断风险类型"""
    change = sector['change_pct']
    if change < -5:
        return "退潮初期，A杀风险，龙头跌停，中位股批量跌停"
    elif change < -3:
        return "高位震荡诱多，成交量萎缩，反弹即是卖点"
    else:
        return "弱势整理，无明显反弹动能"

def get_weekday(date_str):
    """获取星期几"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return weekdays[date.weekday()]

def main():
    """主函数"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    from data_provider import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM stock_kline WHERE date <= ?', (today,))
    latest_date = cursor.fetchone()[0]
    conn.close()
    
    if latest_date != today:
        print(f"今天({today})不是交易日，使用最近交易日({latest_date})的数据...")
        date_str = latest_date
    else:
        print(f"生成 {today} 的板块分析报告...")
        date_str = today
    
    report = generate_report_v5(date_str)
    
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'sector_analysis_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    title = f"A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}-Billy's Claw"
    result = publish_to_mowen(
        title=title,
        content=report,
        tags=["A股分析", "板块分析"],
        auto_publish=True
    )
    
    if result.get('success'):
        mowen_url = result.get('url')
    else:
        mowen_url = f"发布失败: {result.get('error')}"
    
    print(f"墨问链接: {mowen_url}")
    
    return report_path, mowen_url

if __name__ == '__main__':
    main()
