#!/usr/bin/env python3
"""
错误模式分析模块
分析错误发生的规律和根本原因
"""

import json
import os
from datetime import datetime
from collections import defaultdict

ERROR_ANALYSIS_FILE = "/root/.openclaw/workspace/memory/error_pattern_analysis.json"

def analyze_error_pattern(error_name, context, root_cause, prevention):
    """
    分析并记录错误模式
    
    Args:
        error_name: 错误名称
        context: 发生场景
        root_cause: 根本原因
        prevention: 预防措施
    """
    os.makedirs(os.path.dirname(ERROR_ANALYSIS_FILE), exist_ok=True)
    
    if os.path.exists(ERROR_ANALYSIS_FILE):
        with open(ERROR_ANALYSIS_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {"patterns": {}, "trends": []}
    
    # 记录错误模式
    if error_name not in data["patterns"]:
        data["patterns"][error_name] = {
            "first_seen": datetime.now().isoformat(),
            "count": 0,
            "contexts": [],
            "root_cause": root_cause,
            "prevention": prevention
        }
    
    pattern = data["patterns"][error_name]
    pattern["count"] += 1
    pattern["last_seen"] = datetime.now().isoformat()
    pattern["contexts"].append({
        "time": datetime.now().isoformat(),
        "context": context
    })
    
    # 只保留最近10次上下文
    pattern["contexts"] = pattern["contexts"][-10:]
    
    # 记录趋势
    data["trends"].append({
        "time": datetime.now().isoformat(),
        "error": error_name,
        "context": context
    })
    
    # 只保留最近100条趋势
    data["trends"] = data["trends"][-100:]
    
    with open(ERROR_ANALYSIS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return f"✅ 已分析错误模式: {error_name} (发生{pattern['count']}次)"

def get_error_insights():
    """获取错误洞察"""
    if not os.path.exists(ERROR_ANALYSIS_FILE):
        return "暂无错误分析数据"
    
    with open(ERROR_ANALYSIS_FILE, 'r') as f:
        data = json.load(f)
    
    if not data["patterns"]:
        return "暂无错误记录"
    
    insights = []
    
    # 高频错误
    sorted_patterns = sorted(
        data["patterns"].items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )
    
    insights.append("📊 高频错误 Top 3:")
    for name, pattern in sorted_patterns[:3]:
        bar = "█" * min(pattern["count"], 10)
        insights.append(f"  {bar} {name}: {pattern['count']}次")
    
    # 时间趋势分析
    if len(data["trends"]) >= 5:
        recent = data["trends"][-10:]
        error_counts = defaultdict(int)
        for t in recent:
            error_counts[t["error"]] += 1
        
        insights.append("\n📈 最近趋势:")
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            insights.append(f"  - {error}: 最近出现{count}次")
    
    # 根本原因汇总
    insights.append("\n🔍 根本原因分类:")
    root_causes = defaultdict(list)
    for name, pattern in data["patterns"].items():
        root_causes[pattern["root_cause"]].append(name)
    
    for cause, errors in root_causes.items():
        insights.append(f"  - {cause}: {', '.join(errors)}")
    
    return "\n".join(insights)

def check_error_risk(operation_type):
    """检查操作的风险等级"""
    if not os.path.exists(ERROR_ANALYSIS_FILE):
        return "✅ 无历史错误数据"
    
    with open(ERROR_ANALYSIS_FILE, 'r') as f:
        data = json.load(f)
    
    risks = []
    for name, pattern in data["patterns"].items():
        if operation_type.lower() in name.lower():
            risks.append({
                "error": name,
                "count": pattern["count"],
                "prevention": pattern["prevention"]
            })
    
    if risks:
        result = f"⚠️ 该操作类型有 {len(risks)} 个历史错误记录:\n"
        for r in risks:
            result += f"  - {r['error']}: {r['count']}次\n"
            result += f"    预防: {r['prevention']}\n"
        return result
    
    return "✅ 该操作类型无历史错误记录"

if __name__ == "__main__":
    # 测试
    print(analyze_error_pattern(
        "Gateway频繁重启",
        "配置修改后立即重启",
        "缺乏重启计划和等待机制",
        "统一在周日03:00重启，避免频繁重启"
    ))
    print()
    print(analyze_error_pattern(
        "配置文件损坏",
        "手动编辑JSON格式错误",
        "未验证格式就保存",
        "修改前备份，修改后验证JSON格式"
    ))
    print()
    print(get_error_insights())
    print()
    print(check_error_risk("restart"))
