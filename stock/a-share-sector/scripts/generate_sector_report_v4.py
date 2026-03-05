#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师版V4）
- 数据预处理模块
- 只分析主流板块（大产业+大概念）
- 删除第六部分
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

# ============ 数据预处理模块 ============

# 主流板块定义（大产业+大概念）
MAINSTREAM_SECTORS = {
    # 大产业
    '大消费': ['白酒', '食品饮料', '家用电器', '医药', '汽车', '商贸零售', '旅游'],
    '大科技': ['半导体', '芯片', '计算机', '软件', '通信', '电子', '人工智能'],
    '大金融': ['银行', '证券', '保险', '房地产'],
    '大周期': ['有色金属', '煤炭', '钢铁', '化工', '石油', '建材'],
    '大制造': ['军工', '机械', '电力设备', '新能源', '光伏', '风电'],
    # 大概念
    'AI概念': ['人工智能', 'ChatGPT', 'AIGC', '算力', '大模型'],
    '新能源': ['锂电池', '储能', '光伏', '风电', '氢能源'],
    '新基建': ['5G', '数据中心', '特高压', '充电桩'],
    '国企改革': ['央企改革', '国企改革', '中字头'],
}

# 成交额阈值（亿元）
MIN_AMOUNT = 50  # 最小成交额

def preprocess_data(date_str):
    """
    数据预处理模块
    1. 读取原始数据
    2. 筛选主流板块
    3. 计算中间数据
    4. 分类板块阶段
    """
    # 1. 读取原始数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    
    # 2. 筛选主流板块
    raw_sectors = sectors['sectors']
    fund_flow = sectors['fund_flow']
    fund_map = {f['name']: f for f in fund_flow}
    
    # 计算板块成交额（简化：用涨幅*市值估算，实际应查真实成交额）
    mainstream = []
    for s in raw_sectors:
        # 检查是否属于主流板块
        is_mainstream = False
        sector_type = '其他'
        
        for main_cat, keywords in MAINSTREAM_SECTORS.items():
            for kw in keywords:
                if kw in s['name']:
                    is_mainstream = True
                    sector_type = main_cat
                    break
            if is_mainstream:
                break
        
        # 检查成交额（简化处理）
        fund = fund_map.get(s['name'], {})
        amount = abs(fund.get('net_inflow', 0)) / 1e8  # 亿元
        
        if is_mainstream or amount > MIN_AMOUNT:
            s['sector_type'] = sector_type
            s['amount'] = amount
            s['fund_inflow_pct'] = fund.get('net_inflow_pct', 0)
            mainstream.append(s)
    
    # 3. 计算中间数据
    zt_stocks = emotion.get('zt_stocks', [])
    
    for s in mainstream:
        # 匹配涨停股
        sector_zt = match_zt_stocks(s['name'], zt_stocks)
        s['zt_count'] = len(sector_zt)
        s['zt_stocks'] = sector_zt
        
        # 计算板块影响力
        s['influence_score'] = calculate_influence_v2(s, sector_zt)
        
        # 识别龙头
        if sector_zt:
            s['total_dragon'] = sector_zt[0]
            s['follow_dragon'] = sector_zt[1] if len(sector_zt) > 1 else None
        else:
            s['total_dragon'] = None
            s['follow_dragon'] = None
    
    # 4. 分类板块阶段
    result = {
        'main_rise': [],      # 主升期
        'fermentation': [],   # 发酵期
        'high_shake': [],     # 高位震荡
        'decline': [],        # 退潮期
        'chaos': [],          # 混沌期
    }
    
    for s in mainstream:
        change = s['change_pct']
        zt_count = s['zt_count']
        influence = s.get('influence_score', 0)
        
        # 优先按涨停数和涨幅判断
        if zt_count >= 3 and change > 2:
            result['main_rise'].append(s)
        elif zt_count >= 1 and change > 2:
            result['fermentation'].append(s)
        elif zt_count >= 1 and 0 < change <= 2:
            result['high_shake'].append(s)
        elif change < -2:
            result['decline'].append(s)
        else:
            result['chaos'].append(s)
    
    # 排序
    for key in result:
        result[key].sort(key=lambda x: x['influence_score'], reverse=True)
    
    return result, emotion

