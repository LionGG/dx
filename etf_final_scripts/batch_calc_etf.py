#!/usr/bin/env python3
"""
批量计算ETF指标 - 定时任务版
更新日期: 2026-03-09
功能: 数据检查、防重复、交易日判断、日志记录、错误通知
"""

import sys
import os
import json
import pymysql
import logging
import subprocess
import math
from datetime import datetime

# 添加交易日判断工具路径
sys.path.insert(0, '/root/.openclaw/workspace/stock/a-share-warehouse/scripts')
from trading_date import is_trading_date

# 配置日志
LOG_DIR = '/root/.openclaw/workspace/projects/etf-indicators/logs'
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f'{LOG_DIR}/cron.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 添加控制台输出
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# 从secrets加载数据库配置
def load_db_config():
    """从secrets加载数据库配置"""
    secrets_path = os.path.expanduser("~/.openclaw/secrets/secrets.json")
    try:
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
        
        for secret in secrets.get('secrets', []):
            if secret.get('name') == 'mysql-choose-stock':
                entries = {entry['key']: entry['value'] for entry in secret.get('entries', [])}
                return {
                    "host": entries.get('host'),
                    "port": int(entries.get('port', 3306)),
                    "user": entries.get('user'),
                    "password": entries.get('password'),
                    "database": entries.get('database'),
                    "charset": "utf8mb4"
                }
    except Exception as e:
        logging.error(f"加载数据库配置失败: {e}")
    
    return None

DB_CONFIG = load_db_config()

# 飞书配置
FEISHU_USER_ID = "ou_7b3b64c0a18c735401f4e1d172d4c802"  # 宝总个人ID

# 固定的52只ETF列表（由用户确认）
ETF_LIST = [
    '159218', '159326', '159516', '159567', '159590', '159611', '159713', '159755',
    '159819', '159845', '159851', '159865', '159869', '159920', '159928', '159949',
    '159985',  # 2026-03-09新增
    '510300', '510500', '512200', '512400', '512480', '512690', '512710', '512800',
    '512880', '512980', '513090', '513100', '513120', '513130', '513310', '513500',
    '513520', '513630', '515030', '515220', '515790', '515880', '516020', '516160',
    '516510', '516950', '518880', '560080', '560860', '562500', '563300', '563360',
    '588000', '588200', '588790'
]

def check_data_ready(target_date):
    """检查ETF历史数据是否已入库"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT COUNT(DISTINCT stock_code) 
            FROM etf_history 
            WHERE trade_date = '{target_date}' AND deleted = 0
        """)
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count >= 52:  # 应该有52只ETF的数据
            return True, f"数据就绪，共{count}只ETF"
        else:
            return False, f"数据未就绪，只有{count}只ETF（需51只）"
    except Exception as e:
        return False, f"数据检查出错: {e}"

def check_already_calculated(target_date):
    """检查是否已计算过"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM etf_indicators 
            WHERE trade_date = '{target_date}'
        """)
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count >= 52:
            return True, f"已计算过，共{count}条记录"
        else:
            return False, f"未计算完整，只有{count}条记录"
    except Exception as e:
        return False, f"检查出错: {e}"

