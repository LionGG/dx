#!/usr/bin/env python3
"""
短线侠数据抓取 - 使用 /api/getChartByQingxu 接口
获取所有可用字段
"""

import requests
import json
import sqlite3

DB_FILE = "/root/.openclaw/workspace/stock/dx/data/duanxian.db"
API_URL = "https://www.duanxianxia.com/api/getChartByQingxu"

def fetch_all_data():
    """获取所有数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.duanxianxia.com/web/fupan"
    }
    
    try:
        resp = requests.get(API_URL, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def update_database():
    """更新数据库"""
    data = fetch_all_data()
    if not data or data.get('result') != 'success':
        print("获取数据失败")
        return
    
    dates = data.get('Aaxis', [])
    series = data.get('series', {})
    
    # 字段映射
    field_map = {
        'sentiment_index': 'QX',
        'limit_up': 'ZT',
        'limit_down': 'DT',
        'up_count': 'SZ',
        'down_count': 'XD',
        'seal_rate': 'FB',
        'consecutive_height': 'LBGD',
        'limit_up_performance': 'ZTBX',
        'consecutive_performance': 'LBBX',
        'major_pullback': 'KQXY',
        'volume': 'HSLN',
    }
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 获取连板家数列表用于计算连板晋级率
    lb_list = series.get('LB', [])
    zt_list = series.get('ZT', [])
    
    # 只更新2026年的数据
    for i, date in enumerate(dates):
        if date < '2026-01-01':
            continue
        
        updates = []
        values = []
        
        for db_field, api_field in field_map.items():
            if api_field in series and i < len(series[api_field]):
                val = series[api_field][i]
                # 转换数据类型
                if db_field in ['sentiment_index', 'limit_up', 'limit_down', 'up_count', 
                               'down_count', 'consecutive_height', 'major_pullback']:
                    try:
                        val = int(float(val))
                    except:
                        continue
                elif db_field == 'volume':
                    try:
                        val = float(val)
                    except:
                        continue
                elif db_field == 'seal_rate':
                    val = f"{val}%"
                elif db_field in ['limit_up_performance', 'consecutive_performance']:
                    val = f"{val}%"
                
                updates.append(f"{db_field} = ?")
                values.append(val)
        
        # 计算连板晋级率
        if i > 0 and i < len(lb_list) and i-1 < len(zt_list):
            try:
                lb_today = int(float(lb_list[i]))
                zt_yesterday = int(float(zt_list[i-1]))
                if zt_yesterday > 0:
                    promotion_rate = round(lb_today / zt_yesterday * 100, 1)
                    updates.append("consecutive_promotion_rate = ?")
                    values.append(f"{promotion_rate}%")
                    print(f"    计算连板晋级率: {lb_today}/{zt_yesterday} = {promotion_rate}%")
            except:
                pass
        
        if updates:
            # 先检查记录是否存在，不存在则插入
            c.execute("SELECT 1 FROM market_sentiment WHERE date = ?", (date,))
            if not c.fetchone():
                c.execute("INSERT INTO market_sentiment (date) VALUES (?)", (date,))
            
            sql = f"UPDATE market_sentiment SET {', '.join(updates)} WHERE date = ?"
            values.append(date)
            try:
                c.execute(sql, values)
                print(f"✅ 更新 {date}: {len(updates)} 个字段")
            except Exception as e:
                print(f"❌ 更新 {date} 失败: {e}")
    
    conn.commit()
    conn.close()
    print("\n完成!")

def main():
    print("="*70)
    print("短线侠数据抓取 - /api/getChartByQingxu")
    print("="*70)
    update_database()

if __name__ == "__main__":
    main()
