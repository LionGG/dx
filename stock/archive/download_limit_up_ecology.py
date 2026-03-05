#!/usr/bin/env python3
"""
下载涨停板生态数据（涨停池、跌停池、炸板池、强势股池）
"""

import akshare as ak
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime, timedelta

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 涨停池
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zt_pool (
            date TEXT, code TEXT, name TEXT,
            change_pct REAL, close REAL, amount REAL,
            float_market_cap REAL, total_market_cap REAL,
            turnover REAL, seal_amount REAL,
            first_seal_time TEXT, last_seal_time TEXT,
           炸板次数 INTEGER, 涨停统计 TEXT, 连板数 INTEGER, 所属行业 TEXT,
            PRIMARY KEY (date, code)
        )
    ''')
    
    # 跌停池
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dt_pool (
            date TEXT, code TEXT, name TEXT,
            change_pct REAL, close REAL, amount REAL,
            float_market_cap REAL, total_market_cap REAL,
            pe_ratio REAL, turnover REAL, seal_amount REAL,
            last_seal_time TEXT, board_amount REAL,
            连续跌停 INTEGER, 开板次数 INTEGER, 所属行业 TEXT,
            PRIMARY KEY (date, code)
        )
    ''')
    
    # 炸板池
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zbgc_pool (
            date TEXT, code TEXT, name TEXT,
            change_pct REAL, close REAL, limit_up_price REAL,
            amount REAL, float_market_cap REAL, total_market_cap REAL,
            turnover REAL, speed REAL, first_seal_time TEXT,
            炸板次数 INTEGER, 涨停统计 TEXT, amplitude REAL, 所属行业 TEXT,
            PRIMARY KEY (date, code)
        )
    ''')
    
    # 强势股池
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strong_pool (
            date TEXT, code TEXT, name TEXT,
            change_pct REAL, close REAL, limit_up_price REAL,
            amount REAL, float_market_cap REAL, total_market_cap REAL,
            turnover REAL, speed REAL, 是否新高 TEXT, 量比 REAL,
            涨停统计 TEXT, 入选理由 TEXT, 所属行业 TEXT,
            PRIMARY KEY (date, code)
        )
    ''')
    
    conn.commit()
    conn.close()

def download_zt_pool(date_str):
    """下载涨停池"""
    try:
        df = ak.stock_zt_pool_em(date=date_str)
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '代码': 'code', '名称': 'name', '涨跌幅': 'change_pct',
            '最新价': 'close', '成交额': 'amount',
            '流通市值': 'float_market_cap', '总市值': 'total_market_cap',
            '换手率': 'turnover', '封板资金': 'seal_amount',
            '首次封板时间': 'first_seal_time', '最后封板时间': 'last_seal_time',
            '炸板次数': '炸板次数', '涨停统计': '涨停统计',
            '连板数': '连板数', '所属行业': '所属行业'
        })
        df['date'] = date_str
        return df
    except Exception as e:
        print(f"  涨停池下载失败: {e}")
        return None

def download_dt_pool(date_str):
    """下载跌停池"""
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date_str)
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '代码': 'code', '名称': 'name', '涨跌幅': 'change_pct',
            '最新价': 'close', '成交额': 'amount',
            '流通市值': 'float_market_cap', '总市值': 'total_market_cap',
            '动态市盈率': 'pe_ratio', '换手率': 'turnover',
            '封单资金': 'seal_amount', '最后封板时间': 'last_seal_time',
            '板上成交额': 'board_amount', '连续跌停': '连续跌停',
            '开板次数': '开板次数', '所属行业': '所属行业'
        })
        df['date'] = date_str
        return df
    except Exception as e:
        print(f"  跌停池下载失败: {e}")
        return None

def download_zbgc_pool(date_str):
    """下载炸板池"""
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date_str)
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '代码': 'code', '名称': 'name', '涨跌幅': 'change_pct',
            '最新价': 'close', '涨停价': 'limit_up_price',
            '成交额': 'amount', '流通市值': 'float_market_cap',
            '总市值': 'total_market_cap', '换手率': 'turnover',
            '涨速': 'speed', '首次封板时间': 'first_seal_time',
            '炸板次数': '炸板次数', '涨停统计': '涨停统计',
            '振幅': 'amplitude', '所属行业': '所属行业'
        })
        df['date'] = date_str
        return df
    except Exception as e:
        print(f"  炸板池下载失败: {e}")
        return None

