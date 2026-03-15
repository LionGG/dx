#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import sys

def fetch_wechat_article(url, output_file=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/8.0.0',
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(3000)
        
        # 获取标题
        title = page.title()
        
        # 获取完整文章内容
        try:
            article = page.locator('#js_content').inner_text()
        except:
            article = page.content()
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"标题: {title}\n\n")
                f.write(article)
            print(f"文章已保存到: {output_file}")
        else:
            print(f"标题: {title}\n")
            print(article)
        
        browser.close()

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "https://mp.weixin.qq.com/s/TnpxD2Tsbi-x4bxKH-aHsA"
    output = sys.argv[2] if len(sys.argv) > 2 else None
    fetch_wechat_article(url, output)
