#!/usr/bin/env python3
"""
东方财富 API 集成脚本
支持：资讯搜索、金融数据查询、智能选股

Author: Mint
Date: 2026-03-13
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List

class EastmoneyAPI:
    """东方财富 API 客户端"""
    
    BASE_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            api_key: 东方财富 API Key，如未提供则从环境变量或文件读取
        """
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError("未找到 EASTMONEY_APIKEY，请提供 API Key")
        
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
    
    def _load_api_key(self) -> Optional[str]:
        """从环境变量或文件加载 API Key"""
        # 1. 检查环境变量
        api_key = os.environ.get('EASTMONEY_APIKEY')
        if api_key:
            return api_key
        
        # 2. 检查文件
        key_file = '/root/.openclaw/secrets/eastmoney_apikey'
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip()
        
        # 3. 检查 secrets.json
        secrets_file = '/root/.openclaw/secrets/secrets.json'
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
                for secret in secrets.get('secrets', []):
                    if secret.get('name') == 'eastmoney':
                        for entry in secret.get('entries', []):
                            if entry.get('key') == 'api_key':
                                return entry.get('value')
        
        return None
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送 POST 请求
        
        Args:
            endpoint: API 端点（如 /news-search）
            data: 请求数据
            
        Returns:
            API 响应数据
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'请求失败: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'解析响应失败: {str(e)}'}
    
    def search_news(self, query: str, save: bool = False, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        搜索金融资讯
        
        Args:
            query: 搜索关键词，如 "格力电器最新研报"
            save: 是否保存结果到文件
            save_path: 保存路径（默认保存到工作目录）
            
        Returns:
            搜索结果
            
        Examples:
            >>> api.search_news("贵州茅台机构观点")
            >>> api.search_news("商业航天板块近期新闻")
        """
        endpoint = "/news-search"
        data = {'query': query}
        
        result = self._post(endpoint, data)
        
        # 保存结果
        if save and 'error' not in result:
            if not save_path:
                timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'/root/.openclaw/workspace/data/eastmoney_news_{timestamp}.json'
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            result['saved_to'] = save_path
        
        return result
    
    def query_financial(self, tool_query: str, save: bool = False, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        查询金融数据
        
        Args:
            tool_query: 查询语句，如 "东方财富最新价"
            save: 是否保存结果到文件
            save_path: 保存路径
            
        Returns:
            查询结果
            
        Examples:
            >>> api.query_financial("东方财富最新价")
            >>> api.query_financial("贵州茅台财务指标")
            >>> api.query_financial("沪深300指数成分")
        """
        endpoint = "/query"
        data = {'toolQuery': tool_query}
        
        result = self._post(endpoint, data)
        
        if save and 'error' not in result:
            if not save_path:
                timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
                query_clean = tool_query.replace(' ', '_').replace('/', '_')[:20]
                save_path = f'/root/.openclaw/workspace/data/eastmoney_data_{query_clean}_{timestamp}.json'
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            result['saved_to'] = save_path
        
        return result
    
    def select_stock(self, keyword: str, page_no: int = 1, page_size: int = 20, 
                     save_csv: bool = True, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        智能选股
        
        Args:
            keyword: 选股条件，如 "今日涨幅2%的股票"
            page_no: 页码（从1开始）
            page_size: 每页数量（默认20）
            save_csv: 是否保存为 CSV
            save_path: CSV 保存路径
            
        Returns:
            选股结果
            
        Examples:
            >>> api.select_stock("今日涨幅2%的股票")
            >>> api.select_stock("市盈率低于20的银行股", page_size=50)
            >>> api.select_stock("创业板市值大于100亿的股票")
        """
        endpoint = "/stock-screen"
        data = {
            'keyword': keyword,
            'pageNo': page_no,
            'pageSize': page_size
        }
        
        result = self._post(endpoint, data)
        
        # 保存为 CSV
        if save_csv and 'error' not in result:
            data_list = result.get('data', {}).get('data', {}).get('result', {}).get('dataList', [])
            columns = result.get('data', {}).get('data', {}).get('result', {}).get('columns', [])
            
            if data_list and columns:
                if not save_path:
                    timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
                    keyword_clean = keyword.replace(' ', '_').replace('/', '_')[:20]
                    save_path = f'/root/.openclaw/workspace/data/eastmoney_stocks_{keyword_clean}_{timestamp}.csv'
                
                import csv
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    headers = [col.get('title', col.get('key', '')) for col in columns]
                    writer.writerow(headers)
                    # 写入数据
                    keys = [col.get('key', '') for col in columns]
                    for row in data_list:
                        writer.writerow([row.get(k, '') for k in keys])
                
                result['csv_saved_to'] = save_path
        
        return result
    
    def format_news_result(self, result: Dict[str, Any]) -> str:
        """格式化资讯搜索结果为文本"""
        if 'error' in result:
            return f"❌ 查询失败: {result['error']}"
        
        lines = []
        lines.append("📰 资讯搜索结果")
        lines.append("-" * 50)
        
        # 这里根据实际返回结构调整
        lines.append(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
        
        return '\n'.join(lines)
    
    def format_stock_result(self, result: Dict[str, Any]) -> str:
        """格式化选股结果为文本"""
        if 'error' in result:
            return f"❌ 选股失败: {result['error']}"
        
        data = result.get('data', {}).get('data', {})
        total = data.get('result', {}).get('total', 0)
        data_list = data.get('result', {}).get('dataList', [])
        
        lines = []
        lines.append(f"📊 智能选股结果 (共 {total} 只)")
        lines.append("-" * 50)
        
        for i, stock in enumerate(data_list[:10], 1):  # 只显示前10只
            code = stock.get('SECURITY_CODE', 'N/A')
            name = stock.get('SECURITY_SHORT_NAME', 'N/A')
            price = stock.get('NEWEST_PRICE', 'N/A')
            chg = stock.get('CHG', 'N/A')
            lines.append(f"{i}. {name}({code}) 最新价:{price} 涨跌幅:{chg}%")
        
        if len(data_list) > 10:
            lines.append(f"... 还有 {len(data_list) - 10} 只股票")
        
        if 'csv_saved_to' in result:
            lines.append(f"\n📁 CSV已保存: {result['csv_saved_to']}")
        
        return '\n'.join(lines)


# 便捷函数（全局实例）
_api_instance = None

def get_api() -> EastmoneyAPI:
    """获取 API 实例（单例模式）"""
    global _api_instance
    if _api_instance is None:
        _api_instance = EastmoneyAPI()
    return _api_instance


def search_news(query: str, save: bool = False) -> Dict[str, Any]:
    """搜索资讯（便捷函数）"""
    return get_api().search_news(query, save=save)


def query_financial(tool_query: str, save: bool = False) -> Dict[str, Any]:
    """查询金融数据（便捷函数）"""
    return get_api().query_financial(tool_query, save=save)


def select_stock(keyword: str, page_size: int = 20, save_csv: bool = True) -> Dict[str, Any]:
    """智能选股（便捷函数）"""
    return get_api().select_stock(keyword, page_size=page_size, save_csv=save_csv)


if __name__ == '__main__':
    # 测试
    print("🦞 东方财富 API 客户端")
    print("-" * 50)
    
    try:
        api = EastmoneyAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"   API Key: {api.api_key[:20]}...")
        
        # 测试选股
        print("\n📊 测试选股: '今日涨幅2%的股票'")
        result = api.select_stock("今日涨幅2%的股票", page_size=5)
        print(api.format_stock_result(result))
        
    except Exception as e:
        print(f"❌ 错误: {e}")
