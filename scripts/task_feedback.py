#!/usr/bin/env python3
"""
任务反馈评分模块
每次任务后记录评分和反馈
"""

import json
import os
from datetime import datetime

FEEDBACK_FILE = "/root/.openclaw/workspace/memory/task_feedback.json"

def record_feedback(task_name, score, feedback="", details=None):
    """
    记录任务反馈评分
    
    Args:
        task_name: 任务名称
        score: 1-5分评分
        feedback: 文字反馈
        details: 详细数据
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    
    # 加载现有记录
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {"feedbacks": [], "stats": {}}
    
    # 添加新记录
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task_name,
        "score": score,
        "feedback": feedback,
        "details": details or {}
    }
    data["feedbacks"].append(entry)
    
    # 更新统计
    task_stats = data["stats"].get(task_name, {"count": 0, "total_score": 0, "avg_score": 0})
    task_stats["count"] += 1
    task_stats["total_score"] += score
    task_stats["avg_score"] = round(task_stats["total_score"] / task_stats["count"], 2)
    data["stats"][task_name] = task_stats
    
    # 保存
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return f"✅ 已记录反馈: {task_name} - {score}/5分"

def get_stats(task_name=None):
    """获取统计数据"""
    if not os.path.exists(FEEDBACK_FILE):
        return "暂无反馈记录"
    
    with open(FEEDBACK_FILE, 'r') as f:
        data = json.load(f)
    
    if task_name:
        stats = data["stats"].get(task_name)
        if stats:
            return f"{task_name}: 平均 {stats['avg_score']}/5分 (共{stats['count']}次)"
        return f"{task_name}: 无记录"
    
    # 整体统计
    total_tasks = len(data["stats"])
    if total_tasks == 0:
        return "暂无反馈记录"
    
    total_score = sum(s["total_score"] for s in data["stats"].values())
    total_count = sum(s["count"] for s in data["stats"].values())
    overall_avg = round(total_score / total_count, 2) if total_count > 0 else 0
    
    result = f"整体表现: {overall_avg}/5分 (共{total_count}次任务)\n\n各任务统计:\n"
    for task, stats in data["stats"].items():
        result += f"  - {task}: {stats['avg_score']}/5分 ({stats['count']}次)\n"
    
    return result

if __name__ == "__main__":
    # 测试
    print(record_feedback("日记生成", 5, "按时生成，内容完整"))
    print(record_feedback("数据抓取", 4, "成功，但可以更快"))
    print()
    print(get_stats())
