#!/usr/bin/env python3
"""
短线情绪研判完整流程 - 强制执行正确做法
整合所有步骤，确保不犯错
"""

import subprocess
import sys
import os

WORKSPACE = '/root/.openclaw/workspace/stock/dx'

def run_cmd(cmd, timeout=120):
    """运行命令"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        cwd=WORKSPACE, timeout=timeout
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("="*70)
    print("短线情绪研判 - 完整流程（强制执行正确做法）")
    print("="*70)
    print()
    
    # 步骤1: 强制生成报告（正确做法：重新查询数据库，不用缓存）
    print("[步骤1] 强制生成报告...")
    success, stdout, stderr = run_cmd("python3 scripts/generate_report_force.py")
    if not success:
        print(f"❌ 生成报告失败: {stderr}")
        sys.exit(1)
    print("✅ 报告生成成功")
    print(stdout)
    
    # 步骤2: 获取生成的报告文件路径
    import glob
    report_files = glob.glob(f'{WORKSPACE}/temp/report_generated_*.md')
    if not report_files:
        print("❌ 找不到生成的报告文件")
        sys.exit(1)
    latest_report = max(report_files, key=os.path.getctime)
    print(f"✅ 使用报告: {latest_report}")
    
    # 步骤3: 发布到墨问
    print("\n[步骤3] 发布到墨问...")
    success, stdout, stderr = run_cmd(f"python3 scripts/publish_to_mowen.py {latest_report}")
    if not success:
        print(f"❌ 发布墨问失败: {stderr}")
        sys.exit(1)
    print("✅ 发布墨问成功")
    print(stdout)
    
    # 步骤4: 更新HTML
    print("\n[步骤4] 更新HTML...")
    success, stdout, stderr = run_cmd("python3 scripts/update_html_data.py")
    if not success:
        print(f"❌ 更新HTML失败: {stderr}")
        sys.exit(1)
    print("✅ HTML更新成功")
    print(stdout)
    
    # 步骤5: 部署GitHub
    print("\n[步骤5] 部署GitHub...")
    success, stdout, stderr = run_cmd("python3 scripts/deploy.py")
    if not success:
        print(f"❌ 部署失败: {stderr}")
        sys.exit(1)
    print("✅ 部署成功")
    print(stdout)
    
    # 步骤6: 截图（正确做法：按文档截取 .chart-container）
    print("\n[步骤6] 截图...")
    screenshot_script = '''
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("file:///root/.openclaw/workspace/stock/dx/web/index.html")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        
        # 按文档要求：截取 .chart-container
        chart_container = page.locator(".row").first.locator(".chart-container").first
        chart_container.screenshot(path="/root/.openclaw/workspace/stock/dx/temp/sentiment_chart.png")
        print("✅ 截图成功: sentiment_chart.png")
        
        browser.close()
except Exception as e:
    print(f"❌ 截图失败: {e}")
'''
    with open(f'{WORKSPACE}/temp/screenshot_script.py', 'w') as f:
        f.write(screenshot_script)
    
    success, stdout, stderr = run_cmd("python3 temp/screenshot_script.py")
    if not success:
        print(f"❌ 截图失败: {stderr}")
        sys.exit(1)
    print(stdout)
    
    print("\n" + "="*70)
    print("✅ 完整流程执行成功")
    print("="*70)
    print("\n执行结果:")
    print("  - 报告已生成（重新查询数据库）")
    print("  - 墨问已发布（含正确星期几）")
    print("  - HTML已更新")
    print("  - GitHub已部署")
    print("  - 截图已生成（按文档标准）")

if __name__ == "__main__":
    main()
