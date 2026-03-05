#!/usr/bin/env python3
"""
部署脚本 - 只推送 index.html 到 GitHub

使用 GitHub API 直接上传，避免 git 操作超时问题
只操作 index.html，其他文件完全不动
"""

import os
import sys
import base64
import json
import urllib.request
from datetime import datetime

# 导入secrets管理
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_github_token

# 配置
WORKSPACE_DIR = '/root/.openclaw/workspace/stock/dx'
HTML_FILE = os.path.join(WORKSPACE_DIR, 'web', 'index.html')
REPO = 'LionGG/dx'
TOKEN = get_github_token()

def deploy():
    """只推送 index.html，其他文件不动"""
    print("=" * 60)
    print("GitHub 部署脚本 - 仅推送 index.html")
    print("=" * 60)
    
    # 1. 检查文件
    if not os.path.exists(HTML_FILE):
        print(f"✗ 文件不存在: {HTML_FILE}")
        return False
    
    file_size = os.path.getsize(HTML_FILE)
    print(f"✓ HTML文件: {file_size} 字节")
    
    # 2. 读取并编码
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # 3. 准备请求
    headers = {
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Python',
        'Content-Type': 'application/json'
    }
    
    # 4. 获取当前文件 SHA（如果存在）
    sha = None
    try:
        req = urllib.request.Request(
            f'https://api.github.com/repos/{REPO}/contents/index.html',
            headers=headers,
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            file_info = json.loads(resp.read().decode())
            sha = file_info.get('sha')
            print(f"✓ 获取现有文件 SHA")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"✓ 文件不存在，将创建新文件")
        else:
            print(f"⚠ 获取 SHA 失败: {e}")
    except Exception as e:
        print(f"⚠ 获取 SHA 失败: {e}")
    
    # 5. 上传文件
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'message': f'Update sentiment data - {timestamp}',
        'content': encoded
    }
    if sha:
        data['sha'] = sha
    
    try:
        req = urllib.request.Request(
            f'https://api.github.com/repos/{REPO}/contents/index.html',
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='PUT'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            commit_sha = result['commit']['sha'][:12]
            print(f"✓ 部署成功: {commit_sha}")
            print(f"✓ 只推送了 index.html，其他文件未动")
            return True
    except urllib.error.HTTPError as e:
        print(f"✗ 部署失败: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode()
            print(f"  详情: {error_body[:200]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"✗ 部署失败: {e}")
        return False

if __name__ == '__main__':
    success = deploy()
    sys.exit(0 if success else 1)
