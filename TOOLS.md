# TOOLS.md - Local Notes

## 飞书配置

### 我的飞书 Open ID
- **Open ID**: `ou_d19a3f0cab037174af62cc8e9e430192`
- **应用 ID**: `cli_a91e22f1e138dbef`
- **获取方式**: 从飞书消息 mention 标签中解析

### 飞书群配置
- dmPolicy: pairing（私聊需要配对）
- groupPolicy: open（所有群都响应）
- requireMention: true（群里需要@才响应）

---

## 邮箱配置（发邮件Skill）

### QQ邮箱（Billy）
- **邮箱**: 113314650@qq.com
- **SMTP服务器**: smtp.qq.com
- **端口**: 587
- **授权码**: 存储在 `~/.openclaw/secrets/qq_email_auth_code`
- **配置文件**: `~/.openclaw/secrets/email_config.json`
- **Skill路径**: `~/.openclaw/workspace/skills/send-email/`

### 快速发邮件命令
```python
from skills.send-email.send_email import send_email

send_email(
    to="收件人@example.com",
    subject="邮件主题",
    body="邮件正文",
    cc="抄送@example.com"  # 可选
)
```

---

## 与其他龙虾的区别

**小木（另一只龙虾）:**
- 直接运行在飞书机器人后端
- 能直接解析飞书消息原始JSON
- 能看到完整的 sender_id、mention 等元数据

**我（薄荷）:**
- 通过 Kimi-Claw 桥接运行
- 无法直接访问飞书原始消息元数据
- 需要通过其他方式获取自身信息
