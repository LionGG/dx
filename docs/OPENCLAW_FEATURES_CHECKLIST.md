# OpenClaw 2.13-2.26 版本新特性优化清单

## 📋 版本跨度
- 起始版本: 2026.2.13
- 目标版本: 2026.2.26
- 中间版本: 2.14, 2.15, 2.17, 2.19, 2.21, 2.22, 2.23, 2.24, 2.25, 2.26

---

## ✅ 已实施的优化 (P0-P3)

### P0: 日记任务修复 ✅
- 创建日记写作/发送脚本
- 改为 exec 类型任务

### P1: Secrets 管理 ✅
- 创建 secrets.json
- 迁移 5 个敏感配置
- 修改 6 个脚本

### P2: ACP 代理 ✅
- 8个任务改为 isolated 模式
- 使用 agentTurn/exec 类型

### P3: 路由优化 ✅
- 配置 delivery/announce
- 创建通知路由模块

---

## 🎯 待实施的优化 (按优先级排序)

### 【高优先级】安全加固类

#### 1. Delivery Queue 退避机制 (2.26)
**特性**: `Delivery queue/recovery backoff` - 失败发送时持久化 `lastAttemptAt`，防止重试饥饿

**优化动作**:
- [ ] 检查 delivery queue 配置
- [ ] 验证退避机制是否生效
- [ ] 监控队列积压情况

**相关命令**:
```bash
# 检查 delivery queue 状态
ls -la ~/.openclaw/delivery-queue/
```

#### 2. Cron 可靠性增强 (2.26)
**特性**: `Queue/Drain/Cron reliability` - Gateway重启时拒绝新队列入队，避免任务丢失

**优化动作**:
- [ ] 配置 `cron.maxConcurrentRuns` 并行度
- [ ] 设置任务超时保护
- [ ] 验证重启时任务状态

**配置建议**:
```json
{
  "cron": {
    "maxConcurrentRuns": 3,
    "defaultTimeoutSeconds": 300
  }
}
```

#### 3. Session 清理 (2.23)
**特性**: `openclaw sessions cleanup` - 清理缺失 transcript 的 session 记录

**优化动作**:
- [ ] 运行 session 清理
- [ ] 配置磁盘预算控制

**相关命令**:
```bash
openclaw sessions cleanup --fix-missing
```

---

### 【中优先级】功能增强类

#### 4. Web Search Kimi 支持 (2.23)
**特性**: `Tools/web_search` 添加 `provider: "kimi"` 支持

**优化动作**:
- [ ] 配置 Kimi web_search
- [ ] 测试搜索功能

**配置**:
```json
{
  "tools": {
    "web_search": {
      "provider": "kimi"
    }
  }
}
```

#### 5. Heartbeat 策略配置 (2.25)
**特性**: `agents.defaults.heartbeat.directPolicy` - 更清晰的心跳投递语义

**优化动作**:
- [ ] 配置 heartbeat 策略
- [ ] 设置为 `"block"` 或 `"allow"`

**配置**:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "directPolicy": "block"
      }
    }
  }
}
```

#### 6. 模型回退链优化 (2.24-2.26)
**特性**: 改进的模型回退逻辑，支持 `model_cooldown` 分类

**优化动作**:
- [ ] 配置模型回退链
- [ ] 设置 `agents.defaults.models` allowlist

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "models": {
        "primary": "kimi-coding/k2p5",
        "fallbacks": ["kimi/k2p5", "openai/gpt-4o"]
      }
    }
  }
}
```

---

### 【低优先级】监控和工具类

#### 7. Doctor 检查增强 (2.23-2.26)
**特性**: 多项 Doctor 检查改进

**优化动作**:
- [ ] 运行 `openclaw doctor` 检查
- [ ] 修复发现的问题
- [ ] 定期运行检查

**相关命令**:
```bash
openclaw doctor
openclaw doctor --fix
```

#### 8. Sessions 维护 (2.23)
**特性**: 磁盘预算控制和自动清理

**优化动作**:
- [ ] 配置 session 维护参数
- [ ] 设置磁盘预算

**配置**:
```json
{
  "session": {
    "maintenance": {
      "maxDiskBytes": 10737418240,
      "highWaterBytes": 8589934592
    }
  }
}
```

#### 9. 内存搜索多语言支持 (2.22)
**特性**: 西班牙语、葡萄牙语、日语、韩语、阿拉伯语支持

**优化动作**:
- [ ] 测试多语言记忆搜索
- [ ] 如有需要，配置 FTS 模式

---

### 【可选】高级功能类

#### 10. Agents Bindings 路由 (2.26)
**特性**: `openclaw agents bindings/bind/unbind` - 账户级路由管理

**适用场景**: 多账户、多渠道路由

**相关命令**:
```bash
openclaw agents bindings
openclaw agents bind <agent-id> --channel <channel> --account <account>
```

#### 11. External Secrets Management (2.26)
**特性**: `openclaw secrets` 完整工作流

**适用场景**: 比当前 secrets.json 更高级的管理

**相关命令**:
```bash
openclaw secrets audit
openclaw secrets configure
openclaw secrets apply
openclaw secrets reload
```

---

## 📊 实施建议

### 第一阶段（本周）- 安全加固
1. 验证 Delivery Queue 退避机制
2. 配置 Cron 并行度和超时
3. 运行 Session 清理

### 第二阶段（下周）- 功能增强
1. 配置 Kimi web_search
2. 设置 Heartbeat 策略
3. 配置模型回退链

### 第三阶段（月度）- 监控维护
1. 配置 Session 磁盘预算
2. 设置定期 Doctor 检查
3. 评估高级功能需求

---

## 📝 记录位置

- 本文档: `/root/.openclaw/workspace/docs/OPENCLAW_FEATURES_CHECKLIST.md`
- 已实施: `/root/.openclaw/workspace/docs/OPENCLAW_UPGRADE_SUMMARY.md`
- Secrets: `/root/.openclaw/workspace/docs/SECRETS_MANAGEMENT.md`
- ACP优化: `/root/.openclaw/workspace/docs/ACP_OPTIMIZATION.md`

---

*创建时间: 2026-02-28*
*版本: 2026.2.26*
