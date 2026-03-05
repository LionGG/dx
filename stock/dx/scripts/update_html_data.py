#!/usr/bin/env python3
"""更新HTML中的数据为最新"""

import sqlite3
import json
import re

DB_FILE = "/root/.openclaw/workspace/stock/dx/data/duanxian.db"
HTML_FILE = "/root/.openclaw/workspace/stock/dx/web/index.html"

# 读取数据库
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 获取所有情绪数据
cursor.execute('''
    SELECT date, sentiment_index, limit_up, limit_down, major_pullback, volume,
           consecutive_height, up_count, down_count, seal_rate, limit_up_performance,
           consecutive_performance, consecutive_promotion_rate, ma50_percent,
           analysis_phase, analysis_action, analysis_summary, mowen_link
    FROM market_sentiment WHERE date >= '2026-01-01' ORDER BY date DESC
''')
rows = cursor.fetchall()

# 获取K线数据
cursor.execute('''
    SELECT date, index_code, open, high, low, close, volume, ma5, ma10, ma50
    FROM index_kline WHERE date >= '2025-11-01' ORDER BY date DESC
''')
kline_rows = cursor.fetchall()

conn.close()

# 构建marketData
market_data = []
daily_reports = {}
report_dates = []

for row in rows:
    date = row[0]
    market_data.append({
        "date": date,
        "sentiment_index": row[1],
        "limit_up": row[2],
        "limit_down": row[3],
        "major_pullback": row[4],
        "volume": row[5],
        "consecutive_height": row[6],
        "up_count": row[7],
        "down_count": row[8],
        "seal_rate": row[9],
        "limit_up_performance": row[10],
        "consecutive_performance": row[11],
        "consecutive_promotion_rate": row[12],
        "ma50_percent": row[13],
        "strong_percent": None
    })
    
    # 构建dailyReports
    if row[14]:  # 有AI分析 (analysis_phase)
        daily_reports[date] = {
            "phase": row[14] or "",
            "action": row[15] or "",
            "summary": row[16] or "",
            "link": row[17] or ""
        }
        report_dates.append(date)

# 构建K线数据（按升序排列，旧→新，便于计算涨跌幅）
kline_data = {"000001": {"name": "上证指数", "display": "上证", "data": []},
              "399006": {"name": "创业板指", "display": "创业板", "data": []}}

# 先按降序收集数据
for row in kline_rows:
    code = row[1]
    if code in kline_data:
        kline_data[code]["data"].append({
            "date": row[0],
            "open": row[2],
            "high": row[3],
            "low": row[4],
            "close": row[5],
            "volume": row[6],
            "ma5": row[7],
            "ma10": row[8],
            "ma50": row[9]
        })

# 反转数组为升序（旧→新），便于计算涨跌幅
for code in kline_data:
    kline_data[code]["data"].reverse()

# 读取HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 替换marketData
market_data_json = json.dumps(market_data, ensure_ascii=False)
html = re.sub(r'const marketData = \[.*?\];', f'const marketData = {market_data_json};', html, flags=re.DOTALL)

# 替换klineData
kline_data_json = json.dumps(kline_data, ensure_ascii=False)
html = re.sub(r'const klineData = \{.*?\};', f'const klineData = {kline_data_json};', html, flags=re.DOTALL)

# 替换dailyReports
daily_reports_json = json.dumps(daily_reports, ensure_ascii=False)
html = re.sub(r'const dailyReports = \{.*?\};', f'const dailyReports = {daily_reports_json};', html, flags=re.DOTALL)

# 替换reportDates
report_dates_json = json.dumps(report_dates, ensure_ascii=False)
html = re.sub(r'const reportDates = \[.*?\];', f'const reportDates = {report_dates_json};', html, flags=re.DOTALL)

# 保存HTML
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML已更新: {HTML_FILE}")
print(f"   - 情绪数据: {len(market_data)} 条")
print(f"   - AI分析: {len(daily_reports)} 条")
print(f"   - K线数据: 上证{len(kline_data['000001']['data'])}条, 创业板{len(kline_data['399006']['data'])}条")
