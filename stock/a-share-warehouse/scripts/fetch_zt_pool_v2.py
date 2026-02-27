#!/usr/bin/env python3
"""
涨停板生态数据获取 - 基于daily_update_v2.py优化

自动补全最近缺失的数据
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
    
    dates_to_check = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        dates_to_check.append(d)
    
    missing_dates = []
    for date in dates_to_check:
        cursor.execute("SELECT COUNT(*) FROM zt_pool WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        if count == 0:
            missing_dates.append(date)
    
    return missing_dates

def fetch_zt_for_date(conn, date_dash, date_str):
    """获取指定日期的涨停板生态数据"""
    cursor = conn.cursor()
    total = 0
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM zt_pool WHERE date = ?", (date_dash,))
    if cursor.fetchone()[0] > 0:
        log(f"  {date_dash} 涨停池已存在，跳过")
        return True
    
    log(f"  获取 {date_dash} 涨停板生态...")
    
    # 涨停池
    try:
        df = ak.stock_zt_pool_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('zt_pool', conn, if_exists='append', index=False)
            total += len(df)
    except Exception as e:
        log(f"    涨停池失败: {e}")
    
    time.sleep(0.3)
    
    # 跌停池
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('dt_pool', conn, if_exists='append', index=False)
            total += len(df)
    except Exception as e:
        log(f"    跌停池失败: {e}")
    
    time.sleep(0.3)
    
    # 炸板池
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('zbgc_pool', conn, if_exists='append', index=False)
            total += len(df)
    except Exception as e:
        log(f"    炸板池失败: {e}")
    
    time.sleep(0.3)
    
    # 强势股池
    try:
        df = ak.stock_zt_pool_strong_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('strong_pool', conn, if_exists='append', index=False)
            total += len(df)
    except Exception as e:
        log(f"    强势股池失败: {e}")
    
    log(f"  {date_dash}: 共 {total} 条")
    return total >= 0

def fetch_zt_ecology():
    log(f"开始获取涨停板生态数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect(DB_PATH)
    
    missing_dates = get_missing_dates(conn, days=5)
    
    if len(missing_dates) == 0:
        log("  最近5天数据已完整，无需获取")
        conn.close()
        return True
    
    log(f"  需要补全的日期: {missing_dates}")
    
    all_success = True
    for date_dash in missing_dates:
        date_str = date_dash.replace('-', '')
        success = fetch_zt_for_date(conn, date_dash, date_str)
        if not success:
            all_success = False
        time.sleep(1)
    
    conn.close()
    log(f"完成")
    
    return all_success

if __name__ == '__main__':
    success = fetch_zt_ecology()
    sys.exit(0 if success else 1)
