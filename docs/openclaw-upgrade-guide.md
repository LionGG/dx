# OpenClaw 升级经验记录

**版本升级：2026.2.26 → 2026.3.8**
**升级时间：2026-03-10 09:08 ~ 09:18**
**耗时：约10分钟**

---

## ✅ 升级流程（成功版本）

### 1. 检查当前版本
```bash
openclaw --version
```

### 2. 执行升级安装
```bash
npm install -g openclaw@latest
```
- **注意**：npm 安装耗时约5分钟，耐心等待
- 安装完成后需要验证实际使用的版本

### 3. 修复符号链接（关键步骤！）
**问题**：npm 已安装新版本，但系统命令仍指向旧版本
**原因**：符号链接指向 yarn 旧版本

**解决方案**：
```bash
# 找到正确的安装路径
which openclaw
ls -la $(which openclaw)

# 修复符号链接
ln -sf /usr/local/lib/node_modules/openclaw/bin/openclaw.js /usr/local/bin/openclaw
```

### 4. 验证升级成功
```bash
openclaw --version
# 应显示新版本号，如：OpenClaw 2026.3.8 (3caab92)
```

---

## ⚠️ 本次升级的坑

### 1. npm 安装 ≠ 系统可用
**问题**：npm install 显示成功，但 `openclaw --version` 仍是旧版本
**根因**：符号链接未更新，仍指向旧版本的 yarn 安装
**教训**：npm 安装完成后必须验证实际可执行文件的版本

### 2. 符号链接检查
**关键命令**：
```bash
ls -la $(which openclaw)
# 确认链接指向 npm 安装的 node_modules 路径，而非 yarn 路径
```

---

## 📋 升级检查清单

### 升级前
- [ ] 备份当前配置文件：`cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`
- [ ] 记录当前版本：`openclaw --version`
- [ ] 检查定时任务状态，避免升级期间错过任务

### 升级中
- [ ] 执行 `npm install -g openclaw@latest`
- [ ] **耐心等待** npm 安装完成（约5分钟）
- [ ] 检查符号链接：`ls -la $(which openclaw)`
- [ ] 如符号链接错误，手动修复

### 升级后
- [ ] 验证版本：`openclaw --version`
- [ ] 验证配置：`openclaw gateway config.get`
- [ ] 重启 Gateway：`openclaw gateway restart`
- [ ] 验证服务正常：发送测试消息
- [ ] 检查定时任务是否正常运行

---

## 🔧 快速修复命令

如果发现符号链接问题，使用以下一键修复：

```bash
# 1. 找到 npm 安装路径
NPM_PREFIX=$(npm prefix -g)
NEW_OPENCLAW="$NPM_PREFIX/lib/node_modules/openclaw/bin/openclaw.js"

# 2. 备份旧链接
sudo mv $(which openclaw) $(which openclaw).bak

# 3. 创建新链接
sudo ln -sf $NEW_OPENCLAW /usr/local/bin/openclaw

# 4. 验证
openclaw --version
```

---

## 💡 经验教训

### 做得好的地方
1. **耐心等待**：npm 安装耗时5分钟，没有中断
2. **主动排查**：发现版本未变后，主动检查符号链接
3. **及时修复**：发现问题后快速定位并修复

### 需要改进的地方
1. **提前检查**：升级前应该先检查符号链接指向
2. **验证步骤**：npm 安装后应立即验证，而不是等待
3. **文档记录**：符号链接问题耗时约5分钟排查，应提前记录

### 下次升级注意事项
1. **优先检查**：`ls -la $(which openclaw)` 看链接指向
2. **备用方案**：准备符号链接修复命令
3. **时间预留**：预留15分钟升级时间（含排查）
4. **非交易时间**：选择市场闭市时间升级，避免影响定时任务

---

## 📌 关键命令速查

| 操作 | 命令 |
|------|------|
| 检查当前版本 | `openclaw --version` |
| 执行升级 | `npm install -g openclaw@latest` |
| 查看链接指向 | `ls -la $(which openclaw)` |
| 修复符号链接 | `ln -sf /usr/local/lib/node_modules/openclaw/bin/openclaw.js /usr/local/bin/openclaw` |
| 重启 Gateway | `openclaw gateway restart` |

---

## 📝 版本历史

| 日期 | 原版本 | 新版本 | 备注 |
|------|--------|--------|------|
| 2026-03-10 | 2026.2.26 | 2026.3.8 | 首次记录，遇到符号链接问题 |

---

*记录时间: 2026-03-10*
*记录人: 薄荷 🌿*
*下次升级前必读此文档*
