#!/usr/bin/env python3
"""
飞书推送工具 - 公共模块
用于股票数据相关脚本发送通知到飞书群
"""

import requests
import json
import os

# 飞书群机器人 Webhook
GROUP_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/c21f215d-e186-4b3b-bb50-1ebbe4e994df"

def send_to_feishu_group(text, image_path=None):
    """发送消息到飞书群
    
    Args:
        text: 文字内容
        image_path: 图片路径（可选）
    """
    try:
        # 如果提供了图片，先上传图片
        if image_path and os.path.exists(image_path):
            # 上传图片获取image_key
            image_key = upload_image(image_path)
            if image_key:
                # 发送图片+文字
                return send_image_with_text(image_key, text)
        
        # 只发送文字
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

def upload_image(image_path):
    """上传图片到飞书，获取image_key"""
    try:
        # 获取tenant_access_token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_data = {
            "app_id": "cli_a91e22f1e138dbef",
            "app_secret": "AFttWLYp3oprJnfB4gFoHdDMKasA04Nn"
        }
        resp = requests.post(token_url, json=token_data, timeout=10)
        token_result = resp.json()
        tenant_token = token_result.get("tenant_access_token")
        
        if not tenant_token:
            print("❌ 获取tenant_token失败")
            return None
        
        # 上传图片 - 使用正确的API
        upload_url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {"Authorization": f"Bearer {tenant_token}"}
        
        # 需要指定image_type
        with open(image_path, 'rb') as f:
            files = {'image': ('screenshot.png', f, 'image/png')}
            data = {'image_type': 'message'}
            resp = requests.post(upload_url, headers=headers, files=files, data=data, timeout=30)
        
        result = resp.json()
        if result.get("code") == 0:
            image_key = result.get("data", {}).get("image_key")
            print(f"✅ 图片上传成功: {image_key}")
            return image_key
        else:
            print(f"❌ 图片上传失败: {result}")
            return None
    except Exception as e:
        print(f"❌ 图片上传异常: {e}")
        return None

def send_image_with_text(image_key, text):
    """发送图片+文字消息"""
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "短线情绪研判",
                        "content": [
                            [{"tag": "text", "text": text}],
                            [{"tag": "img", "image_key": image_key}]
                        ]
                    }
                }
            }
        }
        
        resp = requests.post(GROUP_WEBHOOK, headers=headers, json=data, timeout=10)
        result = resp.json()
        
        if result.get("code") == 0:
            print("✅ 飞书群图片+文字发送成功")
            return True
        else:
            print(f"❌ 飞书群发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 飞书群发送异常: {e}")
        return False
