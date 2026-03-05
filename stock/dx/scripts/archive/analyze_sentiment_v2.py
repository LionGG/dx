#!/usr/bin/env python3
"""
AI情绪分析 - 简化版
只做一件事：调用子代理完成AI分析并发布到墨问
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

def get_today_data():
    """获取今日数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, up_count, down_count,
               consecutive_height, volume, seal_rate
        FROM market_sentiment 
        ORDER BY date DESC LIMIT 1
    ''')
    today = cursor.fetchone()
    
    cursor.execute('''
        SELECT date, sentiment_index, limit_up, limit_down, up_count, down_count
        FROM market_sentiment 
        ORDER BY date DESC LIMIT 5
    ''')
    recent = cursor.fetchall()
    
    conn.close()
    return today, recent

def main():
    print("="*60)
    print("AI情绪分析 - 简化版")
    print("="*60)
    
    # 1. 获取数据
    today, recent = get_today_data()
    if not today:
        print("❌ 无数据")
        return 1
    
    date = today[0]
    print(f"分析日期: {date}")
    print(f"情绪指数: {today[1]}")
    
    # 2. 构建prompt
    recent_str = "\n".join([f"{r[0]}: 情绪{r[1]}, 涨停{r[2]}, 跌停{r[3]}, 上涨{r[4]}, 下跌{r[5]}" for r in recent])
    
    prompt = f"""分析日期：{date}

【当日情绪数据】
- 情绪指数：{today[1]}
- 涨停家数：{today[2]}
- 跌停家数：{today[3]}
- 上涨家数：{today[4]}
- 下跌家数：{today[5]}
- 连板高度：{today[6]}板
- 量能：{today[7]}亿
- 封板率：{today[8]}

【近5日演变】
{recent_str}

请生成短线情绪研判报告，包含：
1. 当日盘面解读
2. 周期定位与演变
3. 后市策略应对
4. 一句话总结

生成后调用publish_to_mowen发布到墨问，并保存到数据库。"""

    print("\n" + "="*60)
    print("启动子代理进行AI分析...")
    print("="*60)
    print(prompt)
    
    # 3. 启动子代理
    # 子代理完成任务后会直接发布到墨问并保存数据库
    print("\n子代理启动命令:")
    print(f"sessions_spawn(task='{prompt}', runtime='subagent', timeout=120)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
