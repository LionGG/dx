#!/usr/bin/env python3
"""
薄荷日记发送脚本
读取今日日记并发送到飞书
"""

import os
import sys
from datetime import datetime, timedelta

def get_today_date():
    """获取今日日期"""
    return datetime.now().strftime("%Y-%m-%d")

def read_today_journal():
    """读取今日日记"""
    today = get_today_date()
    journal_path = f"/root/.openclaw/workspace/memory/{today}.md"
    
    if not os.path.exists(journal_path):
        return None, f"日记文件不存在: {journal_path}"
    
    try:
        with open(journal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, f"读取日记失败: {e}"

def format_journal_for_feishu(content):
    """格式化日记内容用于飞书推送"""
    lines = content.split('\n')
    
    # 提取标题
    title = "📔 薄荷日记"
    if lines and lines[0].startswith('# '):
        title = lines[0].replace('# ', '📔 ')
    
    # 简化内容，保留主要部分
    summary_lines = []
    in_section = False
    
    for line in lines[1:]:
        # 跳过待补充的段落
        if '（待补充' in line:
            continue
        if line.startswith('---'):
            break
        if line.strip():
            summary_lines.append(line)
    
    summary = '\n'.join(summary_lines[:30])  # 限制长度
    
    return title, summary

def main():
    """主函数"""
    try:
        today = get_today_date()
        print(f"正在读取 {today} 的日记...")
        
        # 读取日记
        content, error = read_today_journal()
        if error:
            print(f"❌ {error}", file=sys.stderr)
            return 1
        
        # 格式化
        title, summary = format_journal_for_feishu(content)
        
        # 输出到stdout（OpenClaw会捕获并发送）
        print(f"{title}\n")
        print(summary)
        print(f"\n---\n✅ 日记发送成功 - {today}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 发送日记失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
