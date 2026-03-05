#!/usr/bin/env python3
"""
A股数据读取模块
从 a-share-warehouse 数据库读取数据
"""

import sqlite3
import os
from datetime import datetime, timedelta

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                       '..', 'a-share-warehouse', 'data', 'akshare_full.db')

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def get_market_summary(date_str):
    """获取市场概况数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取指数数据
    cursor.execute('''
        SELECT code, name, close, change_pct, amount 
        FROM index_kline 
        WHERE date = ? AND code IN ('000001', '399001', '399006', '000688')
    ''', (date_str,))
    indices = {row[0]: {'name': row[1], 'close': row[2], 'change_pct': row[3], 'amount': row[4]} 
               for row in cursor.fetchall()}
    
    # 获取涨跌家数统计（从个股数据计算）
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN change_pct > 0 THEN 1 ELSE 0 END) as up_count,
               SUM(CASE WHEN change_pct < 0 THEN 1 ELSE 0 END) as down_count,
               SUM(CASE WHEN change_pct = 0 THEN 1 ELSE 0 END) as flat_count,
               SUM(amount) as total_amount
        FROM stock_kline 
        WHERE date = ?
    ''', (date_str,))
    row = cursor.fetchone()
    market_stats = {
        'total': row[0],
        'up_count': row[1] or 0,
        'down_count': row[2] or 0,
        'flat_count': row[3] or 0,
        'total_amount': (row[4] or 0) / 1e8  # 转换为亿
    }
    
    # 获取涨停跌停数据
    cursor.execute('''
        SELECT COUNT(*) FROM zt_pool WHERE date = ?
    ''', (date_str.replace('-', ''),))
    limit_up = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM dt_pool WHERE date = ?
    ''', (date_str.replace('-', ''),))
    limit_down = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'indices': indices,
        'market_stats': market_stats,
        'limit_up': limit_up,
        'limit_down': limit_down
    }

def get_sector_data(date_str):
    """获取板块数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取板块涨跌幅排名
    cursor.execute('''
        SELECT code, name, change_pct, sector_type
        FROM sector_kline 
        WHERE date = ?
        ORDER BY change_pct DESC
    ''', (date_str,))
    sectors = [{'code': row[0], 'name': row[1], 'change_pct': row[2], 'type': row[3]} 
               for row in cursor.fetchall()]
    
    # 获取板块资金流向
    cursor.execute('''
        SELECT sector_name, main_net_inflow, main_net_inflow_pct
        FROM sector_fund_flow
        WHERE date = ?
        ORDER BY main_net_inflow DESC
    ''', (date_str,))
    fund_flow = [{'name': row[0], 'net_inflow': row[1], 'net_inflow_pct': row[2]} 
                 for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'sectors': sectors,
        'fund_flow': fund_flow
    }

