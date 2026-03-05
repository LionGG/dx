#!/usr/bin/env python3
"""
补充指数缺失字段 - 使用stock_zh_index_daily + 计算涨跌幅
"""

import akshare as ak
import pandas as pd
import sqlite3

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def update_index_with_calculated_fields():
    """使用stock_zh_index_daily下载数据并计算涨跌幅"""
    print("=" * 60)
    print("补充指数数据（使用stock_zh_index_daily + 计算字段）")
    print("=" * 60)
    
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
            # 使用stock_zh_index_daily（之前成功的API）
            df = ak.stock_zh_index_daily(symbol=symbol)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                continue
            
            # 筛选2026年数据
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= '2026-01-01'].copy()
            
            if len(df) == 0:
                print("✗ 无2026年数据")
                continue
            
            # 按日期排序
            df = df.sort_values('date').reset_index(drop=True)
            
            # 计算涨跌幅、涨跌额、振幅
            df['prev_close'] = df['close'].shift(1)
            df['change_pct'] = ((df['close'] - df['prev_close']) / df['prev_close'] * 100).round(2)
            df['change_amount'] = (df['close'] - df['prev_close']).round(2)
            df['amplitude'] = ((df['high'] - df['low']) / df['prev_close'] * 100).round(2)
            
            # 格式化日期
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # 添加code和name
            df['code'] = code
            df['name'] = name
            
            # 成交额和换手率设为None（该API不提供）
            df['amount'] = None
            df['turnover'] = None
            
            # 保存到数据库
            df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
                'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                'index_kline', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}条")
            success += 1
            
        except Exception as e:
            print(f"✗ {str(e)[:50]}")
    
    conn.close()
    print(f"\n完成: {success}/{len(indexes)} 个指数")
    return success

def verify():
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证更新结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查NULL值
    cursor.execute('SELECT COUNT(*) FROM index_kline WHERE change_pct IS NULL')
    null_change = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM index_kline WHERE amplitude IS NULL')
    null_amp = cursor.fetchone()[0]
    
    print(f"\nchange_pct NULL: {null_change} (首日无前值，正常)")
    print(f"amplitude NULL: {null_amp} (首日无前值，正常)")
    
    # 显示样本数据
    print("\n样本数据（上证指数最近5天）:")
    cursor.execute('''
        SELECT code, name, date, open, close, amplitude, change_pct, change_amount
        FROM index_kline
        WHERE code = '000001'
        ORDER BY date DESC
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    
    print(f'{"代码":<10} {"名称":<12} {"日期":<12} {"开盘":<10} {"收盘":<10} {"振幅":<8} {"涨跌幅":<8} {"涨跌额":<8}')
    print('-' * 90)
    for row in rows:
        print(f'{row[0]:<10} {row[1]:<12} {row[2]:<12} {row[3]:<10.2f} {row[4]:<10.2f} {row[5]:<8.2f} {row[6]:<8.2f} {row[7]:<8.2f}')
    
    conn.close()

if __name__ == '__main__':
    update_index_with_calculated_fields()
    verify()
