#!/usr/bin/env python3
"""
下载行业板块K线数据 - 修复版
"""

import akshare as ak
import pandas as pd
import sqlite3
from pathlib import Path
import time
import random

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_kline (
            date TEXT, code TEXT, name TEXT, sector_type TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL, amplitude REAL,
            change_pct REAL, change_amount REAL, turnover REAL,
            PRIMARY KEY (date, code)
        )
    ''')
    conn.commit()
    conn.close()

def download_sector_industry():
    """下载行业板块数据"""
    print("=" * 50)
    print("下载行业板块列表")
    print("=" * 50)
    
    try:
        # 获取行业板块列表
        df_list = ak.stock_board_industry_name_em()
        print(f"获取到 {len(df_list)} 个行业板块")
        
        conn = sqlite3.connect(DB_PATH)
        success = 0
        
        # 下载前50个行业板块
        sectors = df_list.head(50)
        
        for idx, row in sectors.iterrows():
            code = row['板块代码']
            name = row['板块名称']
            
            print(f"[{idx+1}/{len(sectors)}] {name} ({code})...", end=' ')
            
            try:
                # 使用正确的period参数 '日k'
                df = ak.stock_board_industry_hist_em(symbol=name, period="日k",
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
                df['sector_type'] = 'industry'
                
                # 保存到数据库
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low', 'volume',
                    'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
                
                print(f"✓ {len(df)}条")
                success += 1
                
            except Exception as e:
                print(f"✗ {str(e)[:30]}")
            
            time.sleep(random.uniform(0.3, 0.8))
            
            # 每20个暂停一下
            if (idx + 1) % 20 == 0:
                print(f"  进度: {idx+1}/{len(sectors)}, 成功:{success}")
                time.sleep(2)
        
        conn.close()
        print(f"\n行业板块完成: {success}/{len(sectors)}")
        return success
        
    except Exception as e:
        print(f"获取行业板块列表失败: {e}")
        return 0

def main():
    init_db()
    
    print("开始下载行业板块数据...")
    print(f"数据库: {DB_PATH}")
    
    industry_count = download_sector_industry()
    
    # 统计
    print("\n" + "=" * 50)
    print("下载完成统计")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT code) FROM sector_kline WHERE sector_type="industry"')
    industry_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sector_kline WHERE sector_type="industry"')
    industry_records = cursor.fetchone()[0]
    
    # 列出已下载的行业板块
    cursor.execute('SELECT code, name, COUNT(*) as count FROM sector_kline WHERE sector_type="industry" GROUP BY code, name ORDER BY code')
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"行业板块: {industry_total} 个")
    print(f"总记录: {industry_records} 条")
    print("\n详情:")
    for row in rows[:10]:  # 只显示前10个
        print(f"  {row[0]} {row[1]}: {row[2]}条")
    if len(rows) > 10:
        print(f"  ... 还有 {len(rows)-10} 个板块")

if __name__ == '__main__':
    main()
