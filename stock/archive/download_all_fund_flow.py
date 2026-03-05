#!/usr/bin/env python3
"""
下载板块资金流向数据（行业板块 + 概念板块）
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
        CREATE TABLE IF NOT EXISTS sector_fund_flow (
            date TEXT,
            sector_code TEXT,
            sector_name TEXT,
            sector_type TEXT,
            main_net_inflow REAL,
            main_net_inflow_pct REAL,
            super_large_net_inflow REAL,
            super_large_net_inflow_pct REAL,
            large_net_inflow REAL,
            large_net_inflow_pct REAL,
            medium_net_inflow REAL,
            medium_net_inflow_pct REAL,
            small_net_inflow REAL,
            small_net_inflow_pct REAL,
            PRIMARY KEY (date, sector_code)
        )
    ''')
    conn.commit()
    conn.close()

def download_industry_fund_flow():
    """下载行业板块资金流向"""
    print("=" * 60)
    print("下载行业板块资金流向")
    print("=" * 60)
    
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
            df = ak.stock_sector_fund_flow_hist(symbol=name)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                failed.append((code, name, '无数据'))
                continue
            
            # 筛选2026年数据
            df['日期'] = pd.to_datetime(df['日期'])
            df = df[df['日期'] >= '2026-01-01']
            
            if len(df) == 0:
                print("✗ 无2026年数据")
                failed.append((code, name, '无2026年数据'))
                continue
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '主力净流入-净额': 'main_net_inflow',
                '主力净流入-净占比': 'main_net_inflow_pct',
                '超大单净流入-净额': 'super_large_net_inflow',
                '超大单净流入-净占比': 'super_large_net_inflow_pct',
                '大单净流入-净额': 'large_net_inflow',
                '大单净流入-净占比': 'large_net_inflow_pct',
                '中单净流入-净额': 'medium_net_inflow',
                '中单净流入-净占比': 'medium_net_inflow_pct',
                '小单净流入-净额': 'small_net_inflow',
                '小单净流入-净占比': 'small_net_inflow_pct'
            })
            
            df['sector_code'] = code
            df['sector_name'] = name
            df['sector_type'] = 'industry'
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # 保存到数据库
            df[['date', 'sector_code', 'sector_name', 'sector_type',
                'main_net_inflow', 'main_net_inflow_pct',
                'super_large_net_inflow', 'super_large_net_inflow_pct',
                'large_net_inflow', 'large_net_inflow_pct',
                'medium_net_inflow', 'medium_net_inflow_pct',
                'small_net_inflow', 'small_net_inflow_pct']].to_sql(
                'sector_fund_flow', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}条")
            success += 1
            
        except Exception as e:
            print(f"✗ {str(e)[:40]}")
            failed.append((code, name, str(e)[:50]))
        
        time.sleep(random.uniform(0.3, 0.6))
        
        if (idx + 1) % 50 == 0:
            print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}")
            time.sleep(2)
    
    conn.close()
    print(f"\n行业板块完成: {success}/{total}")
    return success, failed

def download_concept_fund_flow():
    """下载概念板块资金流向"""
    print("\n" + "=" * 60)
    print("下载概念板块资金流向")
    print("=" * 60)
    
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
            df = ak.stock_concept_fund_flow_hist(symbol=name)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                failed.append((code, name, '无数据'))
                continue
            
            # 筛选2026年数据
            df['日期'] = pd.to_datetime(df['日期'])
            df = df[df['日期'] >= '2026-01-01']
            
            if len(df) == 0:
                print("✗ 无2026年数据")
                failed.append((code, name, '无2026年数据'))
                continue
            
            # 重命名列（与行业板块相同）
            df = df.rename(columns={
                '日期': 'date',
                '主力净流入-净额': 'main_net_inflow',
                '主力净流入-净占比': 'main_net_inflow_pct',
                '超大单净流入-净额': 'super_large_net_inflow',
                '超大单净流入-净占比': 'super_large_net_inflow_pct',
                '大单净流入-净额': 'large_net_inflow',
                '大单净流入-净占比': 'large_net_inflow_pct',
                '中单净流入-净额': 'medium_net_inflow',
                '中单净流入-净占比': 'medium_net_inflow_pct',
                '小单净流入-净额': 'small_net_inflow',
                '小单净流入-净占比': 'small_net_inflow_pct'
            })
            
            df['sector_code'] = code
            df['sector_name'] = name
            df['sector_type'] = 'concept'
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # 保存到数据库
            df[['date', 'sector_code', 'sector_name', 'sector_type',
                'main_net_inflow', 'main_net_inflow_pct',
                'super_large_net_inflow', 'super_large_net_inflow_pct',
                'large_net_inflow', 'large_net_inflow_pct',
                'medium_net_inflow', 'medium_net_inflow_pct',
                'small_net_inflow', 'small_net_inflow_pct']].to_sql(
                'sector_fund_flow', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}条")
            success += 1
            
        except Exception as e:
            print(f"✗ {str(e)[:40]}")
            failed.append((code, name, str(e)[:50]))
        
        time.sleep(random.uniform(0.3, 0.6))
        
        if (idx + 1) % 50 == 0:
            print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}")
            time.sleep(2)
    
    conn.close()
    print(f"\n概念板块完成: {success}/{total}")
    return success, failed

def verify():
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT sector_code) FROM sector_fund_flow WHERE sector_type="industry"')
    industry_sectors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT sector_code) FROM sector_fund_flow WHERE sector_type="concept"')
    concept_sectors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sector_fund_flow')
    records = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(date), MAX(date) FROM sector_fund_flow')
    date_range = cursor.fetchone()
    
    print(f"行业板块: {industry_sectors} 个")
    print(f"概念板块: {concept_sectors} 个")
    print(f"总记录数: {records}")
    print(f"日期范围: {date_range[0]} ~ {date_range[1]}")
    
    # 样本数据
    print("\n样本数据（主力净流入前5）:")
    cursor.execute('''
        SELECT sector_type, sector_name, date, main_net_inflow, main_net_inflow_pct
        FROM sector_fund_flow
        ORDER BY main_net_inflow DESC
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} {row[2]}: {row[3]/1e8:.2f}亿 ({row[4]:.2f}%)")
    
    conn.close()

if __name__ == '__main__':
    init_db()
    download_industry_fund_flow()
    download_concept_fund_flow()
    verify()
