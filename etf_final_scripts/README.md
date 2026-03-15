# ETF每日计算指标 - 最终版脚本

## 脚本清单

### 1. batch_calc_etf.py (核心定时任务)
- **用途**: 每日定时任务执行的完整计算脚本
- **功能**: 
  - 内置V5.2完整趋势分公式
  - 52只ETF批量计算
  - 交易日判断、数据检查、防重复
  - 飞书通知、日志记录
- **依赖**: trend_score_v52_final.py, db_config.py

### 2. calc_etf_full_v52.py (单独计算)
- **用途**: 手动计算单只ETF完整指标
- **功能**: RS强度、流动性、趋势分、档位
- **适用**: 测试、补算、单独ETF计算

### 3. trend_score_v52_final.py (趋势分公式)
- **用途**: 趋势分计算核心算法
- **关键**: V5.2版，3/4多头排列+0.5分，完美4/4+1.0分
- **保底**: 完美多头+站上5日线保底3.85分

### 4. db_config.py (数据库配置)
- **用途**: 统一从secrets加载数据库配置
- **依赖**: ~/.openclaw/secrets/secrets.json

## 使用方式

### 定时任务（每日）
```bash
cd /root/.openclaw/workspace/projects/etf-indicators/scripts
python3 batch_calc_etf.py
```

### 单只ETF计算
```bash
python3 calc_etf_full_v52.py 159326
```

### 趋势分测试
```python
from trend_score_v52_final import calculate_trend_score_v52
result = calculate_trend_score_v52('002961', '2026-03-06')
```

## 注意事项
- 脚本依赖etf_history表和index_history表
- 数据库配置从secrets.json读取
- batch_calc_etf.py已内置完整计算逻辑，不依赖其他脚本
