#!/usr/bin/env python3
"""
持仓数据查询工具
示例用法:
  python3 query_portfolio.py --account A --date 2026-03-10
  python3 query_portfolio.py --account A --compare 2026-03-03,2026-03-10
  python3 query_portfolio.py --stock 300059 --start 2026-02-24 --end 2026-03-10
"""

import sqlite3
import argparse
from datetime import datetime

DB_PATH = '/root/.openclaw/workspace/stock-plan/data/portfolio.db'

def query_account_snapshot(account_id, trade_date):
    """查询某账户某日的持仓快照"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT account_id, trade_date, total_assets, total_profit, holding_profit, debt, guarantee_ratio
        FROM portfolio_snapshots
        WHERE account_id = ? AND trade_date = ?
    ''', (account_id, trade_date))
    
    row = cursor.fetchone()
    if not row:
        print(f'未找到数据: 账户{account_id}, 日期{trade_date}')
        conn.close()
        return
    
    print(f'\n📊 账户{account_id} - {trade_date} 持仓快照')
    print('-' * 50)
    print(f'总资产: {row[2]/10000:.2f}万')
    print(f'当日盈亏: {row[3]/10000:+.2f}万')
    print(f'持仓盈亏: {row[4]/10000:+.2f}万')
    if row[5]:
        print(f'融资负债: {row[5]/10000:.2f}万')
    if row[6]:
        print(f'担保比例: {row[6]:.2f}%')
    
    # 查询个股明细
    cursor.execute('''
        SELECT stock_code, stock_name, position_pct, market_value, float_profit
        FROM stock_holdings
        WHERE account_id = ? AND trade_date = ?
        ORDER BY position_pct DESC
    ''', (account_id, trade_date))
    
    print('\n📈 个股持仓明细:')
    print(f'{"代码":<10} {"名称":<12} {"仓位":>8} {"市值":>12} {"浮盈":>12}')
    print('-' * 60)
    for row in cursor.fetchall():
        print(f'{row[0]:<10} {row[1]:<12} {row[2]:>7.1f}% {row[3]/10000:>10.1f}万 {row[4]/10000:>+10.1f}万')
    
    conn.close()

def compare_account_snapshots(account_id, dates_str):
    """对比某账户在两个日期的持仓变化"""
    dates = dates_str.split(',')
    if len(dates) != 2:
        print('对比模式需要两个日期，格式: --compare 2026-03-03,2026-03-10')
        return
    
    date1, date2 = dates[0].strip(), dates[1].strip()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询两个日期的数据
    cursor.execute('''
        SELECT trade_date, total_assets, total_profit, holding_profit
        FROM portfolio_snapshots
        WHERE account_id = ? AND trade_date IN (?, ?)
        ORDER BY trade_date
    ''', (account_id, date1, date2))
    
    rows = cursor.fetchall()
    if len(rows) != 2:
        print(f'数据不足，只找到{len(rows)}条记录')
        conn.close()
        return
    
    print(f'\n📊 账户{account_id} 持仓对比: {date1} vs {date2}')
    print('-' * 60)
    
    row1, row2 = rows[0], rows[1]
    
    asset_change = row2[1] - row1[1]
    profit_change = row2[3] - row1[3]
    
    print(f'总资产: {row1[1]/10000:.2f}万 → {row2[1]/10000:.2f}万 ({asset_change/10000:+.2f}万)')
    print(f'持仓盈亏: {row1[3]/10000:.2f}万 → {row2[3]/10000:.2f}万 ({profit_change/10000:+.2f}万)')
    
    # 查询个股变化
    cursor.execute('''
        SELECT h1.stock_code, h1.stock_name, h1.position_pct as pct1, h1.float_profit as profit1,
               h2.position_pct as pct2, h2.float_profit as profit2
        FROM stock_holdings h1
        LEFT JOIN stock_holdings h2 ON h1.stock_code = h2.stock_code 
            AND h1.account_id = h2.account_id AND h2.trade_date = ?
        WHERE h1.account_id = ? AND h1.trade_date = ?
    ''', (date2, account_id, date1))
    
    print('\n📈 个股变化:')
    print(f'{"代码":<10} {"名称":<12} {"仓位变化":>15} {"浮盈变化":>15}')
    print('-' * 60)
    
    for row in cursor.fetchall():
        code, name, pct1, profit1, pct2, profit2 = row
        pct_change = (pct2 or 0) - pct1
        profit_change = (profit2 or 0) - profit1
        print(f'{code:<10} {name:<12} {pct_change:>+14.1f}% {profit_change/10000:>+13.1f}万')
    
    conn.close()

def query_stock_history(stock_code, start_date, end_date):
    """查询某股票在一段时间内的持仓变化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.account_id, h.trade_date, h.position_pct, h.market_value, h.float_profit, h.current_price
        FROM stock_holdings h
        JOIN portfolio_snapshots s ON h.snapshot_id = s.id
        WHERE h.stock_code = ? AND h.trade_date BETWEEN ? AND ?
        ORDER BY h.trade_date, h.account_id
    ''', (stock_code, start_date, end_date))
    
    rows = cursor.fetchall()
    if not rows:
        print(f'未找到股票{stock_code}在{start_date}至{end_date}的数据')
        conn.close()
        return
    
    print(f'\n📈 股票{stock_code} 持仓历史 ({start_date} 至 {end_date})')
    print('-' * 70)
    print(f'{"日期":<12} {"账户":<6} {"仓位":>8} {"市值":>12} {"浮盈":>12} {"现价":>10}')
    print('-' * 70)
    
    for row in rows:
        print(f'{row[1]:<12} {row[0]:<6} {row[2]:>7.1f}% {row[3]/10000:>10.1f}万 {row[4]/10000:>+10.1f}万 {row[5]:>9.2f}')
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='持仓数据查询工具')
    parser.add_argument('--account', '-a', help='账户ID (A/B/C)')
    parser.add_argument('--date', '-d', help='查询日期 (YYYY-MM-DD)')
    parser.add_argument('--compare', '-c', help='对比两个日期 (date1,date2)')
    parser.add_argument('--stock', '-s', help='股票代码')
    parser.add_argument('--start', help='开始日期')
    parser.add_argument('--end', help='结束日期')
    
    args = parser.parse_args()
    
    if args.account and args.date and not args.compare:
        query_account_snapshot(args.account, args.date)
    elif args.account and args.compare:
        compare_account_snapshots(args.account, args.compare)
    elif args.stock and args.start and args.end:
        query_stock_history(args.stock, args.start, args.end)
    else:
        parser.print_help()
        print('\n示例:')
        print('  python3 query_portfolio.py --account A --date 2026-03-10')
        print('  python3 query_portfolio.py --account A --compare 2026-03-03,2026-03-10')
        print('  python3 query_portfolio.py --stock 300059 --start 2026-02-24 --end 2026-03-10')

if __name__ == '__main__':
    main()
