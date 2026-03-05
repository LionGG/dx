#!/usr/bin/env python3
"""
短线情绪数据抓取 - 任务1
抓取数据并发送飞书通知
"""

import subprocess
import sys
import os
import sqlite3
from datetime import datetime
import sys
sys.path.insert(0, '/root/.openclaw/workspace/stock/dx/scripts')
from timezone_utils import today_str, now_str

WORKSPACE = '/root/.openclaw/workspace/stock/dx'
DB_PATH = os.path.join(WORKSPACE, 'data', 'duanxian.db')

sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))
from feishu_notifier import send_to_feishu_group

def run_cmd(cmd, timeout=120):
    """运行命令"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        cwd=WORKSPACE, timeout=timeout
    )
    return result.returncode == 0, result.stdout, result.stderr

def get_today_data():
    """获取今日数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, up_count, down_count,
               consecutive_height, volume, seal_rate
        FROM market_sentiment ORDER BY date DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    return row

def main():
    today = today_str()
    print(f"="*60)
    print(f"短线情绪数据抓取 - {today}")
    print(f"="*60)
    
    # 1. 抓取短线侠数据
    print("\n[1/3] 抓取短线侠情绪数据...")
    success, stdout, stderr = run_cmd("python3 scripts/crawler.py")
    if not success:
        send_to_feishu_group(f"❌ 数据抓取失败（短线侠）\n\n错误：{stderr[:200]}")
        return 1
    print("✅ 短线侠数据抓取成功")
    
    # 2. 抓取指数K线
    print("\n[2/3] 抓取指数K线数据...")
    success, stdout, stderr = run_cmd("python3 scripts/fetch_kline_sina.py")
    if not success:
        send_to_feishu_group(f"❌ 数据抓取失败（指数K线）\n\n错误：{stderr[:200]}")
        return 1
    print("✅ 指数K线抓取成功")
    
    # 3. 同步MA50
    print("\n[3/3] 同步MA50占比数据...")
    success, stdout, stderr = run_cmd("python3 scripts/sync_ma50_ratio.py")
    if not success:
        send_to_feishu_group(f"❌ 数据抓取失败（MA50）\n\n错误：{stderr[:200]}")
        return 1
    print("✅ MA50同步成功")
    
    # 4. 获取今日数据并发送飞书
    row = get_today_data()
    if not row:
        send_to_feishu_group("❌ 数据抓取成功，但无法读取今日数据")
        return 1
    
    # 检查创业板成交量是否异常（超过1万亿股则除以100）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT volume FROM index_kline WHERE date = ? AND index_code = ?', (row[0], '399006'))
    cyb_volume = cursor.fetchone()
    if cyb_volume and cyb_volume[0] and cyb_volume[0] > 1e12:  # 超过1万亿股
        cursor.execute('UPDATE index_kline SET volume = volume / 100 WHERE date = ? AND index_code = ?', (row[0], '399006'))
        conn.commit()
        print(f"⚠️ 创业板成交量已修正: {cyb_volume[0]} -> {cyb_volume[0]/100}")
    conn.close()
    
    msg = f"""✅ 短线情绪数据抓取成功 - {row[0]}

📊 今日数据
━━━━━━━━━━━━━━━━━━━━━
情绪指数: {row[1]}
涨停/跌停: {row[2]} / {row[3]}
上涨/下跌: {row[4]} / {row[5]}
连板高度: {row[6]}板
量能: {row[7]}亿
封板率: {row[8]}
━━━━━━━━━━━━━━━━━━━━━

下一步：AI分析"""
    
    send_to_feishu_group(msg)
    print("\n✅ 飞书通知已发送")
    print(f"完成时间: {now_str()}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
