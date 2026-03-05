#!/usr/bin/env python3
"""
抖音用户视频监控脚本
监控账号: 1220387595
频率: 每2小时检查一次
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace')

import requests
from bs4 import BeautifulSoup

# 配置
DOUYIN_USER_ID = "1220387595"
DOUYIN_USER_URL = f"https://www.douyin.com/user/{DOUYIN_USER_ID}"
STATE_FILE = Path("/root/.openclaw/workspace/douyin_monitor/state.json")
DATA_DIR = Path("/root/.openclaw/workspace/douyin_monitor")

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)


def load_state():
    """加载上次监控状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_check": None,
        "latest_video_time": None,
        "processed_videos": []
    }


def save_state(state):
    """保存监控状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def fetch_user_videos():
    """
    获取用户主页视频列表
    返回: [(video_id, title, publish_time, video_url), ...]
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.douyin.com/',
    }
    
    try:
        response = requests.get(DOUYIN_USER_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析页面
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试从页面中提取视频数据
        import re
        videos = []
        
        # 查找包含视频数据的 script
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'SSR_HYDRATED_DATA' in script.string:
                match = re.search(r'window\._SSR_HYDRATED_DATA\s*=\s*({.*?})<', script.string)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        video_list = extract_videos_from_data(data)
                        videos.extend(video_list)
                    except json.JSONDecodeError:
                        pass
        
        # 如果上面的方法失败，尝试从 HTML 中直接提取
        if not videos:
            videos = extract_videos_from_html(soup)
        
        return videos
        
    except Exception as e:
        print(f"获取视频列表失败: {e}")
        return []


def extract_videos_from_data(data):
    """从 JSON 数据中提取视频信息"""
    videos = []
    try:
        user_module = data.get('user', {}).get('user', {})
        video_list = user_module.get('videoList', [])
        
        for video in video_list:
            video_id = video.get('awemeId', '')
            title = video.get('desc', '')
            create_time = video.get('createTime', 0)
            video_url = f"https://www.douyin.com/video/{video_id}"
            
            publish_time = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
            videos.append((video_id, title, publish_time, video_url))
    except Exception as e:
        print(f"解析视频数据失败: {e}")
    
    return videos


def extract_videos_from_html(soup):
    """从 HTML 中直接提取视频信息（备用方案）"""
    videos = []
    video_cards = soup.find_all('div', {'data-e2e': 'user-post-item'})
    
    for card in video_cards:
        try:
            link = card.find('a', href=True)
            if not link:
                continue
            
            video_url = link['href']
            if not video_url.startswith('http'):
                video_url = 'https://www.douyin.com' + video_url
            
            video_id = video_url.split('/')[-1].split('?')[0]
            
            title_elem = card.find('div', {'class': 'title'})
            title = title_elem.text.strip() if title_elem else ''
            
            time_elem = card.find('span', {'class': 'time'})
            publish_time = time_elem.text.strip() if time_elem else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            videos.append((video_id, title, publish_time, video_url))
        except Exception:
            continue
    
    return videos


def check_new_videos(videos, state):
    """检查是否有新视频"""
    new_videos = []
    latest_time_str = state.get('latest_video_time')
    
    for video_id, title, publish_time, video_url in videos:
        if video_id in state.get('processed_videos', []):
            continue
        
        if latest_time_str:
            try:
                current_time = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                latest_time = datetime.strptime(latest_time_str, '%Y-%m-%d %H:%M:%S')
                
                if current_time <= latest_time:
                    continue
            except ValueError:
                pass
        
        new_videos.append((video_id, title, publish_time, video_url))
    
    return new_videos


def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始监控抖音账号: {DOUYIN_USER_ID}")
    
    # 加载状态
    state = load_state()
    print(f"上次检查: {state.get('last_check', '无')}")
    print(f"最新视频时间: {state.get('latest_video_time', '无')}")
    
    # 获取视频列表
    videos = fetch_user_videos()
    print(f"获取到 {len(videos)} 个视频")
    
    if not videos:
        print("未获取到视频，可能需要登录或页面结构变化")
        return
    
    # 检查新视频
    new_videos = check_new_videos(videos, state)
    print(f"发现 {len(new_videos)} 个新视频")
    
    if new_videos:
        # 更新状态
        for video_id, title, publish_time, video_url in new_videos:
            state['processed_videos'].append(video_id)
            
            # 更新最新视频时间
            if not state['latest_video_time'] or publish_time > state['latest_video_time']:
                state['latest_video_time'] = publish_time
        
        # 发送通知
        print("\n" + "="*50)
        print("新视频列表:")
        for video_id, title, publish_time, video_url in new_videos:
            print(f"\n📹 {title[:50]}...")
            print(f"⏰ {publish_time}")
            print(f"🔗 {video_url}")
        print("="*50)
    
    # 保存状态
    state['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_state(state)
    
    print(f"\n[{datetime.now()}] 监控完成")


if __name__ == '__main__':
    main()
