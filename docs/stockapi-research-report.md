# 开盘啦(StockAPI)数据接口研究报告

## 一、平台概述

| 项目 | 详情 |
|------|------|
| **平台名称** | StockAPI (开盘啦) |
| **官网** | https://www.stockapi.com.cn |
| **定位** | 专业股票数据服务提供商 |
| **特色** | 量化交易数据、竞价数据、资金流向 |
| **认证方式** | Token认证 |

---

## 二、核心数据接口

### 1. 指数数据接口（含成交额）

#### 上证指数
```
GET https://stockapi.com.cn/v1/index/sh?startDate=2026-03-01&endDate=2026-03-04
```

**返回字段：**
| 字段 | 说明 |
|------|------|
| volume | 成交量 |
| **amount** | **成交额** ✅ |
| high | 最高价 |
| low | 最低价 |
| open | 开盘价 |
| close | 收盘价 |
| change | 涨跌 |
| changeRatio | 涨跌幅 |

#### 深圳成指
```
GET https://stockapi.com.cn/v1/index/sz?startDate=2026-03-01&endDate=2026-03-04
```

#### 上证50
```
GET https://stockapi.com.cn/v1/index/sh50?startDate=2026-03-01&endDate=2026-03-04
```

### 2. 市场情绪数据

#### 情绪周期（涨跌停、上涨家数）
```
GET https://stockapi.com.cn/v1/base/emotionalCycle
```
**更新频率：** 交易日17:00

**返回数据：**
- 涨跌停家数统计
- 市场情绪指标（大面/大肉情绪）
- 市场广度指标（上涨家数/比例）
- 打板成功率数据

### 3. 早盘/尾盘抢筹数据

#### 早盘抢筹（9:26更新）
```
GET https://stockapi.com.cn/v1/base/jjqc?tradeDate=2026-03-04&period=0&type=2
```

**参数说明：**
| 参数 | 说明 |
|------|------|
| tradeDate | 交易日期 |
| period | 0=早盘, 1=尾盘 |
| type | 1=委托金额, 2=成交金额, 3=开盘金额, 4=涨幅 |

#### 尾盘抢筹（15:10更新）
```
GET https://stockapi.com.cn/v1/base/jjqc?tradeDate=2026-03-04&period=1&type=2
```

### 4. 个股历史数据

#### 日线数据（含成交额）
```
GET https://stockapi.com.cn/v1/base/day?token=xxx&code=600004&startDate=2026-03-01&endDate=2026-03-04
```

**返回字段：**
| 字段 | 说明 |
|------|------|
| amount | 成交额 ✅ |
| volume | 成交量 |
| turnoverRatio | 换手率 |
| high/low/open/close | 价格数据 |
| change/changeRatio | 涨跌数据 |

---

## 三、技术指标接口

### 1. KDJ指标
```
GET https://stockapi.com.cn/v1/quota/kdj?code=600004&date=2026-03-04
```

### 2. MACD指标
```
GET https://stockapi.com.cn/v1/quota/macd?code=600004&date=2026-03-04
```

### 3. RSI指标
```
GET https://stockapi.com.cn/v1/quota/rsi?code=600004&date=2026-03-04
```

### 4. 移动平均线
```
GET https://stockapi.com.cn/v1/quota/ma2?code=600004&startDate=2026-03-04&endDate=2026-03-04&ma=5,10,20
```

---

## 四、优势与特点

| 优势 | 说明 |
|------|------|
| **专业竞价数据** | 早盘9:26、尾盘15:10抢筹数据 |
| **情绪指标** | 涨跌停家数、市场情绪周期 |
| **技术指标全** | KDJ、MACD、RSI、MA等 |
| **指数数据** | 上证、深证、上证50等 |
| **更新及时** | 实时行情+定时更新 |

---

## 五、使用建议

### 适用场景
✅ 需要早盘/尾盘竞价数据
✅ 需要市场情绪指标
✅ 需要技术指标计算
✅ 需要指数成交额数据

### 注意事项
⚠️ 需要Token认证（可能需要付费）
⚠️ 先测试免费额度
⚠️ 注意接口调用频率限制

---

## 六、下一步行动

1. **申请Token** - 注册获取API密钥
2. **测试接口** - 用curl或Python测试数据获取
3. **验证数据质量** - 对比其他数据源
4. **接入系统** - 整合到现有数据流程

---

*报告生成时间: 2026-03-04 22:40*
