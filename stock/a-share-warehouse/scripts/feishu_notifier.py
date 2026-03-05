#!/usr/bin/env python3
"""
飞书推送工具 - 公共模块
用于股票数据相关脚本发送通知到飞书群
"""

import requests
import json
import os
import sys

# 导入secrets管理
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_webhook

# 从secrets获取飞书Webhook
GROUP_WEBHOOK = get_feishu_webhook()

def send_to_feishu_group(text):
    """发送文字消息到飞书群"""
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "msg_type": "text",
            "content": {"text": text}
        }
        
        resp = requests.post(GROUP_WEBHOOK, headers=headers, json=data, timeout=10)
        result = resp.json()
        
        if result.get("code") == 0:
            print("✅ 飞书群通知发送成功")
            return True
        else:
            print(f"❌ 飞书群通知发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 飞书群通知发送异常: {e}")
        return False
