# 网页截图Skill

## 方法：Playwright截图

### 安装依赖
```bash
pip3 install playwright
playwright install chromium
playwright install-deps chromium  # 安装系统依赖
```

### 基本用法

#### 截图整个网页
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.goto('https://www.example.com')
    page.screenshot(path='screenshot.png')
    browser.close()
```

#### 截图指定元素
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('https://www.example.com')
    page.wait_for_load_state('networkidle')
    
    # 等待元素渲染
    element = page.locator('.target-element')
    element.wait_for(state='visible')
    
    # 截图元素
    element.screenshot(path='element.png')
    browser.close()
```

#### 截图本地HTML文件
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    # 加载本地文件
    page.goto('file:///path/to/index.html')
    page.wait_for_load_state('networkidle')
    
    # 等待图表渲染（关键！）
    page.wait_for_timeout(5000)
    
    # 截图
    page.screenshot(path='local.png')
    browser.close()
```

### 关键要点

1. **等待页面加载**：`page.wait_for_load_state('networkidle')`
2. **等待元素可见**：`element.wait_for(state='visible')`
3. **等待渲染完成**：`page.wait_for_timeout(5000)`（图表等动态内容需要）
4. **设置视口大小**：`viewport={'width': 1920, 'height': 1080}`

### 常见问题

| 问题 | 解决 |
|------|------|
| 缺少libasound.so.2 | `apt-get install libasound2` |
| 图表渲染不完整 | 增加等待时间 `wait_for_timeout(5000)` |
| 元素找不到 | 使用`wait_for(state='visible')` |

---
记录时间：2026-02-26
