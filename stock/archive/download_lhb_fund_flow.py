#!/usr/bin/env python3
"""
下载资金流向与龙虎榜数据
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
    
    # 龙虎榜每日详情
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lhb_daily (
            date TEXT, code TEXT, name TEXT,
            close REAL, indicator_value REAL,
            volume REAL, amount REAL, indicator TEXT,
            PRIMARY KEY (date, code, indicator)
        )
    ''')
    
    # 板块资金流向排名
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_fund_flow_rank (
            date TEXT, rank INTEGER, name TEXT,
            change_pct REAL, main_net_inflow REAL, main_net_inflow_pct REAL,
            super_large_net_inflow REAL, super_large_net_inflow_pct REAL,
            large_net_inflow REAL, large_net_inflow_pct REAL,
            medium_net_inflow REAL, medium_net_inflow_pct REAL,
            small_net_inflow REAL, small_net_inflow_pct REAL,
            top_stock TEXT,
            PRIMARY KEY (date, rank)
        )
    ''')
    
    conn.commit()
    conn.close()

def download_lhb_daily(date_str):
    """下载龙虎榜每日详情"""
    try:
        df = ak.stock_lhb_detail_daily_sina(date=date_str)
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '股票代码': 'code', '股票名称': 'name',
            '收盘价': 'close', '对应值': 'indicator_value',
            '成交量': 'volume', '成交额': 'amount', '指标': 'indicator'
        })
        df['date'] = date_str
        return df
    except Exception as e:
        print(f"  龙虎榜下载失败: {e}")
        return None

def download_sector_fund_flow_rank():
    """下载板块资金流向排名（当日）"""
    try:
        df = ak.stock_sector_fund_flow_rank()
        if df is None or len(df) == 0:
            return None
        
        df = df.rename(columns={
            '序号': 'rank', '名称': 'name', '今日涨跌幅': 'change_pct',
            '今日主力净流入-净额': 'main_net_inflow',
            '今日主力净流入-净占比': 'main_net_inflow_pct',
            '今日超大单净流入-净额': 'super_large_net_inflow',
            '今日超大单净流入-净占比': 'super_large_net_inflow_pct',
            '今日大单净流入-净额': 'large_net_inflow',
            '今日大单净流入-净占比': 'large_net_inflow_pct',
            '今日中单净流入-净额': 'medium_net_inflow',
            '今日中单净流入-净占比': 'medium_net_inflow_pct',
            '今日小单净流入-净额': 'small_net_inflow',
            '今日小单净流入-净占比': 'small_net_inflow_pct',
            '今日主力净流入最大股': 'top_stock'
        })
        df['date'] = datetime.now().strftime('%Y-%m-%d')
        return df
    except Exception as e:
        print(f"  板块资金流向排名下载失败: {e}")
        return None

def download_history():
    """下载历史数据"""
    init_db()
    
    print("=" * 60)
    print("下载龙虎榜历史数据")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # 清空现有数据
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lhb_daily')
    conn.commit()
    
    # 生成交易日列表（2026-01-05 到 2026-02-13）
    start_date = datetime(2026, 1, 5)
    end_date = datetime(2026, 2, 13)
    
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 周一到周五
            date_str = current.strftime('%Y%m%d')
            print(f"\n下载 {date_str}:")
            
            # 龙虎榜
            df_lhb = download_lhb_daily(date_str)
            if df_lhb is not None:
                df_lhb[['date', 'code', 'name', 'close', 'indicator_value',
                        'volume', 'amount', 'indicator']].to_sql(
                    'lhb_daily', conn, if_exists='append', index=False)
                print(f"  龙虎榜: {len(df_lhb)} 条")
            
            time.sleep(1)
        
        current += timedelta(days=1)
    
    # 下载板块资金流向排名（只下载最新一天）
    print("\n" + "=" * 60)
    print("下载板块资金流向排名")
    print("=" * 60)
    
    # 清空现有数据
    cursor.execute('DELETE FROM sector_fund_flow_rank')
    conn.commit()
    
    df_rank = download_sector_fund_flow_rank()
    if df_rank is not None:
        df_rank[['date', 'rank', 'name', 'change_pct',
                 'main_net_inflow', 'main_net_inflow_pct',
                 'super_large_net_inflow', 'super_large_net_inflow_pct',
                 'large_net_inflow', 'large_net_inflow_pct',
                 'medium_net_inflow', 'medium_net_inflow_pct',
                 'small_net_inflow', 'small_net_inflow_pct',
                 'top_stock']].to_sql(
            'sector_fund_flow_rank', conn, if_exists='append', index=False)
        print(f"  板块排名: {len(df_rank)} 条")
    
    conn.close()
    print("\n下载完成！")

def verify():
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), COUNT(DISTINCT date) FROM lhb_daily')
    records, days = cursor.fetchone()
    print(f"龙虎榜: {records:,} 条记录, {days} 个交易日")
    
    cursor.execute('SELECT COUNT(*) FROM sector_fund_flow_rank')
    rank_records = cursor.fetchone()[0]
    print(f"板块排名: {rank_records} 条")
    
    conn.close()

if __name__ == '__main__':
    download_history()
    verify()
