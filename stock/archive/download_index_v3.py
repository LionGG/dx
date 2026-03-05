#!/usr/bin/env python3
"""
下载指数K线数据 - 使用stock_zh_index_daily_em
"""

import akshare as ak
import pandas as pd
import sqlite3
from pathlib import Path
import time
import random

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_kline (
            date TEXT, code TEXT, name TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL, amplitude REAL,
            change_pct REAL, change_amount REAL, turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    conn.commit()
    conn.close()

def download_index_data():
    """下载主要指数数据"""
    # 主要指数列表
    indexes = [
        ("000001", "上证指数"),
        ("000016", "上证50"),
        ("000300", "沪深300"),
        ("000905", "中证500"),
        ("000852", "中证1000"),
        ("399001", "深证成指"),
        ("399006", "创业板指"),
        ("399673", "创业板50"),
        ("000688", "科创50"),
    ]
    
    print("=" * 50)
    print("下载指数数据")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    success = 0
    
    for code, name in indexes:
        print(f"下载 {name} ({code})...", end=' ')
        
        try:
            # 使用stock_zh_index_daily_em获取指数日线
            df = ak.stock_zh_index_daily_em(symbol=code)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                continue
            
            # 筛选2026年数据
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= '2026-01-01']
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            if len(df) == 0:
                print("✗ 无2026年数据")
                continue
            
            # 添加code和name列
            df['code'] = code
            df['name'] = name
            
            # 确保列名正确
            df = df.rename(columns={
                'open': 'open',
                'close': 'close',
                'high': 'high',
                'low': 'low',
                'volume': 'volume',
                'amount': 'amount',
                'amplitude': 'amplitude',
                'change_pct': 'change_pct',
                'change_amount': 'change_amount',
                'turnover': 'turnover'
            })
            
            # 保存到数据库
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'index_kline', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}条")
            success += 1
            
        except Exception as e:
            print(f"✗ {str(e)[:50]}")
        
        time.sleep(random.uniform(0.5, 1.0))
    
    conn.close()
    print(f"\n指数完成: {success}/{len(indexes)}")
    return success

def main():
    init_db()
    
    print("开始下载指数数据...")
    print(f"数据库: {DB_PATH}")
    
    index_count = download_index_data()
    
    # 统计
    print("\n" + "=" * 50)
    print("下载完成统计")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT code) FROM index_kline')
    index_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM index_kline')
    index_records = cursor.fetchone()[0]
    
    # 列出已下载的指数
    cursor.execute('SELECT code, name, COUNT(*) as count FROM index_kline GROUP BY code, name')
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"指数: {index_total} 个")
    print(f"总记录: {index_records} 条")
    print("\n详情:")
    for row in rows:
        print(f"  {row[0]} {row[1]}: {row[2]}条")

if __name__ == '__main__':
    main()
