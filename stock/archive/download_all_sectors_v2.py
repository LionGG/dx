#!/usr/bin/env python3
"""
下载全部概念和行业板块K线数据 - 修复版
概念板块用 daily，行业板块用 日k
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

def clear_existing_sectors():
    """清空现有板块数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sector_kline')
    conn.commit()
    conn.close()
    print("已清空现有板块数据")

def download_all_concept_sectors():
    """下载全部概念板块数据 - 使用 daily"""
    print("=" * 60)
    print("下载全部概念板块")
    print("=" * 60)
    
    try:
        df_list = ak.stock_board_concept_name_em()
        total = len(df_list)
        print(f"获取到 {total} 个概念板块")
        
        conn = sqlite3.connect(DB_PATH)
        success = 0
        failed = []
        
        for idx, row in df_list.iterrows():
            code = row['板块代码']
            name = row['板块名称']
            
            print(f"[{idx+1}/{total}] {name} ({code})...", end=' ')
            
            try:
                # 概念板块用 daily
                df = ak.stock_board_concept_hist_em(symbol=name, period="daily",
                                                    start_date="20260101", end_date="20261231")
                
                if df is None or len(df) == 0:
                    print("✗ 无数据")
                    failed.append((code, name, '无数据'))
                    continue
                
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '振幅': 'amplitude',
                    '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                })
                df['code'] = code
                df['name'] = name
                df['sector_type'] = 'concept'
                
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low', 'volume',
                    'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
                
                print(f"✓ {len(df)}条")
                success += 1
                
            except Exception as e:
                print(f"✗ {str(e)[:30]}")
                failed.append((code, name, str(e)[:50]))
            
            time.sleep(random.uniform(0.2, 0.5))
            
            if (idx + 1) % 50 == 0:
                print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}")
                time.sleep(2)
        
        conn.close()
        print(f"\n概念板块完成: {success}/{total}")
        return success, failed
        
    except Exception as e:
        print(f"获取概念板块列表失败: {e}")
        return 0, []

def download_all_industry_sectors():
    """下载全部行业板块数据 - 使用 日k"""
    print("\n" + "=" * 60)
    print("下载全部行业板块")
    print("=" * 60)
    
    try:
        df_list = ak.stock_board_industry_name_em()
        total = len(df_list)
        print(f"获取到 {total} 个行业板块")
        
        conn = sqlite3.connect(DB_PATH)
        success = 0
        failed = []
        
        for idx, row in df_list.iterrows():
            code = row['板块代码']
            name = row['板块名称']
            
            print(f"[{idx+1}/{total}] {name} ({code})...", end=' ')
            
            try:
                # 行业板块用 日k
                df = ak.stock_board_industry_hist_em(symbol=name, period="日k",
                                                     start_date="20260101", end_date="20261231")
                
                if df is None or len(df) == 0:
                    print("✗ 无数据")
                    failed.append((code, name, '无数据'))
                    continue
                
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '振幅': 'amplitude',
                    '涨跌幅': 'change_pct', '涨跌额': 'change_amount', '换手率': 'turnover'
                })
                df['code'] = code
                df['name'] = name
                df['sector_type'] = 'industry'
                
                df[['date', 'code', 'name', 'sector_type', 'open', 'close', 'high', 'low', 'volume',
                    'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']].to_sql(
                    'sector_kline', conn, if_exists='append', index=False)
                
                print(f"✓ {len(df)}条")
                success += 1
                
            except Exception as e:
                print(f"✗ {str(e)[:30]}")
                failed.append((code, name, str(e)[:50]))
            
            time.sleep(random.uniform(0.2, 0.5))
            
            if (idx + 1) % 50 == 0:
                print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}")
                time.sleep(2)
        
        conn.close()
        print(f"\n行业板块完成: {success}/{total}")
        return success, failed
        
    except Exception as e:
        print(f"获取行业板块列表失败: {e}")
        return 0, []

def main():
    init_db()
    clear_existing_sectors()
    
    print("开始下载全部板块数据...")
    print(f"数据库: {DB_PATH}")
    print()
    
    concept_success, concept_failed = download_all_concept_sectors()
    industry_success, industry_failed = download_all_industry_sectors()
    
    # 统计
    print("\n" + "=" * 60)
    print("下载完成统计")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT code) FROM sector_kline WHERE sector_type="concept"')
    concept_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT code) FROM sector_kline WHERE sector_type="industry"')
    industry_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sector_kline WHERE sector_type="concept"')
    concept_records = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sector_kline WHERE sector_type="industry"')
    industry_records = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"概念板块: {concept_total} 个, {concept_records} 条记录")
    print(f"行业板块: {industry_total} 个, {industry_records} 条记录")
    print(f"总计: {concept_total + industry_total} 个板块, {concept_records + industry_records} 条记录")

if __name__ == '__main__':
    main()