def calculate_influence_v2(sector, zt_list):
    """计算板块影响力（V2）"""
    score = 0
    # 涨停贡献
    score += min(30, len(zt_list) * 10)
    # 资金流向
    score += min(25, sector.get('fund_inflow_pct', 0) * 2)
    # 涨跌幅
    score += min(20, abs(sector['change_pct']) * 3)
    # 成交额
    score += min(15, sector.get('amount', 0) / 10)
    # 板块类型加成
    if sector.get('sector_type') in ['大科技', '大消费', 'AI概念']:
        score += 10
    return min(100, int(score))

def match_zt_stocks(sector_name, zt_stocks):
    """匹配涨停股"""
    keywords_map = {
        '半导体': ['半导体', '芯片', '集成电路'],
        '人工智能': ['人工智能', 'AI', '大模型'],
        '券商': ['证券', '券商'],
        '新能源': ['新能源', '光伏', '锂电', '储能'],
        '军工': ['军工', '国防', '航空'],
        '白酒': ['白酒', '酒类'],
        '医药': ['医药', '生物', '医疗'],
    }
    
    matched = []
    keywords = keywords_map.get(sector_name, [sector_name])
    
    for z in zt_stocks:
        if z.get('industry'):
            if any(kw in z['industry'] for kw in keywords):
                matched.append(z)
    
    matched.sort(key=lambda x: x.get('boards', 0), reverse=True)
    return matched

# ============ 报告生成模块 ============

def generate_report_v4(date_str):
    """生成板块分析报告（V4）"""
    
    # 数据预处理
    data, emotion = preprocess_data(date_str)
    
    # 生成报告
    report = f"""# A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主升期板块（当前核心战场）

**判定标准**：板块指数5日线上加速，龙头已3板以上，涨停家数>2家

**共性特征**：
- **持续性判断**：主升加速，预计明日分化，关注龙头承接
- **参与策略**：去弱留强，只盯龙头分歧机会，后排补涨已不安全，勿追高
- **风险预警**：一致性过高，注意监管函风险

{generate_main_rise_section(data['main_rise'])}

---

## 二、发酵期板块（明日潜在主线）

**判定标准**：启动2-3日，涨停1-2家，有新催化逻辑

**共性特征**：
- **晋升潜力**：可能晋升主线或支线轮动，观察明日是否出现板块性涨停潮及龙头强度
- **参与策略**：若是Day1观察，Day2确认后上车

{generate_fermentation_section(data['fermentation'])}

---

## 三、高位震荡板块（只卖不买）

**判定标准**：龙头滞涨但未跌停，高位横盘，补涨股活跃但随机性强

**共性特征**：
- **特征**：成交量萎缩/筹码松动/消息刺激钝化
- **策略**：只卖不买，等待二波信号或彻底退潮确认

{generate_high_shake_section(data['high_shake'])}

---

## 四、退潮期板块（坚决回避）

**判定标准**：龙头跌停或A杀，中位股批量跌停，板块指数破10日线

**共性特征**：
- **风险**：A杀/核按钮/反弹即是卖点
- **策略**：坚决回避，不抄底，不抢反弹

{generate_decline_section(data['decline'])}

---

## 五、混沌期板块（观察等待）

**判定标准**：快速轮动、一日游、无明确龙头

**共性特征**：等待题材明确或新催化，暂不参与

{generate_chaos_section(data['chaos'])}

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    
    return report

def generate_main_rise_section(sectors):
    """生成主升期板块内容"""
    if not sectors:
        return "当前无明显主升期板块。"
    
    result = ""
    for i, s in enumerate(sectors[:3], 1):
        total = s.get('total_dragon')
        follow = s.get('follow_dragon')
        
        result += f"""### 1.{i} {s['name']}（{s.get('sector_type', '其他')}）

**板块表现**：板块指数{s['change_pct']:+.2f}%，涨停{s['zt_count']}家，板块影响力{s['influence_score']}/100分

