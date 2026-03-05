#!/usr/bin/env python3
"""
初始化短线情绪数据库
"""

import sqlite3
import requests

DB_FILE = "/root/.openclaw/workspace/duanxianxia_data.db"
API_URL = "https://www.duanxianxia.com/api/getChartByQingxu"

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS market_sentiment (
        date TEXT PRIMARY KEY,
        sentiment_index INTEGER,
        limit_up INTEGER,
        limit_down INTEGER,
        major_pullback INTEGER,
        volume REAL,
        consecutive_height INTEGER,
        up_count INTEGER,
        down_count INTEGER,
        seal_rate TEXT,
        limit_up_performance TEXT,
        consecutive_performance TEXT,
        consecutive_promotion_rate TEXT
    )''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库表结构初始化完成")

def fetch_and_insert_all_data():
    """获取所有历史数据并插入数据库"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.duanxianxia.com/web/fupan"
    }
    
    resp = requests.get(API_URL, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"❌ 获取数据失败: {resp.status_code}")
        return
    
    data = resp.json()
    if data.get('result') != 'success':
        print("❌ API 返回错误")
        return
    
    dates = data.get('Aaxis', [])
    series = data.get('series', {})
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 先插入所有日期（空数据）
    for date in dates:
        c.execute('INSERT OR IGNORE INTO market_sentiment (date) VALUES (?)', (date,))
    
    conn.commit()
    conn.close()
    print(f"✅ 已插入 {len(dates)} 个日期记录")

if __name__ == "__main__":
    print("="*70)
    print("初始化短线情绪数据库")
    print("="*70)
    init_database()
    fetch_and_insert_all_data()
    print("\n完成！现在可以运行 crawler.py 更新数据")