def send_feishu_notification(message):
    """发送飞书通知给宝总个人"""
    try:
        # 使用openclaw message工具发送
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "-t", FEISHU_USER_ID,
            "--message", message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logging.info(f"飞书通知发送成功: {message[:50]}...")
            return True
        else:
            logging.error(f"飞书通知发送失败: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"飞书通知发送异常: {e}")
        return False

def send_notification(success, message, target_date):
    """发送执行结果通知（日志+飞书）"""
    if success:
        full_msg = f"✅ ETF指标计算完成 [{target_date}]\n\n{message}"
        logging.info(full_msg)
        print(full_msg)
        send_feishu_notification(full_msg)
    else:
        full_msg = f"❌ ETF指标计算失败 [{target_date}]\n\n{message}"
        logging.error(full_msg)
        print(full_msg)
        send_feishu_notification(full_msg)
    return full_msg

def get_liquidity_grade(amount_yi):
    """流动性档位"""
    if amount_yi >= 10: return "S"
    elif amount_yi >= 5: return "A"
    elif amount_yi >= 2: return "B"
    else: return "C"

def calculate_volatility(prices, days):
    """计算N日年化波动率
    prices: 价格列表（按时间顺序）
    days: 计算周期（20或60）
    返回: 年化波动率（百分比）
    """
    if len(prices) < days + 1:
        return None
    
    # 取最近days+1天的数据计算days个收益率
    recent_prices = prices[-(days+1):]
    
    # 计算日收益率
    returns = []
    for i in range(1, len(recent_prices)):
        daily_return = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
        returns.append(daily_return)
    
    # 计算标准差
    mean = sum(returns) / len(returns)
    variance = sum([(r - mean) ** 2 for r in returns]) / len(returns)
    std_dev = math.sqrt(variance)
    
    # 年化（假设252个交易日）
    annualized_vol = std_dev * math.sqrt(252) * 100  # 转换为百分比
    
    return annualized_vol

def calculate_volume_strength(amounts, target_idx):
    """计算成交强度得分
    amounts: 成交额列表（按时间顺序，单位：元）
    target_idx: 目标日期在列表中的索引
    返回: 成交强度得分（0-100）
    """
    # 需要至少125天数据（120日历史 + 5日当前）
    if target_idx < 124:
        return None
    
    # 当前5日成交额
    current_5d = sum(amounts[target_idx-4:target_idx+1])
    
    # 近5日均额和近20日均额（用于动量计算）
    avg_5d = current_5d / 5
    avg_20d = sum(amounts[target_idx-19:target_idx+1]) / 20
    
    # 历史5日成交额列表（过去120日，每天向前滚动5日）
    historical_5d = []
    for i in range(target_idx-119, target_idx+1):  # 包含当前日
        if i >= 4:  # 确保有足够数据
            historical_5d.append(sum(amounts[i-4:i+1]))
    
    if len(historical_5d) < 20:  # 至少需要20个样本
        return None
    
    # 计算分位数（当前5日成交额在历史中的排名）
    sorted_hist = sorted(historical_5d)
    rank = 0
    for i, val in enumerate(sorted_hist):
        if val >= current_5d:
            rank = i
            break
    else:
        rank = len(sorted_hist)
    
    percentile = (rank / len(sorted_hist)) * 100
    
    # 计算动量加速度
    if avg_20d > 0:
        momentum = (avg_5d - avg_20d) / avg_20d
    else:
        momentum = 0
    
    # 动量映射到0-100分（-50%~+50% 映射到 0-100分）
    momentum_score = min(100, max(0, 50 + momentum * 50))
    
    # 最终得分：分位×0.6 + 动量×0.4
    vol_score = percentile * 0.6 + momentum_score * 0.4
    
    return round(min(100, max(0, vol_score)), 2)

def calculate_etf_for_date(etf_code, target_date):
    """计算单只ETF指定日期的指标 - 使用完整V5.2趋势分公式"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 获取ETF历史数据（需要150天用于计算均线）
        cursor.execute(f"""
            SELECT trade_date, close_price, amount
            FROM etf_history
            WHERE stock_code = '{etf_code}' AND deleted = 0
            AND trade_date <= '{target_date}'
            ORDER BY trade_date ASC
        """)
        rows = cursor.fetchall()
        
        if len(rows) < 150:
            return None, f"数据不足150天，只有{len(rows)}天"
        
        # 找到目标日期
        target_row = None
        target_idx = -1
        for i, row in enumerate(rows):
            if str(row[0]) == target_date:
                target_row = row
                target_idx = i
                break
        
        if not target_row or target_idx < 120:
            return None, f"无{target_date}数据或数据不足120天"
        
        close_price = float(target_row[1])
        
        # 获取沪深300数据
        cursor.execute(f"""
            SELECT trade_date, close_price
            FROM index_history
            WHERE stock_code = '000300' AND deleted = 0
            AND trade_date <= '{target_date}'
            ORDER BY trade_date ASC
        """)
        index_rows = cursor.fetchall()
        
        if len(index_rows) < 52:
            return None, "指数数据不足"
        
        # 计算均线 (使用pandas风格)
        prices = [float(r[1]) for r in rows[:target_idx+1]]
        
        ma5 = sum(prices[-5:]) / 5
        ma10 = sum(prices[-10:]) / 10
        ma20 = sum(prices[-20:]) / 20
        ma60 = sum(prices[-60:]) / 60
        ma120 = sum(prices[-120:]) / 120
        
        # 计算RS指标
        etf_now = prices[-1]
        etf_21d = prices[-22] if len(prices) >= 22 else prices[0]
        etf_52d = prices[-53] if len(prices) >= 53 else prices[0]
        
        idx_prices = [float(r[1]) for r in index_rows]
        idx_now = idx_prices[-1]
        idx_21d = idx_prices[-22] if len(idx_prices) >= 22 else idx_prices[0]
        idx_52d = idx_prices[-53] if len(idx_prices) >= 53 else idx_prices[0]
        
        etf_ret_21d = (etf_now / etf_21d - 1) * 100
        idx_ret_21d = (idx_now / idx_21d - 1) * 100
        rs_21d = etf_ret_21d - idx_ret_21d
        
        etf_ret_52d = (etf_now / etf_52d - 1) * 100
        idx_ret_52d = (idx_now / idx_52d - 1) * 100
        rs_52d = etf_ret_52d - idx_ret_52d
        
        # 计算流动性
        avg_amount = sum([float(r[2]) for r in rows[max(0, target_idx-4):target_idx+1]]) / 5 / 100000000
        liquidity_grade = get_liquidity_grade(avg_amount)
        
        # 计算趋势分 - 使用完整V5.2公式 (与trend_score_v52_final.py一致)
        p = close_price
        
        # 1. 计算各距离
        dist_ma5 = (p / ma5 - 1) * 100
        dist_ma10 = (p / ma10 - 1) * 100
        dist_ma20 = (p / ma20 - 1) * 100
        dist_ma60 = (p / ma60 - 1) * 100
        dist_ma120 = (p / ma120 - 1) * 100
        
        dist_5_10 = (ma5 / ma10 - 1) * 100
        dist_10_20 = (ma10 / ma20 - 1) * 100
        dist_20_60 = (ma20 / ma60 - 1) * 100
        dist_60_120 = (ma60 / ma120 - 1) * 100
        
        r20 = (p - prices[-21]) / prices[-21] * 100 if len(prices) >= 21 else 0
        
        # 2. 计算各维度分数 (与trend_score_v52_final.py完全一致)
        # 短期均线分
        d5 = dist_ma5
        if d5 >= 8: short_score = 0.8
        elif d5 >= 3: short_score = 0.5 + (d5 - 3) * 0.06
        elif d5 >= -0.5: short_score = 0.35 + d5 * 0.05
        elif d5 >= -4: short_score = max(0.15, 0.325 + (d5 + 0.5) * 0.05)
        elif d5 >= -7: short_score = max(-0.1, 0.2 + (d5 + 4) * 0.033)
        else: short_score = max(-0.35, -0.1 + (d5 + 7) * 0.05)
        
        # 中期均线分
        d20 = dist_ma20
        if d20 >= 12: m1 = 0.55
        elif d20 >= 0: m1 = 0.22 + d20 * 0.0275
        elif d20 >= -10: m1 = max(0.1, 0.22 + d20 * 0.022)
        else: m1 = max(-0.15, 0.1 + (d20 + 10) * 0.02)
        
        d60 = dist_ma60
        if d60 >= 15: m2 = 0.55
        elif d60 >= 0: m2 = 0.22 + d60 * 0.022
        elif d60 >= -12: m2 = max(0.1, 0.22 + d60 * 0.018)
        else: m2 = max(-0.15, 0.1 + (d60 + 12) * 0.017)
        mid_score = (m1 + m2) / 2
        
        # 长期均线分
        d120 = dist_ma120
        if d120 >= 40: long_score = 0.35
        elif d120 >= 0: long_score = 0.12 + d120 * 0.00575
        elif d120 >= -15: long_score = max(0.05, 0.12 + d120 * 0.0047)
        else: long_score = max(-0.15, 0.05 + (d120 + 15) * 0.01)
        
        # 均线排列分 (4项，与trend_score_v52_final.py一致)
        d = dist_5_10
        if d >= 2: a1 = 0.38
        elif d >= 0: a1 = 0.12 + d * 0.13
        elif d >= -5: a1 = max(-0.08, d * 0.016)
        else: a1 = -0.12
        
        d = dist_10_20
        if d >= 3: a2 = 0.38
        elif d >= 0: a2 = 0.12 + d * 0.087
        elif d >= -5: a2 = max(-0.08, d * 0.016)
        else: a2 = -0.12
        
        d = dist_20_60
        if d >= 3: a3 = 0.38
        elif d >= 0: a3 = 0.15 + d * 0.077
        elif d >= -5: a3 = max(-0.1, d * 0.014)
        else: a3 = max(-0.2, -0.1 + (d+5) * 0.02)
        
        d = dist_60_120
        if d >= 8: a4 = 0.38
        elif d >= 0: a4 = 0.12 + d * 0.0325
        elif d >= -8: a4 = max(-0.08, d * 0.01)
        else: a4 = -0.12
        
        align_score = a1 + a2 + a3 + a4
        
        # 3. 判断多头排列 (关键：MA60>MA120标准是>-1%，不是>0)
        is_bull_5_10 = dist_5_10 > 0
        is_bull_10_20 = dist_10_20 > 0
        is_bull_20_60 = dist_20_60 > 0
        is_bull_60_120 = dist_60_120 > -1  # 标准是>-1%，不是>0
        
        bull_count = sum([is_bull_5_10, is_bull_10_20, is_bull_20_60, is_bull_60_120])
        is_perfect_bull = bull_count == 4
        is_3of4_bull = bull_count == 3
        is_above_ma5 = dist_ma5 > -0.5
        
        # 4. 多头排列加分 (V5.2)
        bull_bonus = 0
        if is_perfect_bull and is_above_ma5:
            bull_bonus = 1.0
        elif is_perfect_bull and not is_above_ma5:
            bull_bonus = 0.5
        elif is_3of4_bull and is_above_ma5:
            bull_bonus = 0.5
        
        # 5. 主升浪加分
        main_wave_bonus = 0.3 if (r20 > 50 and bull_count >= 3) else 0
        
        # 6. 总分 (关键：截距0.75)
        bias = 0.75
        total = bias + short_score + mid_score + long_score + align_score + bull_bonus + main_wave_bonus
        
        # 保底3.85分
        if is_perfect_bull and is_above_ma5 and total < 3.85:
            total = 3.85
        
        trend_score = max(0.0, min(5.0, round(total, 1)))
        
        # 计算波动率
        volatility_20d = calculate_volatility(prices, 20)
        volatility_60d = calculate_volatility(prices, 60)
        volatility_ratio = volatility_20d / volatility_60d if volatility_60d and volatility_60d > 0 else None
        
        # 计算成交强度
        amounts = [float(r[2]) for r in rows[:target_idx+1]]
        volume_strength = calculate_volume_strength(amounts, target_idx)
        
        result = {
            'stock_code': etf_code,
            'trade_date': target_date,
            'close_price': round(close_price, 4),
            'rs_21d': round(rs_21d, 4),
            'etf_return_21d': round(etf_ret_21d, 4),
            'index_return_21d': round(idx_ret_21d, 4),
            'rs_52d': round(rs_52d, 4),
            'etf_return_52d': round(etf_ret_52d, 4),
            'index_return_52d': round(idx_ret_52d, 4),
            'avg_amount_5d': round(avg_amount, 4),
            'liquidity_grade': liquidity_grade,
            'trend_score': round(trend_score, 2),
            'volatility_20d': round(volatility_20d, 4) if volatility_20d else None,
            'volatility_ratio': round(volatility_ratio, 4) if volatility_ratio else None,
            'volume_strength': volume_strength
        }
        
        return result, None
        
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def save_to_db(result):
    """保存结果到数据库"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO etf_indicators 
            (stock_code, trade_date, close_price, rs_21d, etf_return_21d, index_return_21d,
             rs_52d, etf_return_52d, index_return_52d, avg_amount_5d, liquidity_grade,
             trend_score, volatility_20d, volatility_ratio, volume_strength, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
            close_price=VALUES(close_price), rs_21d=VALUES(rs_21d), 
            etf_return_21d=VALUES(etf_return_21d), index_return_21d=VALUES(index_return_21d),
            rs_52d=VALUES(rs_52d), etf_return_52d=VALUES(etf_return_52d), 
            index_return_52d=VALUES(index_return_52d), avg_amount_5d=VALUES(avg_amount_5d),
            liquidity_grade=VALUES(liquidity_grade), trend_score=VALUES(trend_score),
            volatility_20d=VALUES(volatility_20d),
            volatility_ratio=VALUES(volatility_ratio), volume_strength=VALUES(volume_strength), update_time=NOW()
        """, (result['stock_code'], result['trade_date'], result['close_price'],
              result['rs_21d'], result['etf_return_21d'], result['index_return_21d'],
              result['rs_52d'], result['etf_return_52d'], result['index_return_52d'],
              result['avg_amount_5d'], result['liquidity_grade'],
              result['trend_score'],
              result['volatility_20d'], result['volatility_ratio'], result['volume_strength']))
        
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"保存失败: {e}")
        return False
    finally:
        conn.close()

def batch_calculate(target_date):
    """批量计算所有ETF"""
    logging.info(f"开始批量计算 {target_date} ETF指标")
    
    success = 0
    failed = 0
    errors = []
    
    for i, etf_code in enumerate(ETF_LIST, 1):
        try:
            result, error = calculate_etf_for_date(etf_code, target_date)
            
            if result:
                if save_to_db(result):
                    success += 1
                    if i % 10 == 0:
                        logging.info(f"已处理 {i}/{len(ETF_LIST)} 只ETF")
                else:
                    failed += 1
                    errors.append(f"{etf_code}: 保存失败")
            else:
                failed += 1
                errors.append(f"{etf_code}: {error}")
                
        except Exception as e:
            failed += 1
            errors.append(f"{etf_code}: {e}")
    
    logging.info(f"批量计算完成: 成功{success}, 失败{failed}")
    return success, failed, errors

def main():
    """主函数 - 定时任务入口"""
    # 获取目标日期
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    logging.info("="*70)
    logging.info(f"ETF指标定时任务启动 - 目标日期: {target_date}")
    logging.info("="*70)
    
    # 1. 检查是否为交易日
    if not is_trading_date(target_date):
        msg = f"{target_date} 非交易日，跳过"
        logging.info(msg)
        print(msg)
        return
    
    # 2. 检查数据是否就绪
    ready, msg = check_data_ready(target_date)
    logging.info(f"数据检查: {msg}")
    if not ready:
        send_notification(False, f"数据未就绪: {msg}", target_date)
        return
    
    # 3. 检查是否已计算
    already_done, msg = check_already_calculated(target_date)
    logging.info(f"重复检查: {msg}")
    if already_done:
        send_notification(True, f"已计算过，跳过: {msg}", target_date)
        return
    
    # 4. 执行计算
    logging.info(f"开始计算 52 只ETF...")
    success, failed, errors = batch_calculate(target_date)
    
    # 5. 发送通知
    if failed == 0:
        send_notification(True, f"全部成功，共{success}只", target_date)
    else:
        error_msg = f"成功{success}只, 失败{failed}只"
        if errors:
            error_msg += f"\n错误详情: {', '.join(errors[:5])}"
        send_notification(False, error_msg, target_date)
    
    logging.info("="*70)
    logging.info("定时任务结束")
    logging.info("="*70)

if __name__ == "__main__":
    main()
