#!/usr/bin/env python3
"""
判断交易日工具
从数据库中获取历史交易日列表，判断某天是否为交易日
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def get_trading_dates():
    """获取所有历史交易日列表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT date FROM stock_kline ORDER BY date')
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dates

def is_trading_date(date_str):
    """
    判断某天是否为交易日
    
    参数:
        date_str: 日期字符串，格式 'YYYY-MM-DD' 或 'YYYYMMDD'
    
    返回:
        bool: 是否为交易日
    """
    # 统一格式
    if len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    # 首先判断是否为周末
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = date_obj.weekday()  # 0=周一, 6=周日
    if weekday >= 5:  # 周六或周日
        return False
    
    # 查询交易日历表
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否有交易日历表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_calendar'")
    if cursor.fetchone():
        cursor.execute('SELECT is_trading_day FROM trading_calendar WHERE date = ?', (date_str,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0] == 1
    else:
        conn.close()
    
    # 如果没有交易日历表，使用历史数据
    trading_dates = get_trading_dates()
    
    # 如果在历史列表中，肯定是交易日
    if date_str in trading_dates:
        return True
    
    # 如果是今天或未来日期，且不是周末，假设是交易日
    today = datetime.now().strftime('%Y-%m-%d')
    if date_str >= today:
        return True
    
    # 如果是过去日期但不在列表中，可能是节假日
    return False

def get_last_trading_date(date=None):
    """
    获取最近一个交易日
    
    参数:
        date: 基准日期，默认为今天。格式 datetime 或 'YYYY-MM-DD'
    
    返回:
        str: 最近交易日，格式 'YYYY-MM-DD'
    """
    if date is None:
        date = datetime.now()
    elif isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    trading_dates = get_trading_dates()
    
    # 从基准日期往前找最近交易日
    check_date = date
    while True:
        date_str = check_date.strftime('%Y-%m-%d')
        if date_str in trading_dates:
            return date_str
        check_date -= timedelta(days=1)
        
        # 防止无限循环，最多查365天
        if (date - check_date).days > 365:
            return None

def get_next_trading_date(date=None):
    """
    获取下一个交易日
    
    参数:
        date: 基准日期，默认为今天。格式 datetime 或 'YYYY-MM-DD'
    
    返回:
        str: 下一个交易日，格式 'YYYY-MM-DD'
    """
    if date is None:
        date = datetime.now()
    elif isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    trading_dates = get_trading_dates()
    
    # 从基准日期往后找下一个交易日
    check_date = date + timedelta(days=1)
    while True:
        date_str = check_date.strftime('%Y-%m-%d')
        if date_str in trading_dates:
            return date_str
        check_date += timedelta(days=1)
        
        # 防止无限循环
        if (check_date - date).days > 365:
            return None

def get_today_trading_date():
    """
    获取今天对应的交易日
    - 如果今天是交易日，返回今天
    - 如果今天不是交易日（周末/节假日），返回最近一个交易日
    
    返回:
        str: 交易日，格式 'YYYY-MM-DD'
    """
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    
    if is_trading_date(today_str):
        return today_str
    else:
        return get_last_trading_date(today)

def format_date(date_str, output_format='dash'):
    """
    格式化日期字符串
    
    参数:
        date_str: 输入日期，格式 'YYYY-MM-DD' 或 'YYYYMMDD'
        output_format: 输出格式，'dash'='YYYY-MM-DD', 'compact'='YYYYMMDD'
    
    返回:
        str: 格式化后的日期
    """
    if len(date_str) == 8:
        # YYYYMMDD -> YYYY-MM-DD
        dash_format = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    else:
        dash_format = date_str
    
    if output_format == 'compact':
        return dash_format.replace('-', '')
    return dash_format

if __name__ == '__main__':
    # 测试
    print("交易日判断工具测试")
    print("=" * 50)
    
    trading_dates = get_trading_dates()
    print(f"历史交易日数量: {len(trading_dates)}")
    print(f"最早交易日: {trading_dates[0]}")
    print(f"最晚交易日: {trading_dates[-1]}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n今天 ({today}) 是交易日: {is_trading_date(today)}")
    
    last_trading = get_last_trading_date()
    print(f"最近交易日: {last_trading}")
    
    today_trading = get_today_trading_date()
    print(f"今天对应的交易日: {today_trading}")
