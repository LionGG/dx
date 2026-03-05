# OpenClaw 多通道共享机制

## 共享（所有通道共用）

| 资源 | 说明 |
|------|------|
| **Gateway实例** | 同一个OpenClaw进程，端口18789 |
| **配置** | 同一个openclaw.json |
| **插件** | feishu、dingtalk-connector等 |
| **数据库** | stock-plan/trade_notes.db |
| **文件系统** | workspace目录 |
| **模型配置** | kimi-coding/k2p5 |

## 不共享（通道独立）

| 资源 | 说明 |
|------|------|
| **App ID/Secret** | 每个通道独立凭证 |
| **Webhook端点** | /feishu vs /dingtalk |
| **消息来源** | 飞书用户 vs 钉钉用户 |
| **会话隔离** | 飞书session vs 钉钉session |

## 关键问题

**Agent是否共享？**
- 默认：所有通道进入同一个Agent（main）
- 可配置：不同通道路由到不同Agent

**当前状态：**
- 飞书 → main Agent（主助手）
- 钉钉 → main Agent（主助手）
- 子代理 trade-assistant 已创建但未绑定

## 要实现独立交易助手

方案1：**通道绑定不同Agent**
```
飞书 → main Agent
钉钉 → trade-assistant Agent
```

方案2：**同一Agent，内容路由**
```
飞书/钉钉 → main Agent → 识别内容 → 分发处理
```

方案3：**完全独立实例**（需要第二个OpenClaw）
