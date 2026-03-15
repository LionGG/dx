#!/usr/bin/env python3
"""
发布到墨问模块
读取传入的 markdown 文件并发布
"""

import requests
import json
import sqlite3
import sys
import re

def markdown_to_mowen_doc(markdown_text):
    """Convert markdown to Mowen doc format"""
    lines = markdown_text.split('\n')
    content = []
    
    for line in lines:
        s = line.strip()
        if not s or s == '---':
            continue
        
        if s.startswith('# '):
            title_text = s[2:].replace('**', '')
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": title_text, "marks": [{"type": "bold"}]}]
            })
        elif s.startswith('## '):
            title_text = s[3:].replace('**', '')
            content.append({"type": "paragraph", "content": []})
            content.append({"type": "paragraph", "content": [{"type": "text", "text": title_text}]})
        elif s.startswith('- '):
            text = s[2:].replace('**', '')
            content.append({"type": "paragraph", "content": [{"type": "text", "text": "• " + text}]})
        else:
            text = s.replace('**', '')
            content.append({"type": "paragraph", "content": [{"type": "text", "text": text}]})
    
    return content

def publish_to_mowen(title, content, tags=None):
    """发布到墨问"""
    if tags is None:
        tags = ["分析报告"]
    
    doc_content = markdown_to_mowen_doc(content)
    
    url = "https://open.mowen.cn/api/open/api/v1/note/create"
    headers = {
        "Authorization": "Bearer ijbrCOAwgLnp9Vu5kdZhw59hUfX72ba8",
        "Content-Type": "application/json"
    }
    
    payload = {
        "body": {"type": "doc", "content": doc_content},
        "settings": {"autoPublish": True, "tags": tags}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        if result.get('code') == 200 or 'noteId' in result:
            note_id = result.get('noteId') or result.get('data', {}).get('note', {}).get('id')
            return {"success": True, "note_id": note_id, "url": f"https://note.mowen.cn/detail/{note_id}"}
        else:
            return {"success": False, "error": result.get('message', 'Unknown error')}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """主函数 - 使用传入的 markdown 文件"""
    
    if len(sys.argv) < 2:
        print("❌ 请提供 markdown 文件路径")
        print("用法: python3 publish_to_mowen.py <report.md>")
        sys.exit(1)
    
    report_file = sys.argv[1]
    
    # 读取传入的报告文件
    with open(report_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 提取标题（第一行）
    title = "A股短线情绪研判"
    first_line = markdown_content.split('\n')[0]
    if first_line.startswith('# '):
        title = first_line[2:].strip()
    
    print(f"✅ 读取报告: {report_file}")
    print(f"✅ 标题: {title}")
    
    # 发布到墨问
    result = publish_to_mowen(title=title, content=markdown_content, tags=["短线情绪", "A股分析"])
    
    if result['success']:
        print(f"✅ 发布成功")
        print(f"   链接: {result['url']}")
        
        # 保存链接到数据库
        conn = sqlite3.connect('/root/.openclaw/workspace/stock/dx/data/duanxian.db')
        cursor = conn.cursor()
        # 从标题中提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
        if date_match:
            report_date = date_match.group(1)
            cursor.execute("UPDATE market_sentiment SET mowen_url = ? WHERE date = ?", (result['url'], report_date))
            conn.commit()
            print(f"✅ 链接已保存到数据库 ({report_date})")
        conn.close()
    else:
        print(f"❌ 发布失败: {result['error']}")

if __name__ == "__main__":
    main()
