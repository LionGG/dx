#!/usr/bin/env python3
"""
每日增量数据更新脚本 - 分时版本
- 15:45 更新：指数、板块、个股、涨停板生态
- 18:00 更新：资金流向、龙虎榜
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time
import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'akshare_full.db')

# 导入交易日判断工具
sys.path.insert(0, SCRIPT_DIR)
from trading_date import get_today_trading_date, format_date

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def log(msg):
    """打印带时间戳的日志"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def update_stock_kline(date_str, date_dash):
    """更新个股K线数据（不复权）"""
    log(f"[1/5] 更新个股K线 - {date_dash}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有股票代码
    cursor.execute('SELECT DISTINCT code FROM stock_kline')
    stocks = [row[0] for row in cursor.fetchall()]
    
    log(f"  共 {len(stocks)} 只股票")
    
    success = 0
    batch_size = 100
    
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        for code in batch:
            try:
                df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                       start_date=date_str, end_date=date_str)
                
                if df is not None and len(df) > 0:
                    cursor.execute('SELECT name FROM stock_kline WHERE code=? LIMIT 1', (code,))
                    name_row = cursor.fetchone()
                    name = name_row[0] if name_row else ''
                    
                    df = df.rename(columns={
                        '日期': 'date', '开盘': 'open', '收盘': 'close',
                        '最高': 'high', '最低': 'low', '成交量': 'volume',
                        '成交额': 'amount', '振幅': 'amplitude',
                        '涨跌幅': 'change_pct', '涨跌额': 'change_amount',
                        '换手率': 'turnover'
                    })
                    df['code'] = code
                    df['name'] = name
                    
                    df[['date', 'code', 'name', 'open', 'close', 'high', 'low',
                        'volume', 'amount', 'amplitude', 'change_pct', 
                        'change_amount', 'turnover']].to_sql(
                        'stock_kline', conn, if_exists='append', index=False)
                    
                    success += 1
                
            except Exception as e:
                pass
            
            time.sleep(0.03)
        
        if (i // batch_size + 1) % 10 == 0:
            log(f"  进度: {min(i+batch_size, len(stocks))}/{len(stocks)}")
    
    conn.close()
    log(f"  完成: 成功 {success}/{len(stocks)}")
    return success

def update_stock_kline_qfq(date_str, date_dash):
    """更新个股K线数据（前复权）"""
    log(f"[2/5] 更新个股K线（前复权） - {date_dash}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有股票代码
    cursor.execute('SELECT DISTINCT code FROM stock_kline')
    stocks = [row[0] for row in cursor.fetchall()]
    
    log(f"  共 {len(stocks)} 只股票")
    
    # 创建前复权表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_kline_qfq (
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
    
    success = 0
    batch_size = 100
    
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        for code in batch:
            try:
                # 关键：adjust="qfq" 获取前复权数据
                df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                       start_date=date_str, end_date=date_str,
                                       adjust="qfq")
                
                if df is not None and len(df) > 0:
                    cursor.execute('SELECT name FROM stock_kline WHERE code=? LIMIT 1', (code,))
                    name_row = cursor.fetchone()
                    name = name_row[0] if name_row else ''
                    
                    df = df.rename(columns={
                        '日期': 'date', '开盘': 'open', '收盘': 'close',
                        '最高': 'high', '最低': 'low', '成交量': 'volume',
                        '成交额': 'amount', '振幅': 'amplitude',
                        '涨跌幅': 'change_pct', '涨跌额': 'change_amount',
                        '换手率': 'turnover'
                    })
                    df['code'] = code
                    df['name'] = name
                    
                    df[['date', 'code', 'name', 'open', 'close', 'high', 'low',
                        'volume', 'amount', 'amplitude', 'change_pct', 
                        'change_amount', 'turnover']].to_sql(
                        'stock_kline_qfq', conn, if_exists='append', index=False)
                    
                    success += 1
                
            except Exception as e:
                pass
            
            time.sleep(0.03)
        
        if (i // batch_size + 1) % 10 == 0:
            log(f"  进度: {min(i+batch_size, len(stocks))}/{len(stocks)}")
    
    conn.close()
    log(f"  完成: 成功 {success}/{len(stocks)}")
    return success

def update_index_kline(date_dash):
    """更新指数K线数据"""
    log(f"[3/5] 更新指数K线 - {date_dash}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT code, name FROM index_kline')
    indices = cursor.fetchall()
    
    success = 0
    
    for code, name in indices:
        try:
            df = ak.stock_zh_index_daily(symbol=code)
            
            if df is not None and len(df) > 0:
                df['date'] = pd.to_datetime(df['date'])
                df = df[df['date'] == date_dash]
                
                if len(df) > 0:
                    # 计算涨跌幅和振幅
                    df_prev = ak.stock_zh_index_daily(symbol=code)
                    if df_prev is not None and len(df_prev) > 1:
                        prev_close = df_prev.iloc[-2]['close']
                        df['amplitude'] = ((df['high'] - df['low']) / prev_close * 100).round(2)
                        df['change_pct'] = ((df['close'] - prev_close) / prev_close * 100).round(2)
                        df['change_amount'] = (df['close'] - prev_close).round(2)
                    else:
                        df['amplitude'] = 0
                        df['change_pct'] = 0
                        df['change_amount'] = 0
                    
                    df['turnover'] = 0
                    df['code'] = code
                    df['name'] = name
                    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                    
                    df[['date', 'code', 'name', 'open', 'close', 'high', 'low',
                        'volume', 'amount', 'amplitude', 'change_pct',
                        'change_amount', 'turnover']].to_sql(
                        'index_kline', conn, if_exists='append', index=False)
                    
                    success += 1
            
        except Exception as e:
            log(f"  {code} 失败: {e}")
    
    conn.close()
    log(f"  完成: 成功 {success}/{len(indices)}")
    return success

def update_sector_kline(date_str, date_dash):
    """更新板块K线数据"""
    log(f"[4/5] 更新板块K线 - {date_dash}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT code, name, sector_type FROM sector_kline')
    sectors = cursor.fetchall()
    
    success = 0
    
    for code, name, sector_type in sectors:
        try:
            if sector_type == 'concept':
                df = ak.stock_board_concept_hist_em(symbol=name, period="daily",
                                                    start_date=date_str, end_date=date_str)
            else:
                df = ak.stock_board_industry_hist_em(symbol=name, period="日k",
                                                     start_date=date_str, end_date=date_str)
            
            if df is not None and len(df) > 0:
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '振幅': 'amplitude',
                    '涨跌幅': 'change_pct', '涨跌额': 'change_amount',
                    '换手率': 'turnover'
                })
                df['code'] = code
                df['name'] = name
                df['sector_type'] = sector_type
                
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low',
                    'volume', 'amount', 'amplitude', 'change_pct',
                    'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
                
                success += 1
            
        except Exception as e:
            pass
        
        time.sleep(0.05)
    
    conn.close()
    log(f"  完成: 成功 {success}/{len(sectors)}")
    return success

def update_limit_up_ecology(date_str, date_dash):
    """更新涨停板生态数据"""
    log(f"[5/5] 更新涨停板生态 - {date_dash}")
    
    conn = get_db_connection()
    
    # 涨停池
    try:
        df = ak.stock_zt_pool_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('zt_pool', conn, if_exists='append', index=False)
            log(f"  涨停池: {len(df)} 条")
    except Exception as e:
        log(f"  涨停池失败: {e}")
    
    # 跌停池
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('dt_pool', conn, if_exists='append', index=False)
            log(f"  跌停池: {len(df)} 条")
    except Exception as e:
        log(f"  跌停池失败: {e}")
    
    # 炸板池
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('zbgc_pool', conn, if_exists='append', index=False)
            log(f"  炸板池: {len(df)} 条")
    except Exception as e:
        log(f"  炸板池失败: {e}")
    
    # 强势股池
    try:
        df = ak.stock_zt_pool_strong_em(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('strong_pool', conn, if_exists='append', index=False)
            log(f"  强势股池: {len(df)} 条")
    except Exception as e:
        log(f"  强势股池失败: {e}")
    
    conn.close()
    log("  完成")

def update_lhb(date_str, date_dash):
    """更新龙虎榜数据（18:00批次）"""
    log(f"[18:00批次] 更新龙虎榜 - {date_dash}")
    
    conn = get_db_connection()
    
    try:
        df = ak.stock_lhb_detail_daily_sina(date=date_str)
        if df is not None and len(df) > 0:
            df['date'] = date_dash
            df.to_sql('lhb_daily', conn, if_exists='append', index=False)
            log(f"  龙虎榜: {len(df)} 条")
        else:
            log("  龙虎榜: 无数据")
    except Exception as e:
        log(f"  龙虎榜失败: {e}")
    
    conn.close()

def update_sector_fund_flow_rank(date_dash):
    """更新板块资金流向排名（18:00批次）- 使用rank API，一次获取所有板块"""
    log("[18:00批次] 更新板块资金流向排名")
    
    conn = get_db_connection()
    
    try:
        df = ak.stock_sector_fund_flow_rank()
        
        if df is not None and len(df) > 0:
            df = df.rename(columns={
                '序号': 'rank',
                '名称': 'name',
                '今日涨跌幅': 'change_pct',
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
            df['date'] = date_dash
            
            df[['date', 'rank', 'name', 'change_pct',
                'main_net_inflow', 'main_net_inflow_pct',
                'super_large_net_inflow', 'super_large_net_inflow_pct',
                'large_net_inflow', 'large_net_inflow_pct',
                'medium_net_inflow', 'medium_net_inflow_pct',
                'small_net_inflow', 'small_net_inflow_pct',
                'top_stock']].to_sql(
                'sector_fund_flow_rank', conn, if_exists='append', index=False)
            
            log(f"  板块资金流向排名: {len(df)} 条")
        else:
            log("  板块资金流向排名: 无数据")
    
    except Exception as e:
        log(f"  板块资金流向排名失败: {e}")
    
    conn.close()

def verify_update(date_dash, batch='1545'):
    """验证更新结果"""
    log("=" * 50)
    log("验证更新结果")
    log("=" * 50)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if batch == '1545':
        tables = [
            ('stock_kline', '个股K线'),
            ('stock_kline_qfq', '个股K线(前复权)'),
            ('index_kline', '指数K线'),
            ('sector_kline', '板块K线'),
            ('zt_pool', '涨停池'),
            ('dt_pool', '跌停池'),
            ('zbgc_pool', '炸板池'),
            ('strong_pool', '强势股池'),
        ]
    else:  # 1800
        tables = [
            ('lhb_daily', '龙虎榜'),
            ('sector_fund_flow_rank', '板块资金流向排名'),
        ]
    
    for table, name in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE date=?', (date_dash,))
        count = cursor.fetchone()[0]
        log(f"{name:12s}: {count} 条")
    
    conn.close()

def run_1545_batch():
    """运行15:45批次更新"""
    log("=" * 60)
    log("AKShare 每日增量更新 - 15:45批次")
    log("=" * 60)
    
    # 获取今天对应的交易日
    trading_date = get_today_trading_date()
    date_str = format_date(trading_date, 'compact')
    date_dash = trading_date
    
    log(f"目标交易日: {date_dash}")
    
    # 执行更新
    update_stock_kline(date_str, date_dash)
    update_stock_kline_qfq(date_str, date_dash)  # 新增：前复权数据
    update_index_kline(date_dash)
    update_sector_kline(date_str, date_dash)
    update_limit_up_ecology(date_str, date_dash)
    
    # 验证
    verify_update(date_dash, '1545')
    
    log("=" * 60)
    log("15:45批次更新完成！")
    log("=" * 60)

def run_1800_batch():
    """运行18:00批次更新"""
    log("=" * 60)
    log("AKShare 每日增量更新 - 18:00批次")
    log("=" * 60)
    
    # 获取今天对应的交易日
    trading_date = get_today_trading_date()
    date_str = format_date(trading_date, 'compact')
    date_dash = trading_date
    
    log(f"目标交易日: {date_dash}")
    
    # 执行更新
    update_lhb(date_str, date_dash)
    update_sector_fund_flow_rank(date_dash)
    
    # 验证
    verify_update(date_dash, '1800')
    
    log("=" * 60)
    log("18:00批次更新完成！")
    log("=" * 60)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        batch = sys.argv[1]
        if batch == '1545':
            run_1545_batch()
        elif batch == '1800':
            run_1800_batch()
        else:
            print("用法: python3 daily_update_v2.py [1545|1800]")
            print("  1545 - 更新指数、板块、个股、涨停板生态")
            print("  1800 - 更新资金流向、龙虎榜")
    else:
        # 默认根据当前时间判断
        now = datetime.now()
        hour = now.hour
        
        if hour < 18:
            run_1545_batch()
        else:
            run_1800_batch()

if __name__ == '__main__':
    main()
