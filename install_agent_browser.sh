#!/bin/bash
# Agent Browser 安装脚本
# 使用系统自带的 chromium-browser

echo "=== Agent Browser 安装 ==="

# 检查浏览器
if command -v chromium-browser &> /dev/null; then
    BROWSER="chromium-browser"
elif command -v google-chrome &> /dev/null; then
    BROWSER="google-chrome"
elif command -v chromium &> /dev/null; then
    BROWSER="chromium"
else
    echo "❌ 未找到浏览器，正在安装..."
    apt-get update && apt-get install -y chromium-browser 2>/dev/null || apt-get install -y chromium 2>/dev/null
fi

# 创建 Skill 目录
SKILL_DIR="/root/.openclaw/workspace/skills/agent-browser"
mkdir -p "$SKILL_DIR"

# 创建 SKILL.md
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
# Agent Browser

浏览器自动化控制技能，基于 Playwright 或系统浏览器。

## 功能

- 网页数据抓取
- 自动化表单填写
- 截图保存
- 页面元素操作

## 使用

```javascript
// 打开网页
browser({ action: "open", url: "https://example.com" })

// 截图
browser({ action: "screenshot", fullPage: true })

// 点击元素
browser({ action: "act", request: { kind: "click", ref: "按钮文本" } })
```

## 配置

使用系统浏览器: chromium-browser
EOF

# 创建简单的浏览器控制脚本
cat > "$SKILL_DIR/browser.sh" << 'EOF'
#!/bin/bash
# 简单的浏览器控制脚本

URL=$1
ACTION=$2

if [ "$ACTION" = "open" ]; then
    chromium-browser --headless --disable-gpu --dump-dom "$URL" 2>/dev/null
elif [ "$ACTION" = "screenshot" ]; then
    chromium-browser --headless --disable-gpu --screenshot=/tmp/screenshot.png "$URL" 2>/dev/null
    echo "/tmp/screenshot.png"
fi
EOF

chmod +x "$SKILL_DIR/browser.sh"

# 注册到 OpenClaw
echo "✅ Agent Browser 安装完成"
echo "📍 位置: $SKILL_DIR"
echo "🌐 浏览器: $(which chromium-browser 2>/dev/null || which google-chrome 2>/dev/null || which chromium 2>/dev/null)"
