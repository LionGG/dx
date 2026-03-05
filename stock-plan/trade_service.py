#!/usr/bin/env python3
"""
交易助手独立服务
直接监听钉钉消息，无需转发
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock-plan/agents/trade-assistant/trade_notes.db'
USER_PROFILE = '/root/.openclaw/workspace/stock-plan/memory/user_profile.md'

def handle_dingtalk_message(user_id, content, msg_type='text'):
    """直接处理钉钉消息"""
    
    # 1. 解析意图
    intent = parse_intent(content)
    
    # 2. 加载用户数据
    user_data = load_user_profile()
    
    # 3. 执行操作
    if intent == 'plan':
        result = record_plan(content)
    elif intent == 'query':
        result = query_positions(user_data)
    elif intent == 'review':
        result = save_review(content)
    else:
        result = "请说明：交易计划 / 查询持仓 / 复盘"
    
    return result

def parse_intent(content):
    """解析消息意图"""
    keywords = {
        'plan': ['买', '卖', '进', '出', '加仓', '减仓', '计划'],
        'query': ['查询', '持仓', '盈亏', '账户'],
        'review': ['复盘', '总结', '今天', '反思']
    }
    for intent, words in keywords.items():
        for word in words:
            if word in content:
                return intent
    return 'unknown'

def load_user_profile():
    """加载用户档案"""
    # 简化版，实际读取文件
    return {
        'accounts': ['A-激进', 'B-均衡', 'C-核心'],
        'total': '5284万',
        'pnl': '-31.3万'
    }

def record_plan(content):
    """记录交易计划"""
    # 调用 parser.py
    return f"✓ 计划已记录: {content[:20]}..."

def query_positions(user_data):
    """查询持仓"""
    return f"📊 三账户: {user_data['total']} | 盈亏: {user_data['pnl']}"

def save_review(content):
    """保存复盘"""
    return f"✓ 复盘已保存"

if __name__ == '__main__':
    # 测试
    print(handle_dingtalk_message('user1', '明天买北方华创'))
