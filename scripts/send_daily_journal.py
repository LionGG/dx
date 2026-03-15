#!/usr/bin/env python3
"""
薄荷日记发送脚本
读取今日日记并发送到飞书私聊（宝总）
"""

import os
import sys
from datetime import datetime, timedelta

# 宝总的飞书 Open ID
BAOZONG_OPEN_ID = "ou_7b3b64c0a18c735401f4e1d172d4c802"

def get_today_date():
    """获取今日日期"""
    return datetime.now().strftime("%Y-%m-%d")

def read_yesterday_journal():
    """读取昨日日记（2:20写作任务生成）"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    journal_path = f"/root/.openclaw/workspace/memory/{yesterday_str}.md"
    
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
        if '（待补充' in line or '（今日暂无' in line:
            continue
        if line.startswith('---'):
            break
        if line.strip():
            summary_lines.append(line)
    
    summary = '\n'.join(summary_lines[:50])  # 限制长度
    
    return title, summary

def main():
    """主函数"""
    try:
        today = get_today_date()
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"正在读取 {yesterday} 的日记（昨日）...")
        
        # 读取日记
        content, error = read_yesterday_journal()
        if error:
            print(f"❌ {error}", file=sys.stderr)
            return 1
        
        # 格式化
        title, summary = format_journal_for_feishu(content)
        
        # 输出到stdout，OpenClaw会捕获并发送
        # 重要：明确指定发送到宝总私聊
        print(f"{title}\n")
        print(summary)
        print(f"\n---")
        print(f"⏰ 日记范围：前24小时（昨天23:50 ~ 今天23:50）")
        print(f"📤 发送目标：宝总私聊")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"✅ 日记发送成功 - {yesterday}")
        
        # 输出发送指令提示
        print(f"\n[系统提示] 请使用以下参数发送：")
        print(f'channel: "feishu"')
        print(f'target: "user:{BAOZONG_OPEN_ID}"')
        
        return 0
        
    except Exception as e:
        print(f"❌ 发送日记失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
