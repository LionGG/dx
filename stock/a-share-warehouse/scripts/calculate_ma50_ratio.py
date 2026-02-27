#!/usr/bin/env python3
"""
MA50占比计算 - 生成趋势图

计算MA50占比，生成图片
输出结果供OpenClaw捕获推送
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'akshare_full.db')
OUTPUT_PATH = os.path.join(PROJECT_DIR, 'ma50_ratio_trend.png')

import sys
sys.path.insert(0, SCRIPT_DIR)
from feishu_notifier import send_to_feishu_group
import subprocess

def send_text_with_image_local(text, image_path):
    """调用外部脚本发送文字+图片"""
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/send-to-feishu-group.py', 'both', text, image_path],
        capture_output=True, text=True
    )
    return result.returncode == 0

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def calculate_ma50_ratio():
    """计算MA50占比并生成趋势图"""
    log("开始计算MA50占比...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 首先检查今天是否有MA50数据，如果没有则计算
    cursor.execute('SELECT COUNT(*) FROM stock_ma50 WHERE date = ?', (today,))
    if cursor.fetchone()[0] == 0:
        log(f"今天({today})无MA50数据，开始计算...")
        
        # 获取所有股票代码
        cursor.execute('SELECT DISTINCT code FROM stock_kline WHERE date = ?', (today,))
        codes = [r[0] for r in cursor.fetchall()]
        
        if len(codes) == 0:
            log(f"错误：今天({today})无个股数据，无法计算MA50")
            conn.close()
            return None
        
        # 为每只股票计算MA50
        calculated = 0
        for code in codes:
            # 获取最近50天的数据
            df = pd.read_sql_query(f'''
                SELECT date, close FROM stock_kline 
                WHERE code = '{code}' 
                ORDER BY date DESC 
                LIMIT 50
            ''', conn)
            
            if len(df) >= 50:
                # 计算MA50
                df = df.sort_values('date')
                df['ma50'] = df['close'].rolling(window=50).mean()
                latest = df.iloc[-1]
                
                if pd.notna(latest['ma50']):
                    deviation = (latest['close'] - latest['ma50']) / latest['ma50'] * 100
                    cursor.execute('INSERT OR REPLACE INTO stock_ma50 VALUES (?, ?, ?, ?, ?)',
                                   (today, code, latest['close'], latest['ma50'], deviation))
                    calculated += 1
        
        conn.commit()
        log(f"MA50计算完成: {calculated}/{len(codes)}只股票")
    
    # 获取多日MA50统计数据
    df = pd.read_sql_query('''
        SELECT 
            date,
            COUNT(*) as total,
            SUM(CASE WHEN close > ma50 THEN 1 ELSE 0 END) as above
        FROM stock_ma50 
        WHERE date >= '2026-01-01'
        GROUP BY date
        ORDER BY date
    ''', conn)
    
    if len(df) == 0:
        log("错误：无MA50数据")
        conn.close()
        return None
    
    df['ratio'] = df['above'] / df['total'] * 100
    
    # 获取最新数据
    latest = df.iloc[-1]
    latest_date = latest['date']
    latest_ratio = latest['ratio']
    latest_total = latest['total']
    latest_above = latest['above']
    
    # 获取昨天数据对比
    if len(df) >= 2:
        yesterday = df.iloc[-2]
        yesterday_ratio = yesterday['ratio']
        change = latest_ratio - yesterday_ratio
    else:
        yesterday_ratio = None
        change = None
    
    # 生成趋势图
    x = range(len(df))
    plt.figure(figsize=(14, 6))
    plt.plot(x, df['ratio'], marker='o', linewidth=2, color='#2E86AB', markersize=4)
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Line')
    
    # 只显示部分日期标签
    step = max(1, len(df) // 10)
    plt.xticks(x[::step], df['date'].iloc[::step], rotation=45)
    
    plt.title('A股MA50占比趋势 (2026)', fontsize=14)
    plt.xlabel('Trading Day')
    plt.ylabel('Ratio (%)')
    plt.ylim(30, 90)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    plt.close()
    
    log(f"图片已保存: {OUTPUT_PATH}")
    log(f"最新占比: {latest_ratio:.2f}% ({latest_date})")
    
    conn.close()
    
    return {
        'date': latest_date,
        'ratio': latest_ratio,
        'total': latest_total,
        'above': latest_above,
        'yesterday_ratio': yesterday_ratio,
        'change': change
    }

def main():
    log(f"开始MA50占比计算任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 计算MA50占比
    data = calculate_ma50_ratio()
    
    if data is None:
        log("任务失败：无法计算MA50占比")
        return 1
    
    # 获取昨天数据对比
    change_str = f"{data['change']:+.2f}%" if data['change'] is not None else "N/A"
    yesterday_str = f"{data['yesterday_ratio']:.2f}%" if data['yesterday_ratio'] is not None else "N/A"
    
    # 发送飞书群消息（文字+图片）
    group_message = f"""✅ MA50占比计算执行成功 - {data['date']}

📊 统计结果
━━━━━━━━━━━━━━━━━━━━━
总股票数: {data['total']}只
MA50上方: {data['above']}只 ({data['ratio']:.2f}%) 🟢
MA50下方: {data['total'] - data['above']}只 ({100 - data['ratio']:.2f}%) 🔴
━━━━━━━━━━━━━━━━━━━━━

📈 趋势对比
昨天: {yesterday_str}
今天: {data['ratio']:.2f}%
变化: {change_str}"""
    
    # 使用昨天的方法发送文字+图片
    send_text_with_image_local(group_message, OUTPUT_PATH)
    log("飞书群文字+图片已发送")
    
    # 输出结果
    personal_message = f"""✅ MA50占比计算执行成功 - {data['date']}

📊 统计结果
━━━━━━━━━━━━━━━━━━━━━
总股票数: {data['total']}只
MA50上方: {data['above']}只 ({data['ratio']:.2f}%) 🟢
MA50下方: {data['total'] - data['above']}只 ({100 - data['ratio']:.2f}%) 🔴
━━━━━━━━━━━━━━━━━━━━━

📈 趋势对比
昨天: {yesterday_str}
今天: {data['ratio']:.2f}%
变化: {change_str}

📁 图片已发送到飞书群"""
    
    print(personal_message)
    
    # 发送飞书群消息
    send_to_feishu_group(personal_message)
    
    log("任务完成")
    return 0

if __name__ == '__main__':
    exit(main())
