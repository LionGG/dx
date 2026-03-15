#!/usr/bin/env python3
"""
数据库配置模块 - ETF指标计算
统一从secrets加载数据库配置
"""

import json
import os

def load_db_config():
    """从secrets加载数据库配置"""
    secrets_path = os.path.expanduser("~/.openclaw/secrets/secrets.json")
    try:
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
        
        for secret in secrets.get('secrets', []):
            if secret.get('name') == 'mysql-choose-stock':
                entries = {entry['key']: entry['value'] for entry in secret.get('entries', [])}
                return {
                    "host": entries.get('host'),
                    "port": int(entries.get('port', 3306)),
                    "user": entries.get('user'),
                    "password": entries.get('password'),
                    "database": entries.get('database'),
                    "charset": "utf8mb4"
                }
    except Exception as e:
        print(f"加载数据库配置失败: {e}")
    
    return None

# 全局配置
DB_CONFIG = load_db_config()
