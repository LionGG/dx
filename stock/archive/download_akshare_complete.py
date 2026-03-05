#!/usr/bin/env python3
"""
AKShare 全量数据下载 - 完整版
正确处理分页，显示真实进度
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime
import time

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'
START_DATE = '20260101'

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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_kline (
            date TEXT, code TEXT, name TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL, amplitude REAL,
            change_pct REAL, change_amount REAL, turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_kline (
            date TEXT, code TEXT, name TEXT, sector_type TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL, amplitude REAL,
            change_pct REAL, change_amount REAL, turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_stocks (
            sector_code TEXT, sector_name TEXT, sector_type TEXT,
            stock_code TEXT, stock_name TEXT, update_date TEXT,
            PRIMARY KEY (sector_code, stock_code)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库: {DB_PATH}")

def download_all_stocks():
    """下载所有个股K线"""
    print("\n" + "=" * 60)
    print("下载所有个股K线...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 获取股票列表（AKShare 内部会自动分页）
    print("  获取股票列表...")
    stock_list = ak.stock_zh_a_spot_em()
    total = len(stock_list)
    print(f"  总股票数: {total}")
    
    success = 0
    failed = 0
    start_time = time.time()
    
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
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude',
                '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
            })
            
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'stock_kline', conn, if_exists='append', index=False)
            
            success += 1
            
            # 每50只显示进度
            if (idx + 1) % 50 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (idx + 1)
                remaining = (total - idx - 1) * avg_time
                print(f"  进度: {idx+1}/{total} ({(idx+1)/total*100:.1f}%), "
                      f"成功:{success}, 失败:{failed}, "
                      f"预计剩余:{remaining/60:.1f}分钟")
                
        except Exception as e:
            failed += 1
    
    conn.close()
    elapsed = time.time() - start_time
    print(f"\n  完成: 成功{success}, 失败{failed}, 用时:{elapsed/60:.1f}分钟")

def download_index_kline():
    """下载指数K线"""
    print("\n" + "=" * 60)
    print("下载指数K线...")
    
    conn = sqlite3.connect(DB_PATH)
    
    indices = [
        ('000001', '上证指数'), ('000016', '上证50'), ('000300', '沪深300'),
        ('000905', '中证500'), ('000852', '中证1000'), ('399001', '深证成指'),
        ('399006', '创业板指'), ('399673', '创业板50'), ('000688', '科创50'),
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
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude',
                '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
            })
            
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'index_kline', conn, if_exists='append', index=False)
            
            print(f"  {name}: {len(df)} 天")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    conn.close()

def download_sectors():
    """下载板块K线和成分股"""
    print("\n" + "=" * 60)
    print("下载板块数据...")
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y%m%d')
    
    # 概念板块
    print("  概念板块...")
    concept_list = ak.stock_board_concept_name_em()
    print(f"    共 {len(concept_list)} 个")
    
    for idx, row in concept_list.iterrows():
        code = row['板块代码']
        name = row['板块名称']
        
        # 板块K线
        try:
            df = ak.stock_board_concept_hist_em(symbol=name, period="日k",
                                                start_date=START_DATE, adjust="")
            if len(df) > 0:
                df['code'] = code
                df['name'] = name
                df['sector_type'] = 'concept'
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '振幅': 'amplitude',
                    '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                })
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low',
                    'volume', 'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
        except:
            pass
        
        # 成分股
        try:
            df_cons = ak.stock_board_concept_cons_em(symbol=name)
            df_cons['sector_code'] = code
            df_cons['sector_name'] = name
            df_cons['sector_type'] = 'concept'
            df_cons['update_date'] = today
            df_cons = df_cons.rename(columns={'代码': 'stock_code', '名称': 'stock_name'})
            df_cons[['sector_code', 'sector_name', 'sector_type', 'stock_code', 'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
        except:
            pass
        
        if (idx + 1) % 50 == 0:
            print(f"    进度: {idx+1}/{len(concept_list)}")
    
    # 行业板块
    print("  行业板块...")
    industry_list = ak.stock_board_industry_name_em()
    print(f"    共 {len(industry_list)} 个")
    
    for idx, row in industry_list.iterrows():
        code = row['板块代码']
        name = row['板块名称']
        
        try:
            df = ak.stock_board_industry_hist_em(symbol=name, period="日k",
                                                 start_date=START_DATE, adjust="")
            if len(df) > 0:
                df['code'] = code
                df['name'] = name
                df['sector_type'] = 'industry'
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '振幅': 'amplitude',
                    '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                })
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low',
                    'volume', 'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
        except:
            pass
        
        try:
            df_cons = ak.stock_board_industry_cons_em(symbol=name)
            df_cons['sector_code'] = code
            df_cons['sector_name'] = name
            df_cons['sector_type'] = 'industry'
            df_cons['update_date'] = today
            df_cons = df_cons.rename(columns={'代码': 'stock_code', '名称': 'stock_name'})
            df_cons[['sector_code', 'sector_name', 'sector_type', 'stock_code', 'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
        except:
            pass
        
        if (idx + 1) % 10 == 0:
            print(f"    进度: {idx+1}/{len(industry_list)}")
    
    conn.close()

def main():
    print("=" * 60)
    print("AKShare 全量数据下载 - 完整版")
    print("=" * 60)
    
    init_db()
    download_all_stocks()
    download_index_kline()
    download_sectors()
    
    print("\n" + "=" * 60)
    print("下载完成")

if __name__ == '__main__':
    main()
