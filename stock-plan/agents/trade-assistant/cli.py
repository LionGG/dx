#!/usr/bin/env python3
"""
交易助手命令行接口
用于子代理直接调用
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core import TradeAssistant, get_assistant
from parser import TradePlanParser


def cmd_record_plan(text: str, date: str = None):
    """记录交易计划"""
    parser = TradePlanParser()
    plan_data = parser.parse(text, date)
    
    assistant = get_assistant()
    plan_id = assistant.save_plan(plan_data)
    assistant.close()
    
    print(json.dumps({
        'success': True,
        'plan_id': plan_id,
        'data': plan_data
    }, ensure_ascii=False, indent=2))


def cmd_list_plans(date: str = None):
    """列出交易计划"""
    assistant = get_assistant()
    plans = assistant.get_today_plans() if date is None else []
    assistant.close()
    
    print(json.dumps({
        'count': len(plans),
        'plans': plans
    }, ensure_ascii=False, indent=2))


def cmd_compare(date: str = None):
    """对比计划与执行"""
    assistant = get_assistant()
    result = assistant.compare_plan_execution(date)
    assistant.close()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_analyze(days: int = 30):
    """分析交易模式"""
    assistant = get_assistant()
    result = assistant.analyze_patterns(days)
    assistant.close()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_daily_summary(date: str = None):
    """生成日报"""
    assistant = get_assistant()
    result = assistant.generate_daily_summary(date)
    assistant.close()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_save_review(content: str, emotion: str = None, plan_id: str = None):
    """保存复盘"""
    date = datetime.now().strftime('%Y-%m-%d')
    
    assistant = get_assistant()
    review_id = assistant.save_review(date, content, emotion, None, plan_id)
    assistant.close()
    
    print(json.dumps({
        'success': True,
        'review_id': review_id
    }, ensure_ascii=False))


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command> [args...]")
        print("")
        print("Commands:")
        print("  record_plan <text> [date]     记录交易计划")
        print("  list_plans [date]             列出计划")
        print("  compare [date]                对比计划与执行")
        print("  analyze [days]                分析交易模式")
        print("  daily_summary [date]          生成日报")
        print("  save_review <content> [emotion] [plan_id]  保存复盘")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'record_plan':
        if len(sys.argv) < 3:
            print("Error: text required")
            sys.exit(1)
        text = sys.argv[2]
        date = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_record_plan(text, date)
    
    elif command == 'list_plans':
        date = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_list_plans(date)
    
    elif command == 'compare':
        date = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_compare(date)
    
    elif command == 'analyze':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cmd_analyze(days)
    
    elif command == 'daily_summary':
        date = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_daily_summary(date)
    
    elif command == 'save_review':
        if len(sys.argv) < 3:
            print("Error: content required")
            sys.exit(1)
        content = sys.argv[2]
        emotion = sys.argv[3] if len(sys.argv) > 3 else None
        plan_id = sys.argv[4] if len(sys.argv) > 4 else None
        cmd_save_review(content, emotion, plan_id)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
