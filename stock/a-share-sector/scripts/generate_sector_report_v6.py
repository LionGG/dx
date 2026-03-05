#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师版V6）
基于实战经验的专业分析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_detail_data, get_zt_pool_detail, get_lhb_data, get_emotion_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

def analyze_sector_stage(sector, zt_list, prev_data=None):
    """
    判断板块阶段（基于实战经验）
    
    经验1：数据维度
    - 板块指数5日/10日涨幅
    - 板块成交额 vs 5日均值
    - 涨停家数及变化趋势
    - 连板梯队完整性
    
    经验2：阶段特征
    - 发酵期：少数涨停，成交温和放大，分歧大
    - 确认期：涨停潮，连板出现，共识形成
    - 主升期：持续放量，龙头加速，情绪高涨
    - 分歧期：高位震荡，炸板增多，多空分歧
    - 退潮期：连续跌停，量能萎缩，恐慌
    
    经验3：主线判定
    - 政策催化 + 资金深度 + 产业逻辑 + 时间窗口
    """
    
    change = sector['change_pct']
    amount = sector.get('amount', 0)
    turnover = sector.get('turnover', 0)
    zt_count = len(zt_list)
    
    # 连板梯队分析
    boards_dist = {}
    for z in zt_list:
        b = z.get('boards', 1)
        boards_dist[b] = boards_dist.get(b, 0) + 1
    max_boards = max(boards_dist.keys()) if boards_dist else 0
    
    # 资金分析
    total_zt_amount = sum(z.get('amount', 0) for z in zt_list)
    avg_seal = sum(z.get('seal_amount', 0) for z in zt_list) / max(len(zt_list), 1)
    
    # 判断阶段
    if zt_count >= 10 and max_boards >= 3:
        stage = "主升期"
        stage_desc = "持续放量，龙头加速，情绪高涨，怕踏空"
        strategy = "持股，不轻易下车"
    elif zt_count >= 5 and max_boards >= 2:
        stage = "确认期"
        stage_desc = "板块涨停潮，连板出现，共识形成，媒体开始报道"
        strategy = "加仓，上核心标的"
    elif zt_count >= 2 and change > 2:
        stage = "发酵期"
        stage_desc = "少数涨停，成交量温和放大，分歧大，很多人不信"
        strategy = "小仓试错，选先手龙头"
    elif change > 3 and zt_count < 2:
        stage = "分歧期"
        stage_desc = "高位震荡，炸板增多，多空分歧，有人止盈"
        strategy = "去弱留强，减高位"
    elif change < -3:
        stage = "退潮期"
        stage_desc = "连续跌停，量能萎缩，恐慌，割肉"
        strategy = "空仓，等下一轮"
    else:
        stage = "混沌期"
        stage_desc = "方向不明，表现平庸"
        strategy = "观望，等待时机"
    
    # 主线判定（四维）
    main_line_score = 0
    main_line_factors = []
    
    # 资金深度
    if total_zt_amount > 50:  # 涨停股总成交>50亿
        main_line_score += 30
        main_line_factors.append("资金深度好")
    elif total_zt_amount > 20:
        main_line_score += 15
        main_line_factors.append("资金深度一般")
    
    # 涨停梯队
    if max_boards >= 5:
        main_line_score += 25
        main_line_factors.append("龙头高度足")
    elif max_boards >= 3:
        main_line_score += 15
    
    # 封单强度
    if avg_seal > 5:  # 平均封单>5亿
        main_line_score += 20
        main_line_factors.append("封单强劲")
    
    # 板块涨幅
    if change > 5:
        main_line_score += 15
    
    is_main_line = main_line_score >= 60
    
    return {
        'stage': stage,
        'stage_desc': stage_desc,
        'strategy': strategy,
        'is_main_line': is_main_line,
        'main_line_score': main_line_score,
        'main_line_factors': main_line_factors,
        'zt_count': zt_count,
        'max_boards': max_boards,
        'boards_dist': boards_dist,
        'total_zt_amount': total_zt_amount,
        'avg_seal': avg_seal
    }

