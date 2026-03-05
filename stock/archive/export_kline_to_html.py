#!/usr/bin/env python3
"""
导出指数K线数据为JSON，嵌入到HTML文件中
"""

import sqlite3
import json
import re

# 路径配置
DB_PATH = '/root/.openclaw/workspace/stock/duanxianxia_data.db'
HTML_PATH = '/root/.openclaw/workspace/stock/web/index.html'

# 指数配置
INDEX_CONFIG = {
    '000001': {'name': '上证指数', 'display': '上证'},
    '399006': {'name': '创业板指', 'display': '创业板'},
    '000985': {'name': '东财全A', 'display': '东财全A'}
}


def export_kline_data():
    """从数据库导出K线数据"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    result = {}
    
    for code in INDEX_CONFIG.keys():
        cursor.execute('''
            SELECT date, open, close, high, low, volume, amount, ma5, ma10, ma50
            FROM index_kline
            WHERE index_code = ?
            ORDER BY date ASC
        ''', (code,))
        
        rows = cursor.fetchall()
        
        # 转换为ECharts需要的格式
        data = []
        for row in rows:
            data.append({
                'date': row['date'],
                'open': round(row['open'], 2) if row['open'] else None,
                'close': round(row['close'], 2) if row['close'] else None,
                'high': round(row['high'], 2) if row['high'] else None,
                'low': round(row['low'], 2) if row['low'] else None,
                'volume': row['volume'],
                'amount': row['amount'],
                'ma5': round(row['ma5'], 2) if row['ma5'] else None,
                'ma10': round(row['ma10'], 2) if row['ma10'] else None,
                'ma50': round(row['ma50'], 2) if row['ma50'] else None
            })
        
        result[code] = {
            'name': INDEX_CONFIG[code]['name'],
            'display': INDEX_CONFIG[code]['display'],
            'data': data
        }
        
        print(f"✓ {INDEX_CONFIG[code]['name']}: {len(data)} 条数据")
    
    conn.close()
    return result


def update_html(kline_data):
    """更新HTML文件，嵌入K线数据"""
    
    # 读取原HTML
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 准备K线数据JSON
    kline_json = json.dumps(kline_data, ensure_ascii=False, separators=(',', ':'))
    
    # 检查是否已有 klineData 变量
    if 'const klineData' in content:
        # 替换现有数据
        pattern = r'const klineData = \{.*?\};'
        replacement = f'const klineData = {kline_json};'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✓ 更新现有 klineData")
    else:
        # 在 marketData 后插入新数据
        pattern = r'(const marketData = \[.*?\];)'
        replacement = r'\1\n\n        // K线数据\n        const klineData = ' + kline_json + ';'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✓ 插入新 klineData")
    
    # 写入文件
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ HTML文件已更新: {HTML_PATH}")


def main():
    print("="*50)
    print("导出K线数据到HTML")
    print("="*50)
    
    # 导出数据
    print("\n从数据库导出数据...")
    kline_data = export_kline_data()
    
    # 更新HTML
    print("\n更新HTML文件...")
    update_html(kline_data)
    
    print("\n" + "="*50)
    print("完成!")
    print("="*50)


if __name__ == '__main__':
    main()