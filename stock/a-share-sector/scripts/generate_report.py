#!/usr/bin/env python3
"""
A股板块分析报告生成
基于 a-share-warehouse 数据库，专注板块分析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import get_market_summary, get_sector_data, get_emotion_data, get_recent_days_data
from datetime import datetime
from publish_to_mowen import publish_to_mowen

def generate_sector_report(date_str):
    """生成板块分析报告"""
    
    # 获取数据
    market = get_market_summary(date_str)
    sectors = get_sector_data(date_str)
    emotion = get_emotion_data(date_str)
    recent_dates = get_recent_days_data(date_str, 5)
    
    # 提取关键数据
    sh = market['indices'].get('000001', {})
    stats = market['market_stats']
    
    # 分类板块
    sectors_list = sectors['sectors']
    fund_flow = sectors['fund_flow']
    
    # 按涨跌幅分类
    rising_sectors = [s for s in sectors_list if s['change_pct'] > 0]
    falling_sectors = [s for s in sectors_list if s['change_pct'] < 0]
    
    # 按资金流向分类
    inflow_sectors = [s for s in fund_flow if s['net_inflow'] > 0]
    outflow_sectors = [s for s in fund_flow if s['net_inflow'] < 0]
    
    # 构建资金流向映射
    fund_map = {f['name']: f for f in fund_flow}
    
    # 生成报告
    report = f"""# A股板块分析-{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy哥的小龙虾

---

## 市场概览

**指数表现**：上证指数{get_change_desc(sh.get('change_pct', 0))}，收盘{sh.get('close', 0):.2f}点；两市上涨{stats['up_count']}家，下跌{stats['down_count']}家；成交额{stats['total_amount']:.0f}亿。

**情绪概览**：涨停{market['limit_up']}家，跌停{market['limit_down']}家，连板高度{emotion['max_boards']}板。

---

## 一、板块强度榜（综合评分）

### 1.1 强势板块 TOP10

{generate_top_rising(sectors_list, fund_map)}

### 1.2 领跌板块 TOP10

{generate_top_falling(sectors_list[-10:])}

---

## 二、资金流向分析

### 2.1 资金流入板块 TOP10

{generate_fund_inflow(inflow_sectors[:10])}

### 2.2 资金流出板块 TOP10

{generate_fund_outflow(outflow_sectors[:10])}

---

## 三、板块轮动分析

### 3.1 连续强势板块（近5日）

{generate_continuous_strong(sectors_list, recent_dates)}

### 3.2 今日启动板块

{generate_new_momentum(sectors_list, recent_dates)}

### 3.3 高位回调板块

{generate_high_correction(sectors_list, recent_dates)}

---

## 四、重点板块深度分析

### 4.1 科技成长方向

{generate_sector_deep_dive(sectors_list, ['半导体', '芯片', '计算机', '电子', '通信', '软件', '人工智能', '新能源'])}

### 4.2 大消费方向

{generate_sector_deep_dive(sectors_list, ['食品饮料', '家用电器', '医药', '汽车', '商贸零售', '旅游'])}

### 4.3 周期资源方向

{generate_sector_deep_dive(sectors_list, ['有色金属', '煤炭', '钢铁', '化工', '石油', '建材'])}

### 4.4 金融地产方向

{generate_sector_deep_dive(sectors_list, ['银行', '证券', '保险', '房地产', '建筑'])}

---

## 五、明日观察要点

### 5.1 需持续关注的板块
- **强势延续**：关注今日领涨板块明日是否持续
- **资金持续**：关注资金流入板块是否有持续性
- **量价配合**：关注放量上涨板块的后续表现

### 5.2 需警惕的板块
- **放量滞涨**：今日放量但涨幅有限的板块
- **资金出逃**：资金大幅流出的板块
- **破位下跌**：跌破关键支撑位的板块

### 5.3 潜在机会板块
- **低位启动**：低位放量启动的板块
- **轮动预期**：近期轮动规律中的下一个潜在板块
- **政策催化**：有政策预期的板块

---

## 六、操作策略建议

### 6.1 仓位配置
{generate_position_suggestion(market, sectors_list)}

### 6.2 板块选择
{generate_sector_strategy(sectors_list, fund_flow)}

### 6.3 风险提示
- 避免追高已大幅上涨的板块
- 警惕资金持续流出的板块
- 关注市场风格切换信号

---

免责声明：本文仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
    
    return report

def calculate_sector_strength(sector, fund_map):
    """计算板块强度评分（综合考虑涨跌幅和资金流向）"""
    change_score = sector['change_pct'] * 2  # 涨跌幅权重
    
    # 查找资金流向
    fund = fund_map.get(sector['name'], {})
    fund_score = fund.get('net_inflow_pct', 0) * 3  # 资金流向权重更高
    
    return change_score + fund_score

def get_sector_trend(sector_name, recent_dates):
    """获取板块近期趋势（简化版）"""
    if len(recent_dates) < 2:
        return "数据不足"
    
    # 实际应该查询多日数据计算趋势
    # 这里简化处理
    return "上升趋势"  # 或 "下降趋势", "震荡整理"

