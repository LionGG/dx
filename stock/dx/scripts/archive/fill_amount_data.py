#!/usr/bin/env python3
"""
补充历史指数数据（含成交额）
使用新浪财经数据源
"""

import sqlite3
import requests
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

def fetch_sina_history(symbol, start_date='20260101'):
    """从新浪财经获取历史数据"""
    try:
        # 新浪财经历史数据API
        url = f"https://quotes.sina.cn/cn/api/quotes.php?symbol={symbol}&dataname=history"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'
        
        data = []
        for line in response.text.strip().split('\n'):
            if symbol in line:
                parts = line.split('"')[1].split(',')
                if len(parts) >= 30:
                    date_str = parts[30].replace('-', '')
                    if date_str >= start_date:
                        data.append({
                            'date': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
                            'open': float(parts[1]),
                            'close': float(parts[3]),
                            'high': float(parts[4]),
                            'low': float(parts[5]),
                            'volume': float(parts[8]),
                            'amount': float(parts[9])
                        })
        return data
    except Exception as e:
        print(f"获取失败: {e}")
        return []

def update_amount_data():
    """更新缺失的成交额数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要更新的日期列表
    cursor.execute('''
        SELECT DISTINCT date 
        FROM index_kline 
        WHERE date >= '2026-01-01' AND amount IS NULL
        ORDER BY date
    ''')
    dates = [r[0] for r in cursor.fetchall()]
    
    if not dates:
        print("没有需要更新的数据")
        return
    
    print(f"需要更新 {len(dates)} 天的数据")
    
    # 获取新浪财经数据
    sh_data = {d['date']: d for d in fetch_sina_history('sh000001')}
    cy_data = {d['date']: d for d in fetch_sina_history('sz399006')}
    
    updated = 0
    for date in dates:
        # 更新上证指数
        if date in sh_data:
            cursor.execute('''
                UPDATE index_kline 
                SET amount = ?
                WHERE date = ? AND index_code = '000001'
            ''', (sh_data[date]['amount'], date))
            if cursor.rowcount > 0:
                updated += 1
        
        # 更新创业板指
        if date in cy_data:
            cursor.execute('''
                UPDATE index_kline 
                SET amount = ?
                WHERE date = ? AND index_code = '399006'
            ''', (cy_data[date]['amount'], date))
            if cursor.rowcount > 0:
                updated += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 已更新 {updated} 条记录的成交额")

if __name__ == '__main__':
    update_amount_data()
