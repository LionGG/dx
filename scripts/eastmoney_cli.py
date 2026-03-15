#!/usr/bin/env python3
"""
东方财富 API 命令行工具
使用方式：
  python3 eastmoney_cli.py <command> [options]

Commands:
  search    资讯搜索
  query     金融数据查询
  select    智能选股

Examples:
  python3 eastmoney_cli.py search "贵州茅台最新研报"
  python3 eastmoney_cli.py query "东方财富最新价"
  python3 eastmoney_cli.py select "今日涨幅2%的股票" --page-size 50
"""

import sys
import argparse
import json
from eastmoney_api import EastmoneyAPI

def main():
    parser = argparse.ArgumentParser(
        description='东方财富金融数据工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s search "格力电器机构观点"
  %(prog)s query "贵州茅台财务指标"
  %(prog)s select "市盈率低于20的银行股" --page-size 20
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索金融资讯')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--save', action='store_true', help='保存结果到文件')
    search_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # query 命令
    query_parser = subparsers.add_parser('query', help='查询金融数据')
    query_parser.add_argument('tool_query', help='查询语句')
    query_parser.add_argument('--save', action='store_true', help='保存结果到文件')
    query_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # select 命令
    select_parser = subparsers.add_parser('select', help='智能选股')
    select_parser.add_argument('keyword', help='选股条件')
    select_parser.add_argument('--page-size', type=int, default=20, help='每页数量（默认20）')
    select_parser.add_argument('--page-no', type=int, default=1, help='页码（默认1）')
    select_parser.add_argument('--no-csv', action='store_true', help='不保存CSV')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 初始化 API
    try:
        api = EastmoneyAPI()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return 1
    
    # 执行命令
    if args.command == 'search':
        result = api.search_news(args.query, save=args.save, save_path=args.output)
        print(api.format_news_result(result))
        
    elif args.command == 'query':
        result = api.query_financial(args.tool_query, save=args.save, save_path=args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2)[:3000])
        
    elif args.command == 'select':
        result = api.select_stock(
            args.keyword, 
            page_no=args.page_no, 
            page_size=args.page_size,
            save_csv=not args.no_csv
        )
        print(api.format_stock_result(result))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
