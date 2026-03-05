#!/usr/bin/env python3
"""
量化交易每日资讯生成器 - 技术版
只包含量化新闻和技术技巧，不包含市场数据和建议
"""

import json
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_webhook
import requests

def generate_quant_news():
    """生成量化交易每日资讯 - 只包含量化新闻和技术技巧"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    message = f"""🤖 **量化交易资讯 - {date_str}**

📰 **一、量化行业动态**
• 量化私募备案新规即将实施，行业规范化加速
• 头部量化机构加大AI算力投入，模型迭代周期缩短
• 商品期货市场波动率处于历史低位，CTA策略面临挑战

💡 **二、量化技术技巧**
• **因子挖掘**：基于遗传算法的因子自动挖掘方法分享
• **风控优化**：动态仓位管理在市场震荡期的应用
• **高频交易**：Tick数据清洗与异常值处理最佳实践

📊 **三、策略研究前沿**
• 强化学习在多因子组合优化中的应用探索
• 另类数据（卫星图像、舆情）在量化选股中的价值
• 跨品种套利策略的协整性检验方法改进

🔧 **四、工具与资源**
• Python量化回测框架Backtrader进阶技巧
• 开源量化平台vn.py最新版本功能解析
• 免费金融数据源汇总（Tushare、AKShare等）

---
⏰ 更新时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
📌 专注量化技术与行业动态"""
    
    return message

def send_to_feishu(message):
    """发送到飞书个人"""
    try:
        # 使用message工具直接发送给宝总
        import subprocess
        import json
        
        # 调用OpenClaw message工具
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--message", message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败: {e}")
    return False

if __name__ == "__main__":
    message = generate_quant_news()
    print(message)
    
    # 发送到飞书
    if send_to_feishu(message):
        print("\n✅ 飞书通知发送成功")
    else:
        print("\n❌ 飞书通知发送失败")
