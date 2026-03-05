#!/usr/bin/env python3
"""
生成本地预览版 HTML - 基于稳定版本 (19:19)
直接复制稳定版本的 HTML，添加本地预览标识
"""

import json
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('/root/.openclaw/workspace/stock/duanxianxia_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_data():
    """获取所有数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 市场数据
    cursor.execute('''
        SELECT * FROM market_sentiment 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    market_data = [dict(row) for row in cursor.fetchall()]
    
    # 研判数据
    cursor.execute('''
        SELECT date, phase, action, summary, mowen_link 
        FROM daily_reports 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    daily_reports = {row['date']: dict(row) for row in cursor.fetchall()}
    
    # K线数据
    kline_data = {}
    for code in ['000001', '000985', '399006']:
        cursor.execute('''
            SELECT date, open, close, high, low, volume, amount, ma50
            FROM index_kline
            WHERE index_code = ? AND date >= '2026-01-01'
            ORDER BY date ASC
        ''', (code,))
        rows = cursor.fetchall()
        
        code_names = {
            '000001': ('上证指数', '上证'),
            '000985': ('东财全A', '东财全A'),
            '399006': ('创业板指', '创业板')
        }
        name, display = code_names[code]
        
        kline_data[code] = {
            'name': name,
            'display': display,
            'data': [dict(row) for row in rows]
        }
    
    conn.close()
    return market_data, daily_reports, kline_data

def generate_local_html():
    """生成本地预览版HTML"""
    
    market_data, daily_reports, kline_data = get_all_data()
    
    # 读取稳定版本的HTML模板
    with open('/tmp/old_index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 替换标题添加本地预览标识
    html = html.replace(
        '<title>A股市场短线情绪走势</title>',
        '<title>A股市场短线情绪走势 - 本地预览</title>'
    )
    
    # 在 header h1 后添加本地预览标识
    html = html.replace(
        '<h1>A股市场短线情绪走势</h1>',
        '<h1>A股市场短线情绪走势<span style="display:inline-block;background:#238636;color:#fff;font-size:12px;padding:2px 8px;border-radius:4px;margin-left:10px;vertical-align:middle">本地预览</span></h1>'
    )
    
    # 保存文件
    output_path = '/root/.openclaw/workspace/stock/web/index-local.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ 本地预览版已生成: {output_path}')
    print(f'   文件大小: {len(html) / 1024:.1f} KB')
    print(f'   市场数据: {len(market_data)} 条')
    print(f'   研判数据: {len(daily_reports)} 条')
    print(f'   K线数据: {len(kline_data)} 个指数')
    return output_path

if __name__ == '__main__':
    generate_local_html()
