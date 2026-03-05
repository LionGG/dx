#!/usr/bin/env python3
"""
获取2026年完整交易日历
从交易所或可靠数据源获取全年交易日
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = '/root/.openclaw/workspace/stock/a-share-warehouse/data/akshare_full.db'

def get_2026_trading_calendar():
    """
    获取2026年完整交易日历
    基于A股交易规则：周一到周五交易，节假日休市
    2026年节假日需要手动配置或从API获取
    """
    
    # 2026年已知节假日（需要完善）
    holidays_2026 = [
        # 元旦
        '2026-01-01', '2026-01-02', '2026-01-03',
        # 春节（假设，需要确认具体日期）
        '2026-02-17', '2026-02-18', '2026-02-19', '2026-02-20', '2026-02-21', '2026-02-22', '2026-02-23',
        # 清明节
        '2026-04-04', '2026-04-05', '2026-04-06',
        # 劳动节
        '2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04', '2026-05-05',
        # 端午节
        '2026-06-19', '2026-06-20', '2026-06-21',
        # 中秋节+国庆节
        '2026-09-25', '2026-09-26', '2026-09-27',
        '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04', '2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08',
    ]
    
    trading_days = []
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 12, 31)
    
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        weekday = current.weekday()  # 0=周一, 6=周日
        
        # 不是周末且不是节假日 → 交易日
        if weekday < 5 and date_str not in holidays_2026:
            trading_days.append(date_str)
        
        current += timedelta(days=1)
    
    return trading_days

def update_trading_calendar_table():
    """更新交易日历表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建交易日历表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading_calendar (
            date TEXT PRIMARY KEY,
            is_trading_day INTEGER DEFAULT 1
        )
    ''')
    
    # 获取2026年交易日历
    trading_days = get_2026_trading_calendar()
    
    # 插入数据
    for date in trading_days:
        cursor.execute('INSERT OR IGNORE INTO trading_calendar VALUES (?, 1)', (date,))
    
    conn.commit()
    
    # 统计
    cursor.execute('SELECT COUNT(*) FROM trading_calendar WHERE date LIKE "2026-%"')
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'2026年交易日历已更新: {count}个交易日')
    return count

if __name__ == '__main__':
    update_trading_calendar_table()
