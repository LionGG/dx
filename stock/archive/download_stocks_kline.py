#!/usr/bin/env python3
"""
AKShare 个股历史K线下载 - 2026年以来
简化版
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock/akshare_kline_2026.db'
START_DATE = '20260101'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_kline (
            date TEXT,
            code TEXT,
            name TEXT,
            open REAL,
            close REAL,
            high REAL,
            low REAL,
            volume REAL,
            amount REAL,
            amplitude REAL,
            change_pct REAL,
            change_amount REAL,
            turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"数据库: {DB_PATH}")

def main():
    print("=" * 60)
    print("下载个股历史K线 - 2026年以来")
    print("=" * 60)
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    # 获取股票列表
    print("\n获取股票列表...")
    stock_list = ak.stock_zh_a_spot_em()
    print(f"总股票数: {len(stock_list)}")
    
    # 只下载前200只
    stock_list = stock_list.head(200)
    print(f"本次下载: {len(stock_list)} 只")
    
    success = 0
    failed = 0
    
    for idx, row in stock_list.iterrows():
        code = row['代码']
        name = row['名称']
        
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                    start_date=START_DATE, adjust="qfq")
            if len(df) == 0:
                failed += 1
                continue
            
            df['code'] = code
            df['name'] = name
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnover'
            })
            
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'stock_kline', conn, if_exists='append', index=False)
            
            success += 1
            
            if (idx + 1) % 50 == 0:
                print(f"  进度: {idx+1}/200, 成功:{success}, 失败:{failed}")
                
        except Exception as e:
            failed += 1
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"下载完成: 成功{success}, 失败{failed}")
    print(f"数据库: {DB_PATH}")

if __name__ == '__main__':
    main()
