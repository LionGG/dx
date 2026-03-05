#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师版V3）
- 合并共性内容
- 章节支持小节
- 删除仓位建议
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data, get_recent_days_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

def generate_sector_analysis_report(date_str):
    """生成板块分析报告（V3）"""
    
    # 获取数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    
    # 提取数据
    sectors_list = sectors['sectors']
    fund_flow = sectors['fund_flow']
    fund_map = {f['name']: f for f in fund_flow}
    zt_stocks = emotion.get('zt_stocks', [])
    
    # 分类板块
    strong_sectors = [s for s in sectors_list if s['change_pct'] > 3]
    rising_sectors = [s for s in sectors_list if 2 <= s['change_pct'] <= 3]
    falling_sectors = [s for s in sectors_list if s['change_pct'] < -2]
    
    # 生成报告
    report = f"""# A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主升期板块（当前核心战场）

**判定标准**：板块指数5日线上加速，龙头已3板以上，涨停家数>10家且持续3日

**共性特征**：
- **持续性判断**：主升加速，预计明日分化，关注龙头承接
- **参与策略**：去弱留强，只盯龙头分歧机会，后排补涨已不安全，勿追高
- **风险预警**：一致性过高，注意监管函风险

### 1.1 {strong_sectors[0]['name'] if strong_sectors else '暂无'}

{generate_sector_detail(strong_sectors[0] if strong_sectors else None, fund_map, zt_stocks)}

### 1.2 {strong_sectors[1]['name'] if len(strong_sectors) > 1 else '暂无'}

{generate_sector_detail(strong_sectors[1] if len(strong_sectors) > 1 else None, fund_map, zt_stocks)}

### 1.3 {strong_sectors[2]['name'] if len(strong_sectors) > 2 else '暂无'}

{generate_sector_detail(strong_sectors[2] if len(strong_sectors) > 2 else None, fund_map, zt_stocks)}

---

## 二、发酵期板块（明日潜在主线）

**判定标准**：启动2-3日，涨停3-8家，有新催化逻辑

**共性特征**：
- **晋升潜力**：可能晋升主线或支线轮动，观察明日是否出现板块性涨停潮及龙头强度
- **参与策略**：若是Day1观察，Day2确认后上车

### 2.1 {rising_sectors[0]['name'] if rising_sectors else '暂无'}

{generate_fermentation_detail(rising_sectors[0] if rising_sectors else None, fund_map, zt_stocks)}

### 2.2 {rising_sectors[1]['name'] if len(rising_sectors) > 1 else '暂无'}

{generate_fermentation_detail(rising_sectors[1] if len(rising_sectors) > 1 else None, fund_map, zt_stocks)}

---

## 三、高位震荡板块（只卖不买）

**判定标准**：龙头滞涨但未跌停，高位横盘，补涨股活跃但随机性强

**共性特征**：
- **特征**：成交量萎缩/筹码松动/消息刺激钝化
- **策略**：只卖不买，等待二波信号或彻底退潮确认

### 3.1 待识别

当前无明显高位震荡板块。

---

## 四、退潮期板块（坚决回避）

**判定标准**：龙头跌停或A杀，中位股批量跌停，板块指数破10日线

**共性特征**：
- **风险**：A杀/核按钮/反弹即是卖点
- **策略**：坚决回避，不抄底，不抢反弹

### 4.1 {falling_sectors[0]['name'] if falling_sectors else '暂无'}

{generate_decline_detail(falling_sectors[0] if falling_sectors else None, fund_map, zt_stocks)}

---

## 五、混沌期板块（观察等待）

**判定标准**：快速轮动、一日游、无明确龙头

**共性特征**：等待题材明确或新催化，暂不参与

{generate_chaos_content(sectors_list)}

---

## 六、明日作战计划

### 6.1 重点进攻方向
{generate_attack_plan(strong_sectors)}

### 6.2 观察等待方向
{generate_watch_plan(rising_sectors)}

### 6.3 坚决回避方向
{generate_avoid_plan(falling_sectors)}

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    
    return report

def generate_sector_detail(sector, fund_map, zt_stocks):
    """生成主升期板块详情"""
    if not sector:
        return "暂无数据"
    
    fund = fund_map.get(sector['name'], {})
    sector_zt = match_zt_stocks(sector['name'], zt_stocks)
    
    total = sector_zt[0] if sector_zt else None
    follow = sector_zt[1] if len(sector_zt) > 1 else None
    
    return f"""**板块表现**：板块指数{sector['change_pct']:+.2f}%，涨停{len(sector_zt)}家

**板块影响力**：{calculate_influence(sector, fund, len(sector_zt))}/100分

