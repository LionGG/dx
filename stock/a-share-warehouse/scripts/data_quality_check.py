#!/usr/bin/env python3
"""
数据质量检查脚本 - 每日检查数据完整性
"""

import sqlite3
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_webhook
import requests

DB_PATH = '/root/.openclaw/workspace/stock/a-share-warehouse/data/akshare_full.db'
MIN_STOCK_COUNT = 5000  # 最少股票数量阈值

def send_alert(message):
    """发送飞书告警"""
    try:
        webhook = get_feishu_webhook()
        headers = {"Content-Type": "application/json"}
        data = {
            "msg_type": "text",
            "content": {"text": f"🚨 数据质量告警\n\n{message}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        }
        requests.post(webhook, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"告警发送失败: {e}")

def check_data_quality():
    """检查数据质量"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    alerts = []
    
    # 检查最近3天的数据
    for i in range(3):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 检查个股数据
        cursor.execute("SELECT COUNT(*) FROM stock_kline WHERE date = ?", (date,))
        stock_count = cursor.fetchone()[0]
        
        if stock_count < MIN_STOCK_COUNT and stock_count > 0:
            alerts.append(f"⚠️ {date} 个股数据异常: {stock_count}条 (正常应>{MIN_STOCK_COUNT})")
        elif stock_count == 0:
            # 检查是否是交易日
            from trading_date import is_trading_date
            if is_trading_date(date):
                alerts.append(f"🚨 {date} 交易日无个股数据!")
    
    conn.close()
    
    if alerts:
        message = "\n".join(alerts)
        message += "\n\n请立即检查数据同步情况!"
        send_alert(message)
        print(message)
        return False
    else:
        print(f"✅ 数据质量检查通过 ({datetime.now().strftime('%Y-%m-%d')})")
        return True

if __name__ == "__main__":
    check_data_quality()
