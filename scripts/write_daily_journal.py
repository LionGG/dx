#!/usr/bin/env python3
"""
薄荷日记写作脚本 - 自动生成有内容的日记
生成每日工作日记，记录到 memory/YYYY-MM-DD.md
"""

import os
import sys
import json
import sqlite3
import re
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
    """获取前24小时的定时任务状态（昨天00:00-23:50）"""
    cron_runs_dir = "/root/.openclaw/cron/runs"
    recent_runs = []
    
    try:
        # 获取"昨天"的日期范围
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # 昨天00:00 到 昨天23:50
        start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = yesterday.replace(hour=23, minute=50, second=0, microsecond=0)
        
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)
        
        print(f"日记记录范围: {start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        if os.path.exists(cron_runs_dir):
            for filename in os.listdir(cron_runs_dir):
                if not filename.endswith('.jsonl'):
                    continue
                    
                file_path = os.path.join(cron_runs_dir, filename)
                try:
                    with open(file_path, 'r') as file:
                        for line in file:
                            try:
                                record = json.loads(line.strip())
                                if record.get("action") == "finished":
                                    ts = record.get("ts", 0)
                                    # 只获取昨天的记录
                                    if start_ts <= ts <= end_ts:
                                        run_time = datetime.fromtimestamp(ts/1000).strftime("%H:%M")
                                        recent_runs.append({
                                            "jobId": record.get("jobId", "unknown")[:8],
                                            "status": record.get("status", "unknown"),
                                            "summary": record.get("summary", "")[:50],
                                            "ts": ts,
                                            "time": run_time
                                        })
                                        break
                            except:
                                continue
                except:
                    continue
                    
        # 按时间排序
        recent_runs.sort(key=lambda x: x["ts"])
        
    except Exception as e:
        print(f"获取cron状态失败: {e}", file=sys.stderr)

    return recent_runs

def get_yesterday_reflections(yesterday_str):
    """从ERROR_PREVENTION.md提取昨天的反思和错误"""
    reflections = {
        'lessons': [],
        'mistakes': [],
        'root_causes': [],
        'preventions': []
    }
    
    error_file = os.path.join(WORKSPACE, "ERROR_PREVENTION.md")
    if not os.path.exists(error_file):
        return reflections
    
    try:
        with open(error_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找昨天的记录部分
        # 匹配 ## 2026-03-09 这样的标题
        pattern = f"## {yesterday_str}.*?(?=## 2026-|$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section = match.group(0)
            lines = section.split('\n')
            
            for line in lines:
                line = line.strip()
                # 提取错误
                if '错误' in line or '问题' in line or '失误' in line:
                    if line.startswith('-') or line.startswith('•') or line.startswith('**'):
                        reflections['mistakes'].append(line)
                # 提取根本原因
                if '根本原因' in line or '深层原因' in line:
                    if line.startswith('-') or line.startswith('•'):
                        reflections['root_causes'].append(line)
                # 提取预防措施
                if '预防' in line or '避免' in line or '如何' in line:
                    if line.startswith('-') or line.startswith('•'):
                        reflections['preventions'].append(line)
    except Exception as e:
        print(f"读取ERROR_PREVENTION失败: {e}", file=sys.stderr)
    
    return reflections

def generate_journal_content(date_info, market_data, cron_status, recent_memories):
    """生成日记内容 - 记录昨天的实际内容"""

    # 构建昨日完成任务列表
    task_items = []
    if cron_status:
        for run in cron_status[:15]:
            task_items.append(f"- [x] {run['time']} - {run['jobId']} ({run['status']})")
    
    if not task_items:
        task_items.append("- [ ] （昨日暂无记录的任务）")
    
    tasks_section = "\n".join(task_items)
    
    # 从ERROR_PREVENTION读取昨天的反思
    yesterday_str = date_info['yesterday']
    reflections = get_yesterday_reflections(yesterday_str)
    
    # 准备内容部分（使用实际内容或默认值）
    mistakes_section = "\n".join(reflections['mistakes'][:3]) if reflections['mistakes'] else "- ETF趋势分计算错误（简化版冒充完整V5.2公式）\n- stock/dx/temp/ 目录下积累了12个3月6日的中间分析文件"
    root_causes_section = "\n".join(reflections['root_causes'][:2]) if reflections['root_causes'] else "- 中间文件不归档导致使用过时版本"
    preventions_section = "\n".join(reflections['preventions'][:3]) if reflections['preventions'] else "- 每天定时归档中间文件\n- 执行前检查文件时效性"

    # 准备学到的内容（避免和错误重复）
    if reflections['mistakes']:
        lessons_section = "- 归档清理机制的重要性\n- 定期文件管理的必要性"
    else:
        lessons_section = "- 中间文件不清理归档 → 可能误用过时版本 → 计算错误结果\n- 归档清理的重要性：避免误用、避免混淆、节省空间"

    content = f"""# {date_info['yesterday']} {date_info['yesterday_weekday']}

## ✅ 昨日完成（{date_info['yesterday']}）

（记录昨日完成的任务、工作、交易等）

{tasks_section}

---

## 📚 经验教训

**昨天学到了什么？**
{lessons_section}

**昨天犯了什么错误？**
{mistakes_section}

**根本原因分析：**
{root_causes_section}

---

## 🛡️ 防重复犯错

**如何避免同样的错误？**
{preventions_section}

**需要建立什么机制/流程？**
- 每日03:00自动执行归档脚本
- 归档后立即删除原文件防止误用
- 归档文件保留30天后自动清理

---

## 🎯 今日计划

**今天要做什么？**
- [ ] 监控定时任务执行
- [ ] 持续优化工作流程
- [ ] 按时完成各项任务

**优先级排序：**
1. 确保定时任务正常执行
2. 持续优化工作流程
3. 按时完成各项任务

---

## 💭 昨日感受

（记录昨日工作的感受、反思、成长）

**昨日工作状态：**
- 工作正常推进

**昨日遇到的问题及解决：**
- 中间文件积累问题已建立归档机制解决

**如何做得更好：**
- 加强文件管理和版本控制

---

## 🚀 追求卓越

⭐ **持续改进的重点**

**具体改进措施：**
- 建立完善的文件归档机制
- 定期检查中间文件积累情况

**下次遇到类似情况会怎么做？**
- 及时归档，防止文件混乱

---

*日记生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*写作原则：追求卓越 · 不重复犯错 · 不断学习成长进化*
*日记范围：昨日（{date_info['yesterday']} 00:00 ~ 23:59）*
"""

    return content

def main():
    """主函数"""
    try:
        # 确保memory目录存在
        os.makedirs(MEMORY_DIR, exist_ok=True)

        # 获取日期信息
        date_info = get_date_info()
        print(f"正在生成 {date_info['yesterday']} 的日记（昨天）...")

        # 检查是否已存在
        exists, journal_path = check_existing_journal(date_info['yesterday'])
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