**龙头梯队**：
- **总龙头**：{total['name'] if total else '待识别'} {total['boards'] if total else 'X'}板（状态：{get_dragon_status(total)}，辨识度：{calculate_recognition(total)}/100）
- **中军**：待识别（需成交额数据）
- **补涨龙**：{follow['name'] if follow else '待识别'} {follow['boards'] if follow else 'X'}板（{get_follow_quality(follow)}）

**驱动因素**：{get_driver_factor(sector['name'])}
"""

def generate_fermentation_detail(sector, fund_map, zt_stocks):
    """生成发酵期板块详情"""
    if not sector:
        return "暂无数据"
    
    fund = fund_map.get(sector['name'], {})
    sector_zt = match_zt_stocks(sector['name'], zt_stocks)
    
    return f"""**板块表现**：板块指数{sector['change_pct']:+.2f}%，涨停{len(sector_zt)}家

**驱动逻辑**：{get_driver_factor(sector['name'])}

**关注标的**：{sector_zt[0]['name'] if sector_zt else '待观察'}
"""

def generate_decline_detail(sector, fund_map, zt_stocks):
    """生成退潮期板块详情"""
    if not sector:
        return "暂无数据"
    
    return f"""**板块表现**：板块指数{sector['change_pct']:+.2f}%

**风险特征**：龙头跌停/中位股批量跌停
"""

def generate_chaos_content(sectors):
    """生成混沌期内容"""
    chaos = [s for s in sectors if -1 <= s['change_pct'] <= 1]
    if len(chaos) > 5:
        return f"当前有{len(chaos)}个板块震荡整理，快速轮动，无明确龙头，暂不参与。"
    return "当前无明显混沌期板块。"

def generate_attack_plan(strong_sectors):
    """生成进攻计划"""
    if strong_sectors:
        names = ', '.join([s['name'] for s in strong_sectors[:2]])
        return f"关注{names}等主升期板块龙头分歧机会"
    return "等待主升期板块出现"

def generate_watch_plan(rising_sectors):
    """生成观察计划"""
    if rising_sectors:
        return f"观察{rising_sectors[0]['name']}等发酵期板块是否晋升主线"
    return "观察市场新题材发酵"

def generate_avoid_plan(falling_sectors):
    """生成回避计划"""
    if falling_sectors:
        return f"回避{falling_sectors[0]['name']}等退潮期板块"
    return "暂无特别需要回避的方向"

def match_zt_stocks(sector_name, zt_stocks):
    """匹配涨停股"""
    sector_keywords = {
        '数字媒体': ['数字媒体', '传媒'],
        '海洋捕捞': ['渔业', '捕捞', '水产'],
        '航海装备': ['航海', '船舶', '造船', '海洋装备', '航空装备'],
        '文字媒体': ['出版', '媒体', '传媒'],
        '半导体': ['半导体', '芯片', '集成电路'],
        '券商': ['证券', '券商', '金融'],
        '新能源': ['新能源', '光伏', '风电', '锂电', '电源'],
        '电力': ['电力', '电网', '电源'],
    }
    
    matched = []
    keywords = sector_keywords.get(sector_name, [sector_name.replace('Ⅱ', '').replace('Ⅲ', '')])
    
    for z in zt_stocks:
        if z.get('industry'):
            if z['industry'] in sector_name or sector_name in z['industry']:
                matched.append(z)
            elif any(kw in z['industry'] for kw in keywords):
                matched.append(z)
    
    matched.sort(key=lambda x: x.get('boards', 0), reverse=True)
    return matched

def calculate_influence(sector, fund, zt_count):
    """计算板块影响力"""
    score = min(40, zt_count * 8)
    score += min(30, fund.get('net_inflow_pct', 0) * 2)
    score += min(20, zt_count * 3)
    score += min(10, abs(sector.get('change_pct', 0)))
    return min(100, int(score))

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
    score = min(40, dragon.get('boards', 0) * 8)
    score += min(30, dragon.get('amount', 0) / 1e8)
    score += 20 if dragon.get('is_first_board', False) else 0
    score += 10 if '龙头' in dragon.get('tags', []) else 0
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

def get_driver_factor(sector_name):
    """获取驱动因素"""
    drivers = {
        '半导体': '国产替代政策+周期反转',
        '芯片': 'AI算力需求+政策支持',
        '新能源': '产业趋势+订单落地',
        '券商': '市场活跃度提升+政策预期',
        '数字媒体': 'AI应用落地+内容变现',
        '海洋': '政策刺激+资源稀缺',
        '航海': '军工订单+造船周期',
    }
    for key, value in drivers.items():
        if key in sector_name:
            return value
    return '资金推动+情绪催化'

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
    
    report = generate_sector_analysis_report(date_str)
    
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
