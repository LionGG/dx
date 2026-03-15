# WeChat Article Reader Skill

**用途**: 绕过微信验证，自动获取微信公众号文章内容

---

## 前置要求

1. **安装Playwright**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **确保Chromium已安装**
   ```bash
   playwright install chromium
   ```

---

## 使用方法

### 方法1: 使用脚本（推荐）

```bash
# 运行微信文章获取脚本
python3 ~/.openclaw/workspace/skills/wechat-reader/fetch_wechat.py "https://mp.weixin.qq.com/s/文章ID"
```

### 方法2: 直接执行命令

```bash
# 进入workspace目录
cd ~/.openclaw/workspace

# 运行Python脚本
python3 scripts/fetch_wechat.py
```

---

## 技术原理

1. **使用Playwright启动Chromium**（无头模式）
2. **设置User-Agent**（模拟微信内置浏览器）
3. **访问文章URL**
4. **等待页面加载**
5. **提取文章正文**（通过#js_content选择器）

---

## 关键代码

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
    )
    
    page = context.new_page()
    page.goto(url, wait_until='networkidle')
    
    # 提取文章正文
    article = page.locator('#js_content').inner_text()
    
    browser.close()
```

---

## 注意事项

- **服务器环境**: 必须使用headless模式（无图形界面）
- **User-Agent**: 模拟微信内置浏览器更容易成功
- **等待时间**: 页面加载需要3-5秒
- **选择器**: 微信文章正文在`#js_content`元素中

---

## 故障排除

| 问题 | 解决 |
|------|------|
| BrowserType.launch: TargetClosedError | 检查Chromium是否安装：`playwright install chromium` |
| 无法提取正文 | 检查页面是否加载完成，增加等待时间 |
| 内容为空 | 检查URL是否正确，文章是否存在 |

---

## 文件位置

- **脚本**: `~/.openclaw/workspace/scripts/fetch_wechat.py`
- **Skill文档**: `~/.openclaw/workspace/skills/wechat-reader/SKILL.md`

---

*创建时间: 2026-03-06*
*用途: 自动获取微信公众号文章内容*
