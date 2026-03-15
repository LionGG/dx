#!/usr/bin/env python3
"""
薄荷日记工作流 - 23:55执行
1. 写作：生成昨日日记
2. 推送：发送飞书卡片
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/scripts')

from datetime import datetime, timedelta
# from feishu_card_wrapper import FeishuCardSender

def get_yesterday_date():
    """获取昨日日期"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def run_write_journal():
    """步骤1：写作日记"""
    print("📖 [步骤1/2] 正在生成日记...")
    try:
        import write_daily_journal
        result = write_daily_journal.main()
        if result == 0:
            print("✅ 日记生成成功")
            return True
        else:
            print("❌ 日记生成失败")
            return False
    except Exception as e:
        print(f"❌ 日记生成异常: {e}")
        return False

def run_send_journal():
    """步骤2：推送日记"""
    print("📤 [步骤2/2] 正在发送日记...")
    try:
        import send_daily_journal_card
        result = send_daily_journal_card.main()
        if result == 0:
            print("✅ 日记发送成功")
            return True
        else:
            print("❌ 日记发送失败")
            return False
    except Exception as e:
        print(f"❌ 日记发送异常: {e}")
        return False

def main():
    """主函数：顺序执行写作+推送"""
    yesterday = get_yesterday_date()
    print(f"🌙 薄荷日记工作流启动 - 生成{yesterday}的日记")
    print("=" * 50)
    
    # 步骤1：写作
    write_ok = run_write_journal()
    if not write_ok:
        print("\n⚠️ 写作失败，跳过推送")
        return 1
    
    print()
    
    # 步骤2：推送
    send_ok = run_send_journal()
    if not send_ok:
        print("\n⚠️ 推送失败")
        return 1
    
    print("\n" + "=" * 50)
    print(f"✅ 日记工作流完成 - {yesterday}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
