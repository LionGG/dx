#!/usr/bin/env python3
"""
从AKShare获取指数K线数据
支持：上证指数(sh000001)、创业板指(sz399006)
"""

import sqlite3
import akshare as ak
from datetime import datetime, timedelta
import time

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

INDEX_CONFIG = {
    'sh000001': {'name': '上证指数', 'code': '000001'},
    'sz399006': {'name': '创业板指', 'code': '399006'}
}

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_kline (
            date TEXT NOT NULL,
            index_code TEXT NOT NULL,
            index_name TEXT,
            open REAL,
            close REAL,
            high REAL,
            low REAL,
            volume REAL,
            amount REAL,
            ma5 REAL,
            ma10 REAL,
            ma50 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date, index_code)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ 数据库表初始化完成")

def fetch_with_retry(symbol, max_retries=3, delay=2):
    """带重试机制的AKShare数据获取"""
    for attempt in range(max_retries):
        try:
            df = ak.stock_zh_index_daily(symbol=symbol)
            if not df.empty:
                return df
            print(f"  尝试 {attempt + 1}/{max_retries}: 返回空数据，{delay}秒后重试...")
            time.sleep(delay)
        except Exception as e:
            print(f"  尝试 {attempt + 1}/{max_retries}: 失败 - {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return None

def verify_today_data(code, expected_date):
    """验证今天数据是否存在"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT 1 FROM index_kline WHERE date = ? AND index_code = ?',
        (expected_date, code)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def fetch_and_save_kline(symbol, name, code):
    """从AKShare获取K线数据并保存（带重试）"""
    print(f"\n获取 {name}({symbol})...")
    
    # 使用重试机制获取数据
    df = fetch_with_retry(symbol)
    
    if df is None or df.empty:
        print(f"  ✗ 获取数据失败，跳过")
        return 0
    
    try:
        # 只保留最近60个交易日
        df = df.tail(60).copy()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        for _, row in df.iterrows():
            date = row['date']
            
            # 计算MA（确保有足够数据）
            date_idx = df[df['date'] == date].index[0]
            idx_in_slice = date_idx - df.index[0]  # 在切片中的相对位置
            ma5 = df.loc[max(0, date_idx-4):date_idx, 'close'].mean() if date_idx >= 4 else None
            ma10 = df.loc[max(0, date_idx-9):date_idx, 'close'].mean() if date_idx >= 9 else None
            ma50 = df.loc[max(0, date_idx-49):date_idx, 'close'].mean() if date_idx >= 49 else None
            
            # 检查是否已存在
            cursor.execute(
                'SELECT 1 FROM index_kline WHERE date = ? AND index_code = ?',
                (date, code)
            )
            exists = cursor.fetchone()
            
            if exists:
                # 更新
                cursor.execute('''
                    UPDATE index_kline SET
                        open = ?, close = ?, high = ?, low = ?,
                        volume = ?,
                        ma5 = ?, ma10 = ?, ma50 = ?
                    WHERE date = ? AND index_code = ?
                ''', (
                    row['open'], row['close'], row['high'], row['low'],
                    row['volume'],
                    ma5, ma10, ma50,
                    date, code
                ))
                updated += 1
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO index_kline
                    (date, index_code, index_name, open, close, high, low,
                     volume, ma5, ma10, ma50)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date, code, name,
                    row['open'], row['close'], row['high'], row['low'],
                    row['volume'],
                    ma5, ma10, ma50
                ))
                inserted += 1
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ 新增 {inserted} 条, 更新 {updated} 条")
        return inserted + updated
        
    except Exception as e:
        print(f"  ✗ 保存数据错误: {e}")
        return 0

def show_latest():
    """显示最新数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n最新数据预览:")
    print("-" * 80)
    
    for code, name in [('000001', '上证指数'), ('399006', '创业板指')]:
        cursor.execute('''
            SELECT date, open, close, high, low, ma5, ma10, ma50
            FROM index_kline
            WHERE index_code = ?
            ORDER BY date DESC
            LIMIT 3
        ''', (code,))
        
        rows = cursor.fetchall()
        print(f"\n{name}({code}):")
        for row in rows:
            print(f"  {row[0]}: 开{row[1]:.2f} 收{row[2]:.2f} 高{row[3]:.2f} 低{row[4]:.2f}")
    
    conn.close()

if __name__ == '__main__':
    init_database()
    
    today = datetime.now().strftime('%Y-%m-%d')
    total = 0
    missing_indices = []
    
    for symbol, config in INDEX_CONFIG.items():
        count = fetch_and_save_kline(symbol, config['name'], config['code'])
        total += count
        
        # 验证今天数据是否存在
        if not verify_today_data(config['code'], today):
            missing_indices.append(config['name'])
            print(f"  ⚠️ 警告: {config['name']} 今天({today})数据缺失!")
    
    print(f"\n{'='*50}")
    print(f"总计更新: {total} 条")
    
    if missing_indices:
        print(f"⚠️ 数据缺失: {', '.join(missing_indices)}")
        print(f"建议: 稍后手动重新运行脚本")
    else:
        print(f"✅ 所有指数今天数据正常")
    
    print(f"{'='*50}")
    
    show_latest()
