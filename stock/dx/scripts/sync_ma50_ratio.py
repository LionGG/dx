#!/usr/bin/env python3
"""
从a-share-warehouse读取MA50占比，写入duanxian.db
供短线情绪研判任务使用，避免重复计算
"""

import sqlite3
from datetime import datetime

# 数据库路径
WAREHOUSE_DB = '/root/.openclaw/workspace/stock/a-share-warehouse/data/akshare_full.db'
DX_DB = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

def sync_ma50_ratio():
    """同步MA50占比数据"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 从a-share-warehouse读取今天的MA50占比
    conn_src = sqlite3.connect(WAREHOUSE_DB)
    cursor_src = conn_src.cursor()
    
    cursor_src.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN close > ma50 THEN 1 ELSE 0 END) as above
        FROM stock_ma50 
        WHERE date = ?
    ''', (today,))
    
    row = cursor_src.fetchone()
    conn_src.close()
    
    if row is None or row[0] == 0:
        print(f"错误：a-share-warehouse中没有今天({today})的MA50数据")
        return False
    
    total = row[0]
    above = row[1]
    ratio = (above / total) * 100 if total > 0 else 0
    
    print(f"从a-share-warehouse读取: {today} MA50占比 = {ratio:.2f}% ({above}/{total})")
    
    # 写入duanxian.db
    conn_dst = sqlite3.connect(DX_DB)
    cursor_dst = conn_dst.cursor()
    
    # 检查今天是否有market_sentiment记录
    cursor_dst.execute('SELECT COUNT(*) FROM market_sentiment WHERE date = ?', (today,))
    if cursor_dst.fetchone()[0] == 0:
        # 插入新记录
        cursor_dst.execute('''
            INSERT INTO market_sentiment (date, ma50_percent) VALUES (?, ?)
        ''', (today, ratio))
    else:
        # 更新现有记录
        cursor_dst.execute('''
            UPDATE market_sentiment SET ma50_percent = ? WHERE date = ?
        ''', (ratio, today))
    
    conn_dst.commit()
    conn_dst.close()
    
    print(f"已写入duanxian.db: {today} = {ratio:.2f}%")
    return True

def main():
    print(f"开始同步MA50占比数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = sync_ma50_ratio()
    if success:
        print("同步成功")
        return 0
    else:
        print("同步失败")
        return 1

if __name__ == '__main__':
    exit(main())
