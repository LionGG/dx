#!/usr/bin/env python3
"""
测试三种数据获取方案
1. 新浪财经API
2. akshare（东方财富）
3. 开盘啦APP接口（如有可用）
"""

import requests
import json
from datetime import datetime, timedelta

# 测试1: 新浪财经API - 指数数据
def test_sina_api():
    """测试新浪财经API"""
    print("="*60)
    print("测试1: 新浪财经API")
    print("="*60)
    
    # 上证指数、创业板指、科创50
    indices = {
        'sh000001': '上证指数',
        'sz399006': '创业板指', 
        'sh000688': '科创50'
    }
    
    results = {}
    for code, name in indices.items():
        url = f"https://hq.sinajs.cn/list={code}"
        headers = {"Referer": "https://finance.sina.com.cn"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.text.split('"')[1].split(',')
            results[name] = {
                'code': code,
                'name': data[0],  # 股票名称（可能有乱码）
                'open': data[1],
                'close': data[3],
                'high': data[4],
                'low': data[5],
                'volume': data[8],  # 成交量
                'amount': data[9],  # 成交额
                'status': 'success'
            }
            print(f"✅ {name}: 收盘{data[3]}, 成交额{float(data[9])/100000000:.2f}亿")
        except Exception as e:
            results[name] = {'status': 'failed', 'error': str(e)}
            print(f"❌ {name}: {e}")
    
    return results

# 测试2: akshare（如果可用）
def test_akshare():
    """测试akshare"""
    print("\n" + "="*60)
    print("测试2: akshare")
    print("="*60)
    
    try:
        import akshare as ak
        # 获取指数历史数据
        df = ak.index_zh_a_hist(symbol="000001", period="daily", 
                                start_date="20250225", end_date="20260304")
        print(f"✅ akshare可用，获取到{len(df)}条数据")
        print(df[['日期', '收盘', '成交额']].tail(3))
        return {'status': 'success', 'count': len(df)}
    except ImportError:
        print("❌ akshare未安装")
        return {'status': 'failed', 'error': 'not installed'}
    except Exception as e:
        print(f"❌ akshare错误: {e}")
        return {'status': 'failed', 'error': str(e)}

# 测试3: 开盘啦接口（根据文档尝试）
def test_kaipanla():
    """测试开盘啦接口（如有可用URL）"""
    print("\n" + "="*60)
    print("测试3: 开盘啦接口")
    print("="*60)
    
    # 根据文档中的接口格式尝试
    # 注意：这些接口可能需要token或签名
    
    test_urls = [
        # 尝试一些可能的接口地址
        "https://app.kaipanla.com/api/v1/change_statistics",
        "https://api.kaipanla.com/v1/base/emotionalCycle",
    ]
    
    results = {}
    for url in test_urls:
        try:
            resp = requests.get(url, timeout=5)
            results[url] = {
                'status_code': resp.status_code,
                'has_data': len(resp.text) > 100
            }
            if resp.status_code == 200:
                print(f"⚠️ {url}: 返回200，可能需要认证")
            else:
                print(f"❌ {url}: 状态{resp.status_code}")
        except Exception as e:
            results[url] = {'error': str(e)}
            print(f"❌ {url}: {e}")
    
    return results

if __name__ == '__main__':
    print(f"开始测试 - {datetime.now()}")
    
    # 运行三个测试
    sina_result = test_sina_api()
    akshare_result = test_akshare()
    kaipanla_result = test_kaipanla()
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    print("\n1. 新浪财经API:")
    for name, data in sina_result.items():
        status = "✅" if data.get('status') == 'success' else "❌"
        print(f"   {status} {name}")
    
    print("\n2. akshare:")
    status = "✅" if akshare_result.get('status') == 'success' else "❌"
    print(f"   {status} {akshare_result.get('status')}")
    
    print("\n3. 开盘啦:")
    print(f"   ⚠️ 需要进一步分析接口认证方式")
    
    print(f"\n测试完成 - {datetime.now()}")
