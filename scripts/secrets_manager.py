#!/usr/bin/env python3
"""
Secrets 管理模块
统一读取和管理敏感信息
"""

import json
import os
from pathlib import Path

SECRETS_FILE = Path("/root/.openclaw/secrets/secrets.json")

def load_secrets():
    """加载所有secrets"""
    if not SECRETS_FILE.exists():
        raise FileNotFoundError(f"Secrets文件不存在: {SECRETS_FILE}")
    
    with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为字典格式方便访问
    secrets = {}
    for secret in data.get('secrets', []):
        name = secret['name']
        entries = {entry['key']: entry['value'] for entry in secret.get('entries', [])}
        secrets[name] = entries
    
    return secrets

def get_secret(secret_name, key=None):
    """
    获取指定secret
    
    Args:
        secret_name: secret名称，如 'mysql-choose-stock', 'feishu-app'
        key: 具体字段，如 'password', 'app_id'。为None时返回整个dict
    
    Returns:
        str or dict: 指定key的值或整个secret dict
    
    Example:
        password = get_secret('mysql-choose-stock', 'password')
        feishu_config = get_secret('feishu-app')
        app_id = feishu_config['app_id']
    """
    secrets = load_secrets()
    
    if secret_name not in secrets:
        raise KeyError(f"Secret '{secret_name}' 不存在")
    
    secret = secrets[secret_name]
    
    if key is None:
        return secret
    
    if key not in secret:
        raise KeyError(f"Key '{key}' 不存在于 secret '{secret_name}'")
    
    return secret[key]

# 便捷函数
def get_mysql_config():
    """获取MySQL配置"""
    return get_secret('mysql-choose-stock')

def get_feishu_app_config():
    """获取飞书应用配置"""
    return get_secret('feishu-app')

def get_feishu_webhook():
    """获取飞书Webhook"""
    return get_secret('feishu-webhook', 'group_webhook')

def get_github_token():
    """获取GitHub Token"""
    return get_secret('github-token', 'token')

if __name__ == '__main__':
    # 测试
    print("Testing secrets module...")
    print(f"MySQL host: {get_secret('mysql-choose-stock', 'host')}")
    print(f"Feishu App ID: {get_secret('feishu-app', 'app_id')}")
    print(f"GitHub Token: {get_github_token()[:10]}...")
    print("✅ Secrets module working!")