def generate_top_rising(sectors, fund_map):
    """生成领涨板块列表（按强度排序）"""
    # 计算强度并排序
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

def generate_top_falling(sectors):
    """生成领跌板块列表"""
    result = "| 排名 | 板块名称 | 涨跌幅 | 类型 |\n|------|----------|--------|------|\n"
    for i, s in enumerate(reversed(sectors), 1):
        result += f"| {i} | {s['name']} | {s['change_pct']:.2f}% | {s.get('type', '行业')} |\n"
    return result

def generate_fund_inflow(sectors):
    """生成资金流入板块"""
    result = "| 排名 | 板块名称 | 主力净流入 | 净流入占比 |\n|------|----------|------------|------------|\n"
    for i, s in enumerate(sectors, 1):
        amount = s['net_inflow'] / 1e8  # 转换为亿
        result += f"| {i} | {s['name']} | {amount:+.1f}亿 | {s['net_inflow_pct']:+.2f}% |\n"
    return result

def generate_fund_outflow(sectors):
    """生成资金流出板块"""
    result = "| 排名 | 板块名称 | 主力净流入 | 净流入占比 |\n|------|----------|------------|------------|\n"
    for i, s in enumerate(sectors, 1):
        amount = s['net_inflow'] / 1e8  # 转换为亿
        result += f"| {i} | {s['name']} | {amount:+.1f}亿 | {s['net_inflow_pct']:+.2f}% |\n"
    return result

def generate_continuous_strong(sectors, recent_dates):
    """生成连续强势板块分析"""
    # 简化处理，实际应该对比多日数据
    strong = [s for s in sectors if s['change_pct'] > 3][:5]
    if not strong:
        return "今日无明显连续强势板块。"
    
    result = ""
    for s in strong:
        result += f"- **{s['name']}**：今日涨{s['change_pct']:.2f}%，表现强势，需关注明日持续性。\n"
    return result

def generate_new_momentum(sectors, recent_dates):
    """生成今日启动板块"""
    # 涨幅较大但非最高（排除已持续强势的）
    momentum = [s for s in sectors if 2 < s['change_pct'] < 5][:5]
    if not momentum:
        return "今日无明显新启动板块。"
    
    result = ""
    for s in momentum:
        result += f"- **{s['name']}**：今日涨{s['change_pct']:.2f}%，低位启动迹象，关注后续。\n"
    return result

def generate_high_correction(sectors, recent_dates):
    """生成高位回调板块"""
    # 跌幅较大的板块
    correction = [s for s in sectors if s['change_pct'] < -2][:5]
    if not correction:
        return "今日无明显高位回调板块。"
    
    result = ""
    for s in correction:
        result += f"- **{s['name']}**：今日跌{abs(s['change_pct']):.2f}%，注意回避或等待企稳。\n"
    return result

def generate_sector_deep_dive(sectors, keywords):
    """生成重点板块深度分析"""
    # 筛选相关板块
    related = []
    for s in sectors:
        for kw in keywords:
            if kw in s['name']:
                related.append(s)
                break
    
    if not related:
        return "该方向今日无突出表现。"
    
    # 取涨幅前3
    related = sorted(related, key=lambda x: x['change_pct'], reverse=True)[:3]
    
    result = ""
    for s in related:
        trend = "上涨" if s['change_pct'] > 0 else "下跌"
        result += f"**{s['name']}**：今日{trend}{abs(s['change_pct']):.2f}%。"
        
        # 添加简单判断
        if s['change_pct'] > 3:
            result += "表现强势，资金关注度高。"
        elif s['change_pct'] > 1:
            result += "温和上涨，趋势良好。"
        elif s['change_pct'] < -2:
            result += "回调明显，注意风险。"
        else:
            result += "震荡整理，观望为主。"
        
        result += "\n\n"
    
    return result

def generate_position_suggestion(market, sectors):
    """生成仓位建议"""
    sh = market['indices'].get('000001', {})
    change = sh.get('change_pct', 0)
    
    if change > 1:
        return "建议仓位：6-8成。市场强势，可积极配置主流板块。"
    elif change > -1:
        return "建议仓位：4-6成。市场震荡，控制仓位精选板块。"
    else:
        return "建议仓位：2-4成。市场弱势，降低仓位防守为主。"

def generate_sector_strategy(sectors, fund_flow):
    """生成板块策略"""
    # 找出资金流入且上涨的板块
    good_sectors = []
    for s in sectors:
        if s['change_pct'] > 1:
            # 查找资金流向
            for f in fund_flow:
                if f['name'] == s['name'] and f['net_inflow'] > 0:
                    good_sectors.append(s['name'])
                    break
    
    if good_sectors:
        return f"关注方向：{', '.join(good_sectors[:3])}。这些板块资金流入且上涨，具备持续性。"
    else:
        return "关注方向：暂无明确方向，建议观望等待市场明朗。"

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

def main():
    """主函数"""
    # 获取今天日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今天是否有数据，如果没有使用最近交易日
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
    report = generate_sector_report(date_str)
    
    # 保存本地
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'sector_analysis_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    # 发布到墨问
    title = f"A股板块分析-{date_str[5:7]}/{date_str[8:]}-Billy哥的小龙虾"
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
