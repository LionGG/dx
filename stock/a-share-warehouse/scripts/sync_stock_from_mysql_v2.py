#!/usr/bin/env python3
"""
个股数据同步 - 从MySQL获取增量数据

自动补全最近缺失的数据
"""

import sqlite3
import pymysql
from datetime import datetime, timedelta
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'akshare_full.db')

# 导入飞书推送模块
sys.path.insert(0, SCRIPT_DIR)
from feishu_notifier import send_to_feishu_group

# 导入交易日判断工具
sys.path.insert(0, SCRIPT_DIR)
from trading_date import is_trading_date
sys.path.insert(0, SCRIPT_DIR)
from trading_date import is_trading_date

MYSQL_HOST = '82.156.239.131'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '1q2w#E$R'
MYSQL_DB = 'choose_stock'

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

def get_missing_dates(conn, days=5):
    """获取最近缺失数据的交易日"""
    cursor = conn.cursor()
    
    dates_to_check = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        dates_to_check.append(d)
    
    missing_dates = []
    for date in dates_to_check:
        cursor.execute("SELECT COUNT(*) FROM stock_kline WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        if count < 100:  # 少于100只股票认为缺失
            missing_dates.append(date)
    
    return missing_dates

def sync_stock_for_date(sqlite_conn, mysql_cursor, date):
    """同步指定日期的个股数据"""
    log(f"  同步 {date} 数据...")
    
    sqlite_cursor = sqlite_conn.cursor()
    
    # 检查是否已有足够数据
    sqlite_cursor.execute("SELECT COUNT(*) FROM stock_kline WHERE date = ?", (date,))
    existing = sqlite_cursor.fetchone()[0]
    
    if existing > 100:
        log(f"    {date} 数据已存在: {existing} 条，跳过")
        return True
    
    # 从MySQL查询
    mysql_cursor.execute("""
        SELECT trade_date, stock_code, open_price, close_price, high_price, low_price,
               volume, amount, amplitude, pct_chg, price_chg, turnover_rate
        FROM stock_history
        WHERE trade_date = %s
    """, (date,))
    
    rows = mysql_cursor.fetchall()
    
    if len(rows) == 0:
        log(f"    {date} MySQL无数据")
        return False
    
    # 插入SQLite
    inserted = 0
    for row in rows:
        try:
            converted = [
                str(row[0]), str(row[1]), '',
                float(row[2]) if row[2] is not None else None,
                float(row[3]) if row[3] is not None else None,
                float(row[4]) if row[4] is not None else None,
                float(row[5]) if row[5] is not None else None,
                float(row[6]) if row[6] is not None else None,
                float(row[7]) if row[7] is not None else None,
                float(row[8]) if row[8] is not None else None,
                float(row[9]) if row[9] is not None else None,
                float(row[10]) if row[10] is not None else None,
                float(row[11]) if row[11] is not None else None
            ]
            
            sqlite_cursor.execute('''
                INSERT OR IGNORE INTO stock_kline 
                (date, code, name, open, close, high, low, volume, amount, 
                 amplitude, change_pct, change_amount, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', converted)
            
            if sqlite_cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            continue
    
    sqlite_conn.commit()
    log(f"    {date}: 插入 {inserted} 条")
    return inserted  # 返回插入数量，不是布尔值

def sync_stock_data():
    log(f"开始同步个股数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 连接MySQL
    try:
        mysql_conn = pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DB, connect_timeout=30
        )
        mysql_cursor = mysql_conn.cursor()
    except Exception as e:
        log(f"MySQL连接失败: {e}")
        return False
    
    # 连接SQLite
    sqlite_conn = sqlite3.connect(DB_PATH)
    
    # 获取最近缺失的日期
    missing_dates = get_missing_dates(sqlite_conn, days=5)
    
    if len(missing_dates) == 0:
        log("  最近5天数据已完整，无需同步")
        mysql_conn.close()
        sqlite_conn.close()
        return True
    
    log(f"  需要补全的日期: {missing_dates}")
    
    # 逐个日期同步
    all_success = True
    has_data_dates = 0
    for date in missing_dates:
        inserted = sync_stock_for_date(sqlite_conn, mysql_cursor, date)
        if inserted > 0:
            has_data_dates += 1
        # 非交易日无数据是正常的，不算失败
    
    # 统计最近交易日数据（在关闭连接前）
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    cursor = sqlite_conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM stock_kline WHERE date = ?', (today,))
    today_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM stock_kline WHERE date = ?', (yesterday,))
    yesterday_count = cursor.fetchone()[0]
    
    # 检查缺失的股票
    cursor.execute('SELECT code FROM stock_kline WHERE date = ?', (yesterday,))
    yesterday_codes = set([r[0] for r in cursor.fetchall()])
    cursor.execute('SELECT code FROM stock_kline WHERE date = ?', (today,))
    today_codes = set([r[0] for r in cursor.fetchall()])
    missing = len(yesterday_codes - today_codes)
    
    mysql_conn.close()
    sqlite_conn.close()
    
    log(f"完成，{has_data_dates} 个日期有数据")
    log(f"统计：今天({today}) {today_count} 条，昨天({yesterday}) {yesterday_count} 条")
    if missing > 0:
        log(f"说明：{missing} 只股票今天无数据（可能停牌/退市）")
    
    return True  # 只要没抛异常就算成功

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    log(f"开始同步个股数据 - 目标日期: {today}")
    
    # 判断今天是否为交易日
    if not is_trading_date(today):
        print(f"""⏭️ 个股数据抓取跳过执行 - {today}

原因: 今天是非交易日（周末/节假日）

说明: 定时任务配置为交易日执行（1-5），
      如看到此消息，可能是 cron 配置错误或调休日。
""")
        return 0
    
    # 连接MySQL
    try:
        mysql_conn = pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DB, connect_timeout=30
        )
        mysql_cursor = mysql_conn.cursor()
    except Exception as e:
        log(f"MySQL连接失败: {e}")
        error_text = f"""❌ 个股数据抓取执行失败 - {today}

原因: MySQL连接失败
{e}"""
        print(error_text)
        send_to_feishu_group(error_text)
        return 1
    
    # 连接SQLite
    sqlite_conn = sqlite3.connect(DB_PATH)
    
    # 首先检查MySQL中是否有今天的数据
    mysql_cursor.execute('SELECT COUNT(*) FROM stock_history WHERE trade_date = %s', (today,))
    mysql_today_count = mysql_cursor.fetchone()[0]
    
    if mysql_today_count == 0:
        # 查找MySQL中最新的数据日期
        mysql_cursor.execute('SELECT MAX(trade_date) FROM stock_history')
        latest_mysql_date = mysql_cursor.fetchone()[0]
        
        mysql_conn.close()
        sqlite_conn.close()
        
        result_text = f"""⚠️ 个股数据抓取执行完成 - {today}

状态: 数据源暂无今天数据
MySQL最新数据日期: {latest_mysql_date}
今天({today})数据条数: 0

说明: 数据源尚未更新今天数据，请稍后重试或检查数据源更新机制。"""
        print(result_text)
        send_to_feishu_group(result_text)
        return 0  # 返回0表示正常完成，只是没有新数据
    
    # 获取最近缺失的日期
    missing_dates = get_missing_dates(sqlite_conn, days=5)
    
    if len(missing_dates) == 0:
        log("  最近5天数据已完整，无需同步")
        mysql_conn.close()
        sqlite_conn.close()
        
        # 获取今天数据量
        cursor = sqlite_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM stock_kline WHERE date = ?', (today,))
        today_count = cursor.fetchone()[0]
        
        result_text = f"""✅ 个股数据抓取执行成功 - {today}

状态: 数据已是最新
今天({today})数据: {today_count}条
说明: 无需同步，数据已完整。"""
        print(result_text)
        send_to_feishu_group(result_text)
        return 0
    
    log(f"  需要补全的日期: {missing_dates}")
    
    # 逐个日期同步
    all_success = True
    has_data_dates = 0
    for date in missing_dates:
        inserted = sync_stock_for_date(sqlite_conn, mysql_cursor, date)
        if inserted > 0:
            has_data_dates += 1
        # 非交易日无数据是正常的，不算失败
    
    # 统计最近交易日数据（在关闭连接前）
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    cursor = sqlite_conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM stock_kline WHERE date = ?', (today,))
    today_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM stock_kline WHERE date = ?', (yesterday,))
    yesterday_count = cursor.fetchone()[0]
    
    # 检查缺失的股票
    cursor.execute('SELECT code FROM stock_kline WHERE date = ?', (yesterday,))
    yesterday_codes = set([r[0] for r in cursor.fetchall()])
    cursor.execute('SELECT code FROM stock_kline WHERE date = ?', (today,))
    today_codes = set([r[0] for r in cursor.fetchall()])
    missing = len(yesterday_codes - today_codes)
    
    mysql_conn.close()
    sqlite_conn.close()
    
    log(f"完成，{has_data_dates} 个日期有数据")
    
    # 输出结果并发送飞书通知
    if today_count > 0:
        result_text = f"""✅ 个股数据抓取执行成功 - {today}

同步结果:
- 今天({today}): {today_count}条 ✅
- 昨天({yesterday}): {yesterday_count}条

说明: 数据同步完成，今天数据已更新。（可能有停牌或退市的股票）"""
        print(result_text)
        send_to_feishu_group(result_text)
    else:
        result_text = f"""⚠️ 个股数据抓取执行完成 - {today}

状态: 今天数据未获取到
昨天({yesterday}): {yesterday_count}条

说明: 数据源可能未更新，请检查数据源状态。"""
        print(result_text)
        send_feishu_notification(result_text)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
