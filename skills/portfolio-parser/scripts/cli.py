#!/usr/bin/env python3
"""
Portfolio Parser CLI
命令行工具，方便直接调用
"""

import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/skills/portfolio-parser/scripts')

from portfolio_parser import (
    parse_portfolio_image, 
    save_to_database, 
    generate_report,
    extract_account_info,
    extract_holdings
)


def main():
    parser = argparse.ArgumentParser(description='持仓图片解析工具')
    parser.add_argument('image_path', help='持仓截图路径')
    parser.add_argument('--account', '-a', required=True, help='账户ID (A/B/C)')
    parser.add_argument('--date', '-d', required=True, help='交易日期 (YYYY-MM-DD)')
    parser.add_argument('--report', '-r', action='store_true', help='生成对比报告')
    
    args = parser.parse_args()
    
    print(f"解析持仓图片: {args.image_path}")
    print(f"账户: {args.account}, 日期: {args.date}")
    
    # 注意：实际解析需要AI视觉，这里只是框架
    # 实际使用时，AI会读取图片并调用以下函数处理
    
    if args.report:
        report = generate_report(args.account, args.date)
        print(report)


if __name__ == '__main__':
    main()
