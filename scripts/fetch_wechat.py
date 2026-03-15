#!/usr/bin/env python3
"""
尝试绕过微信验证获取文章内容
"""
from playwright.sync_api import sync_playwright
import time

def fetch_wechat_article(url):
    with sync_playwright() as p:
        # 启动浏览器（无头模式，服务器环境）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # 创建新页面
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/8.0.0',
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()
        
        # 访问文章
        print(f"正在访问: {url}")
        page.goto(url, wait_until='networkidle')
        
        # 等待页面加载
        time.sleep(3)
        
        # 检查是否需要验证
        if "环境异常" in page.content() or "去验证" in page.content():
            print("检测到验证页面，尝试绕过...")
            
            # 尝试点击验证按钮
            try:
                verify_btn = page.locator('#js_verify')
                if verify_btn.is_visible():
                    print("点击验证按钮...")
                    verify_btn.click()
                    time.sleep(5)
            except:
                print("无法点击验证按钮")
        
        # 获取页面内容
        content = page.content()
        title = page.title()
        
        print(f"页面标题: {title}")
        print(f"内容长度: {len(content)}")
        
        # 尝试提取文章正文
        try:
            # 微信文章正文通常在rich_media_content类中
            article = page.locator('#js_content').inner_text()
            print(f"\n文章正文:\n{article[:2000]}")
        except:
            print("无法提取文章正文")
            print(f"\n页面内容片段:\n{content[:2000]}")
        
        browser.close()

if __name__ == '__main__':
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://mp.weixin.qq.com/s/TnpxD2Tsbi-x4bxKH-aHsA"
    fetch_wechat_article(url)
