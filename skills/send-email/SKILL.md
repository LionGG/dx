# Send Email Skill

通过QQ邮箱发送邮件的简单工具。

## 使用方法

### 命令行
```bash
python3 send_email.py <收件人> <主题> <正文> [抄送]
```

### 示例
```bash
# 简单发送
python3 send_email.py "hr@moonshot.ai" "测试邮件" "这是测试内容"

# 带抄送
python3 send_email.py "hr@moonshot.ai" "测试邮件" "这是测试内容" "cc@example.com"
```

### Python调用
```python
from send_email import send_email

# 发送邮件
send_email(
    to="recipient@example.com",
    subject="邮件主题",
    body="邮件正文",
    cc="cc@example.com"  # 可选
)
```

## 配置

邮箱配置存储在 `~/.openclaw/secrets/email_config.json`：
- SMTP服务器: smtp.qq.com
- 端口: 587
- 发件人: 113314650@qq.com

授权码存储在 `~/.openclaw/secrets/qq_email_auth_code`

## 安全

- 授权码文件权限设置为600（仅所有者可读写）
- 不包含敏感信息的硬编码
