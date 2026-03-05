#!/usr/bin/env python3
"""
补充下载行业板块资金流向数据
"""

import akshare as ak
import pandas as pd
import sqlite3
import time
import random

DB_PATH = '/root/.openclaw/workspace/stock/akshare_full.db'

def download_industry_fund_flow():
    """下载行业板块资金流向"""
    print("=" * 60)
    print("补充下载行业板块资金流向")
    print("=" * 60)
    
    # 获取行业板块列表
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

def verify():
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT sector_type, COUNT(DISTINCT sector_code), COUNT(*) FROM sector_fund_flow GROUP BY sector_type')
    results = cursor.fetchall()
    
    print('资金流向数据分布:')
    for row in results:
        print(f'  {row[0]}: {row[1]} 个板块, {row[2]} 条记录')
    
    conn.close()

if __name__ == '__main__':
    download_industry_fund_flow()
    verify()
