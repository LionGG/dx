#!/bin/bash
# Skill 推荐脚本 - A+B 组合方案
# 执行时间: 每周六/日 22:30
# 内容来源: 1.热门清单更新检查  2.国内社区AI搜索推荐

REPORT_FILE="/tmp/skill_recommendation.txt"
DT=$(date '+%Y-%m-%d')
HAS_CONTENT=false

echo "📦 本周 Skill 推荐 - ${DT}" > $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# ========== 热门 Skill 清单（维护列表） ==========
# 分类：飞书、股票金融、浏览器、天气、实用工具
POPULAR_SKILLS=(
    # 飞书系列
    "feishu-doc:飞书文档操作"
    "feishu-sheets:飞书表格操作" 
    "feishu-wiki:飞书知识库"
    "feishu-drive:飞书云空间"
    "feishu-messaging:飞书消息发送"
    # 股票金融
    "stock-data:股票数据获取"
    "market-sentiment:市场情绪分析"
    "trading-assistant:交易助手"
    # 浏览器自动化
    "web-pilot:网页浏览与抓取"
    "browser:浏览器自动化"
    # 天气
    "weather:天气查询"
    # 实用工具
    "summarize:内容摘要"
    "send-email:邮件发送"
    "healthcheck:系统健康检查"
    "clawhub:Skill管理"
)

# ========== 1. 检查热门清单更新 ==========
echo "🔍 正在检查热门 Skill 更新..." >&2

echo "【热门清单更新】" >> $REPORT_FILE
UPDATE_FOUND=false

if command -v clawhub >/dev/null 2>&1; then
    # 获取已安装 skill 列表
    INSTALLED_JSON=$(clawhub list --json 2>/dev/null || echo "{}")
    
    for skill_info in "${POPULAR_SKILLS[@]}"; do
        skill_name="${skill_info%%:*}"
        skill_desc="${skill_info##*:}"
        
        # 检查是否已安装
        current_version=$(echo "$INSTALLED_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for item in data if isinstance(data, list) else []:
        if item.get('name') == '$skill_name':
            print(item.get('version', 'unknown'))
            break
except:
    pass
" 2>/dev/null)
        
        if [ -n "$current_version" ] && [ "$current_version" != "unknown" ]; then
            # 检查是否有更新
            latest_version=$(echo "$INSTALLED_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for item in data if isinstance(data, list) else []:
        if item.get('name') == '$skill_name':
            latest = item.get('latestVersion', '')
            current = item.get('version', '')
            if latest and latest != current:
                print(f'{current} → {latest}')
            break
except:
    pass
" 2>/dev/null)
            
            if [ -n "$latest_version" ]; then
                echo "• $skill_name: $latest_version" >> $REPORT_FILE
                echo "  $skill_desc" >> $REPORT_FILE
                UPDATE_FOUND=true
            fi
        fi
    done
fi

if [ "$UPDATE_FOUND" = false ]; then
    echo "• 热门清单中已安装的 Skill 均为最新版本" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
HAS_CONTENT=true

# ========== 2. AI 搜索国内社区推荐 ==========
echo "🔍 正在搜索国内社区推荐..." >&2

echo "【国内社区推荐】" >> $REPORT_FILE

# 生成搜索提示词
cat > /tmp/skill_search_prompt.txt << 'PROMPT'
请搜索国内社区（知乎、掘金、CSDN、V2EX）本周关于 OpenClaw Skill 的推荐和讨论。

重点关注：
1. 股票/金融投资相关的 Skill（如：A股数据、行情推送、技术分析）
2. 飞书办公自动化 Skill
3. 浏览器自动化/网页抓取 Skill
4. 其他实用、热门的 Skill

输出格式（3-5个即可）：
• skill名称: 一句话功能简介
  来源：知乎/掘金/CSDN/V2EX
  安装：clawhub install skill名称

只推荐有实际使用价值、评价较好的 Skill。
PROMPT

# 使用 AI 生成推荐（控制 Token）
AI_RESULT=$(openclaw agent --message "$(cat /tmp/skill_search_prompt.txt)" --json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    content = data.get('content', '') or data.get('message', '')
    if content:
        # 限制长度，避免过长
        lines = content.split('\\n')
        filtered = []
        for line in lines[:30]:  # 最多30行
            if line.strip():
                filtered.append(line)
        print('\\n'.join(filtered))
    else:
        print('(本周暂无新的社区推荐)')
except Exception as e:
    print(f'(搜索暂时不可用)')
" 2>/dev/null)

if [ -n "$AI_RESULT" ]; then
    echo "$AI_RESULT" >> $REPORT_FILE
else
    echo "• 本周暂无新的社区推荐" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
HAS_CONTENT=true

# ========== 3. 固定热门推荐（保底内容） ==========
echo "【本周热门 Skill 清单】" >> $REPORT_FILE
echo "• feishu-messaging: 飞书消息发送（已验证稳定）" >> $REPORT_FILE
echo "• web-pilot: 网页浏览与数据抓取" >> $REPORT_FILE
echo "• weather: 天气查询与预报" >> $REPORT_FILE
echo "• stock-data: 股票数据获取（A股/港股）" >> $REPORT_FILE
echo "• summarize: 内容摘要与总结" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "---" >> $REPORT_FILE
echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')" >> $REPORT_FILE
echo "下次更新: 周六/周日 22:30" >> $REPORT_FILE
echo "数据来源: 热门清单检查 + 国内社区搜索" >> $REPORT_FILE

# 输出并发送
cat $REPORT_FILE

openclaw message send --channel feishu --target "ou_7b3b64c0a18c735401f4e1d172d4c802" --message "$(cat $REPORT_FILE)" 2>/dev/null

echo ""
echo "✅ Skill 推荐已发送"

exit 0
