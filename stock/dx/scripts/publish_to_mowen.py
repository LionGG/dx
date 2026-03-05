#!/usr/bin/env python3
"""
发布到墨问模块
优化 markdown 格式转换为墨问 doc 格式
"""

import requests
import json

def markdown_to_mowen_doc(markdown_text):
    """Convert markdown to Mowen doc format - 最终优化版"""
    lines = markdown_text.split('\n')
    content = []
    
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        
        # 跳过分割线 ---
        if s == '---' or s.startswith('---'):
            continue
        
        # 一级标题 - 不加空行，去掉#，去掉**，但要加粗
        if s.startswith('# '):
            title_text = s[2:].replace('**', '')
            content.append({
                "type": "paragraph",
                "content": [{
                    "type": "text",
                    "text": title_text,
                    "marks": [{"type": "bold"}]
                }]
            })
        # 二级标题 - 前面加空行，去掉##，去掉**
        elif s.startswith('## '):
            title_text = s[3:].replace('**', '')
            content.append({"type": "paragraph", "content": []})  # 前面加空行
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": title_text}]
            })
        # 三级标题 - 前面加空行，去掉###，去掉**
        elif s.startswith('### '):
            title_text = s[4:].replace('**', '')
            content.append({"type": "paragraph", "content": []})  # 前面加空行
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": title_text}]
            })
        # 四级标题 - 前面加空行，去掉####，去掉**
        elif s.startswith('#### '):
            title_text = s[5:].replace('**', '')
            content.append({"type": "paragraph", "content": []})  # 前面加空行
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": title_text}]
            })
        # 列表项 - 去掉**
        elif s.startswith('- '):
            text = s[2:].replace('**', '')
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": "• " + text}]
            })
        # 普通段落 - 去掉**
        else:
            text = s.replace('**', '')
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": text}]
            })
    
    return content

def publish_to_mowen(title, content, tags=None, auto_publish=True):
    """
    发布 markdown 内容到墨问
    
    Args:
        title: 笔记标题
        content: Markdown 内容
        tags: 标签列表（默认: ["分析报告"]）
        auto_publish: 是否公开（默认: True）
    
    Returns:
        dict: {"success": bool, "note_id": str, "url": str, "error": str}
    """
    if tags is None:
        tags = ["分析报告"]
    
    # 转换 markdown 为墨问 doc 格式
    doc_content = markdown_to_mowen_doc(content)
    
    # 调用墨问 API
    url = "https://open.mowen.cn/api/open/api/v1/note/create"
    headers = {
        "Authorization": "Bearer ijbrCOAwgLnp9Vu5kdZhw59hUfX72ba8",
        "Content-Type": "application/json"
    }
    
    payload = {
        "body": {
            "type": "doc",
            "content": doc_content
        },
        "settings": {
            "autoPublish": auto_publish,
            "tags": tags
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        if result.get('code') == 200 or 'noteId' in result:
            note_id = result.get('noteId') or result.get('data', {}).get('note', {}).get('id')
            return {
                "success": True,
                "note_id": note_id,
                "url": f"https://note.mowen.cn/detail/{note_id}"
            }
        else:
            return {
                "success": False,
                "error": result.get('message', 'Unknown error')
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
