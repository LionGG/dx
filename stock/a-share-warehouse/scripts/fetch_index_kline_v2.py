#!/usr/bin/env python3
"""
指数数据获取 - 使用稳定接口stock_zh_index_daily
15:05执行，自动补全最近两天缺失的数据
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

# 9个主要指数 - 使用带前缀的代码格式
INDICES = {
    'sh000001': {'code': '000001', 'name': '上证指数'},
    'sz399001': {'code': '399001', 'name': '深证成指'},
    'sz399006': {'code': '399006', 'name': '创业板指'},
    'sh000016': {'code': '000016', 'name': '上证50'},
    'sh000300': {'code': '000300', 'name': '沪深300'},
    'sh000905': {'code': '000905', 'name': '中证500'},
    'sh000688': {'code': '000688', 'name': '科创50'},
    'sz399005': {'code': '399005', 'name': '中小板指'},
    'sh000010': {'code': '000010', 'name': '上证180'}
}

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def get_recent_trading_days(days=5):
    """获取最近N个交易日（排除周末）"""
    trading_days = []
    check_date = datetime.now()
    
    while len(trading_days) < days:
        # 排除周末 (0=周一, 6=周日)
        if check_date.weekday() < 5:
            trading_days.append(check_date.strftime('%Y-%m-%d'))
        check_date -= timedelta(days=1)
    
    return trading_days

def get_missing_dates(conn, days=2):
    """获取最近缺失数据的交易日"""
    cursor = conn.cursor()
    
    # 获取最近N个交易日
    dates_to_check = get_recent_trading_days(days)
    
    # 检查哪些日期没有数据
    missing_dates = []
    for date in dates_to_check:
        cursor.execute("SELECT COUNT(*) FROM index_kline WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        if count < len(INDICES) * 0.5:  # 少于50%认为缺失
            missing_dates.append(date)
    
    return missing_dates

def fetch_all_history(symbol, max_retries=3):
    """获取指数全部历史数据，带重试"""
    for retry in range(max_retries):
        try:
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is not None and len(df) > 0:
                return df
            log(f"  警告: {symbol} 返回空数据，重试 {retry+1}/{max_retries}")
        except Exception as e:
            log(f"  错误: {symbol} 第{retry+1}次尝试失败: {e}")
        time.sleep(1)
    return None

def fetch_index_for_date(conn, target_date):
    """获取指定日期的指数数据"""
    cursor = conn.cursor()
    success = 0
    
    # 将目标日期字符串转为datetime.date用于比较
    from datetime import datetime as dt_module
    target_date_dt = dt_module.strptime(target_date, '%Y-%m-%d').date()
    
    # 检查该日期是否已有足够数据
    cursor.execute("SELECT COUNT(*) FROM index_kline WHERE date = ?", (target_date,))
    existing = cursor.fetchone()[0]
    
    if existing >= len(INDICES) * 0.5:
        log(f"  {target_date} 数据已存在: {existing} 条，跳过")
        return True
    
    log(f"  获取 {target_date} 数据...")
    
    for symbol, config in INDICES.items():
        code = config['code']
        name = config['name']
        
        try:
            # 使用稳定的接口获取全部历史
            df = fetch_all_history(symbol)
            
            if df is None or len(df) == 0:
                log(f"    {name}({code}) 无数据")
                continue
            
            # 筛选目标日期的数据（datetime.date比较）
            df_target = df[df['date'] == target_date_dt]
            
            if len(df_target) == 0:
                log(f"    {name}({code}) {target_date} 无数据")
                continue
            
            row = df_target.iloc[0]
            
            # 计算MA（使用历史数据）
            date_idx = df_target.index[0]
            ma5 = df.loc[max(0, date_idx-4):date_idx, 'close'].mean() if date_idx >= 4 else None
            ma10 = df.loc[max(0, date_idx-9):date_idx, 'close'].mean() if date_idx >= 9 else None
            ma20 = df.loc[max(0, date_idx-19):date_idx, 'close'].mean() if date_idx >= 19 else None
            ma50 = df.loc[max(0, date_idx-49):date_idx, 'close'].mean() if date_idx >= 49 else None
            
            # 检查是否已存在
            cursor.execute(
                'SELECT 1 FROM index_kline WHERE date = ? AND code = ?',
                (target_date, code)
            )
            exists = cursor.fetchone()
            
            if exists:
                # 更新
                cursor.execute('''
                    UPDATE index_kline SET
                        name = ?, open = ?, close = ?, high = ?, low = ?,
                        volume = ?, ma5 = ?, ma10 = ?, ma20 = ?, ma50 = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE date = ? AND code = ?
                ''', (
                    name, row['open'], row['close'], row['high'], row['low'],
                    row['volume'], ma5, ma10, ma20, ma50,
                    target_date, code
                ))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO index_kline
                    (date, code, name, open, close, high, low, volume,
                     ma5, ma10, ma20, ma50, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    target_date, code, name,
                    row['open'], row['close'], row['high'], row['low'], row['volume'],
                    ma5, ma10, ma20, ma50
                ))
            
            success += 1
            time.sleep(0.2)  # 避免请求过快
            
        except Exception as e:
            log(f"    {name}({code}) 失败: {e}")
    
    conn.commit()
    log(f"  {target_date}: 成功 {success}/{len(INDICES)}")
    return success >= len(INDICES) * 0.3  # 至少30%成功

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查表是否存在，如果存在则删除重建（因为字段结构变了）
    cursor.execute("DROP TABLE IF EXISTS index_kline")
    
    cursor.execute('''
        CREATE TABLE index_kline (
            date TEXT NOT NULL,
            code TEXT NOT NULL,
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
            ma5 REAL,
            ma10 REAL,
            ma20 REAL,
            ma50 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date, code)
        )
    ''')
    
    conn.commit()
    conn.close()
    log("✓ 数据库表初始化完成")

def fetch_index_kline():
    log(f"开始获取指数数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化数据库
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    
    # 获取最近缺失的日期（最多2天）
    missing_dates = get_missing_dates(conn, days=2)
    conn.close()
    
    if len(missing_dates) == 0:
        log("  最近2天数据已完整，无需获取")
        return True
    
    log(f"  需要补全的日期: {missing_dates}")
    
    # 逐个日期获取
    all_success = True
    for target_date in missing_dates:
        conn = sqlite3.connect(DB_PATH)
        success = fetch_index_for_date(conn, target_date)
        conn.close()
        
        if not success:
            all_success = False
        time.sleep(1)  # 日期间隔
    
    # 统计信息
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM index_kline WHERE date = ?", (today,))
    today_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM index_kline WHERE date = ?", (yesterday,))
    yesterday_count = cursor.fetchone()[0]
    
    conn.close()
    
    log(f"完成")
    log(f"统计：今天({today}) {today_count} 条，昨天({yesterday}) {yesterday_count} 条")
    
    return all_success

if __name__ == '__main__':
    success = fetch_index_kline()
    sys.exit(0 if success else 1)
