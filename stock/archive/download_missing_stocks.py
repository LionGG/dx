#!/usr/bin/env python3
"""
下载缺失的股票K线数据
"""

import akshare as ak
import pandas as pd
import sqlite3
from pathlib import Path
import time
import random

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'
CSV_DIR = '/root/.openclaw/workspace/stock/a_stock_data/history/stocks'

def get_missing_stocks():
    """获取数据库中缺失的股票代码"""
    # 获取CSV目录中所有股票代码
    csv_files = list(Path(CSV_DIR).glob('*.csv'))
    csv_codes = {f.stem for f in csv_files}
    
    # 获取数据库中已有的股票代码
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT code FROM stock_kline')
    db_codes = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # 找出CSV中有但数据库中没有的（失败的）
    missing = csv_codes - db_codes
    return sorted(list(missing))

def download_stock(code):
    """下载单只股票K线数据"""
    try:
        # 添加前缀
        if code.startswith('6'):
            symbol = f"{code}.sh"
        elif code.startswith('0') or code.startswith('3'):
            symbol = f"{code}.sz"
        elif code.startswith('8') or code.startswith('4'):
            symbol = f"{code}.bj"
        elif code.startswith('92'):
            symbol = f"{code}.bj"
        else:
            symbol = code
        
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                start_date="20260101", end_date="20261231", adjust="")
        
        if df is None or len(df) == 0:
            return None
        
        # 重命名列
        df = df.rename(columns={
            '日期': 'date',
            '股票代码': 'code',
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
        df['name'] = ''
        return df
        
    except Exception as e:
        print(f"  下载失败 {code}: {e}")
        return None

def save_to_db(df):
    """保存到数据库"""
    conn = sqlite3.connect(DB_PATH)
    df[['date', 'code', 'name', 'open', 'close', 'high', 'low', 'volume',
        'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
        'stock_kline', conn, if_exists='append', index=False)
    conn.close()

def main():
    missing = get_missing_stocks()
    print(f"缺失股票: {len(missing)} 只")
    
    if len(missing) == 0:
        print("没有缺失数据")
        return
    
    success = 0
    for i, code in enumerate(missing):
        print(f"[{i+1}/{len(missing)}] 下载 {code}...", end=' ')
        
        df = download_stock(code)
        if df is not None and len(df) > 0:
            save_to_db(df)
            print(f"✓ {len(df)}条")
            success += 1
        else:
            print("✗")
        
        # 随机延迟，避免被封
        time.sleep(random.uniform(0.3, 0.8))
        
        # 每50只保存一次进度
        if (i + 1) % 50 == 0:
            print(f"  进度: {i+1}/{len(missing)}, 成功:{success}")
    
    print(f"\n完成: 成功下载 {success}/{len(missing)} 只股票")

if __name__ == '__main__':
    main()
