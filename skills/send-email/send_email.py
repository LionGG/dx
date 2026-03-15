#!/usr/bin/env python3
"""
Send Email Skill
通过QQ邮箱发送邮件
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 加载配置
CONFIG_FILE = os.path.expanduser("~/.openclaw/secrets/email_config.json")
AUTH_FILE = os.path.expanduser("~/.openclaw/secrets/qq_email_auth_code")

def load_config():
    """加载邮箱配置"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_auth_code():
    """加载授权码"""
    with open(AUTH_FILE, 'r') as f:
        return f.read().strip()

def send_email(to, subject, body, cc=None):
    """
    发送邮件
    
    参数:
        to: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
        cc: 抄送邮箱（可选）
    
    返回:
        True/False 发送是否成功
    """
    try:
        config = load_config()
        auth_code = load_auth_code()
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        msg['To'] = to
        if cc:
            msg['Cc'] = cc
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['sender_email'], auth_code)
        
        recipients = [to]
        if cc:
            recipients.append(cc)
        
        server.sendmail(config['sender_email'], recipients, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"发送失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("用法: python3 send_email.py <收件人> <主题> <正文> [抄送]")
        sys.exit(1)
    
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    cc = sys.argv[4] if len(sys.argv) > 4 else None
    
    if send_email(to, subject, body, cc):
        print("✅ 邮件发送成功")
    else:
        print("❌ 邮件发送失败")
        sys.exit(1)
