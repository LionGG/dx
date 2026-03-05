#!/usr/bin/env python3
"""
检查AKShare数据源状态，如果延迟则发送通知
"""

import akshare as ak
from datetime import datetime
import sys

sys.path.insert(0, '/root/.openclaw/workspace/stock/dx/scripts')
from feishu_notifier import send_to_feishu_group

def check_data_source():
    """检查AKShare数据源是否最新"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"检查日期: {today}")
    print("="*60)
    
    issues = []
    
    # 检查上证指数
    try:
        df = ak.stock_zh_index_daily(symbol='sh000001')
        latest_date = df['date'].iloc[-1]
        print(f"上证指数: 最新数据 {latest_date}")
        if latest_date != today:
            issues.append(f"上证指数数据延迟: {latest_date} (期望: {today})")
    except Exception as e:
        issues.append(f"上证指数获取失败: {e}")
    
    # 检查创业板指
    try:
        df = ak.stock_zh_index_daily(symbol='sz399006')
        latest_date = df['date'].iloc[-1]
        print(f"创业板指: 最新数据 {latest_date}")
        if latest_date != today:
            issues.append(f"创业板指数据延迟: {latest_date} (期望: {today})")
    except Exception as e:
        issues.append(f"创业板指获取失败: {e}")
    
    print("="*60)
    
    if issues:
        print("⚠️ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False, issues
    else:
        print("✅ 数据源正常")
        return True, []

if __name__ == '__main__':
    ok, issues = check_data_source()
    
    if not ok:
        # 发送飞书通知
        today = datetime.now().strftime('%Y-%m-%d')
        message = f"""⚠️ AKShare数据源延迟通知

日期: {today}

发现问题:
"""
        for issue in issues:
            message += f"  • {issue}\n"
        
        message += """
影响:
• 短线情绪研判报告可能无法生成完整指数数据
• HTML页面K线图可能缺失

建议:
1. 等待数据源更新（通常收盘后1-2小时）
2. 手动重新运行 daily_pipeline.py
3. 或考虑使用备用数据源
"""
        send_to_feishu_group(message)
        print("\n已发送飞书通知")
    
    sys.exit(0 if ok else 1)
