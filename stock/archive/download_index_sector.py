#!/usr/bin/env python3
"""
AKShare 指数和板块历史K线下载 - 2026年以来
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
    
    # 指数K线
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_kline (
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
    
    # 板块K线
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_kline (
            date TEXT,
            code TEXT,
            name TEXT,
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
            PRIMARY KEY (date, code)
        )
    ''')
    
    # 板块成分股关系
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_stocks (
            sector_code TEXT,
            sector_name TEXT,
            sector_type TEXT,
            stock_code TEXT,
            stock_name TEXT,
            update_date TEXT,
            PRIMARY KEY (sector_code, stock_code)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库: {DB_PATH}")

def download_index_kline():
    """下载主要指数K线"""
    print("\n" + "=" * 60)
    print("下载指数K线...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 主要指数
    indices = [
        ('000001', '上证指数'),
        ('000016', '上证50'),
        ('000300', '沪深300'),
        ('000905', '中证500'),
        ('000852', '中证1000'),
        ('399001', '深证成指'),
        ('399006', '创业板指'),
        ('399673', '创业板50'),
        ('000688', '科创50'),
    ]
    
    for code, name in indices:
        try:
            df = ak.index_zh_a_hist(symbol=code, period="daily",
                                    start_date=START_DATE, end_date="20261231")
            if len(df) == 0:
                continue
            
            df['code'] = code
            df['name'] = name
            
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
                'index_kline', conn, if_exists='append', index=False)
            
            print(f"  {name}: {len(df)} 天")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    conn.close()

def download_sector_cons():
    """下载板块成分股关系"""
    print("\n" + "=" * 60)
    print("下载板块成分股关系...")
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y%m%d')
    
    # 概念板块（前50个）
    print("  概念板块...")
    concept_list = ak.stock_board_concept_name_em()
    concept_list = concept_list.head(50)
    
    for idx, row in concept_list.iterrows():
        try:
            df = ak.stock_board_concept_cons_em(symbol=row['板块名称'])
            df['sector_code'] = row['板块代码']
            df['sector_name'] = row['板块名称']
            df['sector_type'] = 'concept'
            df['update_date'] = today
            
            df = df.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name'
            })
            
            df[['sector_code', 'sector_name', 'sector_type', 'stock_code', 
                'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
            
            if (idx + 1) % 10 == 0:
                print(f"    进度: {idx+1}/50")
        except Exception as e:
            pass
    
    # 行业板块（前30个）
    print("  行业板块...")
    industry_list = ak.stock_board_industry_name_em()
    industry_list = industry_list.head(30)
    
    for idx, row in industry_list.iterrows():
        try:
            df = ak.stock_board_industry_cons_em(symbol=row['板块名称'])
            df['sector_code'] = row['板块代码']
            df['sector_name'] = row['板块名称']
            df['sector_type'] = 'industry'
            df['update_date'] = today
            
            df = df.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name'
            })
            
            df[['sector_code', 'sector_name', 'sector_type', 'stock_code',
                'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
            
            if (idx + 1) % 10 == 0:
                print(f"    进度: {idx+1}/30")
        except Exception as e:
            pass
    
    conn.close()

def main():
    print("=" * 60)
    print("AKShare 指数和板块数据下载")
    print("=" * 60)
    
    init_db()
    download_index_kline()
    download_sector_cons()
    
    print("\n" + "=" * 60)
    print("下载完成")

if __name__ == '__main__':
    main()
