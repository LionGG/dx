#!/usr/bin/env python3
"""
AI情绪分析 - 完整版
基于prompt.md生成完整研判报告，调用AI API
"""

import sqlite3
import json
import os
import requests
from datetime import datetime

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_FILE = os.path.join(PROJECT_DIR, "data", "duanxian.db")
PROMPT_FILE = os.path.join(PROJECT_DIR, "prompt.md")

# 导入secrets管理
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_secret

# API配置
MOWEN_API_URL = "https://open.mowen.cn/api/open/api/v1/note/create"
MOWEN_API_TOKEN = get_secret('mowen-api', 'token')
KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"
KIMI_API_KEY = "sk-PLACEHOLDER"  # 已废弃，使用AI大脑直接分析

def fetch_data():
    """获取完整数据（情绪+指数K线）"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 获取最新日期
    cursor.execute("SELECT MAX(date) FROM market_sentiment")
    latest_date = cursor.fetchone()[0]
    
    # 获取今日情绪数据
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, major_pullback, volume,
               consecutive_height, up_count, down_count, seal_rate, limit_up_performance,
               consecutive_performance, consecutive_promotion_rate
        FROM market_sentiment 
        WHERE date = ?
    ''', (latest_date,))
    today = cursor.fetchone()
    
    # 获取近5日情绪数据
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, up_count, down_count, 
               consecutive_height, volume, seal_rate
        FROM market_sentiment 
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 5
    ''', (latest_date,))
    recent = cursor.fetchall()
    
    # 获取今日指数数据（上证+创业板）
    cursor.execute('''
        SELECT index_code, open, high, low, close, volume, ma5, ma10, ma50
        FROM index_kline 
        WHERE date = ? AND index_code IN ('000001', '399006')
    ''', (latest_date,))
    indices = cursor.fetchall()
    
    # 获取前一日指数数据（计算涨跌幅）
    cursor.execute('''
        SELECT index_code, close
        FROM index_kline 
        WHERE date < ? AND index_code IN ('000001', '399006')
        ORDER BY date DESC
        LIMIT 2
    ''', (latest_date,))
    prev_indices = cursor.fetchall()
    
    conn.close()
    
    return latest_date, today, recent, indices, prev_indices

def build_prompt(date, today_data, recent_data, indices, prev_indices):
    """构建AI分析的prompt"""
    
    # 读取系统prompt模板
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    # 解析今日数据
    sentiment_index = today_data[1]
    limit_up = today_data[2]
    limit_down = today_data[3]
    major_pullback = today_data[4]
    volume = today_data[5]
    consecutive_height = today_data[6]
    up_count = today_data[7]
    down_count = today_data[8]
    seal_rate = today_data[9]
    limit_up_performance = today_data[10]
    consecutive_performance = today_data[11]
    consecutive_promotion_rate = today_data[12]
    
    # 解析指数数据
    index_info = {}
    for idx in indices:
        code = idx[0]
        index_info[code] = {
            'open': idx[1], 'high': idx[2], 'low': idx[3], 
            'close': idx[4], 'volume': idx[5],
            'ma5': idx[6], 'ma10': idx[7], 'ma50': idx[8]
        }
    
    # 计算涨跌幅
    prev_close = {}
    for idx in prev_indices:
        prev_close[idx[0]] = idx[1]
    
    sh_change = ""
    cy_change = ""
    if '000001' in index_info and '000001' in prev_close:
        change_pct = (index_info['000001']['close'] - prev_close['000001']) / prev_close['000001'] * 100
        sh_change = f"({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
    if '399006' in index_info and '399006' in prev_close:
        change_pct = (index_info['399006']['close'] - prev_close['399006']) / prev_close['399006'] * 100
        cy_change = f"({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
    
    # 构建近5日演变数据
    recent_evolution = "\n".join([
        f"{r[0]}: 情绪{r[1]}, 涨停{r[2]}, 跌停{r[3]}, 上涨{r[5]}, 下跌{r[6]}"
        for r in recent_data
    ])
    
    # 构建用户输入数据
    user_data = f"""
分析日期：{date}

【当日情绪数据】
- 情绪指数：{sentiment_index}
- 涨停家数：{limit_up}
- 跌停家数：{limit_down}
- 上涨家数：{up_count}
- 下跌家数：{down_count}
- 连板高度：{consecutive_height}
- 封板率：{seal_rate}
- 涨停表现：{limit_up_performance}
- 连板表现：{consecutive_performance}
- 连板晋级率：{consecutive_promotion_rate}
- 大幅回撤：{major_pullback}
- 量能：{volume:.0f}亿

【指数数据】
- 上证指数：{index_info.get('000001', {}).get('close', 'N/A')} {sh_change}
- 创业板指：{index_info.get('399006', {}).get('close', 'N/A')} {cy_change}

【近5日演变】
{recent_evolution}

