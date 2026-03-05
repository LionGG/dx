#!/usr/bin/env python3
"""
生成线上部署版本 - 基于本地版本，仅分离数据
"""

import json
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('/root/.openclaw/workspace/stock/duanxianxia_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_production():
    """生成线上版本 - 基于本地版本修改"""
    
    # 读取本地版本
    with open('/root/.openclaw/workspace/stock/web/index-local.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 获取数据
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM market_sentiment 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    market_data = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT date, phase, action, summary, mowen_link 
        FROM daily_reports 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    daily_reports_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # 生成 data.json（全部数据）
    api_data = {
        'version': 'full-v1',
        'market_data': market_data,
        'daily_reports': daily_reports_list
    }
    
    data_json = json.dumps(api_data, ensure_ascii=False, separators=(',', ':'))
    with open('/root/.openclaw/workspace/stock/web/data.json', 'w', encoding='utf-8') as f:
        f.write(data_json)
    
    print(f'✅ data.json: {len(data_json)} bytes ({len(data_json)/1024:.1f} KB)')
    
    # 修改 HTML：
    # 1. 将 marketData 改为空数组
    # 2. 将 dailyReports 改为空对象  
    # 3. 在 initApp 调用前添加数据加载
    
    import re
    
    # 替换 marketData 定义为空数组
    html = re.sub(
        r'const marketData = \[.*?\];',
        'let marketData = [];',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # 替换 dailyReports 定义为空对象
    html = re.sub(
        r'const dailyReports = \{.*?\};',
        'const dailyReports = {};',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # 找到 initApp() 调用，在它之前插入数据加载
    # 将 initApp() 替换为数据加载后再 init
    html = html.replace(
        'initApp();',
        '''// 线上版本：异步加载数据后再初始化
        async function loadDataAndInit() {
            try {
                const res = await fetch('data.json?t=' + Date.now());
                const data = await res.json();
                if (data.market_data) {
                    marketData = data.market_data;
                }
                if (data.daily_reports) {
                    data.daily_reports.forEach(r => dailyReports[r.date] = r);
                }
                // 数据加载完成后再初始化
                initApp();
            } catch (e) {
                console.error('数据加载失败:', e);
                document.body.innerHTML = '<div style="text-align:center;padding:50px;color:#f85149;">数据加载失败，请刷新重试</div>';
            }
        }
        loadDataAndInit();'''
    )
    
    # 保存
    with open('/root/.openclaw/workspace/stock/web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ index.html: {len(html)} bytes ({len(html)/1024:.1f} KB)')
    
    return True

if __name__ == '__main__':
    generate_production()
