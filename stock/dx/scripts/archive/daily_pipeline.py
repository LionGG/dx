#!/usr/bin/env python3
"""
每日自动化流程（增强版）

流程: 数据源检查 → 数据抓取 → AI分析 → HTML生成 → 部署
增加数据源延迟检测和重试机制

用法:
    python3 scripts/daily_pipeline.py

定时任务配置 (crontab):
    20 16 * * * cd /root/.openclaw/workspace/stock/dx && python3 scripts/daily_pipeline.py >> logs/daily_$(date +\%Y\%m\%d).log 2>&1
"""

import subprocess
import sys
import os
import sqlite3
import time
from datetime import datetime

WORKSPACE = '/root/.openclaw/workspace/stock/dx'
DB_PATH = os.path.join(WORKSPACE, 'data', 'duanxian.db')

# 导入飞书推送模块
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))
from feishu_notifier import send_to_feishu_group

def check_data_source():
    """检查AKShare数据源是否最新"""
    import akshare as ak
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n检查数据源状态 (期望日期: {today})")
    print("-" * 60)
    
    issues = []
    
    # 检查上证指数
    try:
        df = ak.stock_zh_index_daily(symbol='sh000001')
        latest_date = df['date'].iloc[-1]
        print(f"上证指数: 最新数据 {latest_date}")
        if latest_date != today:
            issues.append(f"上证指数数据延迟: {latest_date}")
    except Exception as e:
        issues.append(f"上证指数获取失败: {e}")
    
    # 检查创业板指
    try:
        df = ak.stock_zh_index_daily(symbol='sz399006')
        latest_date = df['date'].iloc[-1]
        print(f"创业板指: 最新数据 {latest_date}")
        if latest_date != today:
            issues.append(f"创业板指数据延迟: {latest_date}")
    except Exception as e:
        issues.append(f"创业板指获取失败: {e}")
    
    print("-" * 60)
    
    if issues:
        print("⚠️ 数据源延迟:")
        for issue in issues:
            print(f"  - {issue}")
        return False, issues
    else:
        print("✅ 数据源正常")
        return True, []

def run_step(name, cmd, timeout=300, critical=False):
    """
    执行单个步骤
    
    critical=True: 失败则停止整个流程
    """
    print(f"\n{'='*60}")
    print(f"步骤: {name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            print(result.stdout[-2000:])  # 只打印最后2000字符
        
        if result.returncode != 0:
            print(f"✗ 失败: {result.stderr}")
            if critical:
                return False, True  # 失败且关键
            return False, False
        
        print(f"✓ 成功")
        return True, False
        
    except subprocess.TimeoutExpired:
        print(f"✗ 超时 ({timeout}秒)")
        if critical:
            return False, True
        return False, False
    except Exception as e:
        print(f"✗ 错误: {e}")
        if critical:
            return False, True
        return False, False

def send_notification(today, analysis_phase, mowen_link, success=True, issues=None):
    """发送飞书通知"""
    
    if success:
        feishu_message = f"""📊 短线情绪研判 - {today}

周期定位：{analysis_phase}

查看完整分析：{mowen_link}"""
        send_to_feishu_group(feishu_message)
        print("✅ 飞书通知发送成功")
    else:
        feishu_message = f"""⚠️ 短线情绪研判 - {today}

状态：部分完成

问题：
"""
        if issues:
            for issue in issues:
                feishu_message += f"  • {issue}\n"
        
        feishu_message += f"""
查看页面：{mowen_link}

建议：稍后手动重新运行脚本"""
        send_to_feishu_group(feishu_message)
        print("⚠️ 飞书通知已发送（含问题说明）")

def main():
    start_time = datetime.now()
    today = start_time.strftime('%Y-%m-%d')
    
    print(f"\n{'#'*60}")
    print(f"# A股情绪数据自动化流程 - {today}")
    print(f"{'#'*60}")
    
    # 确保日志目录存在
    os.makedirs(os.path.join(WORKSPACE, 'logs'), exist_ok=True)
    
    # 步骤0: 检查数据源
    print(f"\n{'='*60}")
    print("步骤0: 检查数据源状态")
    print(f"{'='*60}")
    
    data_ok, data_issues = check_data_source()
    
    if not data_ok:
        print("\n⚠️ 数据源有延迟，继续执行但可能生成不完整报告")
    
    # 定义步骤 (名称, 命令, 超时秒数, 是否关键)
    steps = [
        ("1. 抓取短线侠情绪数据", "python3 scripts/crawler.py", 120, True),
        ("2. 抓取指数K线数据(新浪财经)", "python3 scripts/fetch_kline_sina.py", 120, True),
        ("3. 同步MA50占比数据", "python3 scripts/sync_ma50_ratio.py", 60, True),
        ("4. AI分析并发布到墨问", "python3 scripts/analyze_sentiment.py", 300, True),
        ("5. 更新HTML数据", "python3 scripts/update_html_data.py", 60, True),
        ("6. 部署到GitHub", "python3 scripts/deploy.py", 60, False),  # 部署失败不阻断
    ]
    
    failed_steps = []
    critical_failed = False
    
    for name, cmd, timeout, critical in steps:
        success, is_critical = run_step(name, cmd, timeout, critical)
        if not success:
            failed_steps.append(name)
            if is_critical:
                critical_failed = True
                print(f"\n✗ 关键步骤失败，停止执行: {name}")
                break
    
    # 总结
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print("执行总结")
    print(f"{'='*60}")
    print(f"日期: {today}")
    print(f"开始: {start_time.strftime('%H:%M:%S')}")
    print(f"结束: {end_time.strftime('%H:%M:%S')}")
    print(f"耗时: {duration:.1f}秒")
    
    # 收集所有问题
    all_issues = data_issues.copy() if data_issues else []
    if failed_steps:
        all_issues.extend(failed_steps)
        print(f"\n⚠ 失败步骤:")
        for step in failed_steps:
            marker = " (关键)" if critical_failed and step == failed_steps[-1] else ""
            print(f"  - {step}{marker}")
    
    # 从数据库获取AI分析结果
    try:
        sqlite_conn = sqlite3.connect(DB_PATH)
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT analysis_phase, mowen_link 
            FROM market_sentiment 
            WHERE date = ?
        ''', (today,))
        row = cursor.fetchone()
        analysis_phase = row[0] if row else "未生成"
        mowen_link = row[1] if row and row[1] else "https://liongg.github.io/dx/"
        sqlite_conn.close()
    except Exception as e:
        print(f"获取分析结果失败: {e}")
        analysis_phase = "未生成"
        mowen_link = "https://liongg.github.io/dx/"
    
    # 发送通知
    success = not critical_failed and not data_issues
    send_notification(today, analysis_phase, mowen_link, success, all_issues)
    
    if critical_failed:
        print(f"\n✗ 流程未完成，需要人工介入")
        return False
    elif failed_steps or data_issues:
        print(f"\n⚠ 流程完成，但存在问题")
        return True
    else:
        print(f"\n✓ 全部成功")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
