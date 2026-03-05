#!/usr/bin/env python3
"""
飞书文档顺序写入脚本
逐个创建块来保持顺序
"""

import requests
import json
import sys

# 导入secrets管理
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from secrets_manager import get_feishu_app_config

# 从secrets获取配置
_feishu_config = get_feishu_app_config()
APP_ID = _feishu_config['app_id']
APP_SECRET = _feishu_config['app_secret']

def get_token():
    """获取 tenant_access_token"""
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    return resp.json().get("tenant_access_token")

def create_doc(token, title):
    """创建文档"""
    resp = requests.post(
        "https://open.feishu.cn/open-apis/docx/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title}
    )
    return resp.json()["data"]["document"]["document_id"]

def create_block(token, doc_id, parent_id, block_type, content, style=None):
    """创建单个块"""
    data = {
        "children": [{
            "block_type": block_type,
        }]
    }
    
    # 根据块类型设置内容
    if block_type == 1:  # Page (标题)
        data["children"][0]["page"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    elif block_type == 2:  # Text
        data["children"][0]["text"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    elif block_type == 3:  # Heading1
        data["children"][0]["heading1"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    elif block_type == 4:  # Heading2
        data["children"][0]["heading2"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    elif block_type == 5:  # Heading3
        data["children"][0]["heading3"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    elif block_type == 12:  # Bullet
        data["children"][0]["bullet"] = {
            "elements": [{"text_run": {"content": content}}]
        }
    
    resp = requests.post(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=data
    )
    print(f"API Response: {resp.status_code} - {resp.text[:200]}")
    return resp.json() if resp.text else {"code": 0}

def write_doc_in_order(title, blocks):
    """
    按顺序写入文档
    blocks: [(block_type, content), ...]
    """
    token = get_token()
    doc_id = create_doc(token, title)
    print(f"创建文档: {doc_id}")
    
    for block_type, content in blocks:
        result = create_block(token, doc_id, doc_id, block_type, content)
        if result.get("code") != 0:
            print(f"错误: {result.get('msg')}")
            return None
    
    return doc_id

# 定义内容块（按顺序）
blocks = [
    (3, "A股短线情绪研判 - 2026/02/27(周五) - Billy's Claw"),
    (4, "一、当日盘面解读"),
    (5, "指数与量能"),
    (2, "上证指数收4162.88（+0.39%）；创业板指收3310.30（-1.04%），上证微涨创业板回调。全市上涨家数3164家，下跌家数1884家，涨跌比约6.3:3.7，涨多跌少。成交额24880亿，较前一交易日缩量约2%，资金情绪较昨日回暖。"),
    (5, "短线情绪"),
    (2, "情绪修复，赚钱效应回升。情绪指数63（良好区），较前一交易日（54）明显回升；涨停75家（较昨日61家增加），跌停0家（较昨日3家减少），连板晋级率16.4%（较低水平），封板率83.3%（较高）。资金接力意愿回升，连板高度拓展至7板。"),
    (4, "二、周期定位与演变"),
    (2, "当前阶段：震荡修复期，情绪回暖中"),
    (2, "当前周期特征：连板高度拓展至7板，但晋级率仅16.4%，高位接力风险大；跌停家数归零，亏钱效应收敛；MA50占比72.22%，较昨日70.16%继续上升。"),
    (2, "信号判断：情绪回升但未至高潮，需观察明日是否持续。若情绪继续上行至70以上，则可能进入新一轮主升期。"),
    (4, "三、后市策略应对"),
    (2, "关注方向："),
    (12, "低位首板/二板新题材"),
    (12, "趋势股回踩支撑位"),
    (12, "7板龙头分歧后的承接情况"),
    (2, "回避方向："),
    (12, "中位连板股（3-5板）"),
    (12, "高位缩量加速股"),
    (12, "跟风补涨股"),
    (2, "关键信号：情绪指数是否突破70进入高潮区、跌停家数是否维持低位、连板高度能否突破8板。"),
    (2, "一句话：情绪回暖但连板难度大，做低位接力或趋势低吸，不追高。"),
]

if __name__ == "__main__":
    doc_id = write_doc_in_order("A股短线情绪研判 - 2026-02-27", blocks)
    if doc_id:
        print(f"成功! 文档ID: {doc_id}")
        print(f"链接: https://feishu.cn/docx/{doc_id}")
    else:
        print("失败!")
        sys.exit(1)
