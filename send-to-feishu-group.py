#!/usr/bin/env python3
"""
飞书群消息发送工具 - 支持文字和图片
"""

import requests
import json
import sys
import os

# 导入secrets管理
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_webhook, get_feishu_app_config

# 从secrets获取配置
_feishu_config = get_feishu_app_config()
APP_ID = _feishu_config['app_id']
APP_SECRET = _feishu_config['app_secret']
GROUP_WEBHOOK = get_feishu_webhook()

def get_token():
    """获取飞书应用访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    result = resp.json()
    if result.get("code") == 0:
        return result["tenant_access_token"]
    print(f"获取 token 失败: {result}")
    return None

def upload_image(image_path):
    """上传图片获取 image_key"""
    token = get_token()
    if not token:
        return None
    
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"image_type": "message"}
        resp = requests.post(url, headers=headers, files=files, data=data)
    
    result = resp.json()
    if result.get("code") == 0:
        return result["data"]["image_key"]
    print(f"上传图片失败: {result}")
    return None

def send_text(text):
    """发送文字消息到群"""
    headers = {"Content-Type": "application/json"}
    data = {
        "msg_type": "text",
        "content": {"text": text}
    }
    
    resp = requests.post(GROUP_WEBHOOK, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") == 0:
        print("✅ 文字发送成功")
        return True
    else:
        print(f"❌ 文字发送失败: {result.get('msg')}")
        return False

def send_image(image_path):
    """发送图片到群"""
    # 先上传图片
    image_key = upload_image(image_path)
    if not image_key:
        return False
    
    # 发送图片
    headers = {"Content-Type": "application/json"}
    data = {
        "msg_type": "image",
        "content": {"image_key": image_key}
    }
    
    resp = requests.post(GROUP_WEBHOOK, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") == 0:
        print("✅ 图片发送成功")
        return True
    else:
        print(f"❌ 图片发送失败: {result.get('msg')}")
        return False

def send_text_with_image(text, image_path):
    """发送文字+图片"""
    # 先发送文字
    send_text(text)
    # 再发送图片
    return send_image(image_path)

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} text \"要发送的文字\"")
        print(f"  {sys.argv[0]} image /path/to/image.png")
        print(f"  {sys.argv[0]} both \"文字说明\" /path/to/image.png")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "text" and len(sys.argv) >= 3:
        send_text(sys.argv[2])
    
    elif cmd == "image" and len(sys.argv) >= 3:
        send_image(sys.argv[2])
    
    elif cmd == "both" and len(sys.argv) >= 4:
        send_text_with_image(sys.argv[2], sys.argv[3])
    
    else:
        print("参数错误")
        sys.exit(1)

if __name__ == "__main__":
    main()
