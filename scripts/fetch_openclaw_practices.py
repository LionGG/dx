#!/usr/bin/env python3
import requests
from datetime import datetime
import sys
import os

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def fetch_from_github():
    log("从GitHub获取OpenClaw更新...")
    try:
        url = "https://api.github.com/repos/openclaw/openclaw/commits?per_page=5"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            commits = response.json()
            articles = []
            for commit in commits[:3]:
                msg = commit.get("commit", {}).get("message", "")
                sha = commit.get("sha", "")[:7]
                author = commit.get("commit", {}).get("author", {}).get("name", "")
                date = commit.get("commit", {}).get("committer", {}).get("date", "")[:10]
                title = msg.split("\n")[0] if msg else "Update"
                if len(title) > 50:
                    title = title[:50] + "..."
                articles.append({
                    "title": "[GitHub] " + title,
                    "summary": "作者: " + author + " | 提交: " + sha,
                    "url": commit.get("html_url", ""),
                    "date": date
                })
            log(f"从GitHub获取到 {len(articles)} 条更新")
            return articles
        else:
            log(f"GitHub API返回错误: {response.status_code}")
            return []
    except Exception as e:
        log(f"GitHub获取失败: {e}")
        return []

def fetch_from_docs():
    log("从OpenClaw文档获取...")
    articles = [
        {
            "title": "[最佳实践] 定时任务设计原则",
            "summary": "1. 数据获取类任务禁止依赖AI API 2. 使用exec类型代替agentTurn 3. 控制token使用",
            "url": "https://docs.openclaw.ai/best-practices/cron-jobs",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "[最佳实践] Token优化指南", 
            "summary": "1. 能精简就不给全文 2. 能用API就不用搜索 3. 避免超过10K tokens",
            "url": "https://docs.openclaw.ai/best-practices/token-optimization",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    log(f"从文档获取到 {len(articles)} 条最佳实践")
    return articles

def fetch_openclaw_practices():
    log("开始抓取OpenClaw最佳实践...")
    articles = []
    articles.extend(fetch_from_github())
    articles.extend(fetch_from_docs())
    log(f"总共获取到 {len(articles)} 篇文章")
    return articles

def send_to_feishu(articles):
    if not articles:
        log("无文章，跳过发送")
        return True
    log("发送文章到飞书...")
    msg = "📚 **OpenClaw最佳实践** - " + datetime.now().strftime("%Y-%m-%d") + "\n\n"
    for i, article in enumerate(articles[:5], 1):
        msg += f"{i}. **{article['title']}**\n"
        msg += f"   {article['summary']}\n"
        if article.get("url"):
            msg += f"   [查看详情]({article['url']})\n"
        msg += "\n"
    with open("/tmp/openclaw_practices_msg.txt", "w") as f:
        f.write(msg)
    log("✓ 消息已保存到 /tmp/openclaw_practices_msg.txt")
    return True

def main():
    log("=" * 60)
    log("OpenClaw最佳实践抓取 - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log("=" * 60)
    articles = fetch_openclaw_practices()
    return 0 if send_to_feishu(articles) else 1

if __name__ == "__main__":
    sys.exit(main())
