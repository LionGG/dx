#!/usr/bin/env python3
"""
薄荷日记发送脚本（卡片版）
使用 lark-card-sender 发送格式化卡片
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from feishu_card_wrapper import FeishuCardWrapper

def get_yesterday_date():
    """获取昨日日期"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def read_yesterday_journal():
    """读取昨日日记"""
    yesterday_str = get_yesterday_date()
    journal_path = f"/root/.openclaw/workspace/memory/{yesterday_str}.md"
    
    if not os.path.exists(journal_path):
        return None, f"日记文件不存在: {journal_path}"
    
    try:
        with open(journal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, f"读取日记失败: {e}"

def parse_journal_sections(content):
    """解析日记内容为章节"""
    sections = []
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            if current_section:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content).strip()
                })
            current_section = line.replace('## ', '')
            current_content = []
        elif current_section and line.strip():
            current_content.append(line)
    
    if current_section and current_content:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content).strip()
        })
    
    return sections

def main():
    """主函数"""
    yesterday = get_yesterday_date()
    print(f"📔 正在发送 {yesterday} 的日记卡片...")
    
    try:
        # 读取日记
        content, error = read_yesterday_journal()
        if error:
            print(f"❌ {error}", file=sys.stderr)
            # 发送错误卡片
            wrapper = FeishuCardWrapper()
            wrapper.send_system_alert_card(
                '日记读取失败',
                f"无法读取 {yesterday} 的日记文件\n\n原因：{error}",
                'warning'
            )
            return 1
        
        # 解析章节
        sections = parse_journal_sections(content)
        if not sections:
            sections = [{'title': '今日记录', 'content': content[:500]}]
        
        # 限制章节数量，避免卡片过大
        sections = sections[:4]
        
        # 发送卡片
        wrapper = FeishuCardWrapper()
        result = wrapper.send_journal_card(yesterday, sections)
        
        print(f"✅ 日记卡片发送成功")
        print(f"📤 消息ID: {result.get('message_id', 'N/A')}")
        return 0
        
    except Exception as e:
        print(f"❌ 发送日记卡片失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
