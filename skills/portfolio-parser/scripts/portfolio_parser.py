#!/usr/bin/env python3
"""
Portfolio Image Parser
自动解析持仓截图，提取结构化数据并存入数据库
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 数据库路径
DB_PATH = '/root/.openclaw/workspace/stock-plan/data/portfolio.db'


def parse_portfolio_image(image_path: str, account_id: str, trade_date: str) -> Dict:
    """
    解析持仓图片
    
    Args:
        image_path: 图片路径
        account_id: 账户ID (A/B/C)
        trade_date: 交易日期 (YYYY-MM-DD)
    
    Returns:
        解析结果字典
    """
    # 注意：实际使用时，AI会读取图片并提取数据
    # 这里提供结构化处理的框架
    
    result = {
        'image_path': image_path,
        'account_id': account_id,
        'trade_date': trade_date,
        'parsed': False,
        'data': None,
        'error': None
    }
    
    # 实际解析逻辑由AI视觉完成
    # 这里只是数据处理和存储的框架
    
    return result


def extract_account_info(text_content: str) -> Dict:
    """
    从文本内容提取账户信息
    
    Args:
        text_content: AI解析出的文本内容
    
    Returns:
        账户信息字典
    """
    info = {
        'total_assets': None,
        'total_profit': None,
        'holding_profit': None,
        'debt': None,
        'guarantee_ratio': None
    }
    
    # 提取总资产
    match = re.search(r'总资产[：:]\s*([\d,\.]+)', text_content)
    if match:
        info['total_assets'] = parse_amount(match.group(1))
    
    # 提取当日盈亏
    match = re.search(r'当日盈亏[：:]\s*([\+\-]?[\d,\.]+)', text_content)
    if match:
        info['total_profit'] = parse_amount(match.group(1))
    
    # 提取持仓盈亏
    match = re.search(r'持仓盈亏[：:]\s*([\+\-]?[\d,\.]+)', text_content)
    if match:
        info['holding_profit'] = parse_amount(match.group(1))
    
    # 提取融资负债
    match = re.search(r'总负债[：:]\s*([\d,\.]+)', text_content)
    if match:
        info['debt'] = parse_amount(match.group(1))
    
    # 提取担保比例
    match = re.search(r'维持担保比例[：:]\s*([\d\.]+)%?', text_content)
    if match:
        info['guarantee_ratio'] = float(match.group(1))
    
    return info


def extract_holdings(text_content: str) -> List[Dict]:
    """
    从文本内容提取个股持仓
    
    Args:
        text_content: AI解析出的文本内容
    
    Returns:
        持仓列表
    """
    holdings = []
    
    # 按行解析持仓表格
    lines = text_content.split('\n')
    for line in lines:
        # 匹配股票代码（6位数字）
        match = re.search(r'(\d{6})\s+(\S+)\s+([\d\.]+)%?\s+([\d,\.]+)\s+([\+\-]?[\d,\.]+)', line)
        if match:
            holdings.append({
                'stock_code': match.group(1),
                'stock_name': match.group(2),
                'position_pct': float(match.group(3)),
                'market_value': parse_amount(match.group(4)),
                'float_profit': parse_amount(match.group(5))
            })
    
    return holdings


def parse_amount(amount_str: str) -> float:
    """
    解析金额字符串（处理万、万/亿等单位）
    
    Args:
        amount_str: 金额字符串
    
    Returns:
        金额（元）
    """
    amount_str = amount_str.replace(',', '').replace('万', '').replace('亿', '')
    try:
        return float(amount_str) * 10000  # 假设输入是"万"为单位
    except:
        return 0.0


def save_to_database(data: Dict) -> bool:
    """
    保存解析结果到数据库
    
    Args:
        data: 解析后的数据字典
    
    Returns:
        是否成功
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 插入持仓快照
        cursor.execute('''
            INSERT OR REPLACE INTO portfolio_snapshots 
            (account_id, trade_date, total_assets, total_profit, holding_profit, debt, guarantee_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['account_id'],
            data['trade_date'],
            data.get('total_assets'),
            data.get('total_profit'),
            data.get('holding_profit'),
            data.get('debt'),
            data.get('guarantee_ratio')
        ))
        
        snapshot_id = cursor.lastrowid
        
        # 插入个股持仓
        for holding in data.get('holdings', []):
            cursor.execute('''
                INSERT OR REPLACE INTO stock_holdings 
                (snapshot_id, account_id, trade_date, stock_code, stock_name, position_pct, market_value, float_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_id,
                data['account_id'],
                data['trade_date'],
                holding['stock_code'],
                holding['stock_name'],
                holding['position_pct'],
                holding['market_value'],
                holding['float_profit']
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False
    finally:
        conn.close()


def compare_with_yesterday(account_id: str, trade_date: str) -> Dict:
    """
    与昨日持仓对比
    
    Args:
        account_id: 账户ID
        trade_date: 今日日期
    
    Returns:
        对比结果
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取昨日日期
    cursor.execute('''
        SELECT trade_date FROM portfolio_snapshots 
        WHERE account_id = ? AND trade_date < ?
        ORDER BY trade_date DESC LIMIT 1
    ''', (account_id, trade_date))
    
    row = cursor.fetchone()
    if not row:
        return {'error': '无昨日数据'}
    
    yesterday = row[0]
    
    # 获取今日数据
    cursor.execute('''
        SELECT total_assets, total_profit, holding_profit 
        FROM portfolio_snapshots 
        WHERE account_id = ? AND trade_date = ?
    ''', (account_id, trade_date))
    
    today_row = cursor.fetchone()
    if not today_row:
        return {'error': '无今日数据'}
    
    # 获取昨日数据
    cursor.execute('''
        SELECT total_assets, holding_profit 
        FROM portfolio_snapshots 
        WHERE account_id = ? AND trade_date = ?
    ''', (account_id, yesterday))
    
    yesterday_row = cursor.fetchone()
    if not yesterday_row:
        return {'error': '无昨日数据'}
    
    # 计算变化
    asset_change = today_row[0] - yesterday_row[0] if today_row[0] and yesterday_row[0] else 0
    profit_change = today_row[2] - yesterday_row[1] if today_row[2] and yesterday_row[1] else 0
    
    # 获取个股变化
    cursor.execute('''
        SELECT h1.stock_code, h1.stock_name, h1.position_pct as pct1, h1.float_profit as profit1,
               h2.position_pct as pct2, h2.float_profit as profit2
        FROM stock_holdings h1
        LEFT JOIN stock_holdings h2 ON h1.stock_code = h2.stock_code 
            AND h1.account_id = h2.account_id AND h2.trade_date = ?
        WHERE h1.account_id = ? AND h1.trade_date = ?
    ''', (trade_date, account_id, yesterday))
    
    stock_changes = []
    for row in cursor.fetchall():
        code, name, pct1, profit1, pct2, profit2 = row
        stock_changes.append({
            'stock_code': code,
            'stock_name': name,
            'position_change': (pct2 or 0) - pct1,
            'profit_change': (profit2 or 0) - profit1
        })
    
    conn.close()
    
    return {
        'yesterday': yesterday,
        'today': trade_date,
        'asset_change': asset_change,
        'profit_change': profit_change,
        'stock_changes': stock_changes
    }


def generate_report(account_id: str, trade_date: str) -> str:
    """
    生成持仓变化报告
    
    Args:
        account_id: 账户ID
        trade_date: 日期
    
    Returns:
        报告文本
    """
    comparison = compare_with_yesterday(account_id, trade_date)
    
    if 'error' in comparison:
        return f"⚠️ {comparison['error']}"
    
    report = f"""
📊 账户{account_id} - {trade_date} 持仓变化

💰 资产变化: {comparison['asset_change']/10000:+.2f}万
📈 盈亏变化: {comparison['profit_change']/10000:+.2f}万

📋 个股变化:
"""
    
    for change in comparison['stock_changes']:
        report += f"  {change['stock_code']} {change['stock_name']}: "
        report += f"仓位{change['position_change']:+.1f}%, "
        report += f"盈亏{change['profit_change']/10000:+.1f}万\n"
    
    return report


if __name__ == '__main__':
    # 测试
    print("Portfolio Image Parser Skill 已加载")
    print(f"数据库路径: {DB_PATH}")
