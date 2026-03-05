#!/usr/bin/env python3
"""
短线情绪研判 - 强制执行脚本
不允许任何创新，不允许任何改变，严格按照固定流程执行
"""

import subprocess
import sys
import sqlite3

DB_PATH = '/root/.openclaw/workspace/stock/dx/data/duanxian.db'

def run_step(step_name, command):
    """执行步骤，失败则退出"""
    print(f"\n{'='*60}")
    print(f"步骤: {step_name}")
    print('='*60)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 失败: {result.stderr}")
        sys.exit(1)
    print(f"✅ 成功")
    return result.stdout

def main():
    # 步骤1: 数据抓取
    run_step("1. 抓取短线侠情绪数据", 
             "cd /root/.openclaw/workspace/stock/dx && python3 scripts/crawler.py")
    
    # 步骤2: 抓取指数K线
    run_step("2. 抓取指数K线数据", 
             "cd /root/.openclaw/workspace/stock/dx && python3 scripts/fetch_kline_sina.py")
    
    # 步骤3: 同步MA50占比
    run_step("3. 同步MA50占比数据", 
             "cd /root/.openclaw/workspace/stock/dx && python3 scripts/sync_ma50_ratio.py")
    
    # 步骤4: AI分析并发布到墨问（关键步骤）
    print(f"\n{'='*60}")
    print("步骤4: AI分析并发布到墨问")
    print('='*60)
    
    # 必须调用 publish_to_mowen.py，不允许用其他方式
    result = subprocess.run(
        ["python3", "scripts/publish_to_mowen.py"],
        cwd="/root/.openclaw/workspace/stock/dx",
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ 墨问发布失败: {result.stderr}")
        sys.exit(1)
    print(f"✅ 墨问发布成功")
    
    # 步骤5: 验证墨问链接已保存
    print(f"\n{'='*60}")
    print("步骤5: 验证墨问链接")
    print('='*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT mowen_link FROM market_sentiment WHERE date = date('now')")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        print("❌ 墨问链接未保存到数据库")
        sys.exit(1)
    print(f"✅ 墨问链接已保存: {row[0]}")
    
    # 步骤6: 更新HTML
    run_step("6. 更新HTML数据", 
             "cd /root/.openclaw/workspace/stock/dx && python3 scripts/update_html_data.py")
    
    # 步骤7: 部署到GitHub
    run_step("7. 部署到GitHub", 
             "cd /root/.openclaw/workspace/stock/dx && python3 scripts/deploy.py")
    
    # 步骤8: 发送飞书通知（只发送，不确认）
    print(f"\n{'='*60}")
    print("步骤8: 发送飞书通知")
    print('='*60)
    print("飞书通知由定时任务发送，此处不发送")
    print(f"✅ 跳过")
    
    print(f"\n{'='*60}")
    print("所有步骤执行完成")
    print('='*60)

if __name__ == '__main__':
    main()
