#!/usr/bin/env python3
"""
压缩本地预览版并部署
"""

import re

def compress_html(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 压缩 CSS
    # 移除 CSS 注释
    html = re.sub(r'/\*.*?\*/', '', html, flags=re.DOTALL)
    # 压缩 CSS 空白
    html = re.sub(r'\s*\{\s*', '{', html)
    html = re.sub(r'\s*\}\s*', '}', html)
    html = re.sub(r'\s*;\s*', ';', html)
    html = re.sub(r'\s*:\s*', ':', html)
    html = re.sub(r',\s*', ',', html)
    
    # 压缩 JS（简单压缩，保留字符串）
    # 移除 // 注释
    html = re.sub(r'//[^\n]*', '', html)
    # 移除多余空白
    html = re.sub(r'\n\s*\n', '\n', html)
    
    # 压缩 HTML
    # 移除标签间的空白
    html = re.sub(r'>\s+<', '><', html)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    original_size = len(open(input_file, 'rb').read())
    compressed_size = len(open(output_file, 'rb').read())
    
    print(f'✅ {output_file}')
    print(f'   原始: {original_size/1024:.1f} KB')
    print(f'   压缩: {compressed_size/1024:.1f} KB')
    print(f'   减少: {(1-compressed_size/original_size)*100:.1f}%')
    
    return output_file

if __name__ == '__main__':
    compress_html(
        '/root/.openclaw/workspace/stock/web/index-local.html',
        '/root/.openclaw/workspace/stock/web/index.html'
    )
