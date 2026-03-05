#!/usr/bin/env python3
"""
交易助手核心模块
提供计划记录、持仓对比、复盘分析功能
"""

import sqlite3
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 数据库路径
DB_PATH = Path('/root/.openclaw/workspace/stock-plan/agents/trade-assistant/trade_notes.db')
PROFILE_PATH = Path('/root/.openclaw/workspace/stock-plan/memory/user_profile.md')

class TradeAssistant:
    """交易助手核心类"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    # ========== 1. 交易计划记录 ==========
    
    def save_plan(self, plan_data: Dict) -> str:
        """保存交易计划"""
        self.cursor.execute('''
            INSERT INTO trade_plans (
                id, date, created_at, raw_content, symbol, name, action,
                condition_type, condition_value, position_pct, stop_loss, take_profit,
                sentiment_score, certainty_level, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plan_data['id'], plan_data['date'], plan_data['created_at'],
            plan_data['raw_content'], plan_data['symbol'], plan_data['name'],
            plan_data['action'], plan_data['condition_type'], plan_data['condition_value'],
            plan_data['position_pct'], plan_data['stop_loss'], plan_data['take_profit'],
            plan_data['sentiment_score'], plan_data['certainty_level'], plan_data['status']
        ))
        self.conn.commit()
        return plan_data['id']
    
    def get_today_plans(self) -> List[Dict]:
        """获取今日计划"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT * FROM trade_plans 
            WHERE date = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (today,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_plan_by_id(self, plan_id: str) -> Optional[Dict]:
        """根据ID获取计划"""
        self.cursor.execute('SELECT * FROM trade_plans WHERE id = ?', (plan_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # ========== 2. 持仓截图处理 ==========
    
    def save_screenshot(self, date: str, image_url: str, parsed_data: Dict) -> str:
        """保存持仓截图识别结果"""
        screenshot_id = f"ss_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.cursor.execute('''
            INSERT INTO position_screenshots (id, date, image_url, parsed_data, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (screenshot_id, date, image_url, json.dumps(parsed_data), datetime.now().isoformat()))
        self.conn.commit()
        return screenshot_id
    
    def get_latest_screenshot(self, date: str = None) -> Optional[Dict]:
        """获取最新持仓截图"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT * FROM position_screenshots 
            WHERE date = ? 
            ORDER BY uploaded_at DESC LIMIT 1
        ''', (date,))
        row = self.cursor.fetchone()
        if row:
            result = dict(row)
            result['parsed_data'] = json.loads(result['parsed_data'])
            return result
        return None
    
    # ========== 3. 执行记录 ==========
    
    def record_execution(self, plan_id: str, executed_at: str, 
                        actual_price: float, actual_position: float,
                        followed_plan: bool, deviation_reason: str = None,
                        screenshot_id: str = None) -> str:
        """记录交易执行"""
        exec_id = f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.cursor.execute('''
            INSERT INTO trade_executions 
            (id, plan_id, executed_at, actual_price, actual_position, followed_plan, deviation_reason, screenshot_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (exec_id, plan_id, executed_at, actual_price, actual_position, 
              followed_plan, deviation_reason, screenshot_id))
        
        # 更新计划状态
        self.cursor.execute('''
            UPDATE trade_plans SET status = 'executed' WHERE id = ?
        ''', (plan_id,))
        
        self.conn.commit()
        return exec_id
    
    def get_today_executions(self) -> List[Dict]:
        """获取今日执行记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT e.*, p.name, p.symbol, p.action 
            FROM trade_executions e
            JOIN trade_plans p ON e.plan_id = p.id
            WHERE date(e.executed_at) = ?
            ORDER BY e.executed_at DESC
        ''', (today,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ========== 4. 复盘记录 ==========
    
    def save_review(self, date: str, raw_content: str, 
                   emotion_tag: str = None, lesson_extracted: str = None,
                   related_plan_id: str = None) -> str:
        """保存复盘记录"""
        review_id = f"review_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.cursor.execute('''
            INSERT INTO trade_reviews 
            (id, date, raw_content, emotion_tag, lesson_extracted, related_plan_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (review_id, date, raw_content, emotion_tag, lesson_extracted, related_plan_id))
        self.conn.commit()
        return review_id
    
    def get_recent_reviews(self, days: int = 7) -> List[Dict]:
        """获取最近复盘记录"""
        since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT * FROM trade_reviews 
            WHERE date >= ? 
            ORDER BY date DESC
        ''', (since,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ========== 5. 计划与执行对比 ==========
    
    def compare_plan_execution(self, date: str = None) -> Dict:
        """对比计划与执行"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 获取当日计划
        self.cursor.execute('''
            SELECT * FROM trade_plans WHERE date = ?
        ''', (date,))
        plans = [dict(row) for row in self.cursor.fetchall()]
        
        # 获取当日执行
        self.cursor.execute('''
            SELECT e.*, p.name FROM trade_executions e
            JOIN trade_plans p ON e.plan_id = p.id
            WHERE date(e.executed_at) = ?
        ''', (date,))
        executions = [dict(row) for row in self.cursor.fetchall()]
        
        # 计算执行率
        plan_count = len(plans)
        exec_count = len(executions)
        execution_rate = (exec_count / plan_count * 100) if plan_count > 0 else 0
        
        # 统计偏差
        deviations = [e for e in executions if not e['followed_plan']]
        
        return {
            'date': date,
            'plan_count': plan_count,
            'execution_count': exec_count,
            'execution_rate': round(execution_rate, 1),
            'deviation_count': len(deviations),
            'plans': plans,
            'executions': executions,
            'deviations': deviations
        }
    
    # ========== 6. 交易模式分析 ==========
    
    def analyze_patterns(self, days: int = 30) -> Dict:
        """分析交易模式"""
        since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 统计各类型偏差
        self.cursor.execute('''
            SELECT deviation_reason, COUNT(*) as count 
            FROM trade_executions 
            WHERE executed_at >= ? AND followed_plan = 0
            GROUP BY deviation_reason
            ORDER BY count DESC
        ''', (since,))
        deviation_patterns = [dict(row) for row in self.cursor.fetchall()]
        
        # 统计情绪标签
        self.cursor.execute('''
            SELECT emotion_tag, COUNT(*) as count 
            FROM trade_reviews 
            WHERE date >= ?
            GROUP BY emotion_tag
            ORDER BY count DESC
        ''', (since,))
        emotion_patterns = [dict(row) for row in self.cursor.fetchall()]
        
        # 计算整体执行率
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN followed_plan = 1 THEN 1 ELSE 0 END) as followed
            FROM trade_executions 
            WHERE executed_at >= ?
        ''', (since,))
        row = self.cursor.fetchone()
        overall_rate = (row['followed'] / row['total'] * 100) if row['total'] > 0 else 0
        
        return {
            'period_days': days,
            'overall_execution_rate': round(overall_rate, 1),
            'deviation_patterns': deviation_patterns,
            'emotion_patterns': emotion_patterns,
            'total_executions': row['total']
        }
    
    # ========== 7. 生成日报 ==========
    
    def generate_daily_summary(self, date: str = None) -> Dict:
        """生成每日汇总"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        comparison = self.compare_plan_execution(date)
        
        summary = {
            'date': date,
            'plan_count': comparison['plan_count'],
            'execution_count': comparison['execution_count'],
            'execution_rate': comparison['execution_rate'],
            'deviation_count': comparison['deviation_count'],
            'summary_text': self._generate_summary_text(comparison),
            'generated_at': datetime.now().isoformat()
        }
        
        # 保存到数据库
        self.cursor.execute('''
            INSERT OR REPLACE INTO daily_summaries 
            (date, plan_count, execution_count, execution_rate, deviation_count, summary_text, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (summary['date'], summary['plan_count'], summary['execution_count'],
              summary['execution_rate'], summary['deviation_count'],
              summary['summary_text'], summary['generated_at']))
        self.conn.commit()
        
        return summary
    
    def _generate_summary_text(self, comparison: Dict) -> str:
        """生成汇总文本"""
        lines = []
        lines.append(f"当日计划: {comparison['plan_count']}条")
        lines.append(f"实际执行: {comparison['execution_count']}条")
        lines.append(f"执行率: {comparison['execution_rate']}%")
        
        if comparison['deviation_count'] > 0:
            lines.append(f"偏差次数: {comparison['deviation_count']}")
            lines.append("偏差原因需复盘记录")
        
        return '\n'.join(lines)


# 便捷函数接口
def get_assistant() -> TradeAssistant:
    """获取交易助手实例"""
    return TradeAssistant()


if __name__ == '__main__':
    # 测试
    assistant = get_assistant()
    
    # 测试获取今日计划
    plans = assistant.get_today_plans()
    print(f"今日计划: {len(plans)}条")
    
    # 测试对比
    comparison = assistant.compare_plan_execution()
    print(f"执行率: {comparison['execution_rate']}%")
    
    assistant.close()
