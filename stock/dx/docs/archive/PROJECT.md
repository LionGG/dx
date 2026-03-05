# A-Share Duanxian 短线情绪研判项目

## 项目概述

A股短线情绪周期分析与可视化系统。从短线侠网站抓取市场情绪数据，生成每日情绪研判报告，并通过网页可视化展示。

**创建时间**: 2026-02-22  
**状态**: V1.0 已完成，待验证自动更新  
**部署地址**: GitHub Pages

---

## 文档索引

| 文档 | 说明 |
|------|------|
| `PROJECT.md` | 本文件 - 项目概述和结构 |
| `OPERATIONS.md` | 自动化操作流程 - 每日执行步骤 |
| `prompt.md` | AI分析Prompt模板 |
| `SKILL.md` | Skill定义（供OpenClaw调用） |

---

## 项目结构

```
a-share-duanxian/
├── PROJECT.md              # 本文件 - 项目说明
├── prompt.md               # AI分析Prompt模板
├── crawler_trading_day.py  # 数据抓取脚本
├── generate_html.py        # 生成可视化网页
├── qingxu_data.json        # 情绪数据（原始）
├── duanxianxia_data.db     # SQLite数据库
└── web/                    # 可视化网站
    ├── index.html          # 主页面
    ├── data.json           # 图表数据
    └── js/                 # JavaScript文件
```

---

## 核心功能

### 1. 数据抓取
- **源站**: 短线侠 (duanxianxia.com)
- **数据项**: 情绪指数、涨停数、跌停数、连板高度、封板率等
- **频率**: 每个交易日

### 2. 数据分析
- **Prompt**: `prompt.md` 定义分析框架
- **输出**: 每日情绪研判报告
- **发布**: 自动保存到墨问笔记

### 3. 可视化
- **框架**: ECharts
- **图表**: 
  - 情绪指数走势图
  - 涨停/跌停对比
  - 连板高度变化
  - 封板率趋势
- **交互**: 日期切换、指标筛选

---

## 定时任务

| 时间 | 任务 | 脚本 |
|------|------|------|
| 15:45 | 抓取当日情绪数据 | `crawler_trading_day.py` |
| 18:00 | 生成分析报告 | AI分析 + 发布到墨问 |
| 自动 | 更新可视化数据 | `generate_html.py` |

---

## 待验证事项

- [ ] 02-24 观察定时任务是否自动执行
- [ ] 检查数据是否正确抓取
- [ ] 验证分析报告是否正确生成
- [ ] 确认网页数据是否自动更新

---

## 使用说明

### 手动更新数据
```bash
cd /root/.openclaw/workspace/stock/a-share-duanxian
python3 crawler_trading_day.py
```

### 生成网页
```bash
python3 generate_html.py
```

### 部署到GitHub Pages
```bash
./deploy_to_github.sh
```

---

## 版本历史

- **v1.0** (2026-02-22): 初始版本，完成数据抓取、分析、可视化全流程

---

## 相关文件

- 项目根目录: `/root/.openclaw/workspace/stock/a-share-duanxian/`
- 主数据库: `/root/.openclaw/workspace/stock/akshare_full.db` (共享)
- 定时配置: `/root/.openclaw/workspace/stock/CRONTAB.md`
