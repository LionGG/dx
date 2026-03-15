
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("file:///root/.openclaw/workspace/stock/dx/web/index.html")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        
        # 按文档要求：截取 .chart-container
        chart_container = page.locator(".row").first.locator(".chart-container").first
        chart_container.screenshot(path="/root/.openclaw/workspace/stock/dx/temp/sentiment_chart.png")
        print("✅ 截图成功: sentiment_chart.png")
        
        browser.close()
except Exception as e:
    print(f"❌ 截图失败: {e}")
