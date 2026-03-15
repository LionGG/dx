#!/usr/bin/env python3
"""
强制生成报告 - 绝不使用缓存
每次必须重新查询数据库生成
"""

import sqlite3
from datetime import datetime
import sys

DB_FILE = "/root/.openclaw/workspace/stock/dx/data/duanxian.db"
OUTPUT_FILE = "/root/.openclaw/workspace/stock/dx/temp/report_generated_{date}.md"

def generate_report():
    """强制重新生成报告"""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. 获取最新日期（必须从数据库查，不能硬编码）
    cursor.execute("SELECT MAX(date) FROM market_sentiment")
    latest_date = cursor.fetchone()[0]
    
    if not latest_date:
        print("❌ 无法获取最新日期")
        sys.exit(1)
    
    print(f"✅ 最新日期: {latest_date}")
    
    # 2. 计算星期几（必须用代码计算，不能凭记忆）
    date_obj = datetime.strptime(latest_date, '%Y-%m-%d')
    weekday_cn = ['周一','周二','周三','周四','周五','周六','周日'][date_obj.weekday()]
    print(f"✅ 星期几: {weekday_cn}")
    
    # 3. 获取情绪数据（必须查询，不能编造）
    cursor.execute("""
        SELECT sentiment_index, limit_up, limit_down, up_count, down_count,
               consecutive_height, volume, seal_rate
        FROM market_sentiment WHERE date = ?
    """, (latest_date,))
    
    row = cursor.fetchone()
    if not row:
        print(f"❌ 无法获取 {latest_date} 的情绪数据")
        sys.exit(1)
    
    sentiment, limit_up, limit_down, up_count, down_count, height, volume, seal = row
    print(f"✅ 情绪数据: 指数={sentiment}, 涨停={limit_up}, 跌停={limit_down}")
    
    # 4. 获取指数数据（必须查询，缺失要标注）
    cursor.execute("""
        SELECT index_name, close, amount/100000000 
        FROM index_kline WHERE date = ?
    """, (latest_date,))
    
    index_rows = cursor.fetchall()
    index_data = {}
    for idx_row in index_rows:
        index_data[idx_row[0]] = {'close': idx_row[1], 'amount': idx_row[2]}
    
    if index_data:
        print(f"✅ 指数数据: {list(index_data.keys())}")
    else:
        print("⚠️  指数数据缺失（将在报告中标注）")
    
    # 5. 获取昨日数据做对比
    cursor.execute("SELECT * FROM market_sentiment WHERE date < ? ORDER BY date DESC LIMIT 1", (latest_date,))
    yesterday_row = cursor.fetchone()
    
    conn.close()
    
    # 6. 生成报告（所有数据来自数据库查询）
    report = f"""# A股短线情绪研判 - {latest_date}({weekday_cn})

---

## 一、当日盘面解读

**指数表现：**
"""
    
    if '上证指数' in index_data:
        report += f"- 上证指数: {index_data['上证指数']['close']:.2f}\\n"
    else:
        report += "- 上证指数: 数据缺失\\n"
    
    if '创业板指' in index_data:
        report += f"- 创业板指: {index_data['创业板指']['close']:.2f}\\n"
    else:
        report += "- 创业板指: 数据缺失\\n"
    
    report += f"""
**短线情绪：** 情绪指数{sentiment}分，涨停{limit_up}家，跌停{limit_down}家，连板高度{height}板，封板率{seal}。

**涨跌分布：** 上涨{up_count}家，下跌{down_count}家。

---

## 二、周期定位与演变

**当前阶段：** 根据情绪指数{sentiment}分判断

---

## 三、后市策略应对

**一句话：** 基于当日数据分析...

---

**分析时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**数据完整性：** {'✅ 完整' if index_data else '⚠️ 指数数据缺失'}
"""
    
    # 7. 写入文件（必须新文件，不能用缓存）
    output_path = OUTPUT_FILE.format(date=latest_date)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已生成: {output_path}")
    print("✅ 所有数据来自数据库查询，无编造")
    return output_path, latest_date, weekday_cn

if __name__ == "__main__":
    print("="*60)
    print("强制生成报告 - 绝不使用缓存")
    print("="*60)
    print()
    
    report_path, date, weekday = generate_report()
    
    print()
    print("="*60)
    print(f"报告日期: {date}({weekday})")
    print("="*60)
