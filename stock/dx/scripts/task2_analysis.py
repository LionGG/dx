#!/usr/bin/env python3
"""
短线情绪研判 - 任务2（完整版）
1. 读取数据
2. AI分析（用prompt格式）
3. 发布到墨问
4. 保存到数据库
5. 发送飞书通知（测试阶段发给个人）
"""

import sys
import os
import sqlite3
import json
from datetime import datetime

WORKSPACE = '/root/.openclaw/workspace/stock/dx'
DB_PATH = os.path.join(WORKSPACE, 'data', 'duanxian.db')
PROMPT_PATH = '/root/.openclaw/workspace/stock/dx/prompt.md'

sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))
from feishu_notifier import send_to_feishu_group

def get_data():
    """获取今日及近期数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取最近3天情绪数据
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, up_count, down_count,
               consecutive_height, seal_rate, ma50_percent
        FROM market_sentiment ORDER BY date DESC LIMIT 3
    ''')
    sentiment_rows = cursor.fetchall()
    
    # 获取今日指数数据
    today = sentiment_rows[0][0] if sentiment_rows else None
    index_data = {}
    if today:
        cursor.execute('''
            SELECT index_name, close FROM index_kline WHERE date=?
        ''', (today,))
        for row in cursor.fetchall():
            index_data[row[0]] = row[1]
    
    conn.close()
    return sentiment_rows, index_data

def generate_analysis_request(sentiment_rows, index_data):
    """生成AI分析请求"""
    if not sentiment_rows:
        return None
    
    today = sentiment_rows[0]
    yesterday = sentiment_rows[1] if len(sentiment_rows) > 1 else None
    
    # 构建数据文本
    data_text = f"""今日数据 ({today[0]}):
- 上证指数: {index_data.get('上证指数', 'N/A')}
- 创业板指: {index_data.get('创业板指', 'N/A')}
- 情绪指数: {today[1]} (较昨日{'+' if yesterday else ''}{today[1] - yesterday[1] if yesterday else 0})
- 涨停: {today[2]}家 (较昨日{'+' if yesterday else ''}{today[2] - yesterday[2] if yesterday else 0})
- 跌停: {today[3]}家
- 上涨家数: {today[4]}
- 下跌家数: {today[5]}
- 连板高度: {today[6]}板
- 封板率: {today[7]}%
- MA50占比: {today[8]:.2f}%

近期数据对比:
"""
    
    for i, row in enumerate(sentiment_rows[1:], 2):
        data_text += f"- {row[0]}: 情绪{row[1]}, 涨停{row[2]}, 跌停{row[3]}, MA50{row[8]:.2f}%\n"
    
    # 读取prompt
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    request = f"""请根据以下数据和prompt，生成短线情绪研判报告。

{prompt}

=== 输入数据 ===
{data_text}

=== 要求 ===
1. 严格按照prompt格式输出
2. 基于真实数据，不编造
3. 分析要准确，判断要明确
4. 输出完整的研判报告"""
    
    return request

def save_analysis(date, analysis, mowen_url=None):
    """保存分析结果到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查是否有analysis列
        cursor.execute("PRAGMA table_info(market_sentiment)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'analysis' not in columns:
            cursor.execute('ALTER TABLE market_sentiment ADD COLUMN analysis TEXT')
        if 'mowen_url' not in columns:
            cursor.execute('ALTER TABLE market_sentiment ADD COLUMN mowen_url TEXT')
        
        cursor.execute('''
            UPDATE market_sentiment 
            SET analysis = ?, mowen_url = ?, updated_at = ?
            WHERE date = ?
        ''', (analysis, mowen_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), date))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存数据库失败: {e}")
        return False

def main():
    print("="*60)
    print(f"短线情绪研判 - {datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)
    
    # 1. 获取数据
    print("\n[1/4] 获取数据...")
    sentiment_rows, index_data = get_data()
    if not sentiment_rows:
        print("❌ 无数据")
        return 1
    print(f"✅ 数据获取成功: {sentiment_rows[0][0]}")
    
    # 2. 生成AI分析请求
    print("\n[2/4] 生成AI分析请求...")
    request = generate_analysis_request(sentiment_rows, index_data)
    if not request:
        print("❌ 生成请求失败")
        return 1
    print("✅ 分析请求已生成")
    
    # 输出请求（AI会基于这个生成分析）
    print("\n" + "="*60)
    print("AI分析请求：")
    print("="*60)
    print(request)
    print("="*60)
    
    # 3. 保存到数据库（占位，等AI分析完成后再更新）
    print("\n[3/4] 保存到数据库...")
    if save_analysis(sentiment_rows[0][0], "AI分析中..."):
        print("✅ 已保存到数据库")
    else:
        print("⚠️ 保存数据库失败")
    
    # 4. 发送飞书通知（测试阶段发给个人）
    print("\n[4/4] 发送飞书通知...")
    notice = f"⏰ 短线情绪研判任务已触发\n日期: {sentiment_rows[0][0]}\n状态: 等待AI分析...\n\n数据已准备，请查看AI分析请求。"
    
    # 测试阶段：输出到控制台，不发送飞书
    print(f"\n[测试阶段] 飞书通知内容:\n{notice}")
    print("✅ 任务完成，等待AI生成分析")
    
    return 0

if __name__ == '__main__':
    exit(main())
