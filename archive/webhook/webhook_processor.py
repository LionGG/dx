#!/usr/bin/env python3
"""
Webhook 通知处理器 - 轮询通知队列并推送到飞书
"""

import json
import os
import time
import glob
import subprocess

NOTIFY_DIR = "/root/.openclaw/workspace/webhook_logs/notifications"
PROCESSED_DIR = "/root/.openclaw/workspace/webhook_logs/processed"

def process_notifications():
    """处理通知队列"""
    os.makedirs(NOTIFY_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # 获取所有通知文件
    notify_files = glob.glob(f"{NOTIFY_DIR}/notify_*.json")
    
    for notify_file in sorted(notify_files):
        try:
            with open(notify_file, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            message = notification.get('full_message', notification.get('message', ''))
            
            # 使用 openclaw 命令推送
            result = subprocess.run(
                ['openclaw', 'message', 'send', '--channel', 'feishu', '--message', message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 移动已处理的文件
                filename = os.path.basename(notify_file)
                processed_file = f"{PROCESSED_DIR}/{filename}"
                os.rename(notify_file, processed_file)
                print(f"Sent and moved: {filename}")
            else:
                print(f"Failed to send: {filename}, error: {result.stderr}")
                
        except Exception as e:
            print(f"Error processing {notify_file}: {e}")

def main():
    """主循环"""
    print("Webhook notification processor started")
    print(f"Watching: {NOTIFY_DIR}")
    
    while True:
        try:
            process_notifications()
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        # 每 10 秒检查一次
        time.sleep(10)

if __name__ == '__main__':
    main()
