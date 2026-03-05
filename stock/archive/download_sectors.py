#!/usr/bin/env python3
"""
AKShare 板块数据全量下载 - 2026年
用于主线板块分析
"""

import akshare as ak
import pandas as pd
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = '/root/.openclaw/workspace/stock/akshare_sectors.db'

def init_db():
    """初始化板块数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 概念板块列表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concept_list (
            code TEXT PRIMARY KEY,
            name TEXT,
            change_pct REAL,
            total_market_cap REAL,
            turnover REAL,
            up_count INTEGER,
            down_count INTEGER,
            update_date TEXT
        )
    ''')
    
    # 概念板块成分股
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concept_cons (
            concept_code TEXT,
            concept_name TEXT,
            stock_code TEXT,
            stock_name TEXT,
            change_pct REAL,
            amount REAL,
            amplitude REAL,
            update_date TEXT,
            PRIMARY KEY (concept_code, stock_code)
        )
    ''')
    
    # 行业板块列表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS industry_list (
            code TEXT PRIMARY KEY,
            name TEXT,
            change_pct REAL,
            total_market_cap REAL,
            turnover REAL,
            up_count INTEGER,
            down_count INTEGER,
            update_date TEXT
        )
    ''')
    
    # 行业板块成分股
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS industry_cons (
            industry_code TEXT,
            industry_name TEXT,
            stock_code TEXT,
            stock_name TEXT,
            change_pct REAL,
            amount REAL,
            amplitude REAL,
            update_date TEXT,
            PRIMARY KEY (industry_code, stock_code)
        )
    ''')
    
    # 板块资金流向历史
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_fund_flow (
            date TEXT,
            sector_type TEXT,
            sector_code TEXT,
            sector_name TEXT,
            main_net_inflow REAL,
            main_net_inflow_pct REAL,
            super_large_net_inflow REAL,
            large_net_inflow REAL,
            medium_net_inflow REAL,
            small_net_inflow REAL,
            PRIMARY KEY (date, sector_code)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

def download_concept_sectors():
    """下载概念板块数据"""
    print("\n" + "=" * 60)
    print("下载概念板块数据...")
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y%m%d')
    
    # 1. 概念板块列表
    print("  获取概念板块列表...")
    try:
        df_list = ak.stock_board_concept_name_em()
        df_list['update_date'] = today
        df_list.to_sql('concept_list', conn, if_exists='replace', index=False)
        print(f"    ✓ 概念板块: {len(df_list)} 个")
    except Exception as e:
        print(f"    ✗ 失败: {e}")
        conn.close()
        return
    
    # 2. 概念板块成分股
    print("  下载概念板块成分股...")
    total_stocks = 0
    
    for idx, row in df_list.iterrows():
        concept_name = row['板块名称']
        try:
            df_cons = ak.stock_board_concept_cons_em(symbol=concept_name)
            df_cons['concept_code'] = row['板块代码']
            df_cons['concept_name'] = concept_name
            df_cons['update_date'] = today
            
            # 重命名列
            df_cons = df_cons.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name',
                '涨跌幅': 'change_pct',
                '成交额': 'amount',
                '振幅': 'amplitude'
            })
            
            df_cons[['concept_code', 'concept_name', 'stock_code', 'stock_name', 
                     'change_pct', 'amount', 'amplitude', 'update_date']].to_sql(
                'concept_cons', conn, if_exists='append', index=False)
            
            total_stocks += len(df_cons)
            
            if (idx + 1) % 20 == 0:
                print(f"    进度: {idx+1}/{len(df_list)} 板块, {total_stocks} 只股票")
                
        except Exception as e:
            print(f"    ✗ {concept_name}: {e}")
    
    print(f"    ✓ 概念成分股: {total_stocks} 条")
    conn.close()

def download_industry_sectors():
    """下载行业板块数据"""
    print("\n" + "=" * 60)
    print("下载行业板块数据...")
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y%m%d')
    
    # 1. 行业板块列表
    print("  获取行业板块列表...")
    try:
        df_list = ak.stock_board_industry_name_em()
        df_list['update_date'] = today
        df_list.to_sql('industry_list', conn, if_exists='replace', index=False)
        print(f"    ✓ 行业板块: {len(df_list)} 个")
    except Exception as e:
        print(f"    ✗ 失败: {e}")
        conn.close()
        return
    
    # 2. 行业板块成分股
    print("  下载行业板块成分股...")
    total_stocks = 0
    
    for idx, row in df_list.iterrows():
        industry_name = row['板块名称']
        try:
            df_cons = ak.stock_board_industry_cons_em(symbol=industry_name)
            df_cons['industry_code'] = row['板块代码']
            df_cons['industry_name'] = industry_name
            df_cons['update_date'] = today
            
            # 重命名列
            df_cons = df_cons.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name',
                '涨跌幅': 'change_pct',
                '成交额': 'amount',
                '振幅': 'amplitude'
            })
            
            df_cons[['industry_code', 'industry_name', 'stock_code', 'stock_name',
                     'change_pct', 'amount', 'amplitude', 'update_date']].to_sql(
                'industry_cons', conn, if_exists='append', index=False)
            
            total_stocks += len(df_cons)
            
            if (idx + 1) % 10 == 0:
                print(f"    进度: {idx+1}/{len(df_list)} 板块, {total_stocks} 只股票")
                
        except Exception as e:
            print(f"    ✗ {industry_name}: {e}")
    
    print(f"    ✓ 行业成分股: {total_stocks} 条")
    conn.close()

def download_sector_fund_flow():
    """下载板块资金流向"""
    print("\n" + "=" * 60)
    print("下载板块资金流向...")
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y%m%d')
    
    # 行业资金流向
    print("  行业资金流向...")
    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
        df['date'] = today
        df['sector_type'] = 'industry'
        df.to_sql('sector_fund_flow', conn, if_exists='append', index=False)
        print(f"    ✓ 行业资金流向: {len(df)} 条")
    except Exception as e:
        print(f"    ✗ 失败: {e}")
    
    # 概念资金流向
    print("  概念资金流向...")
    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")
        df['date'] = today
        df['sector_type'] = 'concept'
        df.to_sql('sector_fund_flow', conn, if_exists='append', index=False)
        print(f"    ✓ 概念资金流向: {len(df)} 条")
    except Exception as e:
        print(f"    ✗ 失败: {e}")
    
    conn.close()

def main():
    print("=" * 60)
    print("AKShare 板块数据全量下载")
    print("=" * 60)
    
    init_db()
    download_concept_sectors()
    download_industry_sectors()
    download_sector_fund_flow()
    
    print("\n" + "=" * 60)
    print("下载完成")
    print(f"数据库: {DB_PATH}")

if __name__ == '__main__':
    main()
