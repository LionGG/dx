#!/usr/bin/env python3
"""
短线情绪部署 - 任务3
更新HTML、部署、截图、发送飞书
"""

import subprocess
import sys
import os
import sqlite3
import time
from datetime import datetime

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

def check_step2():
    """检查第二步是否完成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT date, mowen_url FROM market_sentiment ORDER BY date DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[1]:
        return False, "第二步未完成（无墨问链接）"
    return True, row[0]

def take_screenshot():
    """截图网页 - 使用Playwright"""
    screenshot_path = '/tmp/dx_screenshot.png'
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.goto('file:///root/.openclaw/workspace/stock/dx/web/index.html')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(5000)  # 等待图表渲染
            
            # 截取情绪图表容器（左上角卡片）
            chart_container = page.locator('.row').first.locator('.chart-container').first
            chart_container.screenshot(path=screenshot_path)
            browser.close()
        
        if os.path.exists(screenshot_path):
            return True, screenshot_path
    except Exception as e:
        print(f"⚠️ Playwright截图失败: {e}")
        # 降级到chromium-browser
        cmd = f"chromium-browser --headless --no-sandbox --screenshot={screenshot_path} --window-size=1200,800 https://liongg.github.io/dx/ 2>/dev/null"
        result = subprocess.run(cmd, shell=True, timeout=30)
        if result.returncode == 0 and os.path.exists(screenshot_path):
            return True, screenshot_path
    
    return False, None

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"="*60)
    print(f"短线情绪部署 - {today}")
    print(f"="*60)
    
    # 1. 检查第二步
    print("\n[1/5] 检查第二步是否完成...")
    ok, date = check_step2()
    if not ok:
        send_to_feishu_group(f"❌ 任务3暂停\n\n原因：{date}")
        return 1
    print(f"✅ 第二步已完成: {date}")
    
    # 2. 更新HTML
    print("\n[2/5] 更新HTML...")
    success, stdout, stderr = run_cmd("python3 scripts/update_html_data.py")
    if not success:
        send_to_feishu_group(f"❌ 任务3失败\n\n原因：HTML更新失败\n{stderr[:200]}")
        return 1
    print("✅ HTML更新成功")
    
    # 3. 部署到GitHub
    print("\n[3/5] 部署到GitHub...")
    success, stdout, stderr = run_cmd("python3 scripts/deploy.py")
    if not success:
        send_to_feishu_group(f"❌ 任务3失败\n\n原因：部署失败\n{stderr[:200]}")
        return 1
    print("✅ 部署成功")
    
    # 4. 等待网页生效
    print("\n[4/5] 等待网页生效...")
    time.sleep(30)
    print("✅ 等待完成")
    
    # 5. 截图
    print("\n[5/5] 截图网页...")
    success, screenshot_path = take_screenshot()
    if not success:
        send_to_feishu_group("⚠️ 任务3部分成功\n\nHTML已更新并部署，但截图失败")
        return 0  # 截图失败不阻断
    print(f"✅ 截图成功: {screenshot_path}")
    
    # 6. 发送飞书（文字+截图）
    msg = f"✅ 短线情绪部署完成 - {date}\n\n网页已更新并部署"
    
    # 发送图片+文字
    from feishu_notifier import send_to_feishu_group
    success = send_to_feishu_group(msg, screenshot_path)
    if success:
        print("\n✅ 飞书图片+文字通知已发送")
    else:
        # 图片发送失败，只发送文字
        send_to_feishu_group(msg)
        print("\n⚠️ 图片发送失败，已发送文字通知")
    return 0

if __name__ == '__main__':
    sys.exit(main())
