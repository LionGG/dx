#!/usr/bin/env python3
"""
持仓数据库初始化脚本
创建SQLite数据库和相关表结构
"""

import sqlite3
import os

DB_PATH = '/root/.openclaw/workspace/stock-plan/data/portfolio.db'

def init_database():
    """初始化数据库和表结构"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 持仓快照表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id VARCHAR(10) NOT NULL,      -- A/B/C
            trade_date DATE NOT NULL,
            total_assets DECIMAL(15,2),           -- 总资产
            total_profit DECIMAL(15,2),           -- 当日盈亏
            holding_profit DECIMAL(15,2),         -- 持仓盈亏
            leverage_ratio DECIMAL(5,2),          -- 杠杆率
            guarantee_ratio DECIMAL(5,2),         -- 担保比例（A账户）
            debt DECIMAL(15,2),                   -- 融资负债
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, trade_date)
        )
    ''')
    
    # 2. 个股持仓明细表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            account_id VARCHAR(10) NOT NULL,
            trade_date DATE NOT NULL,
            stock_code VARCHAR(10) NOT NULL,
            stock_name VARCHAR(50),
            position_pct DECIMAL(5,2),            -- 仓位占比
            market_value DECIMAL(15,2),           -- 市值
            float_profit DECIMAL(15,2),           -- 浮动盈亏
            shares INTEGER,                       -- 股数
            cost_price DECIMAL(10,3),             -- 成本价
            current_price DECIMAL(10,3),          -- 当前价
            daily_profit DECIMAL(15,2),           -- 当日盈亏
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (snapshot_id) REFERENCES portfolio_snapshots(id),
            UNIQUE(account_id, trade_date, stock_code)
        )
    ''')
    
    # 3. 交易记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id VARCHAR(10) NOT NULL,
            trade_date DATE NOT NULL,
            stock_code VARCHAR(10) NOT NULL,
            stock_name VARCHAR(50),
            action VARCHAR(10),                   -- buy/sell
            shares INTEGER,
            price DECIMAL(10,3),
            amount DECIMAL(15,2),
            reason TEXT,                          -- 交易理由
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. 点评/分析报告表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id VARCHAR(10),               -- A/B/C/ALL
            trade_date DATE NOT NULL,
            review_type VARCHAR(20),              -- daily/weekly/summary
            overall_rating VARCHAR(10),           -- 优秀/良好/需改进/危险
            key_issues TEXT,                      -- 主要问题（JSON）
            recommendations TEXT,                 -- 建议（JSON）
            psychology_status VARCHAR(20),        -- 心情状态
            raw_content TEXT,                     -- 完整点评文本
            created_by VARCHAR(20),               -- 薄荷/球球
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, trade_date, review_type)
        )
    ''')
    
    # 5. 交易计划表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id VARCHAR(10) NOT NULL,
            plan_date DATE NOT NULL,
            target_stocks TEXT,                   -- 目标股票（JSON）
            action_type VARCHAR(20),              -- buy/sell/hold
            price_range VARCHAR(50),              -- 价格区间
            position_limit DECIMAL(5,2),          -- 仓位限制
            stop_loss DECIMAL(5,2),               -- 止损位
            take_profit DECIMAL(5,2),             -- 止盈位
            reasoning TEXT,                       -- 理由
            executed BOOLEAN DEFAULT 0,           -- 是否执行
            executed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. 心情/心理记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS psychology_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL,
            account_id VARCHAR(10),               -- 关联账户（可选）
            mood_score INTEGER,                   -- 心情分数 1-10
            anxiety_level INTEGER,                -- 焦虑程度 1-10
            key_events TEXT,                      -- 关键事件
            self_reflection TEXT,                 -- 自我反思
            coping_strategy TEXT,                 -- 应对策略
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshot_account_date ON portfolio_snapshots(account_id, trade_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_holding_account_date ON stock_holdings(account_id, trade_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_date ON trade_records(trade_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_review_date ON trade_reviews(trade_date)')
    
    conn.commit()
    conn.close()
    
    print(f'✅ 数据库初始化完成: {DB_PATH}')
    print('创建的表:')
    print('  - portfolio_snapshots (持仓快照)')
    print('  - stock_holdings (个股持仓明细)')
    print('  - trade_records (交易记录)')
    print('  - trade_reviews (点评/分析报告)')
    print('  - trade_plans (交易计划)')
    print('  - psychology_logs (心情/心理记录)')

if __name__ == '__main__':
    init_database()
