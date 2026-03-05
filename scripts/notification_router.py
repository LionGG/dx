#!/usr/bin/env python3
"""
智能通知路由模块
根据任务类型和结果选择最佳通知方式
"""

import json
from datetime import datetime

class NotificationRouter:
    """通知路由器"""
    
    # 任务分类
    TASK_CATEGORIES = {
        'trading': ['交易计划分析', '交易截图提醒', '量化交易每日资讯'],
        'data': ['个股数据抓取', 'MA50占比计算', '短线情绪研判'],
        'news': ['AI热点新闻', 'OpenClaw每日资讯'],
        'diary': ['薄荷日记-写作', '薄荷日记-发送'],
    }
    
    # 通知模板
    TEMPLATES = {
        'trading': {
            'success': '⚽ {task_name} 完成\n📊 交易相关任务执行成功\n⏰ {time}',
            'failure': '⚠️ {task_name} 失败\n❌ 交易任务执行异常\n⏰ {time}\n请检查交易相关配置',
        },
        'data': {
            'success': '📊 {task_name} 完成\n✅ 数据任务执行成功\n⏰ {time}',
            'failure': '⚠️ {task_name} 失败\n❌ 数据任务执行异常\n⏰ {time}\n请检查数据源连接',
        },
        'news': {
            'success': '📰 {task_name} 完成\n✅ 资讯已推送\n⏰ {time}',
            'failure': '⚠️ {task_name} 失败\n❌ 资讯推送异常\n⏰ {time}',
        },
        'diary': {
            'success': '📔 {task_name} 完成\n✅ 日记已记录\n⏰ {time}',
            'failure': '⚠️ {task_name} 失败\n❌ 日记记录异常\n⏰ {time}\n请检查日记脚本',
        },
        'default': {
            'success': '✅ {task_name} 完成\n⏰ {time}',
            'failure': '❌ {task_name} 失败\n⏰ {time}',
        },
    }
    
    @classmethod
    def get_category(cls, task_name):
        """获取任务分类"""
        for category, tasks in cls.TASK_CATEGORIES.items():
            if task_name in tasks:
                return category
        return 'default'
    
    @classmethod
    def format_notification(cls, task_name, status, details=None):
        """
        格式化通知消息
        
        Args:
            task_name: 任务名称
            status: 'success' 或 'failure'
            details: 额外详情
        
        Returns:
            str: 格式化后的通知消息
        """
        category = cls.get_category(task_name)
        template = cls.TEMPLATES.get(category, cls.TEMPLATES['default'])
        
        message = template.get(status, template['success'])
        
        data = {
            'task_name': task_name,
            'time': datetime.now().strftime('%H:%M:%S'),
        }
        
        result = message.format(**data)
        
        if details:
            result += f"\n\n📋 详情:\n{details}"
        
        return result
    
    @classmethod
    def should_notify(cls, task_name, status, consecutive_errors=0):
        """
        判断是否发送通知
        
        规则：
        - 成功： diary 类总是通知，其他类按需
        - 失败： 总是通知
        - 连续错误： 升级通知级别
        """
        category = cls.get_category(task_name)
        
        if status == 'failure':
            return True
        
        if category == 'diary':
            return True
        
        if consecutive_errors > 0:
            return True
        
        # 默认成功也通知（可以改为False减少打扰）
        return True

# 便捷函数
def notify(task_name, status='success', details=None, consecutive_errors=0):
    """
    发送智能通知
    
    Example:
        from notification_router import notify
        notify('个股数据抓取', 'success', '同步了 5176 条数据')
        notify('交易计划分析', 'failure', '数据库连接失败', consecutive_errors=1)
    """
    router = NotificationRouter()
    
    if not router.should_notify(task_name, status, consecutive_errors):
        return None
    
    message = router.format_notification(task_name, status, details)
    return message

if __name__ == '__main__':
    # 测试
    print("测试通知路由...")
    print()
    
    print("交易任务成功:")
    print(notify('交易计划分析', 'success'))
    print()
    
    print("数据任务成功:")
    print(notify('个股数据抓取', 'success', '同步了 5176 条数据'))
    print()
    
    print("日记任务成功:")
    print(notify('薄荷日记-写作', 'success'))
    print()
    
    print("交易任务失败:")
    print(notify('交易计划分析', 'failure', '数据库连接超时'))
