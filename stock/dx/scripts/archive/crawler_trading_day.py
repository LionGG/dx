#!/usr/bin/env python3
"""
短线侠数据每日抓取 - 交易日判断版
只在A股交易日执行数据抓取
"""

import sys
import os
from datetime import datetime

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# 添加项目目录到路径
sys.path.insert(0, PROJECT_DIR)

from trading_calendar import is_trading_day, get_next_trading_day

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    weekday = datetime.now().strftime('%A')
    
    print(f"="*60)
    print(f"短线侠数据每日抓取 - {today} ({weekday})")
    print(f"="*60)
    
    # 判断今天是否为交易日
    if not is_trading_day(today):
        print(f"\n📅 {today} 不是A股交易日，跳过数据抓取。")
        print(f"   下一个交易日: {get_next_trading_day()}")
        return 0
    
    print(f"\n✅ {today} 是A股交易日，开始抓取数据...")
    print()
    
    # 执行数据抓取
    crawler_path = os.path.join(SCRIPT_DIR, 'crawler.py')
    if os.path.exists(crawler_path):
        import subprocess
        result = subprocess.run(['python3', crawler_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode
    else:
        print(f"❌ 抓取脚本不存在: {crawler_path}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
