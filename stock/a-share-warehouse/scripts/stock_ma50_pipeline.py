#!/usr/bin/env python3
"""
个股数据+MA50工作流
顺序执行：个股数据抓取 → MA50计算
保持原有通知方式不变
"""

import subprocess
import sys
from datetime import datetime

WORKSPACE = '/root/.openclaw/workspace/stock/a-share-warehouse'

def run_script(script_path, timeout=300):
    """运行脚本，保持其原有通知"""
    cmd = f"cd {WORKSPACE} && python3 {script_path}"
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 个股数据+MA50工作流 - {date_str}")
    
    # Step 1: 个股数据抓取（脚本自己发通知）
    print("\n[1/2] 执行个股数据抓取...")
    success, stdout, stderr = run_script('scripts/sync_stock_from_mysql_v2.py', timeout=300)
    
    if not success:
        print("❌ 个股数据抓取失败，停止工作流")
        print(f"错误: {stderr[:200]}")
        return 1
    
    print("✅ 个股数据抓取完成")
    
    # Step 2: MA50计算（脚本自己发通知）
    print("\n[2/2] 执行MA50计算...")
    success, stdout, stderr = run_script('scripts/calculate_ma50_ratio.py', timeout=300)
    
    if not success:
        print("❌ MA50计算失败")
        print(f"错误: {stderr[:200]}")
        return 1
    
    print("✅ MA50计算完成")
    print(f"\n🎉 工作流全部完成 - {datetime.now().strftime('%H:%M:%S')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
