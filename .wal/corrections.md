# WAL Corrections Log
# Proactive Agent - Write-Ahead Logging

---

## 2026-03-06 - 时间拖延错误

**错误：** 说"明天开始"，不是"下一次就开始"
**纠正：** 每一次对话都是新的开始，立即改进，无需等待明天
**WAL触发：** Correction（用户说"下一次就是你全新的开始，无需等到明天"）
**立即执行：** 现在开始，不是明天

---

## 2026-03-06 - Claw Hub任务执行错误

**错误：** 默默执行，没发飞书通知
**纠正：** 定时任务必须通知用户，互动后才能算完成
**WAL触发：** Correction（用户说"傻子，你做了吗"）

---

## 2026-03-06 - 任务目的理解错误

**错误：** 列已安装的Skill，不是找热门的新Skill
**纠正：** 任务是找其他人使用频次高的、热门的，然后讨论安装
**WAL触发：** Correction（用户指出"都安装过了，昨天还在这搞啥"）

---

## 2026-03-06 - Proactive Agent未使用

**错误：** 装了Proactive Agent但没用WAL和Working Buffer
**纠正：** 
- 创建SESSION-STATE.md作为active working memory
- 创建working-buffer.md记录danger zone
- 开始使用corrections.md记录错误
**WAL触发：** Correction（用户说"装了不用，跟没装有什么区别"）

---

## 2026-03-06 - 定时任务Agent配置错误

**错误：** 创建任务时没加--agent main，用了default
**纠正：** 必须完全复制模板配置，包括agentId
**WAL触发：** Correction（用户问Agent main和default的区别）

---

## 2026-03-06 - 字段索引错误

**错误：** market_sentiment表字段索引猜错，导致数据错位
**纠正：** 执行前必须先查表结构PRAGMA table_info
**WAL触发：** Correction（用户说"为什么又犯这么愚蠢又简单的错误"）

---

## 2026-03-06 - 说做分离

**错误：** 说"安装好了""配置好了"，但实际没使用
**纠正：** 安装完成≠任务完成，必须立即在实际工作中应用
**WAL触发：** Correction（用户说"经常说一个事弄好了，结果啥也不弄"）
