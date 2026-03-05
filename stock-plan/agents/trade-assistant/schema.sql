-- 交易助手数据库 Schema

-- 交易计划表
CREATE TABLE trade_plans (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    raw_content TEXT,
    symbol TEXT,
    name TEXT,
    action TEXT CHECK(action IN ('buy', 'sell', 'hold', 'watch')),
    condition_type TEXT CHECK(condition_type IN ('price_break', 'price_below', 'volume', 'indicator', 'time')),
    condition_value REAL,
    position_pct REAL,
    stop_loss REAL,
    take_profit REAL,
    sentiment_score INTEGER,
    certainty_level TEXT CHECK(certainty_level IN ('high', 'medium', 'low')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'executed', 'cancelled', 'expired'))
);

-- 持仓截图识别表
CREATE TABLE position_screenshots (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    image_url TEXT,
    parsed_data TEXT,  -- JSON格式持仓列表
    uploaded_at TEXT
);

-- 执行记录表
CREATE TABLE trade_executions (
    id TEXT PRIMARY KEY,
    plan_id TEXT,
    executed_at TEXT,
    actual_price REAL,
    actual_position REAL,
    followed_plan BOOLEAN,
    deviation_reason TEXT,
    screenshot_id TEXT,
    FOREIGN KEY (plan_id) REFERENCES trade_plans(id),
    FOREIGN KEY (screenshot_id) REFERENCES position_screenshots(id)
);

-- 复盘记录表
CREATE TABLE trade_reviews (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    raw_content TEXT,
    emotion_tag TEXT CHECK(emotion_tag IN ('excited', 'hesitant', 'anxious', 'regretful', 'calm')),
    lesson_extracted TEXT,
    related_plan_id TEXT,
    FOREIGN KEY (related_plan_id) REFERENCES trade_plans(id)
);

-- 每日汇总表
CREATE TABLE daily_summaries (
    date TEXT PRIMARY KEY,
    plan_count INTEGER DEFAULT 0,
    execution_count INTEGER DEFAULT 0,
    execution_rate REAL DEFAULT 0,
    deviation_count INTEGER DEFAULT 0,
    summary_text TEXT,
    generated_at TEXT
);

-- 创建索引
CREATE INDEX idx_plans_date ON trade_plans(date);
CREATE INDEX idx_plans_symbol ON trade_plans(symbol);
CREATE INDEX idx_plans_status ON trade_plans(status);
CREATE INDEX idx_executions_plan ON trade_executions(plan_id);
CREATE INDEX idx_reviews_date ON trade_reviews(date);
