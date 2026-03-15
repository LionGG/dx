#!/usr/bin/env python3
"""
ETF完整指标计算脚本 - 最终版
包含: RS强度、流动性、V5.2趋势分(含档位)
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/etf-indicators/scripts')
from trend_score_v52_etf import calculate_trend_score_v52_etf
import pymysql
from db_config import DB_CONFIG
import pandas as pd

# DB_CONFIG loaded from db_config module

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def get_etf_grade(score):
    """ETF V5.2档位划分"""
    if score >= 4.0: return "极度强势"
    elif score >= 3.5: return "强势"
    elif score >= 2.8: return "中性偏强"
    elif score >= 2.3: return "中性偏弱"
    elif score >= 1.8: return "弱势"
    else: return "极度弱势"

def get_liquidity_grade(amount_yi):
    """流动性档位划分 (单位：亿元)"""
    if amount_yi >= 10: return "S"
    elif amount_yi >= 5: return "A"
    elif amount_yi >= 2: return "B"
    else: return "C"

def calculate_rs_indicators(etf_code, trade_date, conn):
    """计算RS强度指标 (对比沪深300)"""
    # 获取ETF历史数据
    df_etf = pd.read_sql(f"""
        SELECT trade_date, close_price, volume, amount
        FROM etf_history
        WHERE stock_code = '{etf_code}' AND deleted = 0
        AND trade_date <= '{trade_date}'
        ORDER BY trade_date ASC
    """, conn)
    
    if len(df_etf) < 52:
        return None
    
    # 获取沪深300历史数据 (从index_history表)
    df_index = pd.read_sql(f"""
        SELECT trade_date, close_price
        FROM index_history
        WHERE stock_code = '000300' AND deleted = 0
        AND trade_date <= '{trade_date}'
        ORDER BY trade_date ASC
    """, conn)
    
    if len(df_index) < 52:
        return None
    
    # 计算21日收益率
    etf_price_now = df_etf.iloc[-1]['close_price']
    etf_price_21d = df_etf.iloc[-22]['close_price'] if len(df_etf) >= 22 else df_etf.iloc[0]['close_price']
    etf_return_21d = (etf_price_now / etf_price_21d - 1) * 100
    
    index_price_now = df_index.iloc[-1]['close_price']
    index_price_21d = df_index.iloc[-22]['close_price'] if len(df_index) >= 22 else df_index.iloc[0]['close_price']
    index_return_21d = (index_price_now / index_price_21d - 1) * 100
    
    # 计算52日收益率
    etf_price_52d = df_etf.iloc[-53]['close_price'] if len(df_etf) >= 53 else df_etf.iloc[0]['close_price']
    etf_return_52d = (etf_price_now / etf_price_52d - 1) * 100
    
    index_price_52d = df_index.iloc[-53]['close_price'] if len(df_index) >= 53 else df_index.iloc[0]['close_price']
    index_return_52d = (index_price_now / index_price_52d - 1) * 100
    
    # 计算RS（相对强度）
    rs_21d = etf_return_21d - index_return_21d
    rs_52d = etf_return_52d - index_return_52d
    
    # 计算5日平均成交额 (亿元) - 使用amount字段
    avg_amount_5d = df_etf['amount'].tail(5).mean() / 100000000  # 转为亿元
    
    return {
        'rs_21d': round(rs_21d, 4),
        'etf_return_21d': round(etf_return_21d, 4),
        'index_return_21d': round(index_return_21d, 4),
        'rs_52d': round(rs_52d, 4),
        'etf_return_52d': round(etf_return_52d, 4),
        'index_return_52d': round(index_return_52d, 4),
        'avg_amount_5d': round(avg_amount_5d, 4),
        'liquidity_grade': get_liquidity_grade(avg_amount_5d)
    }

def save_all_indicators(etf_code, trade_date, close_price, rs_data, trend_score, trend_grade):
    """保存所有指标到数据库"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO etf_indicators (
                stock_code, trade_date, close_price,
                rs_21d, etf_return_21d, index_return_21d,
                rs_52d, etf_return_52d, index_return_52d,
                avg_amount_5d, liquidity_grade,
                trend_score, trend_grade
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                close_price = VALUES(close_price),
                rs_21d = VALUES(rs_21d),
                etf_return_21d = VALUES(etf_return_21d),
                index_return_21d = VALUES(index_return_21d),
                rs_52d = VALUES(rs_52d),
                etf_return_52d = VALUES(etf_return_52d),
                index_return_52d = VALUES(index_return_52d),
                avg_amount_5d = VALUES(avg_amount_5d),
                liquidity_grade = VALUES(liquidity_grade),
                trend_score = VALUES(trend_score),
                trend_grade = VALUES(trend_grade)
        """, (
            etf_code, trade_date, close_price,
            rs_data['rs_21d'], rs_data['etf_return_21d'], rs_data['index_return_21d'],
            rs_data['rs_52d'], rs_data['etf_return_52d'], rs_data['index_return_52d'],
            rs_data['avg_amount_5d'], rs_data['liquidity_grade'],
            trend_score, trend_grade
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"  保存失败: {e}")
        return False
    finally:
        conn.close()

def calculate_etf_full(etf_code, start_date='2026-01-01'):
    """计算ETF完整指标"""
    conn = get_connection()
    
    # 获取所有交易日 (从etf_history表)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT DISTINCT trade_date, close_price
        FROM etf_history 
        WHERE stock_code = '{etf_code}' 
        AND trade_date >= '{start_date}'
        AND deleted = 0
        ORDER BY trade_date ASC
    """)
    rows = cursor.fetchall()
    cursor.close()
    
    dates = [(row[0].strftime('%Y-%m-%d'), row[1]) for row in rows]
    
    print(f"ETF {etf_code} 共{len(dates)}个交易日")
    print(f"开始计算完整指标...")
    print()
    
    success = 0
    failed = 0
    
    for i, (date, close_price) in enumerate(dates, 1):
        # 计算RS指标
        rs_data = calculate_rs_indicators(etf_code, date, conn)
        if not rs_data:
            failed += 1
            continue
        
        # 计算V5.2趋势分 (ETF版本)
        trend_result = calculate_trend_score_v52_etf(etf_code, date)
        if not trend_result:
            failed += 1
            continue
        
        trend_score = trend_result['score']
        trend_grade = get_etf_grade(trend_score)
        
        # 保存所有数据
        if save_all_indicators(etf_code, date, close_price, rs_data, trend_score, trend_grade):
            success += 1
            if i % 10 == 0:
                print(f"  已处理 {i}/{len(dates)}: {date}")
        else:
            failed += 1
    
    conn.close()
    
    print()
    print(f"✅ 完成! 成功: {success} 条, 失败: {failed} 条")

if __name__ == "__main__":
    import sys
    
    # 支持命令行参数或默认计算159326
    if len(sys.argv) > 1:
        etf_code = sys.argv[1]
    else:
        etf_code = "159326"
    
    start_date = "2026-01-01"
    
    print("="*70)
    print(f"计算ETF {etf_code} 完整指标")
    print("="*70)
    print()
    
    calculate_etf_full(etf_code, start_date)
    
    print()
    print("="*70)
