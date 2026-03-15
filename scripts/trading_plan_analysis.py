#!/usr/bin/env python3
"""
交易计划分析 - 定时任务版
每天 9:10 执行
"""

import sqlite3
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from feishu_card_wrapper import FeishuCardWrapper

def main():
    try:
        conn = sqlite3.connect('/root/.openclaw/workspace/stock-plan/data/portfolio.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(trade_date) FROM portfolio_snapshots")
        latest_date = cursor.fetchone()[0]
        
        cursor.execute("SELECT account_id, total_assets, total_profit FROM portfolio_snapshots WHERE trade_date = ?", (latest_date,))
        accounts = cursor.fetchall()
        
        cursor.execute("SELECT account_id, stock_code, stock_name, position_pct FROM stock_holdings WHERE trade_date = ? ORDER BY account_id, position_pct DESC", (latest_date,))
        holdings = cursor.fetchall()
        
        conn.close()
        
        # 生成报告
        report_lines = [f"**交易计划分析 | {latest_date}**\n"]
        
        total_assets = sum([a[1] for a in accounts])
        total_profit = sum([a[2] for a in accounts])
        report_lines.append(f"**账户概览：**")
        for acc in accounts:
            report_lines.append(f"• 账户{acc[0]}: {acc[1]/10000:.2f}万 | 当日盈亏 {acc[2]:,.0f}")
        report_lines.append(f"• **合计**: {total_assets/10000:.2f}万 | 当日盈亏 {total_profit:,.0f}\n")
        
        report_lines.append("**持仓明细（仓位排序）：**")
        current_acc = None
        count = 0
        for h in holdings:
            if h[0] != current_acc:
                current_acc = h[0]
                report_lines.append(f"\n**账户{current_acc}：**")
            report_lines.append(f"• {h[1]} {h[2]}: {h[3]}%")
            count += 1
            if count >= 15:
                break
        
        report_lines.append(f"\n**今日交易计划：**")
        report_lines.append(f"• 持仓监控：关注高仓位个股")
        report_lines.append(f"• 风险控制：注意市场波动")
        report_lines.append(f"• 计划执行：按既定策略操作")
        
        report = '\n'.join(report_lines)
        
        wrapper = FeishuCardWrapper()
        result = wrapper.sender.send_simple_card(
            receive_id='ou_7b3b64c0a18c735401f4e1d172d4c802',
            receive_id_type='open_id',
            title=f'📊 交易计划分析 | {latest_date}',
            content=report
        )
        
        print(f"✅ 交易计划分析发送成功")
        print(f"消息ID: {result.get('message_id', 'N/A')}")
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
