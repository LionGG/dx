#!/usr/bin/env python3
"""
时区工具 - 统一使用东八区时间
"""

from datetime import datetime, timedelta

# 东八区时区 (UTC+8)
TZ_OFFSET = 8

def now():
    """获取当前东八区时间"""
    return datetime.utcnow() + timedelta(hours=TZ_OFFSET)

def today_str():
    """获取今天日期字符串（东八区）"""
    return (datetime.utcnow() + timedelta(hours=TZ_OFFSET)).strftime('%Y-%m-%d')

def now_str(format='%Y-%m-%d %H:%M:%S'):
    """获取当前时间字符串（东八区）"""
    return (datetime.utcnow() + timedelta(hours=TZ_OFFSET)).strftime(format)

def utc_to_shanghai(utc_dt):
    """UTC时间转换为东八区时间"""
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(TZ_SHANGHAI)

if __name__ == '__main__':
    print(f"当前东八区时间: {now_str()}")
    print(f"今天日期: {today_str()}")
