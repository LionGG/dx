#!/usr/bin/env python3
"""
美股收盘数据获取并发送卡片
每天 07:40 执行，推送昨晚美股收盘数据
使用东方财富API获取三大指数、科技股、中概股数据

美股交易时间：美东时间周一到周五
北京时间推送：周二到周六早上7:40（对应美东周一到周五收盘）
"""

import sys
import json
import requests
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from feishu_card_wrapper import FeishuCardWrapper

BAOZONG_OPEN_ID = "ou_7b3b64c0a18c735401f4e1d172d4c802"

def get_eastmoney_data(secids, fields="f12,f13,f14,f2,f3,f4"):
    """从东方财富获取数据"""
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get"
    params = {
        "fltt": 2,
        "invt": 2,
        "fields": fields,
        "secids": secids
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        return data.get('data', {}).get('diff', [])
    except Exception as e:
        print(f"⚠️ 获取数据失败: {e}")
        return []

def analyze_market_attribution(indices, tech_stocks, china_stocks):
    """基于数据生成市场归因分析"""
    attribution = []
    
    nasdaq = next((i for i in indices if i['name'] == '纳斯达克'), None)
    spx = next((i for i in indices if i['name'] == '标普500'), None)
    
    if not nasdaq or not spx:
        return ["市场波动，需关注后续走势"]
    
    nasdaq_change = nasdaq['change']
    spx_change = spx['change']
    
    if nasdaq_change < -2.0:
        attribution.append("科技股大幅回调，纳指领跌市场")
    elif nasdaq_change < -1.0:
        attribution.append("科技股承压，市场情绪偏谨慎")
    elif nasdaq_change > 1.0:
        attribution.append("科技股领涨，市场风险偏好回升")
    
    if tech_stocks:
        tech_down = [s for s in tech_stocks if s['change'] < -2.0]
        if len(tech_down) >= 2:
            attribution.append("大型科技股集体下挫，拖累大盘")
        elif any(s['change'] < -3.0 for s in tech_stocks):
            worst = min(tech_stocks, key=lambda x: x['change'])
            attribution.append(f"{worst['name']}等权重股大跌，引发市场担忧")
    
    if spx_change < -1.5:
        attribution.append("市场担忧通胀与利率前景，避险情绪升温")
    elif spx_change < -1.0:
        attribution.append("宏观经济数据引发市场对增长前景的担忧")
    
    if china_stocks:
        china_avg = sum(s['change'] for s in china_stocks) / len(china_stocks)
        if china_avg > spx_change + 0.5:
            attribution.append("中概股表现相对抗跌，跑赢美股大盘")
        elif china_avg < spx_change - 0.5:
            attribution.append("中概股跌幅较大，受中美关系等因素影响")
    
    if not attribution:
        attribution.append("市场技术性调整，关注后续美联储政策动向")
    
    return attribution

def get_us_stock_data():
    """获取美股收盘数据"""
    indices_data = get_eastmoney_data("100.DJIA,100.NDX,100.SPX")
    
    indices = []
    index_names = {'DJIA': '道琼斯', 'NDX': '纳斯达克', 'SPX': '标普500'}
    
    for item in indices_data:
        code = item.get('f12', '')
        name = index_names.get(code, item.get('f14', code))
        value = item.get('f2', 0)
        change_pct = item.get('f3', 0)
        change_val = item.get('f4', 0)
        
        indices.append({
            'name': name,
            'value': f"{value:,.2f}",
            'change': change_pct,
            'change_value': f"{change_val:+.2f}"
        })
    
    # 获取科技股
    tech_codes = "105.AAPL,105.MSFT,105.NVDA,105.TSLA,105.AMZN,105.GOOGL"
    tech_data = get_eastmoney_data(tech_codes)
    
    tech_stocks = []
    for item in tech_data:
        name = item.get('f14', '')
        change_pct = item.get('f3', 0)
        name_map = {'苹果': '苹果', 'AAPL': '苹果', '微软': '微软', 'MSFT': '微软',
                   '英伟达': '英伟达', 'NVDA': '英伟达', '特斯拉': '特斯拉', 'TSLA': '特斯拉',
                   '亚马逊': '亚马逊', 'AMZN': '亚马逊', '谷歌-A': '谷歌', 'GOOGL': '谷歌'}
        short_name = name_map.get(name, name)
        tech_stocks.append({'name': short_name, 'change': change_pct})
    
    # 获取中概股
    china_codes = "105.BABA,105.JD,105.PDD,105.BIDU,105.NIO"
    china_data = get_eastmoney_data(china_codes)
    
    china_stocks = []
    for item in china_data:
        name = item.get('f14', '')
        change_pct = item.get('f3', 0)
        name_map = {'阿里巴巴': '阿里', 'BABA': '阿里', '京东': '京东', 'JD': '京东',
                   '拼多多': '拼多多', 'PDD': '拼多多', '百度': '百度', 'BIDU': '百度',
                   '蔚来': '蔚来', 'NIO': '蔚来'}
        short_name = name_map.get(name, name)
        china_stocks.append({'name': short_name, 'change': change_pct})
    
    # 生成市场归因
    attribution = analyze_market_attribution(indices, tech_stocks, china_stocks)
    
    # 生成市场要点
    nasdaq_item = next((i for i in indices if i['name'] == '纳斯达克'), None)
    spx_item = next((i for i in indices if i['name'] == '标普500'), None)
    
    highlights = []
    if nasdaq_item and spx_item:
        direction = '收涨' if spx_item['change'] > 0 else '收跌'
        leader = '领涨' if nasdaq_item['change'] > max([i['change'] for i in indices]) else '领跌'
        highlights.append(f"三大指数全线{direction}，纳指{leader}({nasdaq_item['change']:+.2f}%)")
    
    highlights.extend(attribution)
    
    return {
        'indices': indices,
        'tech_stocks': tech_stocks,
        'china_stocks': china_stocks,
        'highlights': highlights
    }

def build_card_content(data, date_str):
    """构建卡片内容"""
    lines = [f"**美东时间 {date_str} 收盘**\n"]
    
    lines.append("**主要指数：**")
    for idx in data['indices']:
        emoji = "📈" if idx['change'] > 0 else "📉"
        lines.append(f"{emoji} **{idx['name']}**: {idx['value']} ({idx['change']:+.2f}%, {idx['change_value']})")
    
    if data.get('tech_stocks'):
        lines.append("\n**科技股表现：**")
        for stock in data['tech_stocks']:
            emoji = "📈" if stock['change'] > 0 else "📉"
            lines.append(f"{emoji} {stock['name']}: {stock['change']:+.2f}%")
    
    if data.get('china_stocks'):
        lines.append("\n**中概股表现：**")
        for stock in data['china_stocks']:
            emoji = "📈" if stock['change'] > 0 else "📉"
            lines.append(f"{emoji} {stock['name']}: {stock['change']:+.2f}%")
    
    if data.get('highlights'):
        lines.append("\n**市场要点：**")
        for hl in data['highlights']:
            lines.append(f"• {hl}")
    
    return '\n'.join(lines)

def main():
    # 计算昨晚美股日期
    yesterday = datetime.now() - timedelta(days=1)
    weekday = yesterday.weekday()  # 0=周一, 6=周日
    date_str = yesterday.strftime("%Y-%m-%d")
    
    # 美股美东时间周一到周五开盘
    # weekday 0-4 对应美东周一到周五
    if weekday >= 5:  # 周六(5)或周日(6)
        print(f"📅 美东时间 {date_str} 是{'周六' if weekday == 5 else '周日'}，美股休市")
        return 0
    
    print(f"🌙 正在获取美东时间 {date_str} (周{'一二三四五六日'[weekday]}) 美股收盘数据...")
    
    try:
        data = get_us_stock_data()
        
        if not data['indices']:
            print("❌ 未能获取到指数数据")
            return 1
        
        wrapper = FeishuCardWrapper()
        content = build_card_content(data, date_str)
        
        result = wrapper.sender.send_simple_card(
            receive_id=BAOZONG_OPEN_ID,
            receive_id_type='open_id',
            title=f"🌙 美股收盘 | {date_str}",
            content=content
        )
        
        print(f"✅ 美股收盘卡片发送成功")
        print(f"📤 消息ID: {result.get('message_id', 'N/A')}")
        return 0
        
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
