#!/usr/bin/env python3
"""
执行前检查模块 - 防止重复犯错
"""

import json
import os
from datetime import datetime

ERROR_PREVENTION_FILE = "/root/.openclaw/workspace/memory/ERROR_PREVENTION.md"

def load_error_prevention():
    """加载错误预防记录"""
    if not os.path.exists(ERROR_PREVENTION_FILE):
        return []
    
    with open(ERROR_PREVENTION_FILE, 'r') as f:
        content = f.read()
    
    # 简单解析已纠正的错误
    errors = []
    sections = content.split("### ")
    for section in sections[1:]:  # 跳过第一个空部分
        lines = section.strip().split("\n")
        if lines:
            error_name = lines[0].strip()
            errors.append(error_name)
    
    return errors

def check_before_action(action_type, details=""):
    """
    执行操作前检查
    
    Args:
        action_type: 操作类型 (restart_gateway, edit_config, modify_cron, etc.)
        details: 操作详情
    
    Returns:
        (can_proceed, warning_message)
    """
    errors = load_error_prevention()
    warnings = []
    
    # 检查特定操作类型的风险
    if action_type == "restart_gateway":
        warnings.append("⚠️ 检查点: 上次重启问题 - 避免频繁重启")
        warnings.append("✅ 确认: 是否必须现在重启？能否等待周日 03:00？")
        warnings.append("✅ 确认: 当前是否有正在执行的任务？")
        
    elif action_type == "edit_config":
        warnings.append("⚠️ 检查点: 上次配置损坏 - 必须备份")
        warnings.append("✅ 确认: 是否已备份原文件？")
        warnings.append("✅ 确认: 是否已验证 JSON 格式？")
        
    elif action_type == "modify_cron":
        warnings.append("⚠️ 检查点: 避免重复创建任务")
        warnings.append("✅ 确认: 是否已检查现有任务列表？")
        warnings.append("✅ 确认: 脚本是否已手动测试？")
        
    elif action_type == "modify_script":
        warnings.append("⚠️ 检查点: 上次硬编码密码问题")
        warnings.append("✅ 确认: 是否使用了 secrets_manager？")
        warnings.append("✅ 确认: 是否检查了敏感信息泄露？")
    
    # 通用检查
    if warnings:
        return True, "\n".join(warnings)
    
    return True, "✅ 无特殊风险检查点"

def log_action(action_type, details, result):
    """记录操作日志"""
    log_file = "/root/.openclaw/workspace/memory/action_log.md"
    
    with open(log_file, 'a') as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**操作**: {action_type}\n")
        f.write(f"**详情**: {details}\n")
        f.write(f"**结果**: {result}\n")
        f.write("---\n")

if __name__ == "__main__":
    # 测试
    print("测试执行前检查...")
    can_proceed, warning = check_before_action("restart_gateway")
    print(warning)
    print()
    can_proceed, warning = check_before_action("edit_config")
    print(warning)
