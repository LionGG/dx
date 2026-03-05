#!/usr/bin/env python3
"""
从新浪财经获取指数K线数据
备用方案：当AKShare数据延迟时使用
"""

import sqlite3
import requests
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

def fetch_realtime_from_sina():
    """从新浪财经获取实时数据"""
    try:
        url = "https://hq.sinajs.cn/list=sh000001,sz399006"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'
        
        data = {}
        for line in response.text.strip().split('\n'):
            if 'sh000001' in line or 'sz399006' in line:
                parts = line.split('"')[1].split(',')
                symbol = 'sh000001' if 'sh000001' in line else 'sz399006'
                data[symbol] = {
                    'name': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[3]),
                    'high': float(parts[4]),
                    'low': float(parts[5]),
                    'volume': float(parts[8]),
                    'date': parts[30]
                }
        return data
    except Exception as e:
        print(f"获取失败: {e}")
        return None

if __name__ == '__main__':
    data = fetch_realtime_from_sina()
    if data:
        for symbol, info in data.items():
            print(f"{info['name']}: {info['close']} ({info['date']})")
    else:
        print("获取数据失败")