def generate_report_v6(date_str):
    """生成报告V6"""
    
    # 获取数据
    market = get_market_summary(date_str)
    sectors, fund_flow = get_sector_detail_data(date_str)
    zt_stocks = get_zt_pool_detail(date_str)
    lhb_data = get_lhb_data(date_str)
    emotion = get_emotion_data(date_str)
    
    # 分类板块
    main_sectors = []      # 主线板块
    potential_sectors = [] # 潜在板块
    risk_sectors = []      # 风险板块
    
    for s in sectors:
        # 匹配涨停股
        sector_zt = [z for z in zt_stocks if z['industry'] in s['name'] or s['name'] in z['industry']]
        
        # 分析阶段
        analysis = analyze_sector_stage(s, sector_zt)
        s['analysis'] = analysis
        s['zt_list'] = sector_zt
        
        # 分类（放宽条件）
        if analysis['is_main_line'] or (analysis['zt_count'] >= 2 and s['change_pct'] > 3) or analysis['max_boards'] >= 3:
            main_sectors.append(s)
        elif analysis['stage'] in ['发酵期'] or (analysis['zt_count'] >= 1 and s['change_pct'] > 2):
            potential_sectors.append(s)
        elif s['change_pct'] < -2 or analysis['stage'] in ['退潮期']:
            risk_sectors.append(s)
    
    # 排序（按主线分数）
    main_sectors.sort(key=lambda x: x['analysis']['main_line_score'], reverse=True)
    potential_sectors.sort(key=lambda x: x['analysis']['main_line_score'], reverse=True)
    
    # 生成报告
    report = f"""# A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主线板块（重仓参与）

**判定标准**：主升期/确认期，主线分数≥60，资金深度+涨停梯队+封单强度达标

{generate_main_section(main_sectors[:3])}

---

## 二、潜在板块（小仓试错）

**判定标准**：发酵期，有晋升主线可能，需观察持续性

{generate_potential_section(potential_sectors[:3])}

---

## 三、风险板块（坚决回避）

**判定标准**：退潮期/分歧期，或跌幅>2%，回避为主

{generate_risk_section(risk_sectors[:3])}

---

## 四、市场总结

**今日涨停**：{market.get('limit_up', 0)}家 | **跌停**：{market.get('limit_down', 0)}家
**最高连板**：{max([z.get('boards', 0) for z in zt_stocks], default=0)}板
**主线板块数**：{len(main_sectors)}个 | **潜在板块数**：{len(potential_sectors)}个

**明日策略**：
- 主线板块：{main_sectors[0]['name'] if main_sectors else '待观察'} 等，去弱留强
- 潜在板块：关注是否晋升主线
- 整体仓位：根据主线板块数量和质量动态调整

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    return report

def generate_main_section(sectors):
    """生成主线板块分析"""
    if not sectors:
        return "当前无明显主线板块。"
    
    result = ""
    for i, s in enumerate(sectors, 1):
        a = s['analysis']
        zt_list = s.get('zt_list', [])
        
        # 龙头列表
        dragons = '、'.join([f"{z['name']}{z['boards']}板" for z in zt_list[:3]]) if zt_list else '待识别'
        
        result += f"""### {i}. {s['name']}（{a['stage']}）

**板块表现**：指数{s['change_pct']:+.2f}%，成交{s['amount']:.0f}亿，换手{s['turnover']:.1f}%

**涨停分析**：涨停{a['zt_count']}家，最高{a['max_boards']}板，涨停总成交{a['total_zt_amount']:.0f}亿，平均封单{a['avg_seal']:.1f}亿

**龙头梯队**：{dragons}

**阶段特征**：{a['stage_desc']}

**主线判定**：分数{a['main_line_score']}/100（{'、'.join(a['main_line_factors']) if a['main_line_factors'] else '待观察'}）

**操作策略**：{a['strategy']}

---

"""
    return result

def generate_potential_section(sectors):
    """生成潜在板块分析"""
    if not sectors:
        return "当前无明显潜在板块。"
    
    result = ""
    for i, s in enumerate(sectors, 1):
        a = s['analysis']
        
        # 一日游判断
        if a['total_zt_amount'] < 20:
            yry = "⚠️ 可能一日游（资金深度不足）"
        elif a['max_boards'] < 2:
            yry = "⚠️ 可能一日游（无高度龙头）"
        else:
            yry = "✓ 有发酵潜力"
        
        result += f"""### {i}. {s['name']}（{a['stage']}）

**板块表现**：指数{s['change_pct']:+.2f}%，涨停{a['zt_count']}家

**持续性判断**：{yry}

**晋升条件**：明日涨停≥5家且出现3板龙头，可确认晋升主线

**操作策略**：{a['strategy']}

---

"""
    return result

def generate_risk_section(sectors):
    """生成风险板块分析"""
    if not sectors:
        return "当前无明显风险板块。"
    
    result = ""
    for i, s in enumerate(sectors, 1):
        a = s['analysis']
        
        result += f"""### {i}. {s['name']}（{a['stage']}）

**风险特征**：{a['stage_desc']}

**板块表现**：指数{s['change_pct']:+.2f}%

**回避策略**：{a['strategy']}

---

"""
    return result

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
    
    report = generate_report_v6(date_str)
    
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
