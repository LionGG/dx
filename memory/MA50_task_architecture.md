# MA50占比计算任务 - 正确架构

## 执行流程

### 1. 定时触发
- OpenClaw Cron 定时触发（15:10）
- 执行脚本：`calculate_ma50_ratio.py`

### 2. 脚本职责
脚本执行业务逻辑：
1. 计算MA50占比
2. 生成趋势图（保存到文件）
3. **调用 `feishu_group_sender.send_to_group()` 推送到飞书群（文字）**
4. 输出结果到控制台（供OpenClaw捕获）

### 3. 推送方式
| 目标 | 方式 | 负责方 |
|------|------|--------|
| 飞书群（文字） | `send_to_group()` | 脚本 |
| 个人（文字） | OpenClaw捕获输出 | OpenClaw |
| 飞书群（图片） | 需要额外实现 | 待完成 |

## 关键代码

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace')
from feishu_group_sender import send_to_group

# 计算完成后，推送到群
group_message = f"""✅ MA50占比计算...
...
"""
send_to_group(group_message)

# 输出到控制台（供OpenClaw推送到个人）
print(group_message)
```

## 错误做法（今天犯的错误）
- ❌ 在脚本里直接调用 webhook URL
- ❌ 删除群推送代码
- ❌ 混淆 OpenClaw 推送和脚本推送的职责

## 正确做法
- ✅ 脚本负责：业务逻辑 + 群推送（文字）
- ✅ OpenClaw负责：捕获输出 + 个人推送
- ✅ 两者配合，不是替代关系

## 记忆方法
**"脚本管群，OpenClaw管个人"**

---
记录时间：2026-02-26 15:45
