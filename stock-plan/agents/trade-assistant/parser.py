#!/usr/bin/env python3
"""
交易计划解析器
从语音/文字中提取结构化交易信息
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Optional

class TradePlanParser:
    """交易计划解析器"""
    
    # 股票名称到代码的映射（简化版，实际应查询数据库）
    STOCK_MAP = {
        '北方华创': '002371.SZ',
        '中芯国际': '688981.SH',
        '中国船舶': '600150.SH',
        '宁德时代': '300750.SZ',
        '比亚迪': '002594.SZ',
        '茅台': '600519.SH',
        '五粮液': '000858.SZ',
    }
    
    def parse(self, text: str, date: str = None) -> Optional[Dict]:
        """
        解析交易计划文本
        
        示例输入：
        - "明天北方华创突破28就进，2成仓，27止损"
        - "中国船舶跌破25卖出，清仓"
        - "观察宁德时代，等回调到180"
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        result = {
            'id': str(uuid.uuid4())[:8],
            'date': date,
            'created_at': datetime.now().isoformat(),
            'raw_content': text,
            'symbol': None,
            'name': None,
            'action': 'watch',  # 默认观察
            'condition_type': None,
            'condition_value': None,
            'position_pct': None,
            'stop_loss': None,
            'take_profit': None,
            'sentiment_score': 50,
            'certainty_level': 'medium',
            'status': 'active'
        }
        
        # 1. 提取股票名称
        name = self._extract_stock_name(text)
        if name:
            result['name'] = name
            result['symbol'] = self.STOCK_MAP.get(name, 'UNKNOWN')
        
        # 2. 判断操作类型
        result['action'] = self._extract_action(text)
        
        # 3. 提取条件
        condition = self._extract_condition(text)
        if condition:
            result['condition_type'] = condition['type']
            result['condition_value'] = condition['value']
        
        # 4. 提取仓位
        position = self._extract_position(text)
        if position:
            result['position_pct'] = position
        
        # 5. 提取止损
        stop_loss = self._extract_stop_loss(text)
        if stop_loss:
            result['stop_loss'] = stop_loss
        
        # 6. 提取止盈
        take_profit = self._extract_take_profit(text)
        if take_profit:
            result['take_profit'] = take_profit
        
        # 7. 判断确定性级别
        result['certainty_level'] = self._extract_certainty(text)
        
        return result
    
    def _extract_stock_name(self, text: str) -> Optional[str]:
        """提取股票名称"""
        for name in self.STOCK_MAP.keys():
            if name in text:
                return name
        
        # 尝试匹配"XX股份"、"XX科技"等模式
        patterns = [
            r'([\u4e00-\u9fa5]{2,6}(?:股份|科技|医药|生物|电子|软件|芯片|半导体|汽车|银行|证券|保险|地产|航空|船舶| Media|集团))',
            r'([\u4e00-\u9fa5]{2,4}(?:茅|王))',  # 茅台、宁王等
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_action(self, text: str) -> str:
        """判断操作类型"""
        buy_keywords = ['买', '进', '入', '加仓', '建仓', '抄底', '跟进']
        sell_keywords = ['卖', '出', '减仓', '清仓', '止盈', '止损', '割肉']
        
        for kw in buy_keywords:
            if kw in text:
                return 'buy'
        
        for kw in sell_keywords:
            if kw in text:
                return 'sell'
        
        # 观察类关键词
        watch_keywords = ['观察', '关注', '看看', '等', '如果']
        for kw in watch_keywords:
            if kw in text:
                return 'watch'
        
        return 'watch'
    
    def _extract_condition(self, text: str) -> Optional[Dict]:
        """提取条件"""
        # 价格突破
        break_match = re.search(r'(?:突破|站上|超过|大于|≥|>=)\s*(\d+(?:\.\d+)?)', text)
        if break_match:
            return {'type': 'price_break', 'value': float(break_match.group(1))}
        
        # 价格跌破
        below_match = re.search(r'(?:跌破|低于|小于|≤|<=)\s*(\d+(?:\.\d+)?)', text)
        if below_match:
            return {'type': 'price_below', 'value': float(below_match.group(1))}
        
        # 回调到某个价格
        pullback_match = re.search(r'(?:回调|跌到|到|至)\s*(\d+(?:\.\d+)?)', text)
        if pullback_match:
            return {'type': 'price_below', 'value': float(pullback_match.group(1))}
        
        return None
    
    def _extract_position(self, text: str) -> Optional[float]:
        """提取仓位百分比"""
        # 匹配"X成仓"、"X%"、"百分之X"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*成(?:仓|)',
            r'(\d+(?:\.\d+)?)\s*%',
            r'百分之\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*成',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                # "成"是10%，"%"是1%
                if '成' in text and '%' not in text:
                    return value * 10
                return value
        
        # 全仓、半仓、轻仓、重仓
        if '全仓' in text or '满仓' in text:
            return 100
        if '半仓' in text:
            return 50
        if '轻仓' in text:
            return 20
        if '重仓' in text:
            return 80
        
        return None
    
    def _extract_stop_loss(self, text: str) -> Optional[float]:
        """提取止损价"""
        # 止损27、跌破27走、27止损
        patterns = [
            r'止损\s*(\d+(?:\.\d+)?)',
            r'跌破\s*(\d+(?:\.\d+)?)\s*(?:走|卖|出)',
            r'(\d+(?:\.\d+)?)\s*止损',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_take_profit(self, text: str) -> Optional[float]:
        """提取止盈价"""
        patterns = [
            r'止盈\s*(\d+(?:\.\d+)?)',
            r'涨到\s*(\d+(?:\.\d+)?)\s*卖',
            r'(\d+(?:\.\d+)?)\s*止盈',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_certainty(self, text: str) -> str:
        """判断确定性级别"""
        high_keywords = ['肯定', '一定', '必须', '绝对', '满仓', '全仓']
        low_keywords = ['看看', '观察', '可能', '也许', '试试', '如果']
        
        for kw in high_keywords:
            if kw in text:
                return 'high'
        
        for kw in low_keywords:
            if kw in text:
                return 'low'
        
        return 'medium'


# 测试
if __name__ == '__main__':
    parser = TradePlanParser()
    
    test_cases = [
        "明天北方华创突破28就进，2成仓，27止损",
        "中国船舶跌破25卖出，清仓",
        "观察宁德时代，等回调到180",
        "中芯国际必须买，全仓干",
    ]
    
    for text in test_cases:
        print(f"\n输入: {text}")
        result = parser.parse(text)
        if result:
            print(f"解析: {result['name']} {result['action']} 条件{result['condition_value']} 仓位{result['position_pct']}% 止损{result['stop_loss']} 确定性{result['certainty_level']}")
