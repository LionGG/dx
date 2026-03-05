#!/usr/bin/env python3
"""
使用 ngrok 暴露 webhook 服务到外网
"""

import subprocess
import time
import json
import os

from pyngrok import ngrok

# 配置
WEBHOOK_PORT = 8080

def start_ngrok():
    """启动 ngrok 隧道"""
    # 连接到本地 8080 端口
    public_url = ngrok.connect(WEBHOOK_PORT, "http")
    print(f"ngrok tunnel created: {public_url}")
    return public_url

def main():
    try:
        # 启动隧道
        public_url = start_ngrok()
        
        # 显示接口信息
        print("\n" + "="*50)
        print("Webhook 服务已暴露到外网")
        print("="*50)
        print(f"\n公网地址: {public_url}")
        print(f"\n接口地址:")
        print(f"  健康检查: {public_url}/")
        print(f"  交易通知: {public_url}/webhook/trade")
        print(f"  通用通知: {public_url}/webhook/feishu")
        print("\n" + "="*50)
        print("按 Ctrl+C 停止")
        print("="*50)
        
        # 保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping ngrok...")
        ngrok.kill()
        print("Stopped.")

if __name__ == '__main__':
    main()
