#!/usr/bin/env python3
"""
AI情绪分析子代理调用脚本
用于完全自动化的情绪研判流程
"""

import subprocess
import sys
import os

WORKSPACE = '/root/.openclaw/workspace/stock/dx'

def spawn_analysis_agent():
    """调用子代理生成AI分析"""
    
    # 构建子代理任务
    task = """你是A股短线情绪研判专家。

请执行以下任务：
1. 读取 /root/.openclaw/workspace/stock/dx/prompt.md 获取分析模板
2. 读取 /root/.openclaw/workspace/stock/dx/data/duanxian.db 获取今日数据
3. 按照prompt模板格式生成完整的情绪研判报告
4. 将报告保存到数据库

执行步骤：
- 使用 sqlite3 读取最新日期的情绪数据和指数数据
- 按照prompt.md的格式生成报告（一、当日盘面解读；二、周期定位与演变；三、后市策略应对）
- 保存到 daily_reports 表和更新 market_sentiment 表

输出要求：
- 严格按照prompt.md的格式
- 数据要准确
- 分析要专业、直接、犀利

完成后返回："分析完成" 和报告的一句话总结。"""

    # 使用 sessions_spawn 创建子代理
    result = subprocess.run(
        ['openclaw', 'sessions', 'spawn',
         '--runtime', 'subagent',
         '--agent', 'main',
         '--mode', 'run',
         '--task', task,
         '--timeout', '300'],
        capture_output=True,
        text=True,
        timeout=310
    )
    
    return result.returncode == 0, result.stdout, result.stderr

if __name__ == '__main__':
    print("调用AI分析子代理...")
    success, stdout, stderr = spawn_analysis_agent()
    
    if success:
        print("✅ 子代理调用成功")
        print(stdout[-1000:] if len(stdout) > 1000 else stdout)
    else:
        print("❌ 子代理调用失败")
        print(stderr[-500:] if stderr else "无错误信息")
        sys.exit(1)
