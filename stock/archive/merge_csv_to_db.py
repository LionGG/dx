#!/usr/bin/env python3
"""
合并已有CSV数据到数据库
"""

import pandas as pd
import sqlite3
from pathlib import Path
import glob

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'
CSV_DIR = '/root/.openclaw/workspace/stock/a_stock_data/history/stocks'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_kline (
            date TEXT, code TEXT, name TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL, amplitude REAL,
            change_pct REAL, change_amount REAL, turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    conn.commit()
    conn.close()

def merge_csv_to_db():
    print("合并CSV数据到数据库...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 获取所有CSV文件
    csv_files = glob.glob(f'{CSV_DIR}/*.csv')
    total = len(csv_files)
    print(f"共 {total} 个文件")
    
    success = 0
    for i, csv_file in enumerate(csv_files):
        try:
            df = pd.read_csv(csv_file)
            if len(df) == 0:
                continue
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '股票代码': 'code',
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
            
            # 添加name列（从代码获取）
            df['name'] = ''
            
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'stock_kline', conn, if_exists='append', index=False)
            
            success += 1
            
            if (i + 1) % 500 == 0:
                print(f"  进度: {i+1}/{total}, 成功:{success}")
                
        except Exception as e:
            print(f"  ✗ {csv_file}: {e}")
    
    conn.close()
    print(f"\n完成: 成功导入 {success} 只股票")

if __name__ == '__main__':
    init_db()
    merge_csv_to_db()
