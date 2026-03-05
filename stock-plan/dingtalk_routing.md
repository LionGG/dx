# 钉钉通道 - 交易助手路由配置

## 通道绑定
- **钉钉** → trade-assistant 子代理
- **飞书** → main Agent（主助手）

## 交易助手功能

### 1. 记录交易计划
发送格式：
```
明天北方华创突破28就进，2成仓，27止损
```

### 2. 查询持仓
发送：
```
查询持仓
```

### 3. 发送截图
直接发送持仓截图，自动识别分析

### 4. 复盘记录
发送格式：
```
复盘：今天没按计划买，犹豫了
```

## 数据存储
- 数据库：stock-plan/agents/trade-assistant/trade_notes.db
- 用户档案：stock-plan/memory/user_profile.md

## 市场数据
自动复用：a-share-dx 短线情绪研判数据
