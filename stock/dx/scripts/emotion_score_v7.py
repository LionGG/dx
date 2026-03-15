#!/usr/bin/env python3
"""
短线情绪值计算模块 - V7最终版

最终公式:
情绪值 = 20 + 涨停×0.4 - 跌停×0.7 + 涨跌比映射(0-25) + (封板率-70%)×0.3

记录时间: 2026-03-07 16:35
"""

def calculate_emotion_score(limit_up, limit_down, up_count, down_count, sealing_rate):
    """
    计算短线情绪值
    
    参数:
        limit_up: 涨停数
        limit_down: 跌停数  
        up_count: 上涨家数
        down_count: 下跌家数
        sealing_rate: 封板率 (%)
    
    返回:
        emotion_score: 情绪值 (0-100)
    """
    # 1. 基础分
    base_score = 20
    
    # 2. 涨停加分 (+0.4/个)
    limit_up_score = limit_up * 0.4
    
    # 3. 跌停减分 (-0.7/个)
    limit_down_score = limit_down * 0.7
    
    # 4. 涨跌比映射 (0-25分)
    # 涨跌比 = 上涨家数 / 下跌家数
    if down_count == 0:
        adr_ratio = 10.0  # 极端情况，全部上涨
    else:
        adr_ratio = up_count / down_count
    
    # 映射到0-25分 (线性映射: ratio=0->0分, ratio=5->25分)
    adr_score = min(25, max(0, adr_ratio * 5))
    
    # 5. 封板率调整 ((封板率-70%)×0.3)
    # 封板率>70%加分, <70%减分
    sealing_adjustment = (sealing_rate - 70) * 0.3
    
    # 计算总分
    total = base_score + limit_up_score - limit_down_score + adr_score + sealing_adjustment
    
    # 限制在0-100范围
    total = max(0, min(100, total))
    
    return round(total, 2)


def get_emotion_grade(score):
    """
    根据情绪值判断档位
    
    档位:
        高情绪: ≥65分
        中情绪: 45-65分
        低情绪: <45分
    """
    if score >= 65:
        return "高情绪", "积极做多"
    elif score >= 45:
        return "中情绪", "谨慎操作"
    else:
        return "低情绪", "控制风险"


if __name__ == "__main__":
    # 测试示例
    test_cases = [
        # (涨停, 跌停, 上涨家数, 下跌家数, 封板率)
        (80, 5, 3500, 1500, 75),   # 高情绪场景
        (40, 20, 2000, 3000, 65),  # 中情绪场景
        (20, 50, 800, 4200, 55),   # 低情绪场景
    ]
    
    print("情绪值计算测试 (V7公式):")
    print("公式: 情绪值 = 20 + 涨停×0.4 - 跌停×0.7 + 涨跌比映射(0-25) + (封板率-70%)×0.3")
    print("-" * 60)
    
    for limit_up, limit_down, up_count, down_count, sealing_rate in test_cases:
        score = calculate_emotion_score(limit_up, limit_down, up_count, down_count, sealing_rate)
        grade, advice = get_emotion_grade(score)
        
        print(f"涨停:{limit_up} 跌停:{limit_down} 涨跌比:{up_count}/{down_count} 封板率:{sealing_rate}%")
        print(f"  -> 情绪值: {score}分 ({grade}) - {advice}")
        print()
