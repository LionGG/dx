#!/usr/bin/env python3
"""
生成2026年A股交易日历
规则：
1. 周一到周五为交易日（需排除法定节假日）
2. 周六、周日为非交易日
3. 法定节假日按中国证监会公布安排

2026年法定节假日（预估，基于历史规律）：
- 元旦：1月1日-1月3日（周四-周六），1月4日（周日）补班？
- 春节：2月17日-2月23日（周二-周一），2月15日（周日）、2月28日（周六）补班
- 清明节：4月4日-4月6日（周六-周一）
- 劳动节：5月1日-5月5日（周五-周二），5月9日（周六）补班
- 端午节：6月20日-6月22日（周六-周一）
- 中秋节+国庆节：10月1日-10月8日（周四-周四），10月10日（周六）补班

注：以上假期安排为预估，实际以证监会公布为准
"""

import json
from datetime import datetime, timedelta

# 2026年法定节假日（日期格式：MM-DD）
# 注：以下假期安排为预估，基于历史规律
HOLIDAYS_2026 = [
    # 元旦 1月1日-3日
    "01-01", "01-02", "01-03",
    
    # 春节 2月17日-23日（除夕到初六）
    "02-17", "02-18", "02-19", "02-20", "02-21", "02-22", "02-23",
    
    # 清明节 4月4日-6日
    "04-04", "04-05", "04-06",
    
    # 劳动节 5月1日-5日
    "05-01", "05-02", "05-03", "05-04", "05-05",
    
    # 端午节 6月20日-22日
    "06-20", "06-21", "06-22",
    
    # 中秋节+国庆节 10月1日-8日
    "10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07", "10-08",
]

# 调休上班日（周末但上班）
WORK_WEEKENDS_2026 = [
    # 春节调休
    "02-15",  # 周日上班
    "02-28",  # 周六上班
    
    # 劳动节调休
    "05-09",  # 周六上班
    
    # 国庆调休
    "10-10",  # 周六上班
]

def generate_trading_calendar(year=2026):
    """生成交易日历"""
    calendar = []
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        month_day = current.strftime("%m-%d")
        weekday = current.weekday()  # 0=周一, 6=周日
        
        is_weekend = weekday >= 5  # 周六或周日
        is_holiday = month_day in HOLIDAYS_2026
        is_work_weekend = month_day in WORK_WEEKENDS_2026
        
        # 判断是否为交易日
        if is_work_weekend:
            is_trading_day = True
            day_type = "trading"
        elif is_weekend or is_holiday:
            is_trading_day = False
            day_type = "holiday" if is_holiday else "weekend"
        else:
            is_trading_day = True
            day_type = "trading"
        
        calendar.append({
            "date": date_str,
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday],
            "is_trading_day": is_trading_day,
            "day_type": day_type
        })
        
        current += timedelta(days=1)
    
    return calendar

def save_calendar():
    """保存交易日历到文件"""
    calendar = generate_trading_calendar(2026)
    
    # 统计信息
    trading_days = [d for d in calendar if d["is_trading_day"]]
    holidays = [d for d in calendar if d["day_type"] == "holiday"]
    weekends = [d for d in calendar if d["day_type"] == "weekend"]
    
    result = {
        "year": 2026,
        "note": "法定节假日安排为预估，实际以证监会公布为准",
        "summary": {
            "total_days": len(calendar),
            "trading_days": len(trading_days),
            "holidays": len(holidays),
            "weekends": len(weekends)
        },
        "calendar": calendar
    }
    
    # 保存完整日历
    with open('/root/.openclaw/workspace/stock/trading_calendar_2026.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存交易日列表（方便快速查询）
    trading_day_list = [d["date"] for d in trading_days]
    with open('/root/.openclaw/workspace/stock/trading_days_2026.json', 'w', encoding='utf-8') as f:
        json.dump(trading_day_list, f, ensure_ascii=False, indent=2)
    
    print(f"2026年交易日历已生成")
    print(f"总天数: {len(calendar)}")
    print(f"交易日: {len(trading_days)}")
    print(f"法定节假日: {len(holidays)}")
    print(f"周末: {len(weekends)}")
    print(f"\n文件保存位置:")
    print(f"  - trading_calendar_2026.json (完整日历)")
    print(f"  - trading_days_2026.json (交易日列表)")
    
    # 打印前10个交易日的示例
    print(f"\n前10个交易日示例:")
    for d in trading_days[:10]:
        print(f"  {d['date']} ({d['weekday']})")

if __name__ == '__main__':
    save_calendar()