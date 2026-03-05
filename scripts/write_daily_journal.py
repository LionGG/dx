#!/usr/bin/env python3
"""
薄荷日记写作脚本
生成每日工作日记，记录到 memory/YYYY-MM-DD.md
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
DB_PATH = os.path.join(WORKSPACE, "stock/a-share-warehouse/data/akshare_full.db")
DX_DB_PATH = os.path.join(WORKSPACE, "stock/dx/data/duanxian.db")

def get_chinese_weekday(date_obj):
    """获取中文星期"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[date_obj.weekday()]

def get_date_info():
    """获取日期信息"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    return {
        "today": today.strftime("%Y-%m-%d"),
        "today_cn": f"{today.month}月{today.day}日",
        "yesterday": yesterday.strftime("%Y-%m-%d"),
        "weekday": get_chinese_weekday(today),
        "yesterday_weekday": get_chinese_weekday(yesterday),
    }

def check_existing_journal(date_str):
    """检查日记是否已存在"""
    journal_path = os.path.join(MEMORY_DIR, f"{date_str}.md")
    return os.path.exists(journal_path), journal_path

def get_recent_memory_files(days=3):
    """获取最近几天的记忆文件"""
    files = []
    today = datetime.now()

    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        file_path = os.path.join(MEMORY_DIR, f"{date_str}.md")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                files.append({
                    "date": date_str,
                    "content": content[:2000]  # 只取前2000字
                })

    return files

def get_market_data():
    """获取市场数据摘要"""
    data = {
        "ma50": None,
        "stock_count": None,
    }

    # 获取MA50数据
    try:
        if os.path.exists(DX_DB_PATH):
            conn = sqlite3.connect(DX_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT date, ma50_percent FROM market_sentiment ORDER BY date DESC LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                data["ma50"] = rows
            conn.close()
    except Exception as e:
        print(f"获取MA50数据失败: {e}", file=sys.stderr)

    # 获取个股数据量
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM stock_kline WHERE date = ?", (yesterday,))
            result = cursor.fetchone()
            if result:
                data["stock_count"] = result[0]
            conn.close()
    except Exception as e:
        print(f"获取个股数据失败: {e}", file=sys.stderr)

    return data

def get_cron_status():
    """获取定时任务状态"""
    cron_runs_dir = "/root/.openclaw/cron/runs"
    recent_runs = []

    try:
        if os.path.exists(cron_runs_dir):
            files = sorted(os.listdir(cron_runs_dir), key=lambda x: os.path.getmtime(os.path.join(cron_runs_dir, x)), reverse=True)
            for f in files[:10]:
                file_path = os.path.join(cron_runs_dir, f)
                try:
                    with open(file_path, 'r') as file:
                        for line in file:
                            try:
                                record = json.loads(line.strip())
                                if record.get("action") == "finished":
                                    recent_runs.append({
                                        "jobId": record.get("jobId", "unknown")[:8],
                                        "status": record.get("status", "unknown"),
                                        "summary": record.get("summary", "")[:50],
                                        "ts": record.get("ts", 0)
                                    })
                                    break
                            except:
                                continue
                except:
                    continue
    except Exception as e:
        print(f"获取cron状态失败: {e}", file=sys.stderr)

    return recent_runs

def generate_journal_content(date_info, market_data, cron_status, recent_memories):
    """生成日记内容 - 按宝总要求：聚焦自我改进，不堆砌数据"""

    content = f"""# {date_info['today']} {date_info['weekday']}

## ✅ 今日完成

（记录今天完成的任务、工作、交易等）

- [ ]
- [ ]
- [ ]

---

## 📚 经验教训

**今天学到了什么？**
-

**犯了什么错误？**
-

**根本原因分析：**
-

---

## 🛡️ 防重复犯错

**如何避免同样的错误？**
-

**需要建立什么机制/流程？**
-

---

## 🎯 明日计划

**明天要做什么？**
- [ ]
- [ ]
- [ ]

**优先级排序：**
1.
2.
3.

---

## 💭 我的感受

（记录AI助手今日工作的感受、反思、成长）

**今日工作状态：**
-

**遇到的问题及解决：**
-

**如何做得更好：**
-

---

## 🚀 追求卓越

⭐ **持续改进的重点**

**具体改进措施：**
-

**下次遇到类似情况会怎么做？**
-

---

*日记生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*写作原则：追求卓越 · 不重复犯错 · 不断学习成长进化*
"""

    return content

def main():
    """主函数"""
    try:
        # 确保memory目录存在
        os.makedirs(MEMORY_DIR, exist_ok=True)

        # 获取日期信息
        date_info = get_date_info()
        print(f"正在生成 {date_info['today']} 的日记...")

        # 检查是否已存在
        exists, journal_path = check_existing_journal(date_info['today'])
        if exists:
            print(f"日记已存在: {journal_path}")
            print("跳过生成")
            return 0

        # 收集数据
        market_data = get_market_data()
        cron_status = get_cron_status()
        recent_memories = get_recent_memory_files()

        # 生成内容
        content = generate_journal_content(date_info, market_data, cron_status, recent_memories)

        # 写入文件
        with open(journal_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 日记已生成: {journal_path}")
        return 0

    except Exception as e:
        print(f"❌ 生成日记失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
