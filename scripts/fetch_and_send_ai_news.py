#!/usr/bin/env python3
"""
AI新闻抓取并发送卡片
每天早上8:30执行
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from feishu_card_wrapper import FeishuCardWrapper

def fetch_ai_news():
    """
    抓取AI新闻
    TODO: 实际应从机器之心、量子位等API获取
    """
    # 示例数据，实际应替换为真实抓取逻辑
    return [
        {
            'title': 'OpenAI发布GPT-5预览版',
            'summary': '新一代大模型在推理能力上有显著提升，支持多模态输入输出',
            'source': '机器之心',
            'url': 'https://example.com/1',
            'category': '🤖'
        },
        {
            'title': 'Google Gemini更新多语言支持',
            'summary': '新增20种语言支持，中文理解能力大幅提升',
            'source': '量子位',
            'url': 'https://example.com/2',
            'category': '🌐'
        },
        {
            'title': 'AI芯片市场竞争加剧',
            'summary': '英伟达、AMD、英特尔纷纷推出新一代AI训练芯片',
            'source': 'TechCrunch',
            'url': 'https://example.com/3',
            'category': '💻'
        }
    ]

def main():
    """主函数"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📰 正在获取 {today} AI新闻...")
    
    try:
        # 获取新闻
        news_items = fetch_ai_news()
        
        if not news_items:
            print("⚠️ 无新闻数据，发送提示卡片")
            wrapper = FeishuCardWrapper()
            wrapper.send_system_alert_card(
                'AI新闻获取',
                f"{today} 暂未获取到AI新闻数据",
                'info'
            )
            return 0
        
        # 发送新闻卡片
        wrapper = FeishuCardWrapper()
        result = wrapper.send_ai_news_card(today, news_items)
        
        print(f"✅ AI新闻卡片发送成功")
        print(f"📤 消息ID: {result.get('message_id', 'N/A')}")
        print(f"📊 发送新闻数: {len(news_items)}")
        return 0
        
    except Exception as e:
        print(f"❌ 发送AI新闻卡片失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
