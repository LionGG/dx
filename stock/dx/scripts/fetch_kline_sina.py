#!/usr/bin/env python3
"""
从新浪财经获取指数K线数据（主数据源）
AKShare作为备用数据源

重要注意事项：
1. 新浪财经成交量单位是"手"（1手=100股），需要乘以100转换为"股"
2. 新浪财经有成交额数据，AKShare历史数据没有成交额
3. 优先使用新浪财经，AKShare作为备用

支持：上证指数(sh000001)、创业板指(sz399006)
"""

import sqlite3
import requests
import akshare as ak
from datetime import datetime, timedelta
import time

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

INDEX_CONFIG = {
    'sh000001': {'name': '上证指数', 'code': '000001', 'sina_code': 'sh000001'},
    'sz399006': {'name': '创业板指', 'code': '399006', 'sina_code': 'sz399006'}
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

def fetch_from_sina_realtime():
    """
    从新浪财经获取实时数据
    
    注意：新浪财经的成交量单位是"手"，需要乘以100转换为"股"
    """
    try:
        url = "https://hq.sinajs.cn/list=sh000001,sz399006"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'
        
        data = {}
        for line in response.text.strip().split('\n'):
            if 'sh000001' in line or 'sz399006' in line:
                parts = line.split('"')[1].split(',')
                symbol = 'sh000001' if 'sh000001' in line else 'sz399006'
                
                # 重要：新浪财经成交量单位是"手"，需要乘以100转换为"股"
                # 但创业板的数据可能是"股"而不是"手"，需要特殊处理
                volume_raw = float(parts[8])
                
                # 创业板成交量异常大（超过1万亿），说明单位已经是"股"，不需要再乘100
                if symbol == 'sz399006' and volume_raw > 1e10:  # 超过100亿股
                    volume_gu = volume_raw  # 已经是股
                    print(f"    创业板成交量单位识别为'股': {volume_gu:,.0f}")
                else:
                    volume_shou = volume_raw  # 手
                    volume_gu = volume_shou * 100   # 转换为股
                
                data[symbol] = {
                    'name': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[3]),
                    'high': float(parts[4]),
                    'low': float(parts[5]),
                    'volume': volume_gu,  # 已转换为股
                    'amount': float(parts[9]),  # 成交额（元）
                    'date': parts[30]  # 格式：2026-03-02
                }
        
        return data
        
    except Exception as e:
        print(f"  ✗ 新浪财经获取失败: {e}")
        return None

def fetch_from_akshare(symbol, name, code):
    """
    从AKShare获取历史数据（备用）
    
    注意：AKShare的stock_zh_index_daily接口返回的成交量单位是"股"
    但数据可能有延迟，不适合获取当日实时数据
    """
    print(f"  使用AKShare备用数据源...")
    
    try:
        df = ak.stock_zh_index_daily(symbol=symbol)
        
        if df is None or df.empty:
            print(f"    ✗ AKShare数据为空")
            return None
        
        # 只保留最近60个交易日
        df = df.tail(60).copy()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        for _, row in df.iterrows():
            date = row['date']
            
            # 计算MA
            date_idx = df[df['date'] == date].index[0]
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
                cursor.execute('''
                    UPDATE index_kline SET
                        open = ?, close = ?, high = ?, low = ?,
                        volume = ?, amount = ?,
                        ma5 = ?, ma10 = ?, ma50 = ?
                    WHERE date = ? AND index_code = ?
                ''', (
                    row['open'], row['close'], row['high'], row['low'],
                    row['volume'], None,  # AKShare历史数据没有成交额
                    ma5, ma10, ma50,
                    date, code
                ))
                updated += 1
            else:
                cursor.execute('''
                    INSERT INTO index_kline
                    (date, index_code, index_name, open, close, high, low,
                     volume, amount, ma5, ma10, ma50)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date, code, name,
                    row['open'], row['close'], row['high'], row['low'],
                    row['volume'], None,
                    ma5, ma10, ma50
                ))
                inserted += 1
        
        conn.commit()
        conn.close()
        
        print(f"    ✓ AKShare: 新增 {inserted} 条, 更新 {updated} 条")
        return inserted + updated
        
    except Exception as e:
        print(f"    ✗ AKShare错误: {e}")
        return 0

def update_ma_values(code):
    """更新MA值（基于最新数据重新计算）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取该指数所有数据，按日期排序
    cursor.execute('''
        SELECT date, close FROM index_kline 
        WHERE index_code = ? 
        ORDER BY date ASC
    ''', (code,))
    
    rows = cursor.fetchall()
    
    if len(rows) < 5:
        conn.close()
        return
    
    # 重新计算MA
    closes = [r[1] for r in rows]
    dates = [r[0] for r in rows]
    
    for i, (date, _) in enumerate(rows):
        ma5 = sum(closes[max(0, i-4):i+1]) / min(5, i+1) if i >= 4 else None
        ma10 = sum(closes[max(0, i-9):i+1]) / min(10, i+1) if i >= 9 else None
        ma50 = sum(closes[max(0, i-49):i+1]) / min(50, i+1) if i >= 49 else None
        
        cursor.execute('''
            UPDATE index_kline 
            SET ma5 = ?, ma10 = ?, ma50 = ?
            WHERE date = ? AND index_code = ?
        ''', (ma5, ma10, ma50, date, code))
    
    conn.commit()
    conn.close()

def save_sina_data(data):
    """
    保存新浪财经数据到数据库
    
    注意：数据已经过单位转换（手→股）
    """
    if not data:
        return 0, []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved = 0
    missing_history = []  # 记录需要补充历史数据的指数
    
    for symbol, info in data.items():
        if symbol not in INDEX_CONFIG:
            continue
        
        config = INDEX_CONFIG[symbol]
        date = info['date']
        
        # 检查今天数据是否已存在
        cursor.execute(
            'SELECT close FROM index_kline WHERE date = ? AND index_code = ?',
            (date, config['code'])
        )
        row = cursor.fetchone()
        
        if row:
            # 更新今天数据
            cursor.execute('''
                UPDATE index_kline SET
                    open = ?, close = ?, high = ?, low = ?,
                    volume = ?, amount = ?
                WHERE date = ? AND index_code = ?
            ''', (
                info['open'], info['close'], info['high'], info['low'],
                info['volume'], info['amount'],
                date, config['code']
            ))
            print(f"  ✓ 更新 {config['name']} 今天数据: 收{info['close']:.2f}, 量{info['volume']/1e8:.2f}亿股")
        else:
            # 插入今天数据
            cursor.execute('''
                INSERT INTO index_kline
                (date, index_code, index_name, open, close, high, low, volume, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date, config['code'], config['name'],
                info['open'], info['close'], info['high'], info['low'],
                info['volume'], info['amount']
            ))
            print(f"  ✓ 插入 {config['name']} 今天数据: 收{info['close']:.2f}, 量{info['volume']/1e8:.2f}亿股")
            missing_history.append(symbol)  # 需要补充历史数据
        
        saved += 1
    
    conn.commit()
    conn.close()
    
    return saved, missing_history

