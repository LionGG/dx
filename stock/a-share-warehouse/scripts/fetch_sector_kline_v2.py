#!/usr/bin/env python3
"""
板块数据获取 - 基于daily_update_v2.py优化
16:01执行 - 自动补全最近缺失的数据
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'akshare_full.db')

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def get_missing_dates(conn, days=5):
    """获取最近缺失数据的交易日"""
    cursor = conn.cursor()
    
    # 获取最近N天
    dates_to_check = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        dates_to_check.append(d)
    
    # 检查哪些日期没有足够数据
    missing_dates = []
    for date in dates_to_check:
        cursor.execute("SELECT COUNT(*) FROM sector_kline WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        if count < 50:  # 少于50个板块认为缺失
            missing_dates.append(date)
    
    return missing_dates

def fetch_sector_for_date(conn, date_dash, date_str):
    """获取指定日期的板块数据"""
    cursor = conn.cursor()
    total = 0
    
    # 检查该日期是否已有足够数据
    cursor.execute("SELECT COUNT(*) FROM sector_kline WHERE date = ?", (date_dash,))
    existing = cursor.fetchone()[0]
    
    if existing >= 100:
        log(f"  {date_dash} 板块K线已存在: {existing} 条，跳过")
        return True
    
    log(f"  获取 {date_dash} 板块数据...")
    
    # 1. 行业板块
    try:
        industry_df = ak.stock_board_industry_name_em()
        industry_names = industry_df['板块名称'].tolist()
        
        for name in industry_names:
            try:
                df = ak.stock_board_industry_hist_em(symbol=name, period="日k",
                                                     start_date=date_str, end_date=date_str)
                
                if df is not None and len(df) > 0:
                    df = df.rename(columns={
                        '日期': 'date', '开盘': 'open', '收盘': 'close',
                        '最高': 'high', '最低': 'low', '成交量': 'volume',
                        '成交额': 'amount', '振幅': 'amplitude',
                        '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                    })
                    df['code'] = ''
                    df['name'] = name
                    df['sector_type'] = 'industry'
                    
                    df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low',
                        'volume', 'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                        'sector_kline', conn, if_exists='append', index=False)
                    total += 1
                
                time.sleep(0.03)
            except:
                continue
    except Exception as e:
        log(f"    行业板块失败: {e}")
    
    # 2. 概念板块
    try:
        concept_df = ak.stock_board_concept_name_em()
        concept_names = concept_df['板块名称'].tolist()
        
        for name in concept_names:
            try:
                df = ak.stock_board_concept_hist_em(symbol=name, period="日k",
                                                    start_date=date_dash, end_date=date_dash)
                
                if df is not None and len(df) > 0:
                    df = df.rename(columns={
                        '日期': 'date', '开盘': 'open', '收盘': 'close',
                        '最高': 'high', '最低': 'low', '成交量': 'volume',
                        '成交额': 'amount', '振幅': 'amplitude',
                        '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                    })
                    df['code'] = ''
                    df['name'] = name
                    df['sector_type'] = 'concept'
                    
                    df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low',
                        'volume', 'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                        'sector_kline', conn, if_exists='append', index=False)
                    total += 1
                
                time.sleep(0.03)
            except:
                continue
    except Exception as e:
        log(f"    概念板块失败: {e}")
    
    log(f"  {date_dash}: 板块K线 {total} 条")
    return total > 0

def fetch_sector_data():
    log(f"开始获取板块数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 获取最近缺失的日期
    missing_dates = get_missing_dates(conn, days=5)
    
    if len(missing_dates) == 0:
        log("  最近5天数据已完整，无需获取")
        conn.close()
        return True
    
    log(f"  需要补全的日期: {missing_dates}")
    
    # 逐个日期获取
    all_success = True
    for date_dash in missing_dates:
        date_str = date_dash.replace('-', '')
        success = fetch_sector_for_date(conn, date_dash, date_str)
        if not success:
            all_success = False
        time.sleep(1)
    
    conn.close()
    log(f"完成")
    
    return all_success

if __name__ == '__main__':
    success = fetch_sector_data()
    sys.exit(0 if success else 1)
