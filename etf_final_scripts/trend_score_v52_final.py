#!/usr/bin/env python3
"""
趋势分公式 - V5.2版 (最终优化版)
调整: 
1. 3/4多头排列 + MA5>-0.5% → +0.5分
2. 4/4完美多头 + MA5>-0.5% → +1.0分 (可触发保底3.85)
"""

import pymysql
from db_config import DB_CONFIG
import pandas as pd

# DB_CONFIG loaded from db_config module

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def calculate_trend_score_v52(stock_code, target_date=None):
    """V5.2 - 3/4多头排列+0.5分"""
    
    conn = get_connection()
    try:
        df = pd.read_sql(f"""
            SELECT trade_date, close_price, volume
            FROM stock_history WHERE stock_code = '{stock_code}' AND deleted = 0
            ORDER BY trade_date ASC
        """, conn)
        
        if len(df) < 150: return None
        
        for m in [5, 10, 20, 60, 120]:
            df[f'ma{m}'] = df['close_price'].rolling(m).mean()
        
        if target_date:
            df['date_str'] = df['trade_date'].astype(str)
            target_row = df[df['date_str'] == target_date]
            if len(target_row) == 0: return None
            cur = target_row.iloc[0]
        else:
            cur = df.iloc[-1]
        
        p = cur['close_price']
        
        f = {
            'dist_ma5': (p/cur['ma5']-1)*100,
            'dist_ma10': (p/cur['ma10']-1)*100,
            'dist_ma20': (p/cur['ma20']-1)*100,
            'dist_ma60': (p/cur['ma60']-1)*100,
            'dist_ma120': (p/cur['ma120']-1)*100,
            'dist_5_10': (cur['ma5']/cur['ma10']-1)*100,
            'dist_10_20': (cur['ma10']/cur['ma20']-1)*100,
            'dist_20_60': (cur['ma20']/cur['ma60']-1)*100,
            'dist_60_120': (cur['ma60']/cur['ma120']-1)*100,
            'r20': (p-df.iloc[-21]['close_price'])/df.iloc[-21]['close_price']*100,
        }
        
        scores = {}
        
        # 基础因子
        d5 = f['dist_ma5']
        if d5 >= 8: scores['short'] = 0.8
        elif d5 >= 3: scores['short'] = 0.5 + (d5 - 3) * 0.06
        elif d5 >= -0.5: scores['short'] = 0.35 + d5 * 0.05
        elif d5 >= -4: scores['short'] = max(0.15, 0.325 + (d5 + 0.5) * 0.05)
        elif d5 >= -7: scores['short'] = max(-0.1, 0.2 + (d5 + 4) * 0.033)
        else: scores['short'] = max(-0.35, -0.1 + (d5 + 7) * 0.05)
        
        d20 = f['dist_ma20']
        if d20 >= 12: m1 = 0.55
        elif d20 >= 0: m1 = 0.22 + d20 * 0.0275
        elif d20 >= -10: m1 = max(0.1, 0.22 + d20 * 0.022)
        else: m1 = max(-0.15, 0.1 + (d20 + 10) * 0.02)
        
        d60 = f['dist_ma60']
        if d60 >= 15: m2 = 0.55
        elif d60 >= 0: m2 = 0.22 + d60 * 0.022
        elif d60 >= -12: m2 = max(0.1, 0.22 + d60 * 0.018)
        else: m2 = max(-0.15, 0.1 + (d60 + 12) * 0.017)
        scores['mid'] = (m1 + m2) / 2
        
        d120 = f['dist_ma120']
        if d120 >= 40: scores['long'] = 0.35
        elif d120 >= 0: scores['long'] = 0.12 + d120 * 0.00575
        elif d120 >= -15: scores['long'] = max(0.05, 0.12 + d120 * 0.0047)
        else: scores['long'] = max(-0.15, 0.05 + (d120 + 15) * 0.01)
        
        d = f['dist_5_10']
        if d >= 2: a1 = 0.38
        elif d >= 0: a1 = 0.12 + d * 0.13
        elif d >= -5: a1 = max(-0.08, d * 0.016)
        else: a1 = -0.12
        
        d = f['dist_10_20']
        if d >= 3: a2 = 0.38
        elif d >= 0: a2 = 0.12 + d * 0.087
        elif d >= -5: a2 = max(-0.08, d * 0.016)
        else: a2 = -0.12
        
        d = f['dist_20_60']
        if d >= 3: a3 = 0.38
        elif d >= 0: a3 = 0.15 + d * 0.077
        elif d >= -5: a3 = max(-0.1, d * 0.014)
        else: a3 = max(-0.2, -0.1 + (d+5) * 0.02)
        
        d = f['dist_60_120']
        if d >= 8: a4 = 0.38
        elif d >= 0: a4 = 0.12 + d * 0.0325
        elif d >= -8: a4 = max(-0.08, d * 0.01)
        else: a4 = -0.12
        scores['align'] = a1 + a2 + a3 + a4
        
        # 判断条件
        is_bull_5_10 = f['dist_5_10'] > 0
        is_bull_10_20 = f['dist_10_20'] > 0
        is_bull_20_60 = f['dist_20_60'] > 0
        is_bull_60_120 = f['dist_60_120'] > -1
        
        bull_count = sum([is_bull_5_10, is_bull_10_20, is_bull_20_60, is_bull_60_120])
        is_perfect_bull = bull_count == 4
        is_3of4_bull = bull_count == 3
        is_above_ma5 = f['dist_ma5'] > -0.5
        
        # V5.2: 多头排列加分 (3/4给+0.5分)
        bull_bonus = 0
        if is_perfect_bull and is_above_ma5:
            bull_bonus = 1.0
        elif is_perfect_bull and not is_above_ma5:
            bull_bonus = 0.5
        elif is_3of4_bull and is_above_ma5:
            bull_bonus = 0.5  # V5.2: 3/4多头+站上5日线 +0.5分
        
        # 主升浪额外加分
        r20 = f['r20']
        is_close_bull = bull_count >= 3
        main_wave_bonus = 0.3 if (r20 > 50 and is_close_bull) else 0
        
        # 总分
        bias = 0.75
        total = bias + scores['short'] + scores['mid'] + scores['long'] + \
                scores['align'] + bull_bonus + main_wave_bonus
        
        # 保底3.85分 (只有完美4/4多头才能触发)
        if is_perfect_bull and is_above_ma5 and total < 3.85:
            total = 3.85
        
        score = max(0.0, min(5.0, round(total, 1)))
        
        if score >= 4.5: grade = "极度强势"
        elif score >= 3.8: grade = "强势"
        elif score >= 3.0: grade = "中性偏强"
        elif score >= 2.5: grade = "中性偏弱"
        elif score >= 2.0: grade = "弱势"
        else: grade = "极度弱势"
        
        return {
            'score': score, 'grade': grade,
            'details': {
                'bias': bias, 'short_pos': scores['short'], 'mid_pos': scores['mid'],
                'long_pos': scores['long'], 'alignment': scores['align'],
                'bull_bonus': bull_bonus, 'main_wave_bonus': main_wave_bonus,
                'bull_count': bull_count, 'is_perfect_bull': is_perfect_bull,
                'is_3of4_bull': is_3of4_bull, 'is_above_ma5': is_above_ma5,
                'ma5_dist': f['dist_ma5'], 'r20': r20
            }
        }
    finally:
        conn.close()

if __name__ == "__main__":
    result = calculate_trend_score_v52('002961', '2026-03-06')
    print(f"瑞达期货V5.2: {result['score']}分 (3/4多头, +{result['details']['bull_bonus']:.1f}分)")
