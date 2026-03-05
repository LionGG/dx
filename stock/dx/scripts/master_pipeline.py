#!/usr/bin/env python3
"""
短线情绪研判工作流 - 主控脚本
顺序执行：task1 -> task2 -> task3，失败即停，独立通知
"""

import subprocess
import sys
import os
from datetime import datetime

WORKSPACE = '/root/.openclaw/workspace/stock/dx'

def run_task(script_name, task_name, timeout=300):
    """运行子任务，返回成功/失败"""
    print(f"\n{'='*60}")
    print(f"开始执行: {task_name}")
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    cmd = f"cd {WORKSPACE} && python3 scripts/{script_name}"
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        timeout=timeout
    )
    
    success = result.returncode == 0
    duration = "X"  # 简化处理
    
    if success:
        print(f"✅ {task_name}成功")
        # 发送成功通知
        send_notification(f"✅ {task_name}成功 - {datetime.now().strftime('%Y-%m-%d')}\n状态: 执行完成")
    else:
        print(f"❌ {task_name}失败")
        print(f"错误: {result.stderr[:200]}")
        # 发送失败通知
        send_notification(f"❌ {task_name}失败 - {datetime.now().strftime('%Y-%m-%d')}\n原因: {result.stderr[:100]}\n后续任务已停止")
    
    return success

def send_notification(message):
    """发送飞书通知"""
    try:
        # 使用OpenClaw message工具
        import subprocess
        subprocess.run([
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--message", message
        ], capture_output=True, timeout=30)
    except:
        pass

def main():
    """主工作流"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 短线情绪研判工作流启动 - {date_str}")
    
    # Task 1: 数据抓取
    if not run_task("task1_data_fetch.py", "数据抓取"):
        print("\n❌ 工作流终止：数据抓取失败")
        return 1
    
    # Task 2: AI分析
    if not run_task("task2_analysis.py", "AI分析"):
        print("\n❌ 工作流终止：AI分析失败")
        return 1
    
    # Task 3: 部署发布
    if not run_task("task3_deploy.py", "部署发布"):
        print("\n❌ 工作流终止：部署发布失败")
        return 1
    
    print(f"\n{'='*60}")
    print("✅ 工作流全部完成")
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
