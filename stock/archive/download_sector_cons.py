#!/usr/bin/env python3
"""
下载全部板块成分股数据
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
        CREATE TABLE IF NOT EXISTS sector_stocks (
            sector_code TEXT,
            sector_name TEXT,
            sector_type TEXT,
            stock_code TEXT,
            stock_name TEXT,
            update_date TEXT,
            PRIMARY KEY (sector_code, stock_code)
        )
    ''')
    conn.commit()
    conn.close()

def clear_existing():
    """清空现有数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sector_stocks')
    conn.commit()
    conn.close()
    print("已清空现有板块成分股数据")

def download_concept_cons():
    """下载概念板块成分股"""
    print("=" * 60)
    print("下载概念板块成分股")
    print("=" * 60)
    
    # 获取概念板块列表
    df_list = ak.stock_board_concept_name_em()
    total = len(df_list)
    print(f"获取到 {total} 个概念板块")
    
    conn = sqlite3.connect(DB_PATH)
    success = 0
    failed = []
    total_stocks = 0
    
    for idx, row in df_list.iterrows():
        code = row['板块代码']
        name = row['板块名称']
        
        print(f"[{idx+1}/{total}] {name} ({code})...", end=' ')
        
        try:
            df = ak.stock_board_concept_cons_em(symbol=name)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                failed.append((code, name, '无数据'))
                continue
            
            # 准备数据
            df['sector_code'] = code
            df['sector_name'] = name
            df['sector_type'] = 'concept'
            df['update_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            # 重命名列
            df = df.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name'
            })
            
            # 保存到数据库
            df[['sector_code', 'sector_name', 'sector_type', 'stock_code', 'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}只")
            success += 1
            total_stocks += len(df)
            
        except Exception as e:
            print(f"✗ {str(e)[:40]}")
            failed.append((code, name, str(e)[:50]))
        
        time.sleep(random.uniform(0.3, 0.6))
        
        if (idx + 1) % 50 == 0:
            print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}, 成分股:{total_stocks}")
            time.sleep(2)
    
    conn.close()
    print(f"\n概念板块完成: {success}/{total}, 成分股总数: {total_stocks}")
    return success, failed, total_stocks

def download_industry_cons():
    """下载行业板块成分股"""
    print("\n" + "=" * 60)
    print("下载行业板块成分股")
    print("=" * 60)
    
    # 获取行业板块列表
    df_list = ak.stock_board_industry_name_em()
    total = len(df_list)
    print(f"获取到 {total} 个行业板块")
    
    conn = sqlite3.connect(DB_PATH)
    success = 0
    failed = []
    total_stocks = 0
    
    for idx, row in df_list.iterrows():
        code = row['板块代码']
        name = row['板块名称']
        
        print(f"[{idx+1}/{total}] {name} ({code})...", end=' ')
        
        try:
            df = ak.stock_board_industry_cons_em(symbol=name)
            
            if df is None or len(df) == 0:
                print("✗ 无数据")
                failed.append((code, name, '无数据'))
                continue
            
            # 准备数据
            df['sector_code'] = code
            df['sector_name'] = name
            df['sector_type'] = 'industry'
            df['update_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            # 重命名列
            df = df.rename(columns={
                '代码': 'stock_code',
                '名称': 'stock_name'
            })
            
            # 保存到数据库
            df[['sector_code', 'sector_name', 'sector_type', 'stock_code', 'stock_name', 'update_date']].to_sql(
                'sector_stocks', conn, if_exists='append', index=False)
            
            print(f"✓ {len(df)}只")
            success += 1
            total_stocks += len(df)
            
        except Exception as e:
            print(f"✗ {str(e)[:40]}")
            failed.append((code, name, str(e)[:50]))
        
        time.sleep(random.uniform(0.3, 0.6))
        
        if (idx + 1) % 50 == 0:
            print(f"  进度: {idx+1}/{total}, 成功:{success}, 失败:{len(failed)}, 成分股:{total_stocks}")
            time.sleep(2)
    
    conn.close()
    print(f"\n行业板块完成: {success}/{total}, 成分股总数: {total_stocks}")
    return success, failed, total_stocks

def main():
    init_db()
    clear_existing()
    
    print("开始下载板块成分股数据...")
    print(f"数据库: {DB_PATH}")
    print()
    
    # 下载概念板块成分股
    concept_success, concept_failed, concept_stocks = download_concept_cons()
    
    # 下载行业板块成分股
    industry_success, industry_failed, industry_stocks = download_industry_cons()
    
    # 统计
    print("\n" + "=" * 60)
    print("下载完成统计")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT sector_code) FROM sector_stocks WHERE sector_type="concept"')
    concept_sectors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT sector_code) FROM sector_stocks WHERE sector_type="industry"')
    industry_sectors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT stock_code) FROM sector_stocks')
    unique_stocks = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sector_stocks')
    total_records = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"概念板块: {concept_sectors} 个, {concept_stocks} 条成分股记录")
    print(f"行业板块: {industry_sectors} 个, {industry_stocks} 条成分股记录")
    print(f"涉及个股: {unique_stocks} 只")
    print(f"总计: {total_records} 条板块-个股映射关系")

if __name__ == '__main__':
    main()
