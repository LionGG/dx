#!/usr/bin/env python3
"""
补充指数缺失字段：amount, amplitude, change_pct, change_amount, turnover
使用 stock_zh_index_spot_em 获取实时数据计算
"""

import akshare as ak
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def update_index_data():
    """更新指数数据，补充缺失字段"""
    print("=" * 60)
    print("补充指数缺失字段")
    print("=" * 60)
    
    # 获取指数实时行情数据
    print("\n获取指数实时数据...")
    df_spot = ak.stock_zh_index_spot_em()
    print(f"获取到 {len(df_spot)} 个指数")
    
    # 提取需要的字段（指数没有换手率字段）
    df_spot = df_spot[['代码', '名称', '成交额', '振幅', '涨跌幅', '涨跌额']]
    df_spot.columns = ['code', 'name', 'amount', 'amplitude', 'change_pct', 'change_amount']
    
    # 清理代码格式 (sz399001 -> 399001)
    df_spot['code'] = df_spot['code'].str[2:]
    
    # 我们只更新数据库中已有的9个指数
    target_codes = ['000001', '000016', '000300', '000905', '000852', '399001', '399006', '399673', '000688']
    df_spot = df_spot[df_spot['code'].isin(target_codes)]
    
    print(f"\n需要更新的指数: {len(df_spot)} 个")
    print(df_spot[['code', 'name']].to_string())
    
    # 由于实时数据只有最新一天，我们需要用另一种方式
    # 使用 index_zh_a_hist 重新下载完整数据
    print("\n重新下载指数完整数据...")
    
    indexes = [
        ("sh000001", "上证指数"),
        ("sh000016", "上证50"),
        ("sh000300", "沪深300"),
        ("sh000905", "中证500"),
        ("sh000852", "中证1000"),
        ("sz399001", "深证成指"),
        ("sz399006", "创业板指"),
        ("sz399673", "创业板50"),
        ("sh000688", "科创50"),
    ]
    
    conn = sqlite3.connect(DB_PATH)
    
    # 先删除现有指数数据
    cursor = conn.cursor()
    cursor.execute('DELETE FROM index_kline')
    conn.commit()
    print("已清空现有指数数据")
    
    success = 0
    for symbol, name in indexes:
        code = symbol[2:]
        print(f"下载 {name} ({code})...", end=' ')
        
        try:
            # 使用 index_zh_a_hist 获取完整数据（含涨跌幅等）
            df = ak.index_zh_a_hist(symbol=symbol, period="daily", 
                                    start_date="20260101", end_date="20261231")
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                continue
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnover'
            })
            df['code'] = code
            df['name'] = name
            
            # 保存到数据库
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount']].to_sql(
                'index_kline', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}条")
            success += 1
            
        except Exception as e:
            print(f"✗ {str(e)[:50]}")
    
    conn.close()
    print(f"\n完成: {success}/{len(indexes)} 个指数")

def verify_update():
    """验证更新结果"""
    print("\n" + "=" * 60)
    print("验证更新结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查NULL值
    cursor.execute('SELECT COUNT(*) FROM index_kline WHERE amount IS NULL')
    null_amount = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM index_kline WHERE change_pct IS NULL')
    null_change = cursor.fetchone()[0]
    
    print(f"\namount NULL: {null_amount}")
    print(f"change_pct NULL: {null_change}")
    
    # 显示样本数据
    print("\n样本数据:")
    cursor.execute('''
        SELECT code, name, date, open, close, amount, change_pct
        FROM index_kline
        WHERE code = '000001'
        ORDER BY date DESC
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    
    print(f'{"代码":<10} {"名称":<12} {"日期":<12} {"开盘":<10} {"收盘":<10} {"成交额":<15} {"涨跌幅":<8}')
    print('-' * 80)
    for row in rows:
        print(f'{row[0]:<10} {row[1]:<12} {row[2]:<12} {row[3]:<10.2f} {row[4]:<10.2f} {row[5]:<15.0f} {row[6]:<8.2f}')
    
    conn.close()

if __name__ == '__main__':
    update_index_data()
    verify_update()
