#!/usr/bin/env python3
"""
Phase 2: 资源优化工具
- 内联小文件 (cache.js < 3KB)
- 压缩内联 JavaScript
- 生成优化后的单文件 HTML
"""

import os
import re
import json

def minify_js(js_content):
    """简单的 JS 压缩：移除注释和多余空白"""
    # 移除单行注释
    js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
    # 移除多行注释
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    # 移除行首行尾空白
    js_content = '\n'.join(line.strip() for line in js_content.split('\n'))
    # 移除空行
    js_content = re.sub(r'\n\s*\n', '\n', js_content)
    # 移除行尾分号前的空格
    js_content = re.sub(r'\s*;\s*', ';', js_content)
    # 移除逗号后的空格
    js_content = re.sub(r',\s+', ',', js_content)
    # 移除冒号后的空格
    js_content = re.sub(r':\s+', ':', js_content)
    # 移除等号后的空格
    js_content = re.sub(r'=\s+', '=', js_content)
    return js_content.strip()

def inline_cache_js(html_content, cache_js_path):
    """将 cache.js 内联到 HTML 中"""
    with open(cache_js_path, 'r', encoding='utf-8') as f:
        cache_js = f.read()
    
    # 压缩 JS
    minified_js = minify_js(cache_js)
    
    # 替换 script src 为内联
    script_tag = f'<script>{minified_js}</script>'
    html_content = html_content.replace(
        '<script src="js/cache.js"></script>',
        script_tag
    )
    
    return html_content

def optimize_for_production(input_html, output_html, cache_js_path):
    """生成生产环境优化的 HTML"""
    with open(input_html, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. 内联 cache.js
    html = inline_cache_js(html, cache_js_path)
    
    # 2. 移除 HTML 注释
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # 3. 压缩内联 CSS（移除多余空白）
    def minify_css_in_html(match):
        css = match.group(1)
        # 移除 CSS 注释
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # 移除多余空白
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s+', '{', css)
        css = re.sub(r';\s+', ';', css)
        css = re.sub(r',\s+', ',', css)
        css = re.sub(r':\s+', ':', css)
        return f'<style>{css}</style>'
    
    html = re.sub(r'<style>(.*?)</style>', minify_css_in_html, html, flags=re.DOTALL)
    
    # 4. 压缩内联 JS（除了已经压缩的 DataCache）
    def minify_js_in_html(match):
        js = match.group(1)
        # 跳过 DataCache（已经压缩过）
        if 'DataCache' in js and 'KEYS' in js[:500]:
            return f'<script>{js}</script>'
        return f'<script>{minify_js(js)}</script>'
    
    html = re.sub(r'<script>(.*?)</script>', minify_js_in_html, html, flags=re.DOTALL)
    
    # 5. 移除多余空行
    html = re.sub(r'\n\s*\n', '\n', html)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    original_size = os.path.getsize(input_html)
    optimized_size = os.path.getsize(output_html)
    savings = original_size - optimized_size
    
    print(f"✓ 优化完成")
    print(f"  原始大小: {original_size:,} bytes ({original_size/1024:.1f} KB)")
    print(f"  优化后: {optimized_size:,} bytes ({optimized_size/1024:.1f} KB)")
    print(f"  节省: {savings:,} bytes ({savings/1024:.1f} KB, {savings/original_size*100:.1f}%)")
    
    return output_html

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, 'web')
    
    input_html = os.path.join(web_dir, 'index.html')
    output_html = os.path.join(web_dir, 'index.optimized.html')
    cache_js = os.path.join(web_dir, 'js', 'cache.js')
    
    optimize_for_production(input_html, output_html, cache_js)
