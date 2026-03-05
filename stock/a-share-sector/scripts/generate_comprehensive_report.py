#!/usr/bin/env python3
"""
A股收盘分析报告生成（综合版）
结合原板块分析 + 新prompt的量化判定逻辑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data, get_recent_days_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

def generate_comprehensive_report(date_str):
    """生成综合收盘分析报告"""
    
    # 获取数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    recent_dates = get_recent_days_data(date_str, 5)
    
    # 提取关键数据
    sh = market['indices'].get('000001', {})
    cy = market['indices'].get('399006', {})
    kc = market['indices'].get('000688', {})
    stats = market['market_stats']
    
    sectors_list = sectors['sectors']
    fund_flow = sectors['fund_flow']
    fund_map = {f['name']: f for f in fund_flow}
    
    # 计算关键指标
    limit_up = market['limit_up']
    limit_down = market['limit_down']
    up_count = stats['up_count']
    down_count = stats['down_count']
    total_amount = stats['total_amount']
    
    # 量化判定
    market_status = judge_market_status(limit_up, limit_down, up_count, down_count)
    emotion_stage = judge_emotion_stage(limit_up, limit_down, emotion['max_boards'])
    
    # 生成报告
    report = f"""# A股收盘分析-{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy哥的小龙虾

---

## 数据输入区

**市场全局**
- 沪指：{sh.get('close', 0):.2f}点，{get_change_desc(sh.get('change_pct', 0))}
- 创业板：{cy.get('close', 0):.2f}点，{get_change_desc(cy.get('change_pct', 0))}
- 科创50：{kc.get('close', 0):.2f}点，{get_change_desc(kc.get('change_pct', 0))}
- 全市涨跌比：{up_count}:{down_count}
- 涨停：{limit_up}家 / 跌停：{limit_down}家

---

## 一、盘面整体分析

### 1.1 【{market_status['status']}】

**量化判定**：
- 涨停家数：{limit_up}家（判定阈值：>80高潮/50-80主升/30-50分化/<30退潮）
- 涨跌比：{up_count/down_count:.1f}:1（判定阈值：>2:1强势/<1:2弱势）
- 跌停家数：{limit_down}家（判定阈值：>20家恐慌）

**当前判定**：{market_status['status']}

**近5日情绪演变**：{get_evolution_trend(recent_dates)}

### 1.2 盘面数据摘要

