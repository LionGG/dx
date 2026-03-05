#!/usr/bin/env python3
"""
记录交易计划到数据库
"""

import sqlite3
import sys
sys.path.insert(0, '/root/.openclaw/workspace/agents/trade-assistant')
from parser import TradePlanParser
from datetime import datetime

def save_plan(plan_data):
    conn = sqlite3.connect('/root/.openclaw/workspace/agents/trade-assistant/trade_notes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trade_plans (
            id, date, created_at, raw_content, symbol, name, action,
            condition_type, condition_value, position_pct, stop_loss, take_profit,
            sentiment_score, certainty_level, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        plan_data['id'], plan_data['date'], plan_data['created_at'],
        plan_data['raw_content'], plan_data['symbol'], plan_data['name'],
        plan_data['action'], plan_data['condition_type'], plan_data['condition_value'],
        plan_data['position_pct'], plan_data['stop_loss'], plan_data['take_profit'],
        plan_data['sentiment_score'], plan_data['certainty_level'], plan_data['status']
    ))
    
    conn.commit()
    conn.close()
    print(f"计划已保存: {plan_data['id']}")

if __name__ == '__main__':
    # 手动构建计划数据（因为语音内容较复杂，parser无法完全提取）
    plan = {
        'id': 'plan_' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'date': '2026-02-24',
        'created_at': datetime.now().isoformat(),
        'raw_content': '港股假期表现还行，明天用融资加仓券商或威胜信息，补仓后冲高踢掉，让个别股票扭亏为盈',
        'symbol': 'MULTI',  # 多标的
        'name': '券商板块/威胜信息',
        'action': 'buy',
        'condition_type': 'time',  # 开盘即操作
        'condition_value': None,
        'position_pct': None,  # 融资加仓，比例未明确
        'stop_loss': None,
        'take_profit': None,
        'sentiment_score': 60,
        'certainty_level': 'medium',
        'status': 'active'
    }
    
    save_plan(plan)
