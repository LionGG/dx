# 钉钉消息路由规则

## 识别来源
if message.channel == "dingtalk":
    → 转发给 trade-assistant 子代理

## 子代理信息
- sessionKey: agent:main:subagent:dba0d885-2f9b-4cf3-aaa7-1142f7c983ac
- label: trade-assistant
- 已加载数据：用户持仓、市场环境

## 转发方式
主代理收到钉钉消息 → 调用 sessions_send → trade-assistant 处理 → 返回结果