请基于以上数据，按照输出格式生成完整的情绪研判报告。
"""
    
    return system_prompt, user_data

def call_ai_api(system_prompt, user_data):
    """调用AI大脑生成分析（通过子代理）"""
    # 构建完整prompt
    full_prompt = f"{system_prompt}\n\n{user_data}\n\n请基于以上数据，按照输出格式生成完整的情绪研判报告。"
    
    # 输出prompt供子代理使用
    print("\n" + "="*70)
    print("AI分析请求 - 需要子代理完成")
    print("="*70)
    print(full_prompt)
    print("="*70)
    
    # 返回None，让上层知道需要子代理分析
    # 子代理完成任务后会直接调用publish_to_mowen
    return None

def parse_analysis(content):
    """解析AI返回的内容，提取三部分"""
    
    phase = ""
    action = ""
    summary = ""
    
    # 尝试提取周期阶段
    if "当前阶段：" in content:
        start = content.find("当前阶段：") + 6
        end = content.find("\n", start)
        if end == -1:
            end = len(content)
        phase = content[start:end].strip()
    
    # 尝试提取操作策略（在"后市策略应对"或"操作方向"部分）
    if "操作方向：" in content:
        start = content.find("操作方向：")
        end = content.find("关键信号：", start)
        if end == -1:
            end = content.find("一句话：", start)
        if end == -1:
            end = len(content)
        action = content[start:end].strip()
    elif "操作策略：" in content:
        start = content.find("操作策略：") + 6
        end = content.find("\n\n", start)
        if end == -1:
            end = len(content)
        action = content[start:end].strip()
    
    # 尝试提取一句话总结
    if "一句话：" in content:
        start = content.find("一句话：") + 5
        end = content.find("\n", start)
        if end == -1:
            end = len(content)
        summary = content[start:end].strip()
    
    # 如果解析失败，使用默认值
    if not phase:
        phase = "震荡期"
    if not action:
        action = "控制仓位，精选个股"
    if not summary:
        summary = "震荡分化，谨慎操作"
    
    return phase, action, summary, content

def publish_to_mowen(date, full_report):
    """发布完整报告到墨问笔记"""
    
    headers = {
        'Authorization': f'Bearer {MOWEN_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 将markdown内容分段
    lines = full_report.split('\n')
    content_blocks = []
    
    for line in lines:
        if line.strip():
            content_blocks.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
    
    payload = {
        'body': {
            'type': 'doc',
            'content': content_blocks
        },
        'settings': {
            'autoPublish': True,
            'tags': ['A股分析', '短线情绪', '自动发布']
        }
    }
    
    try:
        response = requests.post(MOWEN_API_URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if 'noteId' in result:
            note_id = result['noteId']
            mowen_link = f"https://note.mowen.cn/detail/{note_id}"
            print(f"✅ 已发布到墨问: {mowen_link}")
            return mowen_link
        else:
            print(f"⚠️ 墨问发布失败: {result}")
            return ""
    except Exception as e:
        print(f"❌ 墨问发布出错: {e}")
        return ""

def save_to_database(date, phase, action, summary, mowen_link, full_report):
    """保存分析结果到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 保存到market_sentiment表
    cursor.execute('''
        UPDATE market_sentiment 
        SET analysis_phase = ?, analysis_action = ?, analysis_summary = ?, mowen_link = ?
        WHERE date = ?
    ''', (phase, action, summary, mowen_link, date))
    
    # 保存完整报告到daily_reports表
    cursor.execute('''
        INSERT OR REPLACE INTO daily_reports (date, full_report)
        VALUES (?, ?)
    ''', (date, full_report))
    
    conn.commit()
    conn.close()
    print(f"✅ 分析结果已保存到数据库: {date}")

def main():
    print("="*70)
    print("AI情绪分析 - 完整版")
    print("="*70)
    
    # 1. 获取数据
    print("\n[1/4] 获取数据...")
    date, today_data, recent_data, indices, prev_indices = fetch_data()
    print(f"  分析日期: {date}")
    print(f"  今日情绪指数: {today_data[1]}")
    print(f"  近5日数据: {len(recent_data)} 条")
    print(f"  指数数据: {len(indices)} 条")
    
    # 2. 构建Prompt
    print("\n[2/4] 构建AI Prompt...")
    system_prompt, user_data = build_prompt(date, today_data, recent_data, indices, prev_indices)
    
    # 3. 调用AI分析
    print("\n[3/4] 调用AI分析...")
    full_report = call_ai_api(system_prompt, user_data)
    
    if not full_report:
        print("\n" + "="*70)
        print("需要AI大脑分析")
        print("="*70)
        print("请基于以上prompt进行情绪研判分析，")
        print("然后手动将分析结果保存到数据库。")
        print("="*70)
        return 1  # 返回1表示需要外部AI介入
    
    # 4. 发布到墨问
    print("\n[4/4] 发布到墨问...")
    mowen_link = publish_to_mowen(date, full_report)
    
    # 5. 保存到数据库
    save_to_database(date, phase, action, summary, mowen_link, full_report)
    
    print("\n" + "="*70)
    print("✅ 分析完成！")
    print("="*70)

if __name__ == '__main__':
    main()
