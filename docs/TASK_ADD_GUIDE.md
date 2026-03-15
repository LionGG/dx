# 定时任务添加指南

**用途**：添加新定时任务时对照执行，确保一次性配置成功

---

## 标准流程（5步法）

### 第1步：复制模板
找一个正常运行的任务作为模板，复制其完整配置

```bash
# 查看现有任务配置示例
jq '.jobs[] | select(.name == "美股收盘推送")' /root/.openclaw/workspace/cron-jobs-updated.json
```

### 第2步：修改必要字段
修改以下字段为新任务信息：
- `id` - 唯一标识（uuidgen生成）
- `name` - 任务名称
- `schedule.expr` - cron表达式（分 时 日 月 周）
- `schedule.kind` - 固定为"cron"
- `payload.text` - 任务说明和指令

### 第3步：核查完整配置
添加后必须检查所有字段：

```bash
# 核查新任务的完整配置
jq '.jobs[] | select(.name == "新任务名") | {
  name: .name,
  has_id: has("id"),
  has_agentId: has("agentId"),
  has_schedule: has("schedule"),
  has_sessionTarget: has("sessionTarget"),
  has_wakeMode: has("wakeMode"),
  has_payload: has("payload"),
  has_state: has("state"),
  has_delivery: has("delivery"),
  has_announce: has("announce")
}' /root/.openclaw/workspace/cron-jobs-updated.json
```

**必须全部为true**

### 第4步：验证JSON格式
```bash
# 验证JSON格式正确
python3 -c "import json; json.load(open('/root/.openclaw/workspace/cron-jobs-updated.json')); print('✅ JSON格式正确')"
```

### 第5步：手动测试
添加后立即手动触发测试：
```bash
# 手动触发任务测试
openclaw task trigger --name "新任务名"
```

---

## 必需字段清单

| 字段 | 说明 | 示例 |
|------|------|------|
| id | 唯一标识 | "task-uuid-1234" |
| agentId | 代理ID | "main" |
| name | 任务名称 | "每日Skill搜索" |
| enabled | 是否启用 | true |
| schedule.kind | 调度类型 | "cron" |
| schedule.expr | cron表达式 | "0 22 * * *" |
| schedule.tz | 时区 | "Asia/Shanghai" |
| sessionTarget | 会话目标 | "main" |
| wakeMode | 唤醒模式 | "now" |
| payload.kind | 负载类型 | "systemEvent" |
| payload.text | 任务指令 | "执行任务..." |
| state.nextRunAtMs | 下次运行时间 | 时间戳 |
| delivery.mode | 投递模式 | "announce" |
| delivery.channel | 投递渠道 | "feishu" |
| announce | 是否通知 | true |

---

## 常见错误

### 错误1：缺少wakeMode
**现象**：任务不触发
**解决**：添加 `"wakeMode": "now"`

### 错误2：缺少state
**现象**：任务不触发
**解决**：添加 `"state": {"nextRunAtMs": 时间戳}`

### 错误3：缺少delivery
**现象**：任务执行后没通知
**解决**：添加 `"delivery": {"mode": "announce", "channel": "feishu"}`

### 错误4：JSON格式错误
**现象**：Gateway无法启动
**解决**：用python3验证JSON格式

---

## 检查脚本

保存为 `check_new_task.sh`：

```bash
#!/bin/bash
# 检查新任务配置

TASK_NAME=$1

echo "=== 检查任务: $TASK_NAME ==="

jq --arg name "$TASK_NAME" '.jobs[] | select(.name == $name) | {
  name: .name,
  id: has("id"),
  agentId: has("agentId"),
  enabled: has("enabled"),
  schedule: has("schedule"),
  sessionTarget: has("sessionTarget"),
  wakeMode: has("wakeMode"),
  payload: has("payload"),
  state: has("state"),
  delivery: has("delivery"),
  announce: has("announce")
}' /root/.openclaw/workspace/cron-jobs-updated.json

echo ""
echo "=== JSON格式检查 ==="
python3 -c "import json; json.load(open('/root/.openclaw/workspace/cron-jobs-updated.json')); print('✅ JSON格式正确')"
```

使用方法：
```bash
chmod +x check_new_task.sh
./check_new_task.sh "新任务名"
```

---

## 记住

**不核查不结束**
**不测试不部署**
**错了就记录，下次不再犯**

---

*创建时间: 2026-03-05*
*用途: 添加定时任务时对照执行*
