# 短线情绪研判任务 - 执行检查清单
# 创建时间：2026-03-03
# 用途：每天执行任务前检查，确保不犯错

## 任务执行顺序
1. 任务1：数据抓取 (16:20)
2. 任务2：AI分析 (16:25)
3. 任务3：部署通知 (16:30)

## 关键检查点

### 任务1 - 数据抓取
- [ ] 抓取短线侠数据成功
- [ ] 抓取指数K线成功（创业板成交量已修正/100）
- [ ] 同步MA50成功
- [ ] 发送飞书通知（成功/失败都要通知）

### 任务2 - AI分析
- [ ] 检查数据完整性
- [ ] 启动子代理完成AI分析
- [ ] 发布到墨问（必须公开）
- [ ] 保存到数据库（墨问链接、周期、策略、总结）
- [ ] 发送飞书通知（核心信息+墨问链接）

### 任务3 - 部署通知
- [ ] 检查第二步完成（数据库有墨问链接）
- [ ] 更新HTML
- [ ] 部署到GitHub
- [ ] 截图（左上角情绪图表卡片，等待5秒加载）
- [ ] 发送飞书（文字+截图）

## 截图方法（已验证）
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('file:///root/.openclaw/workspace/stock/dx/web/index.html')
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(5000)  # 等待5秒让图表渲染
    
    chart_container = page.locator('.row').first.locator('.chart-container').first
    chart_container.screenshot(path='sentiment_chart.png')
    browser.close()
```

## 常见错误及解决

### 错误1：创业板成交量多100倍
**原因**：新浪返回的是"手"，已*100转为"股"，但可能又被乘了一次
**解决**：检查数据库，如不对则手动除以100

### 错误2：截图截的是整个网页而非左上角卡片
**原因**：使用了full_page=True或clip参数
**解决**：使用chart_container.screenshot()截取特定元素

### 错误3：截图时卡片还没加载完
**原因**：没有等待图表渲染
**解决**：page.wait_for_timeout(5000)等待5秒

### 错误4：墨问链接是私有的
**原因**：调用publish_to_mowen时auto_publish=False
**解决**：确保auto_publish=True

### 错误5：飞书群没收到图片
**原因**：send_to_feishu_group函数不支持图片
**解决**：使用upload_image上传图片获取image_key，再发送

## 脚本文件位置
- 任务1：/root/.openclaw/workspace/stock/dx/scripts/task1_data_fetch.py
- 任务2：/root/.openclaw/workspace/stock/dx/scripts/task2_analysis.py
- 任务3：/root/.openclaw/workspace/stock/dx/scripts/task3_deploy.py
- 飞书通知：/root/.openclaw/workspace/stock/dx/scripts/feishu_notifier.py
- 墨问发布：/root/.openclaw/workspace/stock/dx/scripts/publish_to_mowen.py

## Prompt模板位置
- /root/.openclaw/workspace/stock/dx/prompt.md

## 详细流程文档
- /root/.openclaw/workspace/stock/dx/TASK_DX_FINAL.md

---
执行口诀：先检查、再执行、后验证
