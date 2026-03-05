#!/usr/bin/env python3
"""
生成优化版网页 - Phase 4 完整版本
包含: localStorage缓存 + JS模块化 + 增量数据更新
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
    
    cursor.execute('''
        SELECT * FROM market_sentiment 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    market_data = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT date, phase, action, summary, mowen_link 
        FROM daily_reports 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    daily_reports = {row['date']: dict(row) for row in cursor.fetchall()}
    
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

def generate_html():
    """生成 Phase 4 版本 HTML"""
    
    market_data, daily_reports, kline_data = get_all_data()
    
    # 读取 Phase 4 模板
    with open('/root/.openclaw/workspace/stock/web/index-local.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 替换内嵌数据
    template = template.replace(
        'const marketData = [{"date": "2026-02-13", "sentiment_index": 35',
        f'const marketData = {json.dumps(market_data, ensure_ascii=False)}'
    )
    
    # 替换研判数据
    template = template.replace(
        'const dailyReports = {',
        f'const dailyReports = {json.dumps(daily_reports, ensure_ascii=False)};\n        const dailyReports_old = {{'
    )
    
    # 恢复变量名
    template = template.replace('const dailyReports_old = {', 'const dailyReports = {')
    
    # 替换 K 线数据
    template = template.replace(
        'const klineData = {"000001":',
        f'const klineData = {json.dumps(kline_data, ensure_ascii=False)}'
    )
    
    # 替换 reportDates
    report_dates = list(daily_reports.keys())
    template = template.replace(
        'const reportDates = ["2026-02-09", "2026-02-10", "2026-02-11", "2026-02-12", "2026-02-13"]',
        f'const reportDates = {json.dumps(sorted(report_dates))}'
    )
    
    # 更新 currentReportIndex
    template = template.replace(
        'let currentReportIndex = 4',
        f'let currentReportIndex = {len(report_dates) - 1}'
    )
    
    # 保存
    output_path = '/root/.openclaw/workspace/stock/web/index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f'✅ Phase 4 网页已生成: {output_path}')
    print(f'   文件大小: {len(template) / 1024:.1f} KB')
    print(f'   市场数据: {len(market_data)} 条')
    print(f'   研判数据: {len(daily_reports)} 条')
    return output_path

if __name__ == '__main__':
    generate_html()
