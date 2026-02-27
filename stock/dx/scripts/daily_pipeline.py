#!/usr/bin/env python3
"""
每日自动化流程 - 16:00 执行

流程: 数据抓取 → AI分析 → HTML生成 → 部署
只推送 index.html，其他文件不动

用法:
    python3 scripts/daily_pipeline.py

定时任务 (已配置):
    0 16 * * * cd /root/.openclaw/workspace/stock/dx && python3 scripts/daily_pipeline.py >> logs/daily_$(date +\%Y\%m\%d).log 2>&1
"""

import subprocess
import sys
import os
from datetime import datetime

WORKSPACE = '/root/.openclaw/workspace/stock/dx'

# 导入飞书推送模块
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))
from feishu_notifier import send_to_feishu_group

def capture_screenshot(output_path):
    """截图情绪图表卡片"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # 加载本地HTML文件
            html_path = os.path.join(WORKSPACE, 'web', 'index.html')
            page.goto(f'file://{html_path}')
            page.wait_for_load_state('networkidle')
            
            # 等待图表渲染完成
            page.wait_for_timeout(5000)
            
            # 截图第一个情绪图表卡片（情绪指数K线）
            chart_card = page.locator('.chart-container').first
            chart_card.wait_for(state='visible')
            chart_card.screenshot(path=output_path)
            browser.close()
            
            return True
    except Exception as e:
        print(f"截图失败: {e}")
        return False

def send_feishu_with_image(text, image_path):
    """发送文字+图片到飞书群"""
    try:
        result = subprocess.run(
            ['python3', '/root/.openclaw/workspace/send-to-feishu-group.py', 'both', text, image_path],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def run_step(name, cmd, timeout=300, critical=False):
    """
    执行单个步骤
    
    critical=True: 失败则停止整个流程
    """
    print(f"\n{'='*60}")
    print(f"步骤: {name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            print(result.stdout[-2000:])  # 只打印最后2000字符
        
        if result.returncode != 0:
            print(f"✗ 失败: {result.stderr}")
            if critical:
                return False, True  # 失败且关键
            return False, False
        
        print(f"✓ 成功")
        return True, False
        
    except subprocess.TimeoutExpired:
        print(f"✗ 超时 ({timeout}秒)")
        if critical:
            return False, True
        return False, False
    except Exception as e:
        print(f"✗ 错误: {e}")
        if critical:
            return False, True
        return False, False

def main():
    start_time = datetime.now()
    today = start_time.strftime('%Y-%m-%d')
    print(f"\n{'#'*60}")
    print(f"# A股情绪数据自动化流程 - {today}")
    print(f"{'#'*60}")
    
    # 确保日志目录存在
    os.makedirs(os.path.join(WORKSPACE, 'logs'), exist_ok=True)
    
    # 定义步骤 (名称, 命令, 超时秒数, 是否关键)
    steps = [
        ("1. 抓取短线侠情绪数据", "python3 scripts/crawler.py", 120, True),
        ("2. 抓取AKShare K线数据", "python3 scripts/fetch_kline_akshare.py", 120, True),
        ("3. 同步MA50占比数据", "python3 scripts/sync_ma50_ratio.py", 60, True),
        ("4. AI分析并发布到墨问", "python3 scripts/analyze_sentiment.py", 300, True),
        ("5. 更新HTML数据", "python3 scripts/update_html_data.py", 60, True),
        ("6. 部署到GitHub", "python3 scripts/deploy.py", 60, False),  # 部署失败不阻断
    ]
    
    failed_steps = []
    critical_failed = False
    
    for name, cmd, timeout, critical in steps:
        success, is_critical = run_step(name, cmd, timeout, critical)
        if not success:
            failed_steps.append(name)
            if is_critical:
                critical_failed = True
                print(f"\n✗ 关键步骤失败，停止执行: {name}")
                break
    
    # 总结
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print("执行总结")
    print(f"{'='*60}")
    print(f"日期: {today}")
    print(f"开始: {start_time.strftime('%H:%M:%S')}")
    print(f"结束: {end_time.strftime('%H:%M:%S')}")
    print(f"耗时: {duration:.1f}秒")
    
    if failed_steps:
        print(f"\n⚠ 失败步骤:")
        for step in failed_steps:
            marker = " (关键)" if critical_failed and step == failed_steps[-1] else ""
            print(f"  - {step}{marker}")
    
    # 从数据库获取AI分析结果
    try:
        sqlite_conn = sqlite3.connect(DB_PATH)
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT analysis_phase, mowen_link 
            FROM market_sentiment 
            WHERE date = ?
        ''', (today,))
        row = cursor.fetchone()
        analysis_phase = row[0] if row else "未生成"
        mowen_link = row[1] if row and row[1] else f"https://liongg.github.io/dx/"
        sqlite_conn.close()
    except:
        analysis_phase = "未生成"
        mowen_link = "https://liongg.github.io/dx/"
    
    # 生成飞书群推送消息（按照确认格式）
    feishu_message = f"""📊 短线情绪研判 - {today}

周期定位：{analysis_phase}

查看完整分析：{mowen_link}"""
    
    # 截图并发送飞书群通知（文字+图片）
    screenshot_path = os.path.join(WORKSPACE, 'screenshot.png')
    if capture_screenshot(screenshot_path):
        print("✅ 网页截图完成")
        if send_feishu_with_image(feishu_message, screenshot_path):
            print("✅ 飞书群通知发送成功（文字+图片）")
        else:
            # 图片发送失败，只发文字
            send_to_feishu_group(feishu_message)
            print("⚠️ 图片发送失败，已发送文字")
    else:
        # 截图失败，只发文字
        send_to_feishu_group(feishu_message)
        print("⚠️ 截图失败，已发送文字")
    
    if critical_failed:
        print(f"\n✗ 流程未完成，需要人工介入")
        return False
    elif failed_steps:
        print(f"\n⚠ 流程完成，但有非关键步骤失败")
        return True
    else:
        print(f"\n✓ 全部成功")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
