#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师版）
基于新prompt：板块阶段分析 + 实战策略
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data, get_recent_days_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

def generate_sector_analysis_report(date_str):
    """生成板块分析报告（交易大师版）"""
    
    # 获取数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    recent_dates = get_recent_days_data(date_str, 5)
    
    # 提取关键数据（仅作分析参考，不输出）
    sh = market['indices'].get('000001', {})
    sectors_list = sectors['sectors']
    fund_flow = sectors['fund_flow']
    fund_map = {f['name']: f for f in fund_flow}
    
    # 分类板块（基于涨跌幅和资金流向）
    strong_sectors = [s for s in sectors_list if s['change_pct'] > 3]
    rising_sectors = [s for s in sectors_list if 2 <= s['change_pct'] <= 3]
    falling_sectors = [s for s in sectors_list if s['change_pct'] < -2]
    
    # 生成报告
    report = f"""# A股板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主升期板块（当前核心战场）

{generate_main_rise_sectors(strong_sectors, fund_map, emotion, market)}

---

## 二、发酵期板块（明日潜在主线）

{generate_fermentation_sectors(rising_sectors, fund_map)}

---

## 三、高位震荡板块（只卖不买）

{generate_high_shake_sectors(sectors_list, fund_map)}

---

## 四、退潮期板块（坚决回避）

{generate_decline_sectors(falling_sectors, fund_map)}

---

## 五、混沌期板块（观察等待）

{generate_chaos_sectors(sectors_list)}

---

## 六、明日作战计划

### 6.1 重点进攻方向
{generate_attack_plan(strong_sectors)}

### 6.2 观察等待方向
{generate_watch_plan(rising_sectors)}

### 6.3 坚决回避方向
{generate_avoid_plan(falling_sectors)}

### 6.4 仓位建议
{generate_position_advice(sh.get('change_pct', 0), len(strong_sectors))}

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    
    return report

def generate_main_rise_sectors(sectors, fund_map, emotion, market):
    """生成主升期板块分析（含龙头识别）"""
    if not sectors:
        return "当前无明显主升期板块，市场处于分化或混沌期。"
    
    result = ""
    limit_up = emotion.get('limit_up', 50)
    zt_stocks = emotion.get('zt_stocks', [])  # 从emotion获取
    
    for i, s in enumerate(sectors[:3], 1):
        fund = fund_map.get(s['name'], {})
        
        # 识别板块内龙头 - 使用行业匹配
        sector_zt = []
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
        
        # 直接匹配
        for z in zt_stocks:
            if z.get('industry'):
                # 精确匹配
                if z['industry'] in s['name'] or s['name'] in z['industry']:
                    sector_zt.append(z)
                    continue
                # 关键词匹配
                keywords = sector_keywords.get(s['name'], [s['name'].replace('Ⅱ', '').replace('Ⅲ', '')])
                if any(kw in z['industry'] for kw in keywords):
                    sector_zt.append(z)
        
        sector_zt.sort(key=lambda x: x.get('boards', 0), reverse=True)
        
        # 龙头梯队识别
        total_dragon = sector_zt[0] if sector_zt else None
        mid_dragon = identify_mid_dragon(s['name'], market)
        follow_dragon = sector_zt[1] if len(sector_zt) > 1 else None
        
        # 计算板块影响力
        influence_score = calculate_influence(s, fund, len(sector_zt))
        
        result += f"""### {s['name']}

**板块表现**：板块指数{s['change_pct']:+.2f}%，涨停{len(sector_zt)}家，占全市涨停{min(30, int(len(sector_zt)/max(limit_up,1)*100))}%

**板块影响力**：{influence_score}/100分（涨停家数{len(sector_zt)*5}分+资金流入{fund.get('net_inflow_pct', 0)*2:.0f}分+辨识度{min(20, len(sector_zt)*3)}分）

**龙头梯队**：
- **总龙头**：{total_dragon['name'] if total_dragon else '待识别'} {total_dragon['boards'] if total_dragon else 'X'}板（逻辑：{get_driver_factor(s['name'])}，状态：{get_dragon_status(total_dragon)}，辨识度：{calculate_recognition(total_dragon)}/100）
- **中军**：{mid_dragon['name'] if mid_dragon else '待识别'}（趋势：5日线上{get_trend_status(mid_dragon)}，成交额{mid_dragon.get('amount', 'X')}亿，板块影响力：{mid_dragon.get('influence', '中')}）
- **补涨龙**：{follow_dragon['name'] if follow_dragon else '待识别'} {follow_dragon['boards'] if follow_dragon else 'X'}板（{get_follow_quality(follow_dragon)}）

**驱动因素**：{get_driver_factor(s['name'])}

**持续性判断**：{get_sustainability(s, fund, len(sector_zt))}

**参与策略**：{get_strategy(s, total_dragon)}

**风险预警**：{get_risk_warning(s, total_dragon, len(sector_zt))}

"""
    return result

def generate_fermentation_sectors(sectors, fund_map):
    """生成发酵期板块分析"""
    if not sectors:
        return "当前无明显发酵期板块。"
    
    result = ""
    for i, s in enumerate(sectors[:2], 1):
        fund = fund_map.get(s['name'], {})
        
        result += f"""### {s['name']}

**表现**：启动2-3日，涨停家数待统计，梯队待观察

**驱动逻辑**：{get_driver_factor(s['name'])}，新催化/老主线分支延伸