def download_strong_pool(date_str):
    """下载强势股池"""
    try:
        df = ak.stock_zt_pool_strong_em(date=date_str)
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '代码': 'code', '名称': 'name', '涨跌幅': 'change_pct',
            '最新价': 'close', '涨停价': 'limit_up_price',
            '成交额': 'amount', '流通市值': 'float_market_cap',
            '总市值': 'total_market_cap', '换手率': 'turnover',
            '涨速': 'speed', '是否新高': '是否新高',
            '量比': '量比', '涨停统计': '涨停统计',
            '入选理由': '入选理由', '所属行业': '所属行业'
        })
        df['date'] = date_str
        return df
    except Exception as e:
        print(f"  强势股池下载失败: {e}")
        return None

def download_all(date_str):
    """下载某一天的所有涨停板生态数据"""
    print(f"\n下载 {date_str} 的涨停板生态数据:")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 涨停池
    df_zt = download_zt_pool(date_str)
    if df_zt is not None:
        df_zt[['date', 'code', 'name', 'change_pct', 'close', 'amount',
               'float_market_cap', 'total_market_cap', 'turnover', 'seal_amount',
               'first_seal_time', 'last_seal_time', '炸板次数', '涨停统计', '连板数', '所属行业']].to_sql(
            'zt_pool', conn, if_exists='append', index=False)
        print(f"  涨停池: {len(df_zt)} 条")
    
    # 跌停池
    df_dt = download_dt_pool(date_str)
    if df_dt is not None:
        df_dt[['date', 'code', 'name', 'change_pct', 'close', 'amount',
               'float_market_cap', 'total_market_cap', 'pe_ratio', 'turnover', 'seal_amount',
               'last_seal_time', 'board_amount', '连续跌停', '开板次数', '所属行业']].to_sql(
            'dt_pool', conn, if_exists='append', index=False)
        print(f"  跌停池: {len(df_dt)} 条")
    
    # 炸板池
    df_zbgc = download_zbgc_pool(date_str)
    if df_zbgc is not None:
        df_zbgc[['date', 'code', 'name', 'change_pct', 'close', 'limit_up_price',
                 'amount', 'float_market_cap', 'total_market_cap', 'turnover', 'speed',
                 'first_seal_time', '炸板次数', '涨停统计', 'amplitude', '所属行业']].to_sql(
            'zbgc_pool', conn, if_exists='append', index=False)
        print(f"  炸板池: {len(df_zbgc)} 条")
    
    # 强势股池
    df_strong = download_strong_pool(date_str)
    if df_strong is not None:
        df_strong[['date', 'code', 'name', 'change_pct', 'close', 'limit_up_price',
                   'amount', 'float_market_cap', 'total_market_cap', 'turnover', 'speed',
                   '是否新高', '量比', '涨停统计', '入选理由', '所属行业']].to_sql(
            'strong_pool', conn, if_exists='append', index=False)
        print(f"  强势股池: {len(df_strong)} 条")
    
    conn.close()

def download_history():
    """下载历史数据（2026-01-05 到 2026-02-13）"""
    init_db()
    
    print("=" * 60)
    print("下载涨停板生态历史数据")
    print("=" * 60)
    
    # 生成交易日列表（2026-01-05 到 2026-02-13）
    start_date = datetime(2026, 1, 5)
    end_date = datetime(2026, 2, 13)
    
    current = start_date
    while current <= end_date:
        # 跳过周末
        if current.weekday() < 5:  # 0-4 是周一到周五
            date_str = current.strftime('%Y%m%d')
            download_all(date_str)
            time.sleep(1)  # 避免请求过快
        
        current += timedelta(days=1)
    
    print("\n下载完成！")

def verify():
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for table in ['zt_pool', 'dt_pool', 'zbgc_pool', 'strong_pool']:
        cursor.execute(f'SELECT COUNT(*), COUNT(DISTINCT date) FROM {table}')
        records, days = cursor.fetchone()
        print(f"{table:15s}: {records:5,} 条记录, {days:2} 个交易日")
    
    conn.close()

if __name__ == '__main__':
    download_history()
    verify()
