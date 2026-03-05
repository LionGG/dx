#!/usr/bin/env python3
"""
读取短线情绪研判数据
复用 a-share-dx 的分析结论
"""

import sqlite3
from datetime import datetime

DX_DB_PATH = '/root/.openclaw/workspace/stock/a-share-dx/data/duanxian.db'

def get_latest_market_analysis():
    """获取最新市场分析"""
    conn = sqlite3.connect(DX_DB_PATH)
    cursor = conn.cursor()
    
    # 获取最新分析
    cursor.execute('''
        SELECT date, phase, action, summary, mowen_link 
        FROM daily_reports 
        ORDER BY date DESC 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    
    # 获取最新情绪数据
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, consecutive_height
        FROM market_sentiment
        ORDER BY date DESC
        LIMIT 1
    ''')
    sentiment = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'date': row[0],
            'phase': row[1],           # 如：退潮期，冰点试探中
            'action': row[2],          # 如：关注冰点期新题材首板
            'summary': row[3],         # 如：冰点未至，但已在路上
            'mowen_link': row[4],
            'sentiment_index': sentiment[1] if sentiment else None,
            'limit_up': sentiment[2] if sentiment else None,
            'limit_down': sentiment[3] if sentiment else None,
            'max_boards': sentiment[4] if sentiment else None,  # consecutive_height
        }
    return None

def get_sector_analysis():
    """获取板块分析（从web/data.json）"""
    import json
    try:
        with open('/root/.openclaw/workspace/stock/a-share-dx/web/data.json', 'r') as f:
            data = json.load(f)
        return {
            'latest': data.get('data', [])[-1] if data.get('data') else None,
            'trend': data.get('data', [])[-5:] if len(data.get('data', [])) >= 5 else data.get('data', [])
        }
    except:
        return None

def generate_trading_context():
    """生成交易环境上下文"""
    analysis = get_latest_market_analysis()
    sector = get_sector_analysis()
    
    if not analysis:
        return "暂无市场分析数据"
    
    context = f"""## 市场环境（{analysis['date']}）

**情绪周期**：{analysis['phase']}

**数据概览**：
- 情绪指数：{analysis['sentiment_index']}
- 涨停：{analysis['limit_up']}家 / 跌停：{analysis['limit_down']}家
- 连板高度：{analysis['max_boards']}板

**策略建议**：{analysis['action']}

**市场总结**：{analysis['summary']}

**详细分析**：{analysis['mowen_link']}
"""
    return context

if __name__ == '__main__':
    print(generate_trading_context())