上证指数{get_change_desc(sh.get('change_pct', 0))}，创业板指{get_change_desc(cy.get('change_pct', 0))}，科创50{get_change_desc(kc.get('change_pct', 0))}。两市上涨{up_count}家，下跌{down_count}家，涨跌比{up_count//max(down_count//1000, 1)}:1，{get_market_effect(up_count, down_count)}。涨停{limit_up}家，跌停{limit_down}家{get_dt_warning(limit_down)}。成交额{total_amount:.0f}亿，呈现{get_volume_trend(sh.get('change_pct', 0), up_count, down_count)}态势。

### 1.3 次日风控点位

- **情绪退潮信号**：若明日涨停<{int(limit_up*0.7)}家或跌停>{int(limit_down*1.5)}家，立即减仓至30%
- **板块切换信号**：关注今日强势板块龙头是否断板，及潜在板块批量涨停

---

## 二、短线情绪分析

### 2.1 【{emotion_stage}】

**数据支撑**：
- 连板高度：{emotion['max_boards']}板
- 涨停家数：{limit_up}家
- 跌停家数：{limit_down}家

**阶段判定**：{emotion_stage}

### 2.2 市场风格偏好

**量化统计**：
- 10cm涨停：{limit_up}家（估算）
- 连板高度：{emotion['max_boards']}板
- **风格判定**：{get_style_judgment(limit_up, emotion['max_boards'])}

### 2.3 短线操作策略

基于上述量化指标，明日策略：
- **仓位建议**：{get_position_suggestion(market_status['status'])}
- **风险规避**：{get_risk_warning(emotion_stage)}

---

## 三、主流板块分析（交易作战地图）

### 3.1 主升期板块（当前核心战场，70%仓位）
**判定标准**：板块指数5日线上加速，龙头已3板以上，涨停家数>10家且持续3日

{generate_main_rise_sectors(sectors_list, fund_map, emotion)}

### 3.2 发酵期板块（明日潜在主线，30%仓位试错）
**判定标准**：首日或次日异动，涨停3-8家，有新催化逻辑

{generate_fermentation_sectors(sectors_list, fund_map)}

### 3.3 退潮期板块（0仓位，坚决回避）
**判定标准**：龙头跌停或A杀，中位股批量跌停，板块指数破10日线

{generate_decline_sectors(sectors_list, fund_map)}

### 3.4 混沌期/随机轮动（不分析，直接过滤）
{generate_chaos_sectors(sectors_list)}

### 3.5 板块切换预警（重要！）
**当前资金流向**：从弱势板块流出 → 流入强势板块
**切换信号**：若主升板块出现退散信号，且发酵板块逆势走强，则启动仓位切换（70%→30%，30%→70%）

---

## 四、明日观察要点

### 4.1 需持续关注的板块
- 今日领涨板块明日是否持续
- 资金流入板块是否有持续性
- 放量上涨板块的后续表现

### 4.2 需警惕的信号
- 放量滞涨板块
- 资金大幅流出板块
- 涨停家数骤降

### 4.3 潜在机会
- 低位启动板块
- 轮动预期板块

---

免责声明：以上分析基于历史数据，不构成投资建议，明日开盘需结合竞价数据动态调整。
"""
    
    return report

def judge_market_status(limit_up, limit_down, up_count, down_count):
    """判定市场状态"""
    ratio = up_count / max(down_count, 1)
    
    if limit_up > 80 and ratio > 2:
        return {'status': '情绪高潮期', 'level': 'high'}
    elif limit_up >= 50 and limit_up <= 80:
        return {'status': '主升期', 'level': 'mid-high'}
    elif limit_up >= 30 and limit_up < 50:
        return {'status': '分化期/混沌期', 'level': 'mid'}
    elif limit_up < 30 or limit_down > 20:
        return {'status': '退潮期/冰点期', 'level': 'low'}
    else:
        return {'status': '震荡整理', 'level': 'neutral'}

def judge_emotion_stage(limit_up, limit_down, max_boards):
    """判定情绪周期阶段"""
    if max_boards >= 5 and limit_up >= 50 and limit_down < 10:
        return '主升期'
    elif max_boards >= 3 and limit_up >= 30:
        return '震荡期'
    elif limit_down > 15:
        return '退潮期'
    else:
        return '混沌期'

def get_weekday(date_str):
    """获取星期几"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return weekdays[date.weekday()]

def get_change_desc(change_pct):
    """获取涨跌幅描述"""
    if change_pct > 0:
        return f"涨{change_pct:.2f}%"
    elif change_pct < 0:
        return f"跌{abs(change_pct):.2f}%"
    else:
        return "平"

def get_evolution_trend(dates):
    """获取演变趋势描述"""
    if len(dates) >= 2:
        return f"从{dates[0]}到{dates[-1]}，观察趋势变化"
    return "数据不足"

def get_market_effect(up_count, down_count):
    """获取赚钱效应评价"""
    ratio = up_count / max(down_count, 1)
    if ratio > 2:
        return "赚钱效应较好"
    elif ratio > 1:
        return "赚钱效应一般"
    else:
        return "亏钱效应明显"

def get_dt_warning(limit_down):
    """获取跌停警告"""
    if limit_down > 15:
        return "（恐慌情绪蔓延）"
    elif limit_down > 10:
        return "（情绪降温）"
    return ""

def get_volume_trend(index_change, up_count, down_count):
    """获取量能趋势"""
    if index_change > 0 and up_count > down_count:
        return "量价齐升"
    elif index_change < 0 and up_count < down_count:
        return "放量下跌"
    else:
        return "缩量整理"

def get_style_judgment(limit_up, max_boards):
    """获取风格判定"""
    if max_boards >= 5:
        return "10cm连板主导，资金偏好强势股"
    elif limit_up > 60:
        return "10cm活跃，连板与首板并重"
    else:
        return "趋势抱团为主，资金偏好低位"

def get_position_suggestion(status):
    """获取仓位建议"""
    suggestions = {
        '情绪高潮期': '70-100%，积极做多',
        '主升期': '60-80%，重仓参与',
        '分化期/混沌期': '30-50%，控制仓位',
        '退潮期/冰点期': '0-20%，防守为主',
        '震荡整理': '40-60%，灵活应对'
    }
    return suggestions.get(status, '50%，均衡配置')

def get_risk_warning(emotion_stage):
    """获取风险警告"""
    if emotion_stage == '退潮期':
        return '坚决回避中位股（3-4板），只留龙头或空仓'
    elif emotion_stage == '震荡期':
        return '谨慎追高，关注低位补涨'
    return '正常参与，注意节奏'

def calculate_sector_strength(sector, fund_map):
    """计算板块强度评分"""
    change_score = sector['change_pct'] * 2
    fund = fund_map.get(sector['name'], {})
    fund_score = fund.get('net_inflow_pct', 0) * 3
    return change_score + fund_score

def generate_sector_strength_table(sectors, fund_map):
    """生成板块强度表"""
    for s in sectors:
        s['strength'] = calculate_sector_strength(s, fund_map)
    
    sorted_sectors = sorted(sectors, key=lambda x: x['strength'], reverse=True)
    
    result = "| 排名 | 板块名称 | 涨跌幅 | 资金流向 | 强度评分 |\n"
    result += "|------|----------|--------|----------|----------|\n"
    for i, s in enumerate(sorted_sectors[:10], 1):
        fund = fund_map.get(s['name'], {})
        fund_pct = fund.get('net_inflow_pct', 0)
        result += f"| {i} | {s['name']} | {s['change_pct']:+.2f}% | {fund_pct:+.2f}% | {s['strength']:.1f} |\n"
    return result

def generate_top_sectors_analysis(sectors, fund_map):
    """生成领涨板块深度分析"""
    result = ""
    for i, s in enumerate(sectors, 1):
        fund = fund_map.get(s['name'], {})
        trend = "强势上涨" if s['change_pct'] > 3 else "温和上涨"
        result += f"**{i}. {s['name']}**：{trend}，涨{s['change_pct']:.2f}%，资金净流入{fund.get('net_inflow_pct', 0):.2f}%。"
        
        if s['change_pct'] > 3:
            result += "板块效应明显，关注明日持续性。"
        else:
            result += "稳步上涨，趋势良好。"
        result += "\n\n"
    return result

def generate_fund_inflow_table(fund_flow):
    """生成资金流入表"""
    result = ""
    for i, f in enumerate(fund_flow, 1):
        amount = f['net_inflow'] / 1e8
        result += f"{i}. {f['name']}: {amount:+.1f}亿 ({f['net_inflow_pct']:+.2f}%)\n"
    return result

def generate_fund_outflow_table(fund_flow):
    """生成资金流出表"""
    result = ""
    for i, f in enumerate(reversed(fund_flow), 1):
        amount = f['net_inflow'] / 1e8
        result += f"{i}. {f['name']}: {amount:+.1f}亿 ({f['net_inflow_pct']:+.2f}%)\n"
    return result

def generate_main_rise_sectors(sectors, fund_map, emotion):
    """生成主升期板块分析"""
    # 筛选强势板块（涨幅>3%，资金流入）
    main_sectors = [s for s in sectors if s['change_pct'] > 3]
    
    if not main_sectors:
        return "当前无明显主升期板块，市场处于分化或退潮期。"
    
    result = ""
    for i, s in enumerate(main_sectors[:2], 1):  # 最多展示2个
        fund = fund_map.get(s['name'], {})
        
        # 计算强度评分
        policy_score = 20 if s['change_pct'] > 5 else 15  # 政策分数
        fund_score = min(abs(fund.get('net_inflow_pct', 0)) * 2, 30)  # 资金分数
        industry_score = 20  # 产业分数（简化）
        window_score = 20 if emotion['max_boards'] >= 4 else 15  # 窗口分数
        total_score = policy_score + fund_score + industry_score + window_score
        
        result += f"#### 3.1.{i} {s['name']}\n\n"
        result += f"**主线强度评分**：{total_score}/100分（政策{policy_score}分+资金{fund_score:.0f}分+产业{industry_score}分+窗口{window_score}分）\n\n"
        result += f"**阶段细分**：【主升加速期】\n\n"
        result += f"**龙头梯队与策略**：\n"
        result += f"- **板块表现**：涨{s['change_pct']:.2f}%，资金净流入{fund.get('net_inflow_pct', 0):.2f}%\n"
        result += f"- **明日策略**：若继续强势可持股，若放量滞涨考虑减仓\n\n"
        result += f"**阶段退散信号**（满足任一即减仓）：\n"
        result += f"- [ ] 板块指数跌破5日线\n"
        result += f"- [ ] 涨停家数较今日减少40%以上\n"
        result += f"- [ ] 出现批量跌停\n\n"
        result += f"**明日交易计划**：\n"
        result += f"- 若板块继续强势：持股不动\n"
        result += f"- 若出现退散信号：无条件降至30%仓位\n\n"
    
    return result

def generate_fermentation_sectors(sectors, fund_map):
    """生成发酵期板块分析"""
    # 筛选发酵期板块（涨幅2-5%，非最高）
    ferment_sectors = [s for s in sectors if 2 <= s['change_pct'] <= 5]
    
    if not ferment_sectors:
        return "当前无明显发酵期板块。"
    
    result = ""
    for i, s in enumerate(ferment_sectors[:2], 1):
        fund = fund_map.get(s['name'], {})
        
        # 风险评估
        if s['change_pct'] > 4 and fund.get('net_inflow_pct', 0) > 1:
            risk_level = "低风险（真发酵）"
        elif s['change_pct'] > 3:
            risk_level = "中风险（需确认）"
        else:
            risk_level = "高风险（观察为主）"
        
        result += f"#### 3.2.{i} {s['name']}\n\n"
        result += f"**一日游风险评级**：【{risk_level}】\n\n"
        result += f"**四维判定**：\n"
        result += f"- 资金：资金净流入{fund.get('net_inflow_pct', 0):.2f}%\n"
        result += f"- 涨幅：{s['change_pct']:.2f}%\n"
        result += f"- 类型：{s.get('type', '行业')}\n\n"
        result += f"**阶段定位**：【发酵期（观察或轻仓试错）】\n\n"
        result += f"**明日策略**：\n"
        result += f"- 若早盘有3只以上快速涨停：打板最强龙头\n"
        result += f"- 若走势分化：放弃或低吸中军\n\n"
    
    return result

def generate_decline_sectors(sectors, fund_map):
    """生成退潮期板块分析"""
    # 筛选弱势板块（跌幅>2%）
    decline_sectors = [s for s in sectors if s['change_pct'] < -2]
    
    if not decline_sectors:
        return "当前无明显退潮期板块。"
    
    result = ""
    for i, s in enumerate(decline_sectors[:2], 1):
        fund = fund_map.get(s['name'], {})
        result += f"- **{s['name']}**（弱势）：跌{abs(s['change_pct']):.2f}%，资金流出{abs(fund.get('net_inflow_pct', 0)):.2f}%。风险：继续回避，持有者反抽清仓。\n\n"
    
    return result

def generate_chaos_sectors(sectors):
    """生成混沌期板块"""
    # 筛选震荡板块（-1%到1%之间）
    chaos_sectors = [s for s in sectors if -1 <= s['change_pct'] <= 1]
    
    if len(chaos_sectors) > 5:
        return f"- 当前有{len(chaos_sectors)}个板块震荡整理，无明显方向，暂不参与。\n"
    return ""

def main():
    """主函数"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今天是否有数据
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
        print(f"生成 {today} 的收盘分析报告...")
        date_str = today
    
    # 生成报告
    report = generate_comprehensive_report(date_str)
    
    # 保存本地
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'analysis_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    # 发布到墨问
    title = f"A股收盘分析-{date_str[5:7]}/{date_str[8:]}-Billy哥的小龙虾"
    result = publish_to_mowen(
        title=title,
        content=report,
        tags=["A股分析", "收盘报告"],
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