**晋升潜力**：【可能晋升主线】，观察明日是否出现板块性涨停潮及龙头强度

**关注标的**：潜在龙头待识别

"""
    return result

def generate_high_shake_sectors(sectors, fund_map):
    """生成高位震荡板块分析"""
    # 筛选近期涨幅大但今日涨幅小的板块
    shake_sectors = [s for s in sectors if 0 < s['change_pct'] < 2 and s['change_pct'] > 5]
    
    if not shake_sectors:
        return "当前无明显高位震荡板块。"
    
    result = ""
    for s in shake_sectors[:2]:
        result += f"""### {s['name']}

**状态**：龙头滞涨但未跌停，高位横盘，补涨股活跃但随机性强

**特征**：成交量萎缩/筹码松动/消息刺激钝化

**策略**：只卖不买，等待二波信号或彻底退潮确认

"""
    return result

def generate_decline_sectors(sectors, fund_map):
    """生成退潮期板块分析"""
    if not sectors:
        return "当前无明显退潮期板块。"
    
    result = ""
    for i, s in enumerate(sectors[:2], 1):
        result += f"""### {s['name']}

**表现**：龙头跌停/连板股批量跌停/阴跌不止

**风险**：A杀/核按钮/反弹即是卖点

**策略**：坚决回避，不抄底，不抢反弹

"""
    return result

def generate_chaos_sectors(sectors):
    """生成混沌期板块分析"""
    # 筛选震荡的板块
    chaos = [s for s in sectors if -1 <= s['change_pct'] <= 1]
    
    if len(chaos) > 10:
        return f"当前有{len(chaos)}个板块震荡整理，快速轮动，无明确龙头，等待题材明确或新催化，暂不参与。"
    return "当前无明显混沌期板块。"

def generate_attack_plan(strong_sectors):
    """生成进攻计划"""
    if strong_sectors:
        return f"关注{strong_sectors[0]['name']}等主升期板块龙头分歧机会"
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

def generate_position_advice(index_change, main_sector_count):
    """生成仓位建议"""
    if main_sector_count >= 2 and index_change > 0:
        return "市场强势，主升期板块明确，建议6-8成仓位，重点参与主线"
    elif main_sector_count >= 1:
        return "市场震荡，有主线但分化，建议4-6成仓位，精选个股"
    else:
        return "市场弱势，无明显主线，建议2-4成仓位，防守为主"

def get_driver_factor(sector_name):
    """获取板块驱动因素（简化版）"""
    drivers = {
        '半导体': '国产替代政策+周期反转',
        '芯片': 'AI算力需求+政策支持',
        '新能源': '产业趋势+订单落地',
        '券商': '市场活跃度提升+政策预期',
        '银行': '高股息防御+估值修复',
        'AI': '技术突破+应用场景落地',
        '医药': '创新药政策+业绩改善',
        '消费': '复苏预期+政策刺激',
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

def identify_mid_dragon(sector_name, market):
    """识别中军股（成交额大、趋势稳）"""
    # 简化版，实际应查询板块内成交额最大的非连板股
    return {'name': '待识别', 'amount': 'X', 'influence': '中', 'trend': '稳定'}

def calculate_influence(sector, fund, zt_count):
    """计算板块影响力分数"""
    score = min(40, zt_count * 8)  # 涨停家数分数
    score += min(30, fund.get('net_inflow_pct', 0) * 2)  # 资金分数
    score += min(20, zt_count * 3)  # 辨识度分数
    score += min(10, abs(sector.get('change_pct', 0)))  # 涨幅分数
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
    """计算辨识度分数"""
    if not dragon:
        return 50
    score = min(40, dragon.get('boards', 0) * 8)  # 连板高度
    score += min(30, dragon.get('amount', 0) / 1e8)  # 成交额
    score += 20 if dragon.get('is_first_board', False) else 0  # 首板时间
    score += 10 if '龙头' in dragon.get('tags', []) else 0  # 标签
    return min(100, int(score))

def get_trend_status(stock):
    """判断趋势状态"""
    if not stock:
        return '加速'
    return stock.get('trend', '加速')

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

def get_sustainability(sector, fund, zt_count):
    """判断持续性"""
    if sector.get('change_pct', 0) > 5 and fund.get('net_inflow_pct', 0) > 2:
        return '主升加速，预计明日分化，关注龙头承接'
    elif zt_count >= 5:
        return '强上强，关注前排持续性'
    else:
        return '跟风上涨，持续性存疑'

def get_strategy(sector, dragon):
    """生成参与策略"""
    if sector.get('change_pct', 0) > 5:
        return '去弱留强，只盯龙头分歧机会，后排补涨已不安全，勿追高'
    elif dragon and dragon.get('boards', 0) >= 5:
        return '龙头高位，只考虑分歧低吸，不追涨'
    else:
        return '关注龙头晋级机会，后排谨慎'

def get_risk_warning(sector, dragon, zt_count):
    """生成风险预警"""
    risks = []
    if sector.get('change_pct', 0) > 6:
        risks.append('一致性过高')
    if dragon and dragon.get('boards', 0) >= 6:
        risks.append('监管函风险')
    if zt_count > 10:
        risks.append('板块过热')
    return '、'.join(risks) if risks else '注意分化风险'

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
        print(f"生成 {today} 的板块分析报告...")
        date_str = today
    
    # 生成报告
    report = generate_sector_analysis_report(date_str)
    
    # 保存本地
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'sector_analysis_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    # 发布到墨问
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
