#!/usr/bin/env python3
"""
下载指数K线数据到数据库
支持：上证指数(000001)、创业板指(399006)、东财全A(000985)
"""

import sqlite3
import requests
import json
from datetime import datetime, timedelta
import sys

# 数据库路径
DB_PATH = '/root/.openclaw/workspace/stock/duanxianxia_data.db'

# 指数配置
INDEX_CONFIG = {
    '000001': {'name': '上证指数', 'code': '000001'},
    '399006': {'name': '创业板指', 'code': '399006'},
    '000985': {'name': '东财全A', 'code': '000985'}
}

# API基础URL
BASE_URL = 'https://50.liusha.net'


def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_kline (
            date TEXT NOT NULL,
            index_code TEXT NOT NULL,
            index_name TEXT,
            open REAL,
            close REAL,
            high REAL,
            low REAL,
            volume REAL,
            amount REAL,
            ma5 REAL,
            ma10 REAL,
            ma50 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date, index_code)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ 数据库表初始化完成")


def fetch_kline_data(index_code, start_date, end_date):
    """从liusha网站获取K线数据"""
    url = f'{BASE_URL}/index/price'
    params = {
        'index_code': index_code,
        'include_ma': 'true',
        'start_date': start_date,
        'end_date': end_date
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            return data['data']
        else:
            print(f"  ✗ 获取{index_code}数据失败: {data.get('message', '未知错误')}")
            return None
    except Exception as e:
        print(f"  ✗ 请求{index_code}数据出错: {e}")
        return None


def save_to_database(index_code, index_name, prices):
    """保存K线数据到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for price in prices:
        date = price['date']
        
        # 检查是否已存在
        cursor.execute(
            'SELECT 1 FROM index_kline WHERE date = ? AND index_code = ?',
            (date, index_code)
        )
        exists = cursor.fetchone()
        
        if exists:
            # 更新
            cursor.execute('''
                UPDATE index_kline SET
                    open = ?, close = ?, high = ?, low = ?,
                    volume = ?, amount = ?,
                    ma5 = ?, ma10 = ?, ma50 = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE date = ? AND index_code = ?
            ''', (
                price.get('open'), price.get('close'), 
                price.get('high'), price.get('low'),
                price.get('volume'), price.get('amount'),
                price.get('ma5'), price.get('ma10'), price.get('ma50'),
                date, index_code
            ))
            updated += 1
        else:
            # 插入
            cursor.execute('''
                INSERT INTO index_kline
                (date, index_code, index_name, open, close, high, low,
                 volume, amount, ma5, ma10, ma50)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date, index_code, index_name,
                price.get('open'), price.get('close'), 
                price.get('high'), price.get('low'),
                price.get('volume'), price.get('amount'),
                price.get('ma5'), price.get('ma10'), price.get('ma50')
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    return inserted, updated


def download_all_indices(start_date=None, end_date=None):
    """下载所有指数的K线数据"""
    if not start_date or not end_date:
        # 默认下载最近60个交易日
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"\n{'='*50}")
    print(f"下载指数K线数据")
    print(f"日期范围: {start_date} 至 {end_date}")
    print(f"{'='*50}\n")
    
    total_inserted = 0
    total_updated = 0
    
    for code, config in INDEX_CONFIG.items():
        print(f"下载 {config['name']}({code})...")
        
        data = fetch_kline_data(code, start_date, end_date)
        
        if data and 'prices' in data:
            prices = data['prices']
            inserted, updated = save_to_database(code, config['name'], prices)
            total_inserted += inserted
            total_updated += updated
            print(f"  ✓ 新增 {inserted} 条, 更新 {updated} 条")
        else:
            print(f"  ✗ 无数据")
    
    print(f"\n{'='*50}")
    print(f"总计: 新增 {total_inserted} 条, 更新 {total_updated} 条")
    print(f"{'='*50}\n")


def show_latest_data():
    """显示最新的几条数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n最新数据预览:")
    print("-" * 80)
    
    for code, config in INDEX_CONFIG.items():
        cursor.execute('''
            SELECT date, open, close, high, low, volume, ma5, ma10, ma50
            FROM index_kline
            WHERE index_code = ?
            ORDER BY date DESC
            LIMIT 3
        ''', (code,))
        
        rows = cursor.fetchall()
        print(f"\n{config['name']}({code}):")
        for row in rows:
            print(f"  {row[0]}: 开{row[1]:.2f} 收{row[2]:.2f} 高{row[3]:.2f} 低{row[4]:.2f} MA5:{row[6]:.2f}")
    
    conn.close()


if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 下载数据（默认最近90天，覆盖60个交易日）
    download_all_indices()
    
    # 显示最新数据
    show_latest_data()