**龙头梯队**：
- **总龙头**：{total['name'] if total else '待识别'} {total['boards'] if total else 'X'}板（状态：{get_dragon_status(total)}，辨识度：{calculate_recognition(total)}/100）
- **补涨龙**：{follow['name'] if follow else '待识别'} {follow['boards'] if follow else 'X'}板（{get_follow_quality(follow)}）

**驱动因素**：{get_driver_factor_v2(s['name'], s.get('sector_type'))}

"""
    return result

def generate_fermentation_section(sectors):
    """生成发酵期板块内容"""
    if not sectors:
        return "当前无明显发酵期板块。"
    
    result = ""
    for i, s in enumerate(sectors[:2], 1):
        total = s.get('total_dragon')
        
        result += f"""### 2.{i} {s['name']}（{s.get('sector_type', '其他')}）

**板块表现**：板块指数{s['change_pct']:+.2f}%，涨停{s['zt_count']}家，板块影响力{s['influence_score']}/100分

**驱动逻辑**：{get_driver_factor_v2(s['name'], s.get('sector_type'))}

**关注标的**：{total['name'] if total else '待观察'}

"""
    return result

def generate_high_shake_section(sectors):
    """生成高位震荡板块内容"""
    if not sectors:
        return "当前无明显高位震荡板块。"
    
    result = ""
    for i, s in enumerate(sectors[:2], 1):
        result += f"""### 3.{i} {s['name']}（{s.get('sector_type', '其他')}）

**板块表现**：板块指数{s['change_pct']:+.2f}%，板块影响力{s['influence_score']}/100分

**风险特征**：龙头滞涨，补涨股随机性强

"""
    return result

def generate_decline_section(sectors):
    """生成退潮期板块内容"""
    if not sectors:
        return "当前无明显退潮期板块。"
    
    result = ""
    for i, s in enumerate(sectors[:2], 1):
        result += f"""### 4.{i} {s['name']}（{s.get('sector_type', '其他')}）

**板块表现**：板块指数{s['change_pct']:+.2f}%，板块影响力{s['influence_score']}/100分

**风险特征**：龙头跌停或A杀，中位股批量跌停

"""
    return result

def generate_chaos_section(sectors):
    """生成混沌期板块内容"""
    if len(sectors) <= 3:
        return "当前无明显混沌期主流板块。"
    
    names = ', '.join([s['name'] for s in sectors[:5]])
    return f"当前有{len(sectors)}个板块处于混沌期（{names}等），快速轮动，无明确龙头，暂不参与。"

# ============ 辅助函数 ============

def get_dragon_status(dragon):
    """判断龙头状态"""
    if not dragon:
        return '加速'
    boards = dragon.get('boards', 0)
    if boards >= 5:
        return '高位加速'
    elif boards >= 3:
        return '分歧转一致'
    else:
        return '启动加速'

def calculate_recognition(dragon):
    """计算辨识度"""
    if not dragon:
        return 50
    score = min(50, dragon.get('boards', 0) * 10)
    score += 20 if dragon.get('is_first_board', False) else 0
    return min(100, int(score))

def get_follow_quality(dragon):
    """判断跟风质量"""
    if not dragon:
        return '跟风'
    if dragon.get('boards', 0) >= 3:
        return '细分龙头'
    elif dragon.get('amount', 0) > 1e8:
        return '放量跟风'
    else:
        return '纯跟风'

def get_driver_factor_v2(sector_name, sector_type):
    """获取驱动因素（V2）"""
    drivers = {
        '大消费': '消费复苏+政策刺激',
        '大科技': '国产替代+技术突破',
        '大金融': '政策宽松+估值修复',
        '大周期': '经济复苏+资源涨价',
        '大制造': '制造业升级+订单增长',
        'AI概念': 'AI应用落地+算力需求',
        '新能源': '产业趋势+政策支持',
    }
    return drivers.get(sector_type, '资金推动+情绪催化')

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
    
    report = generate_report_v4(date_str)
    
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
