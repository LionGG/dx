#!/usr/bin/env python3
"""
板块与个股关系数据获取 - 每周六凌晨2点执行
增量更新，已有数据不变
"""

import akshare as ak
import pandas as pd
import sqlite3
from datetime import datetime
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'akshare_full.db')

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def fetch_sector_stocks():
    today = datetime.now().strftime('%Y-%m-%d')
    log(f"开始获取板块与个股关系 - {today}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查本周是否已更新
    cursor.execute("SELECT MAX(update_date) FROM sector_stocks")
    last_update = cursor.fetchone()[0]
    
    if last_update == today:
        log(f"  今日已更新过: {last_update}，跳过获取")
        conn.close()
        return True
    
    log(f"  上次更新: {last_update}，开始获取...")
    
    # 获取已有数据，用于增量判断
    cursor.execute("SELECT sector_name, stock_code FROM sector_stocks")
    existing_pairs = set(cursor.fetchall())
    log(f"  数据库中已有 {len(existing_pairs)} 条记录")
    
    total_inserted = 0
    
    # 1. 获取行业板块成分股
    try:
        log("  获取行业板块列表...")
        industry_df = ak.stock_board_industry_name_em()
        industry_names = industry_df['板块名称'].tolist()
        log(f"    共 {len(industry_names)} 个行业板块")
        
        for sector_name in industry_names:
            try:
                # 获取板块成分股
                stocks_df = ak.stock_board_industry_cons_em(symbol=sector_name)
                
                for _, row in stocks_df.iterrows():
                    stock_code = str(row.get('代码', ''))
                    stock_name = str(row.get('名称', ''))
                    
                    # 检查是否已存在
                    if (sector_name, stock_code) in existing_pairs:
                        continue
                    
                    cursor.execute('''
                        INSERT INTO sector_stocks 
                        (sector_code, sector_name, sector_type, stock_code, stock_name, update_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        stock_code,  # sector_code 用股票代码占位
                        sector_name,
                        'industry',
                        stock_code,
                        stock_name,
                        today
                    ))
                    
                    if cursor.rowcount > 0:
                        total_inserted += 1
                
                conn.commit()
                
                # 每10个板块报告一次进度
                if industry_names.index(sector_name) % 10 == 0:
                    log(f"    进度: {industry_names.index(sector_name)}/{len(industry_names)} - {sector_name}")
                
                time.sleep(0.1)
                
            except Exception as e:
                log(f"    {sector_name} 获取失败: {e}")
                continue
        
        log(f"    ✓ 行业板块处理完成")
        
    except Exception as e:
        log(f"    ✗ 行业板块获取失败: {e}")
    
    time.sleep(1)
    
    # 2. 获取概念板块成分股
    try:
        log("  获取概念板块列表...")
        concept_df = ak.stock_board_concept_name_em()
        concept_names = concept_df['板块名称'].tolist()
        log(f"    共 {len(concept_names)} 个概念板块")
        
        for sector_name in concept_names:
            try:
                # 获取板块成分股
                stocks_df = ak.stock_board_concept_cons_em(symbol=sector_name)
                
                for _, row in stocks_df.iterrows():
                    stock_code = str(row.get('代码', ''))
                    stock_name = str(row.get('名称', ''))
                    
                    # 检查是否已存在
                    if (sector_name, stock_code) in existing_pairs:
                        continue
                    
                    cursor.execute('''
                        INSERT INTO sector_stocks 
                        (sector_code, sector_name, sector_type, stock_code, stock_name, update_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        stock_code,
                        sector_name,
                        'concept',
                        stock_code,
                        stock_name,
                        today
                    ))
                    
                    if cursor.rowcount > 0:
                        total_inserted += 1
                
                conn.commit()
                
                # 每10个板块报告一次进度
                if concept_names.index(sector_name) % 10 == 0:
                    log(f"    进度: {concept_names.index(sector_name)}/{len(concept_names)} - {sector_name}")
                
                time.sleep(0.1)
                
            except Exception as e:
                log(f"    {sector_name} 获取失败: {e}")
                continue
        
        log(f"    ✓ 概念板块处理完成")
        
    except Exception as e:
        log(f"    ✗ 概念板块获取失败: {e}")
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM sector_stocks")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    log(f"✓ 完成: 新增 {total_inserted} 条，总计 {total_count} 条")
    
    return total_inserted >= 0

def main():
    log(f"{'='*60}")
    log(f"板块与个股关系数据获取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'='*60}")
    
    success = fetch_sector_stocks()
    
    if success:
        log("✓ 完成")
        return 0
    else:
        log("✗ 失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
