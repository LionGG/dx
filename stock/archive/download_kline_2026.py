#!/usr/bin/env python3
"""
AKShare 历史K线数据下载 - 2026年以来
板块指数 + 个股
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = '/root/.openclaw/workspace/stock/akshare_kline_2026.db'
START_DATE = '20260101'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 板块K线
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_kline (
            date TEXT,
            sector_code TEXT,
            sector_name TEXT,
            sector_type TEXT,
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
            PRIMARY KEY (date, sector_code)
        )
    ''')
    
    # 个股K线
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
    print(f"数据库初始化完成: {DB_PATH}")

def download_sector_kline(sector_code, sector_name, sector_type):
    """下载板块历史K线"""
    try:
        if sector_type == 'concept':
            df = ak.stock_board_concept_hist_em(symbol=sector_name, period="日k", 
                                                start_date=START_DATE, adjust="")
        else:
            df = ak.stock_board_industry_hist_em(symbol=sector_name, period="日k",
                                                 start_date=START_DATE, adjust="")
        
        if len(df) == 0:
            return 0
        
        df['sector_code'] = sector_code
        df['sector_name'] = sector_name
        df['sector_type'] = sector_type
        
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
        
        return df
    except Exception as e:
        print(f"    ✗ {sector_name}: {e}")
        return None

def download_stock_kline(code, name):
    """下载个股历史K线"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                start_date=START_DATE, adjust="qfq")
        if len(df) == 0:
            return 0
        
        df['code'] = code
        df['name'] = name
        
        # 列名已经是英文
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
        
        return df
    except Exception as e:
        return None

def main():
    print("=" * 60)
    print("AKShare 历史K线数据下载 - 2026年以来")
    print("=" * 60)
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    # 1. 下载主要板块指数K线
    print("\n下载板块指数K线...")
    
    # 概念板块（只取前50个）
    print("  概念板块...")
    concept_list = ak.stock_board_concept_name_em()
    concept_list = concept_list.head(50)  # 只取前50
    
    for idx, row in concept_list.iterrows():
        df = download_sector_kline(row['板块代码'], row['板块名称'], 'concept')
        if df is not None:
            df[['date', 'sector_code', 'sector_name', 'sector_type', 'open', 'close',
                'high', 'low', 'volume', 'amount', 'amplitude', 'change_pct',
                'change_amount', 'turnover']].to_sql('sector_kline', conn, if_exists='append', index=False)
            print(f"    {row['板块名称']}: {len(df)} 天")
    
    # 行业板块（只取前30个）
    print("  行业板块...")
    industry_list = ak.stock_board_industry_name_em()
    industry_list = industry_list.head(30)
    
    for idx, row in industry_list.iterrows():
        df = download_sector_kline(row['板块代码'], row['板块名称'], 'industry')
        if df is not None:
            df[['date', 'sector_code', 'sector_name', 'sector_type', 'open', 'close',
                'high', 'low', 'volume', 'amount', 'amplitude', 'change_pct',
                'change_amount', 'turnover']].to_sql('sector_kline', conn, if_exists='append', index=False)
            print(f"    {row['板块名称']}: {len(df)} 天")
    
    # 2. 下载个股K线（只取前100只）
    print("\n下载个股K线（前100只）...")
    stock_list = ak.stock_zh_a_spot_em()
    stock_list = stock_list.head(100)
    
    for idx, row in stock_list.iterrows():
        code = row['代码']
        name = row['名称']
        df = download_stock_kline(code, name)
        if df is not None:
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'stock_kline', conn, if_exists='append', index=False)
            if (idx + 1) % 20 == 0:
                print(f"    进度: {idx+1}/100")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("下载完成")
    print(f"数据库: {DB_PATH}")

if __name__ == '__main__':
    main()
