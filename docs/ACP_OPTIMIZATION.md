# P2 - ACP 代理执行定时任务 优化报告

## ✅ 优化完成

### 优化原理

OpenClaw 2026.2.26 版本引入了 ACP/Thread-bound agents 特性，支持两种 sessionTarget 模式：

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| **main** | 在主会话中执行，共享上下文 | 需要交互、需要历史记录的任务 |
| **isolated** | 独立会话执行，完全隔离 | 纯执行类、数据抓取类任务 |

### 优化内容

#### 1. 已改为 isolated + agentTurn 的任务（8个）

| 任务名称 | 执行时间 | 模式 | 优势 |
|----------|----------|------|------|
| 薄荷日记-写作 | 02:00 | isolated + exec | 独立执行，失败可重试 |
| 薄荷日记-发送 | 08:00 | isolated + exec | 独立执行，失败可重试 |
| AI热点新闻 | 08:30 | isolated + agentTurn | 独立分析，不干扰主会话 |
| 量化交易每日资讯 | 12:00 | isolated + agentTurn | 独立整理，定时推送 |
| OpenClaw每日资讯 | 17:00 | isolated + agentTurn | 独立整理，定时推送 |
| 个股数据抓取 | 16:05 | isolated + agentTurn | 数据抓取，失败隔离 |
| MA50占比计算 | 16:10 | isolated + agentTurn | 计算任务，独立执行 |
| 短线情绪研判 | 16:20 | isolated + agentTurn | 复杂流程，隔离执行 |

#### 2. 保持 main + systemEvent 的任务（2个）

| 任务名称 | 执行时间 | 模式 | 原因 |
|----------|----------|------|------|
| 交易计划分析 | 09:10 | main + systemEvent | 需要与老二交易助手交互 |
| 交易截图提醒 | 19:00 | main + systemEvent | 需要检查截图状态，交互确认 |

### 优化效果

#### 1. 错误隔离
- isolated 任务失败不会影响主会话
- 每个任务有独立的执行环境
- 失败任务可以独立重试

#### 2. 更好的监控
```bash
# 查看任务执行历史
openclaw cron runs <job-id>

# 查看任务状态
openclaw cron list
```

#### 3. 性能提升
- isolated 任务并行执行，互不干扰
- 主会话保持响应，不受后台任务影响
- agentTurn 模式支持更复杂的推理和执行

### 配置示例

#### isolated + agentTurn 模式
```json
{
  "name": "个股数据抓取",
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "执行个股数据同步任务...",
    "timeoutSeconds": 300
  }
}
```

#### isolated + exec 模式（脚本执行）
```json
{
  "name": "薄荷日记-写作",
  "sessionTarget": "isolated",
  "payload": {
    "kind": "exec",
    "command": ["/usr/bin/python3", "/path/to/script.py"],
    "cwd": "/workspace"
  }
}
```

#### main + systemEvent 模式（交互类）
```json
{
  "name": "交易计划分析",
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ 交易计划分析任务触发..."
  }
}
```

## 📋 后续建议

### 1. 监控任务执行情况
```bash
# 定期检查任务执行状态
openclaw cron list

# 查看失败任务
openclaw cron runs <job-id>
```

### 2. 调整超时时间
根据任务实际执行时间调整 `timeoutSeconds`：
- 简单任务：60-120 秒
- 数据抓取：180-300 秒
- 复杂分析：300-600 秒

### 3. 启用失败通知
可以为 isolated 任务配置 `announce: true`，在失败时发送通知：
```json
{
  "name": "任务名称",
  "sessionTarget": "isolated",
  "announce": true,
  "payload": {...}
}
```

## 🔧 故障排查

### 任务没有执行
1. 检查任务状态：`openclaw cron list`
2. 检查 Gateway 状态：`openclaw gateway status`
3. 检查执行历史：`openclaw cron runs <job-id>`

### 任务执行失败
1. 查看详细日志：`openclaw cron runs <job-id>`
2. 检查 timeout 设置是否足够
3. 检查脚本路径和权限

## 📚 相关文档

- OpenClaw Changelog: 2026.2.26 ACP/Thread-bound agents
- 配置文件: `/root/.openclaw/cron/jobs.json`
- Secrets 管理: `/root/.openclaw/workspace/docs/SECRETS_MANAGEMENT.md`

---

*优化完成时间: 2026-02-28*
*OpenClaw 版本: 2026.2.26*
