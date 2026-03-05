#!/usr/bin/env python3
"""
OpenClaw最佳实践文章抓取 - 晚上19:30执行
抓取OpenClaw相关最佳实践，总结后飞书推送
"""

import requests
from datetime import datetime
import sys
import os

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def fetch_openclaw_practices():
    """抓取OpenClaw最佳实践文章"""
    log("开始抓取OpenClaw最佳实践...")
    
    # 数据来源：官方文档、GitHub、社区文章
    sources = [
        {"name": "OpenClaw官方文档", "url": "https://docs.openclaw.ai"},
        {"name": "GitHub", "url": "https://github.com/openclaw/openclaw"},
    ]
    
    articles = []
    
    # TODO: 实现具体的抓取逻辑
    
    log(f"获取到 {len(articles)} 篇文章")
    return articles

def send_to_feishu(articles):
    """发送文章到飞书"""
    if not articles:
        log("无文章，跳过发送")
        return True
    
    log("发送文章到飞书...")
    
    # 构建消息
    message = "📚 **OpenClaw最佳实践** - {}\n\n".format(datetime.now().strftime('%Y-%m-%d'))
    
    for i, article in enumerate(articles[:3], 1):  # 最多3条
        message += f"{i}. **{article['title']}**\n"
        message += f"   {article['summary']}\n"
        message += f"   [原文]({article['url']})\n\n"
    
    # 发送飞书消息
    try:
        import subprocess
        result = subprocess.run([
            'curl', '-X', 'POST', 'http://localhost:8080/api/message/send',
            '-H', 'Content-Type: application/json',
            '-d', f'{{"channel":"feishu","to":"ou_7b3b64c0a18c735401f4e1d172d4c802","message":"{message}"}}'
        ], capture_output=True, timeout=10)
        
        log("✓ 发送成功")
        return True
    except Exception as e:
        log(f"✗ 发送失败: {e}")
        return False

def main():
    log(f"{'='*60}")
    log(f"OpenClaw最佳实践抓取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'='*60}")
    
    # 抓取文章
    articles = fetch_openclaw_practices()
    
    # 发送飞书
    success = send_to_feishu(articles)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
