#!/usr/bin/env python3
"""
龙虎榜和资金流向数据获取 - 基于daily_update_v2.py优化
17:50执行 - 自动补全最近缺失的数据
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
        cursor.execute("SELECT COUNT(*) FROM lhb_daily WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        if count == 0:
            missing_dates.append(date)
    
    return missing_dates

def fetch_lhb_fund_for_date(conn, date_dash, date_str):
    """获取指定日期的龙虎榜和资金流向"""
    cursor = conn.cursor()
    total = 0
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM lhb_daily WHERE date = ?", (date_dash,))
    if cursor.fetchone()[0] > 0:
        log(f"  {date_dash} 龙虎榜已存在，跳过")
        return True
    
    log(f"  获取 {date_dash} 龙虎榜和资金流向...")
    
    # 龙虎榜
    try:
        df = ak.stock_lhb_detail_daily_sina(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('lhb_daily', conn, if_exists='append', index=False)
            total += len(df)
    except Exception as e:
        log(f"    龙虎榜失败: {e}")
    
    time.sleep(0.5)
    
    # 板块资金流向排名
    try:
        df = ak.stock_sector_fund_flow_rank()
        if df is not None and len(df) > 0:
            column_map = {
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
            }
            existing_cols = {k: v for k, v in column_map.items() if k in df.columns}
            df = df.rename(columns=existing_cols)
            df['date'] = date_dash
            
            for col in ['rank', 'name', 'change_pct', 'main_net_inflow', 'main_net_inflow_pct',
                       'super_large_net_inflow', 'super_large_net_inflow_pct', 'large_net_inflow',
                       'large_net_inflow_pct', 'medium_net_inflow', 'medium_net_inflow_pct',
                       'small_net_inflow', 'small_net_inflow_pct', 'top_stock']:
                if col not in df.columns:
                    df[col] = None
            
            df[['date', 'rank', 'name', 'change_pct', 'main_net_inflow', 'main_net_inflow_pct',
                'super_large_net_inflow', 'super_large_net_inflow_pct', 'large_net_inflow',
                'large_net_inflow_pct', 'medium_net_inflow', 'medium_net_inflow_pct',
                'small_net_inflow', 'small_net_inflow_pct', 'top_stock']].to_sql(
                'sector_fund_flow_rank', conn, if_exists='append', index=False)
            
            total += len(df)
    except Exception as e:
        log(f"    板块资金流向失败: {e}")
    
    log(f"  {date_dash}: 共 {total} 条")
    return total >= 0

def fetch_lhb_fund():
    log(f"开始获取龙虎榜和资金流向 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
        success = fetch_lhb_fund_for_date(conn, date_dash, date_str)
        if not success:
            all_success = False
        time.sleep(1)
    
    conn.close()
    log(f"完成")
    
    return all_success

if __name__ == '__main__':
    success = fetch_lhb_fund()
    sys.exit(0 if success else 1)