def show_latest():
    """显示最新数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n最新数据预览:")
    print("-" * 80)
    
    for code, name in [('000001', '上证指数'), ('399006', '创业板指')]:
        cursor.execute('''
            SELECT date, open, close, high, low, ma5, ma10, ma50, volume, amount
            FROM index_kline
            WHERE index_code = ?
            ORDER BY date DESC
            LIMIT 3
        ''', (code,))
        
        rows = cursor.fetchall()
        print(f"\n{name}({code}):")
        for row in rows:
            vol_str = f"{row[8]/1e8:.2f}亿股" if row[8] else "N/A"
            amt_str = f"{row[9]/1e8:.0f}亿" if row[9] else "N/A"
            print(f"  {row[0]}: 开{row[1]:.2f} 收{row[2]:.2f} 高{row[3]:.2f} 低{row[4]:.2f} 量{vol_str}")
    
    conn.close()

def main():
    init_database()
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*60}")
    print(f"指数K线数据抓取 - {today}")
    print(f"主数据源: 新浪财经 | 备用: AKShare")
    print(f"重要: 新浪财经成交量单位是'手'，已转换为'股'")
    print(f"{'='*60}")
    
    # 第一步：从新浪财经获取今日数据
    print("\n步骤1: 从新浪财经获取今日数据...")
    sina_data = fetch_from_sina_realtime()
    
    if not sina_data:
        print("  ✗ 新浪财经获取失败，将使用AKShare")
        sina_data = {}
    
    # 保存新浪数据
    saved_count, missing_history = save_sina_data(sina_data)
    
    # 第二步：用AKShare补充历史数据（如果需要）
    total_akshare = 0
    if missing_history:
        print(f"\n步骤2: 使用AKShare补充历史数据...")
        for symbol in missing_history:
            config = INDEX_CONFIG[symbol]
            count = fetch_from_akshare(symbol, config['name'], config['code'])
            total_akshare += count
    
    # 第三步：更新MA值
    print(f"\n步骤3: 更新移动平均线...")
    for config in INDEX_CONFIG.values():
        update_ma_values(config['code'])
    print("  ✓ MA值更新完成")
    
    # 总结
    print(f"\n{'='*60}")
    print("执行总结")
    print(f"{'='*60}")
    print(f"新浪财经: {saved_count} 个指数今日数据")
    if total_akshare > 0:
        print(f"AKShare备用: {total_akshare} 条历史数据")
    
    # 检查今天数据是否完整
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    missing_today = []
    for config in INDEX_CONFIG.values():
        cursor.execute(
            'SELECT 1 FROM index_kline WHERE date = ? AND index_code = ?',
            (today, config['code'])
        )
        if not cursor.fetchone():
            missing_today.append(config['name'])
    conn.close()
    
    if missing_today:
        print(f"⚠️ 今天数据缺失: {', '.join(missing_today)}")
    else:
        print(f"✅ 所有指数今天数据正常")
    
    print(f"{'='*60}")
    
    show_latest()

if __name__ == '__main__':
    main()