def get_emotion_data(date_str):
    """获取情绪数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取涨停池详细信息
    cursor.execute('''
        SELECT code, name, 连板数, 所属行业
        FROM zt_pool
        WHERE date = ?
        ORDER BY 连板数 DESC
    ''', (date_str.replace('-', ''),))
    zt_stocks = [{'code': row[0], 'name': row[1], 'boards': row[2], 'industry': row[3]} 
                 for row in cursor.fetchall()]
    
    # 计算连板高度
    max_boards = max([s['boards'] for s in zt_stocks], default=0)
    
    # 获取昨日数据对比
    prev_date = get_prev_trading_day(date_str)
    if prev_date:
        cursor.execute('SELECT COUNT(*) FROM zt_pool WHERE date = ?', (prev_date.replace('-', ''),))
        prev_zt_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM dt_pool WHERE date = ?', (prev_date.replace('-', ''),))
        prev_dt_count = cursor.fetchone()[0]
    else:
        prev_zt_count = 0
        prev_dt_count = 0
    
    conn.close()
    
    return {
        'zt_stocks': zt_stocks,
        'max_boards': max_boards,
        'prev_zt_count': prev_zt_count,
        'prev_dt_count': prev_dt_count
    }

def get_prev_trading_day(date_str):
    """获取前一个交易日"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT date FROM stock_kline 
        WHERE date < ? 
        ORDER BY date DESC 
        LIMIT 1
    ''', (date_str,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_recent_days_data(date_str, n=5):
    """获取最近N天数据用于演变分析"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT date FROM stock_kline 
        WHERE date <= ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (date_str, n))
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(dates)

def get_sector_detail_data(date_str):
    """获取板块详细数据（含成交额、换手率等）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取板块K线数据（含成交额、换手率）
    cursor.execute('''
        SELECT name, close, change_pct, amount, turnover, volume,
               open, high, low, amplitude
        FROM sector_kline 
        WHERE date = ?
        ORDER BY change_pct DESC
    ''', (date_str,))
    
    sectors = []
    for row in cursor.fetchall():
        sectors.append({
            'name': row[0],
            'close': row[1],
            'change_pct': row[2],
            'amount': row[3] / 1e8 if row[3] else 0,
            'turnover': row[4],
            'volume': row[5],
            'open': row[6],
            'high': row[7],
            'low': row[8],
            'amplitude': row[9]
        })
    
    # 获取板块资金流向
    cursor.execute('''
        SELECT sector_name, main_net_inflow, main_net_inflow_pct,
               super_large_net_inflow, large_net_inflow
        FROM sector_fund_flow 
        WHERE date = ?
    ''', (date_str,))
    
    fund_flow = {row[0]: {
        'main_net_inflow': row[1] / 1e8 if row[1] else 0,
        'main_net_inflow_pct': row[2],
        'super_large': row[3] / 1e8 if row[3] else 0,
        'large': row[4] / 1e8 if row[4] else 0
    } for row in cursor.fetchall()}
    
    conn.close()
    return sectors, fund_flow

def get_zt_pool_detail(date_str):
    """获取涨停池详细数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 日期格式转换 2026-02-13 -> 20260213
    date_compact = date_str.replace('-', '')
    
    cursor.execute('''
        SELECT code, name, change_pct, close, amount, 
               float_market_cap, turnover, seal_amount,
               first_seal_time, 炸板次数, 连板数, 所属行业
        FROM zt_pool 
        WHERE date = ?
        ORDER BY 连板数 DESC, first_seal_time ASC
    ''', (date_compact,))
    
    zt_stocks = []
    for row in cursor.fetchall():
        zt_stocks.append({
            'code': row[0],
            'name': row[1],
            'change_pct': row[2],
            'close': row[3],
            'amount': row[4] / 1e8 if row[4] else 0,
            'float_cap': row[5] / 1e8 if row[5] else 0,
            'turnover': row[6],
            'seal_amount': row[7] / 1e8 if row[7] else 0,
            'first_seal_time': row[8],
            '炸板次数': row[9],
            'boards': row[10],
            'industry': row[11]
        })
    
    conn.close()
    return zt_stocks

def get_sector_stocks(sector_name, date_str):
    """获取板块内所有个股（用于找中军）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先找板块代码
    cursor.execute('''
        SELECT DISTINCT sector_code 
        FROM sector_stocks 
        WHERE sector_name = ?
    ''', (sector_name,))
    row = cursor.fetchone()
    
    if not row:
        # 尝试模糊匹配
        cursor.execute('''
            SELECT DISTINCT sector_code, sector_name
            FROM sector_stocks 
            WHERE sector_name LIKE ?
        ''', (f'%{sector_name}%',))
        row = cursor.fetchone()
    
    if not row:
        return []
    
    sector_code = row[0]
    
    # 获取板块内个股当日表现
    cursor.execute('''
        SELECT s.stock_code, s.stock_name, k.close, k.change_pct, 
               k.amount, k.turnover
        FROM sector_stocks s
        LEFT JOIN stock_kline k ON s.stock_code = k.code AND k.date = ?
        WHERE s.sector_code = ?
    ''', (date_str, sector_code))
    
    stocks = []
    for row in cursor.fetchall():
        if row[2]:  # 有数据
            stocks.append({
                'code': row[0],
                'name': row[1],
                'close': row[2],
                'change_pct': row[3],
                'amount': row[4] / 1e8 if row[4] else 0,
                'turnover': row[5]
            })
    
    # 按成交额排序（找中军）
    stocks.sort(key=lambda x: x['amount'], reverse=True)
    conn.close()
    return stocks

def get_lhb_data(date_str):
    """获取龙虎榜数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 日期格式转换
    date_compact = date_str.replace('-', '')
    
    cursor.execute('''
        SELECT code, name, close, indicator_value, amount, indicator
        FROM lhb_daily 
        WHERE date = ?
    ''', (date_compact,))
    
    lhb = []
    for row in cursor.fetchall():
        lhb.append({
            'code': row[0],
            'name': row[1],
            'close': row[2],
            'indicator_value': row[3],
            'amount': row[4] / 1e8 if row[4] else 0,
            'indicator': row[5]
        })
    
    conn.close()
    return lhb

if __name__ == '__main__':
    # 测试
    test_date = '2026-02-13'
    print(f'测试日期: {test_date}')
    print(f'市场概况: {get_market_summary(test_date)}')
    print(f'板块数据: {len(get_sector_data(test_date)["sectors"])} 个板块')
    print(f'情绪数据: {get_emotion_data(test_date)}')
