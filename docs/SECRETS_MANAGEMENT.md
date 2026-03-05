# Secrets 管理文档

## 📁 文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| Secrets 配置文件 | `/root/.openclaw/secrets/secrets.json` | 存储所有敏感信息 |
| Secrets 管理模块 | `/root/.openclaw/workspace/scripts/secrets_manager.py` | Python 读取接口 |

---

## 🔐 Secrets 配置文件格式

文件位置：`/root/.openclaw/secrets/secrets.json`

```json
{
  "version": 1,
  "secrets": [
    {
      "name": "secret-name",
      "description": "描述信息",
      "entries": [
        {"key": "key1", "value": "value1"},
        {"key": "key2", "value": "value2"}
      ]
    }
  ]
}
```

---

## 📋 当前配置的 Secrets

### 1. MySQL 数据库连接
```json
{
  "name": "mysql-choose-stock",
  "description": "MySQL choose_stock数据库连接信息",
  "entries": [
    {"key": "host", "value": "82.156.239.131"},
    {"key": "port", "value": "3306"},
    {"key": "user", "value": "root"},
    {"key": "password", "value": "***"},
    {"key": "database", "value": "choose_stock"}
  ]
}
```

### 2. 飞书应用配置
```json
{
  "name": "feishu-app",
  "description": "飞书应用配置",
  "entries": [
    {"key": "app_id", "value": "cli_a91e22f1e138dbef"},
    {"key": "app_secret", "value": "***"}
  ]
}
```

### 3. 飞书 Webhook
```json
{
  "name": "feishu-webhook",
  "description": "飞书群机器人Webhook",
  "entries": [
    {"key": "group_webhook", "value": "https://open.feishu.cn/open-apis/bot/v2/hook/..."}
  ]
}
```

### 4. GitHub Token
```json
{
  "name": "github-token",
  "description": "GitHub API Token",
  "entries": [
    {"key": "token", "value": "ghp_***"}
  ]
}
```

---

## 🐍 Python 使用方法

### 基础用法

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_secret

# 获取单个值
password = get_secret('mysql-choose-stock', 'password')
app_id = get_secret('feishu-app', 'app_id')
webhook = get_secret('feishu-webhook', 'group_webhook')
token = get_secret('github-token', 'token')
```

### 获取整个配置

```python
from secrets_manager import get_mysql_config, get_feishu_app_config

# MySQL 配置
mysql_config = get_mysql_config()
host = mysql_config['host']
port = int(mysql_config['port'])
user = mysql_config['user']
password = mysql_config['password']
database = mysql_config['database']

# 飞书配置
feishu_config = get_feishu_app_config()
app_id = feishu_config['app_id']
app_secret = feishu_config['app_secret']
```

### 便捷函数

```python
from secrets_manager import (
    get_mysql_config,      # 获取 MySQL 完整配置
    get_feishu_app_config, # 获取飞书应用配置
    get_feishu_webhook,    # 获取飞书 Webhook URL
    get_github_token       # 获取 GitHub Token
)
```

---

## 📝 实际应用示例

### MySQL 连接

```python
import pymysql
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_mysql_config

config = get_mysql_config()
conn = pymysql.connect(
    host=config['host'],
    port=int(config['port']),
    user=config['user'],
    password=config['password'],
    database=config['database'],
    connect_timeout=30
)
```

### 飞书 API 调用

```python
import requests
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_app_config

config = get_feishu_app_config()
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={
        "app_id": config['app_id'],
        "app_secret": config['app_secret']
    }
)
token = resp.json().get("tenant_access_token")
```

### GitHub API 调用

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_github_token

token = get_github_token()
headers = {'Authorization': f'token {token}'}
```

---

## 🔒 安全注意事项

1. **文件权限**：secrets.json 权限设为 600（仅所有者可读写）
   ```bash
   chmod 600 /root/.openclaw/secrets/secrets.json
   ```

2. **不要提交到 Git**：确保 secrets.json 在 .gitignore 中

3. **备份**：定期备份 secrets.json 到安全位置

4. **更新密钥**：定期轮换 API Key 和 Token

---

## 🔧 添加新的 Secret

编辑 `/root/.openclaw/secrets/secrets.json`，在 `secrets` 数组中添加：

```json
{
  "name": "new-secret-name",
  "description": "描述",
  "entries": [
    {"key": "key1", "value": "value1"},
    {"key": "key2", "value": "value2"}
  ]
}
```

然后在代码中使用：
```python
value = get_secret('new-secret-name', 'key1')
```

---

## 📚 相关文件

- 已迁移使用 secrets 的脚本：
  - `/root/.openclaw/workspace/stock/a-share-warehouse/scripts/sync_stock_from_mysql_v2.py`
  - `/root/.openclaw/workspace/stock/a-share-warehouse/scripts/feishu_notifier.py`
  - `/root/.openclaw/workspace/stock/dx/scripts/analyze_sentiment.py`
  - `/root/.openclaw/workspace/stock/dx/scripts/deploy.py`
  - `/root/.openclaw/workspace/send-to-feishu-group.py`
  - `/root/.openclaw/workspace/write_feishu_doc_in_order.py`

---

*创建时间: 2026-02-28*
*版本: 1.0*
