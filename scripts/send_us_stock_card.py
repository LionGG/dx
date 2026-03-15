#!/usr/bin/env python3
"""
美股收盘数据卡片发送脚本
"""

import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from feishu_card_wrapper import FeishuCardWrapper

def main():
    """主函数"""
    # 计算昨晚美股日期（美东时间比北京时间慢12-13小时）
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"🌙 正在发送 {date_str} 美股收盘卡片...")
    
    try:
        # 这里应该从数据库或API获取实际数据
        # 现在使用示例数据
        indices = [
            {'name': '道琼斯', 'value': '47,501.00', 'change': -1.20},
            {'name': '纳斯达克', 'value': '19,500.00', 'change': 0.50},
            {'name': '标普500', 'value': '5,400.00', 'change': -0.30}
        ]
        
        highlights = [
            "科技股表现分化",
            "中概股普遍上涨",
            "美联储议息会议临近"
        ]
        
        wrapper = FeishuCardWrapper()
        result = wrapper.send_us_stock_card(date_str, indices, highlights)
        
        print(f"✅ 美股收盘卡片发送成功")
        print(f"📤 消息ID: {result.get('message_id', 'N/A')}")
        return 0
        
    except Exception as e:
        print(f"❌ 发送美股卡片失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
