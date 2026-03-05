#!/usr/bin/env python3
"""
抖音用户视频监控脚本 - 使用浏览器方式
监控账号: 1220387595
频率: 每2小时检查一次
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 配置
DOUYIN_USER_ID = "1220387595"
DOUYIN_USER_URL = f"https://www.douyin.com/user/{DOUYIN_USER_ID}"
STATE_FILE = Path("/root/.openclaw/workspace/douyin_monitor/state.json")
DATA_DIR = Path("/root/.openclaw/workspace/douyin_monitor")
LOG_FILE = DATA_DIR / "monitor.log"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)


def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')


def load_state():
    """加载上次监控状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_check": None,
        "latest_video_time": None,
        "processed_videos": [],
        "video_history": []
    }


def save_state(state):
    """保存监控状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def parse_video_time(time_str):
    """解析抖音时间格式"""
    # 抖音时间格式可能是：
    # - "2024-01-15 08:30" (标准格式)
    # - "昨天 08:30"
    # - "3天前"
    # - "2024-01-15"
    
    now = datetime.now()
    
    try:
        # 尝试标准格式
        if '-' in time_str and ':' in time_str:
            return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        elif '-' in time_str:
            return datetime.strptime(time_str, '%Y-%m-%d')
    except ValueError:
        pass
    
    # 处理相对时间
    if '昨天' in time_str:
        return now.replace(day=now.day-1)
    elif '天前' in time_str:
        days = int(time_str.replace('天前', '').strip())
        return now.replace(day=now.day-days)
    elif '小时前' in time_str:
        hours = int(time_str.replace('小时前', '').strip())
        return now.replace(hour=now.hour-hours)
    
    return now


def check_new_videos(videos, state):
    """
    检查是否有新视频
    videos: [(video_id, title, publish_time_str, video_url), ...]
    """
    new_videos = []
    latest_time_str = state.get('latest_video_time')
    processed = set(state.get('processed_videos', []))
    
    for video_id, title, publish_time_str, video_url in videos:
        # 如果已经处理过，跳过
        if video_id in processed:
            continue
        
        # 如果有上次记录的时间，比较时间
        if latest_time_str:
            try:
                current_time = datetime.strptime(publish_time_str, '%Y-%m-%d %H:%M:%S')
                latest_time = datetime.strptime(latest_time_str, '%Y-%m-%d %H:%M:%S')
                
                if current_time <= latest_time:
                    continue
            except (ValueError, TypeError):
                # 时间解析失败，当作新视频处理
                pass
        
        new_videos.append((video_id, title, publish_time_str, video_url))
    
    return new_videos


def update_state_with_videos(videos, state):
    """用获取到的视频更新状态"""
    for video_id, title, publish_time, video_url in videos:
        # 添加到已处理列表
        if video_id not in state['processed_videos']:
            state['processed_videos'].append(video_id)
        
        # 更新最新视频时间
        if not state['latest_video_time'] or publish_time > state['latest_video_time']:
            state['latest_video_time'] = publish_time
        
        # 添加到历史记录
        video_record = {
            "id": video_id,
            "title": title,
            "publish_time": publish_time,
            "url": video_url,
            "found_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 避免重复
        existing = [v for v in state['video_history'] if v['id'] == video_id]
        if not existing:
            state['video_history'].append(video_record)
    
    # 限制历史记录数量（保留最近100条）
    state['video_history'] = state['video_history'][-100:]
    
    return state


def format_notification(new_videos):
    """格式化通知消息"""
    if not new_videos:
        return None
    
    message = "🎬 抖音账号有新视频\n\n"
    
    for i, (video_id, title, publish_time, video_url) in enumerate(new_videos, 1):
        message += f"{i}. 📹 {title[:60]}{'...' if len(title) > 60 else ''}\n"
        message += f"   ⏰ {publish_time}\n"
        message += f"   🔗 {video_url}\n\n"
    
    message += f"共 {len(new_videos)} 个新视频"
    
    return message


def main():
    """主函数 - 供外部调用"""
    log(f"开始监控抖音账号: {DOUYIN_USER_ID}")
    
    # 加载状态
    state = load_state()
    log(f"上次检查: {state.get('last_check', '无')}")
    log(f"最新视频时间: {state.get('latest_video_time', '无')}")
    log(f"已处理视频数: {len(state.get('processed_videos', []))}")
    
    return state


def process_videos(videos):
    """处理获取到的视频列表"""
    state = load_state()
    
    log(f"获取到 {len(videos)} 个视频")
    
    if not videos:
        log("警告: 未获取到视频")
        return None
    
    # 检查新视频
    new_videos = check_new_videos(videos, state)
    log(f"发现 {len(new_videos)} 个新视频")
    
    # 更新状态
    state = update_state_with_videos(videos, state)
    
    # 保存状态
    state['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_state(state)
    
    # 生成通知
    if new_videos:
        notification = format_notification(new_videos)
        log("新视频:\n" + notification)
        return notification
    
    log("没有新视频")
    return None


if __name__ == '__main__':
    main()
