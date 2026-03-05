#!/usr/bin/env python3
"""
A股板块分析报告生成（交易大师完整版 V6）
项目: a-share-sector
位置: stock/a-share-sector/scripts/

核心分析框架:
- 主线判定: 资金深度+涨停梯队+封单强度+中军力量，分数≥50
- 阶段判断: 主升/确认/发酵/分歧/退潮/混沌
- 一日游识别: 资金深度<30亿 或 无高度龙头
- 板块合并: 相似板块（如航海装备Ⅱ/Ⅲ）合并显示

数据维度:
- 板块指数: 涨幅、成交额、换手率
- 涨停股: 家数、连板高度、封单金额、涨停时间
- 中军股: 成交额>10亿且涨幅>3%
- 龙虎榜: 机构/游资参与度

关键词匹配策略:
- 同义词扩展: 航海装备→船舶/造船/海洋装备
- 上下游关联: 新能源→光伏/锂电/储能
- 模糊匹配: 其他数字媒体→数字媒体

报告结构:
1. 主线板块（重仓参与）- 判定标准+数据分析+主线判定
2. 发酵板块（小仓试错）- 一日游判断+操作建议
3. 风险板块（坚决回避）- 风险特征+板块表现

迭代记录:
- V6: 完整分析引擎，中军识别，板块合并
- 待优化: 风险板块判定标准（需结合实际案例）

作者: Billy's Claw
日期: 2026-02-23
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_provider import (
    get_market_summary, get_sector_detail_data, 
    get_zt_pool_detail, get_lhb_data, get_emotion_data,
    get_sector_stocks  # 新增
)
from datetime import datetime
from publish_to_mowen import publish_to_mowen

# ============ 核心分析引擎 ============

class SectorAnalyzer:
    """板块分析器（基于交易大师经验）"""
    
    def __init__(self, date_str):
        self.date_str = date_str
        self.market = get_market_summary(date_str)
        self.sectors, self.fund_flow = get_sector_detail_data(date_str)
        self.zt_stocks = get_zt_pool_detail(date_str)
        self.lhb_data = get_lhb_data(date_str)
        self.emotion = get_emotion_data(date_str)
        # 缓存板块个股数据
        self._sector_stocks_cache = {}
        
    def _get_sector_stocks(self, sector_name):
        """获取板块内个股（带缓存）"""
        if sector_name not in self._sector_stocks_cache:
            self._sector_stocks_cache[sector_name] = get_sector_stocks(sector_name, self.date_str)
        return self._sector_stocks_cache[sector_name]
        
    def analyze_all(self):
        """分析所有板块"""
        results = []
        
        for sector in self.sectors:
            # 匹配涨停股
            sector_zt = self._match_zt_stocks(sector['name'])
            sector['zt_list'] = sector_zt
            
            # 计算核心指标
            metrics = self._calculate_metrics(sector, sector_zt)
            
            # 判断阶段
            stage = self._judge_stage(sector, metrics)
            
            # 主线判定
            main_line = self._judge_main_line(sector, metrics, stage)
            
            # 生成操作建议
            strategy = self._generate_strategy(stage, main_line, metrics)
            
            results.append({
                'sector': sector,
                'metrics': metrics,
                'stage': stage,
                'main_line': main_line,
                'strategy': strategy
            })
        
        # 分类排序
        main_sectors = [r for r in results if r['main_line']['is_main_line']]
        ferment_sectors = [r for r in results if r['stage']['name'] == '发酵期' and not r['main_line']['is_main_line']]
        risk_sectors = [r for r in results if r['stage']['name'] in ['退潮期', '分歧期']]
        
        # 智能合并：所有板块按个股重复度合并
        main_sectors = self._merge_sectors_by_stocks(main_sectors)
        ferment_sectors = self._merge_sectors_by_stocks(ferment_sectors)
        risk_sectors = self._merge_sectors_by_stocks(risk_sectors)
        
        main_sectors.sort(key=lambda x: x['main_line']['score'], reverse=True)
        ferment_sectors.sort(key=lambda x: x['metrics']['influence'], reverse=True)
        
        return {
            'main': main_sectors[:3],
            'ferment': ferment_sectors[:3],
            'risk': risk_sectors[:3],
            'market': self.market,
            'emotion': self.emotion
        }
    
    def _merge_sectors_by_stocks(self, sectors):
        """智能合并板块：检测涨停股和中军重复度（适用于所有板块）"""
        if len(sectors) <= 1:
            return sectors
        
        merged = []
        used = set()
        
        for i, item1 in enumerate(sectors):
            if i in used:
                continue
            
            # 获取第一个板块的个股集合
            zt_codes1 = {z['code'] for z in item1['sector']['zt_list']}
            mid_codes1 = {s['code'] for s in item1['metrics'].get('mid_stocks', [])}
            all_stocks1 = zt_codes1 | mid_codes1
            
            # 找重复度高的其他板块
            merge_candidates = [item1]
            for j, item2 in enumerate(sectors[i+1:], i+1):
                if j in used:
                    continue
                
                zt_codes2 = {z['code'] for z in item2['sector']['zt_list']}
                mid_codes2 = {s['code'] for s in item2['metrics'].get('mid_stocks', [])}
                all_stocks2 = zt_codes2 | mid_codes2
                
                # 计算重复度
                if len(all_stocks1) > 0 and len(all_stocks2) > 0:
                    overlap = len(all_stocks1 & all_stocks2)
                    total_unique = len(all_stocks1 | all_stocks2)
                    overlap_ratio = overlap / total_unique if total_unique > 0 else 0
                    
                    # 重复度>50%则合并
                    if overlap_ratio > 0.5:
                        merge_candidates.append(item2)
                        used.add(j)
            
            used.add(i)
            
            # 合并多个板块
            if len(merge_candidates) > 1:
                merged_item = self._combine_sectors(merge_candidates)
                merged.append(merged_item)
            else:
                merged.append(item1)
        
        return merged
    
    def _combine_sectors(self, items):
        """合并多个板块数据"""
        # 取分数最高的作为主板块
        items.sort(key=lambda x: x['main_line']['score'], reverse=True)
        main_item = items[0]
        
        # 合并名称
        names = [item['sector']['name'] for item in items]
        # 提取核心词（去掉"其他"、"Ⅱ"、"Ⅲ"等）
        core_names = []
        for name in names:
            core = name.replace('其他', '').replace('Ⅱ', '').replace('Ⅲ', '')
            if core not in core_names:
                core_names.append(core)
        
        # 如果合并后只剩一个核心词，就用它
        if len(core_names) == 1:
            main_item['sector']['name'] = core_names[0]
        else:
            main_item['sector']['name'] = '/'.join(core_names[:2])
        
        # 合并涨停股（去重）
        all_zt = {}
        for item in items:
            for z in item['sector']['zt_list']:
                if z['code'] not in all_zt:
                    all_zt[z['code']] = z
        main_item['sector']['zt_list'] = list(all_zt.values())
        
        # 合并中军（去重）
        all_mid = {}
        for item in items:
            for s in item['metrics'].get('mid_stocks', []):
                if s['code'] not in all_mid:
                    all_mid[s['code']] = s
        main_item['metrics']['mid_stocks'] = list(all_mid.values())
        
        # 重新计算指标
        zt_list = main_item['sector']['zt_list']
        main_item['metrics']['zt_count'] = len(zt_list)
        main_item['metrics']['max_boards'] = max([z.get('boards', 0) for z in zt_list], default=0)
        main_item['metrics']['total_zt_amount'] = sum(z.get('amount', 0) for z in zt_list)
        main_item['metrics']['avg_seal'] = sum(z.get('seal_amount', 0) for z in zt_list) / max(len(zt_list), 1)
        main_item['metrics']['mid_count'] = len(main_item['metrics']['mid_stocks'])
        main_item['metrics']['mid_total_amount'] = sum(s.get('amount', 0) for s in main_item['metrics']['mid_stocks'])
        
        # 重新计算影响力
        m = main_item['metrics']
        influence = 0
        influence += min(25, m['zt_count'] * 5)
        influence += min(20, m['max_boards'] * 4)
        influence += min(15, main_item['sector']['change_pct'] * 2)
        influence += min(15, main_item['sector'].get('amount', 0) / 10)
        influence += min(10, m['avg_seal'])
        influence += min(10, main_item['sector'].get('turnover', 0) / 2)
        influence += min(10, m['mid_count'] * 3)
        influence += 5 if m['zt_count'] >= 2 else 0
        m['influence'] = min(100, int(influence))
        
        return main_item
    
    def _merge_similar_sectors(self, sectors):
        """合并相似板块（如航海装备Ⅱ、Ⅲ合并为航海装备）"""
        merged = []
        seen_groups = set()
        
        for item in sectors:
            name = item['sector']['name']
            
            # 检查是否属于已处理的组
            group_key = None
            if '航海装备' in name:
                group_key = '航海装备'
            elif '数字媒体' in name:
                group_key = '数字媒体'
            elif '半导体' in name or '芯片' in name:
                group_key = '半导体'
            else:
                group_key = name
            
            if group_key in seen_groups:
                continue
            
            seen_groups.add(group_key)
            
            # 如果是组合并，更新显示名称
            if group_key != name:
                item['sector']['name'] = group_key
            
            merged.append(item)
        
        return merged
    
    def _match_zt_stocks(self, sector_name):
        """匹配板块内涨停股（支持同义词）"""
        # 扩展关键词库（包含同义词、上下游）
        keywords = {
            '数字媒体': ['数字媒体', '传媒', '影视', '出版'],
            '其他数字媒体': ['数字媒体', '传媒', '影视', '出版'],
            '文字媒体': ['数字媒体', '传媒', '出版'],
            '海洋捕捞': ['渔业', '捕捞', '水产', '养殖'],
            '渔业': ['渔业', '捕捞', '水产', '养殖'],
            '航海装备': ['航海', '船舶', '造船', '海洋装备', '港口', '航运'],
            '航海装备Ⅱ': ['航海', '船舶', '造船', '海洋装备', '港口', '航运'],
            '航海装备Ⅲ': ['航海', '船舶', '造船', '海洋装备', '港口', '航运'],
            '船舶制造': ['船舶', '造船', '海洋装备'],
            '半导体': ['半导体', '芯片', '集成电路', '晶圆', '光刻'],
            '芯片': ['半导体', '芯片', '集成电路'],
            '券商': ['证券', '券商', '金融'],
            '新能源': ['新能源', '光伏', '锂电', '储能', '电源', '电池'],
            '光伏': ['光伏', '太阳能', '新能源'],
            '锂电池': ['锂电', '电池', '新能源'],
            '军工': ['军工', '国防', '航空', '航天', '船舶', '兵器'],
            '白酒': ['白酒', '酒类', '饮料', '消费'],
            '医药': ['医药', '医疗', '生物', '制药', '疫苗'],
            '汽车': ['汽车', '汽车零部件', '电动车', '新能源车'],
            '汽车零部件': ['汽车', '汽车零部件', '电动车'],
            '电力': ['电力', '电网', '电源', '发电', '新能源'],
            '通信': ['通信', '5G', '网络', '通讯'],
            '计算机': ['计算机', '软件', 'IT', '互联网'],
            '化工': ['化工', '化学', '材料'],
            '有色': ['有色', '金属', '稀土', '锂', '钴'],
            '煤炭': ['煤炭', '能源', '电力'],
            '钢铁': ['钢铁', '金属', '材料'],
            '建筑': ['建筑', '工程', '基建', '房地产'],
            '房地产': ['房地产', '地产', '建筑'],
            '电子': ['电子', '元器件', '半导体', '芯片'],
            '机械': ['机械', '设备', '制造'],
        }
        
        matched = []
        # 先精确匹配
        kws = keywords.get(sector_name, [])
        
        # 如果没有，尝试提取核心词并匹配
        if not kws:
            # 去掉数字、符号，提取核心词
            core = sector_name.replace('Ⅱ', '').replace('Ⅲ', '').replace('其他', '')
            kws = [core]
            
            # 尝试包含关系匹配
            for key, vals in keywords.items():
                if key in sector_name or sector_name in key:
                    kws = vals
                    break
        
        # 匹配涨停股
        for z in self.zt_stocks:
            if z.get('industry'):
                # 直接匹配
                if any(kw in z['industry'] for kw in kws):
                    matched.append(z)
                    continue
                # 匹配股票名称（有些涨停股行业不准，但名字有关）
                if any(kw in z.get('name', '') for kw in kws[:2]):
                    matched.append(z)
        
        matched.sort(key=lambda x: x.get('boards', 0), reverse=True)
        return matched
    
    def _calculate_metrics(self, sector, zt_list):
        """计算核心指标（含中军）"""
        # 基础数据
        change = sector['change_pct']
        amount = sector.get('amount', 0)
        turnover = sector.get('turnover', 0)
        zt_count = len(zt_list)
        
        # 涨停数据分析
        boards_dist = {}
        total_zt_amount = 0
        total_seal = 0
        max_boards = 0
        
        for z in zt_list:
            b = z.get('boards', 1)
            boards_dist[b] = boards_dist.get(b, 0) + 1
            total_zt_amount += z.get('amount', 0)
            total_seal += z.get('seal_amount', 0)
            max_boards = max(max_boards, b)
        
        avg_seal = total_seal / max(zt_count, 1)
        
        # 找中军（大成交额+大涨）
        sector_stocks = self._get_sector_stocks(sector['name'])
        mid_stocks = [s for s in sector_stocks if s['amount'] > 10 and s['change_pct'] > 3]
        mid_count = len(mid_stocks)
        mid_total_amount = sum(s['amount'] for s in mid_stocks)
        
        # 影响力计算（加入中军）
        influence = 0
        influence += min(25, zt_count * 5)           # 涨停家数
        influence += min(20, max_boards * 4)         # 连板高度
        influence += min(15, change * 2)             # 涨跌幅
        influence += min(15, amount / 10)            # 成交额
        influence += min(10, avg_seal)               # 封单强度
        influence += min(10, turnover / 2)           # 换手率
        influence += min(10, mid_count * 3)          # 中军数量（新增）
        influence += 5 if zt_count >= 2 else 0       # 梯队完整度
        
        return {
            'change': change,
            'amount': amount,
            'turnover': turnover,
            'zt_count': zt_count,
            'max_boards': max_boards,
            'boards_dist': boards_dist,
            'total_zt_amount': total_zt_amount,
            'avg_seal': avg_seal,
            'mid_count': mid_count,              # 中军数量
            'mid_total_amount': mid_total_amount, # 中军成交额
            'mid_stocks': mid_stocks[:3],        # 中军列表
            'influence': min(100, int(influence))
        }
    
    def _judge_stage(self, sector, metrics):
        """判断板块阶段（基于经验2）"""
        change = metrics['change']
        zt_count = metrics['zt_count']
        max_boards = metrics['max_boards']
        
        # 主升期：持续放量，龙头加速
        if max_boards >= 5 and zt_count >= 3:
            return {
                'name': '主升期',
                'desc': '持续放量，龙头加速，情绪高涨，怕踏空',
                'strategy': '持股，不轻易下车'
            }
        
        # 确认期：板块涨停潮，连板出现
        if zt_count >= 5 and max_boards >= 2:
            return {
                'name': '确认期',
                'desc': '板块涨停潮，连板出现，共识形成，媒体开始报道',
                'strategy': '加仓，上核心标的'
            }
        
        # 发酵期：少数涨停，成交温和放大
        if zt_count >= 2 and change > 2:
            return {
                'name': '发酵期',
                'desc': '少数涨停，成交量温和放大，分歧大，很多人不信',
                'strategy': '小仓试错，选先手龙头'
            }
        
        # 分歧期：高位震荡，炸板增多
        if change > 3 and zt_count < 2:
            return {
                'name': '分歧期',
                'desc': '高位震荡，炸板增多，多空分歧，有人止盈',
                'strategy': '去弱留强，减高位'
            }
        
        # 退潮期：连续跌停，量能萎缩
        if change < -3:
            return {
                'name': '退潮期',
                'desc': '连续跌停，量能萎缩，恐慌，割肉',
                'strategy': '空仓，等下一轮'
            }
        
        # 混沌期
        return {
            'name': '混沌期',
            'desc': '方向不明，表现平庸',
            'strategy': '观望，等待时机'
        }
    
    def _judge_main_line(self, sector, metrics, stage):
        """
        主线判定（基于经验3）
        主线 = 政策催化 + 资金深度 + 产业逻辑 + 时间窗口
        """
        score = 0
        factors = []
        
        # 1. 资金深度（最重要）
        if metrics['total_zt_amount'] > 100:  # 涨停股总成交>100亿
            score += 30
            factors.append('资金深度极佳')
        elif metrics['total_zt_amount'] > 50:
            score += 20
            factors.append('资金深度良好')
        elif metrics['total_zt_amount'] > 20:
            score += 10
            factors.append('资金深度一般')
        
        # 2. 涨停梯队
        if metrics['max_boards'] >= 5:
            score += 25
            factors.append('龙头高度足')
        elif metrics['max_boards'] >= 3:
            score += 15
            factors.append('有连板梯队')
        
        # 3. 封单强度
        if metrics['avg_seal'] > 5:
            score += 20
            factors.append('封单强劲')
        elif metrics['avg_seal'] > 2:
            score += 10
            factors.append('封单一般')
        
        # 4. 板块涨幅
        if metrics['change'] > 5:
            score += 15
        elif metrics['change'] > 3:
            score += 10
        
        # 5. 涨停家数
        if metrics['zt_count'] >= 10:
            score += 10
        elif metrics['zt_count'] >= 5:
            score += 5
        
        # 5. 中军贡献（新增）
        if metrics['mid_count'] >= 2:
            score += 10
            factors.append('中军强劲')
        elif metrics['mid_count'] >= 1:
            score += 5
            factors.append('有中军')
        
        # 判定主线（分数≥50且处于主升/确认/发酵期）
        is_main = score >= 50 and stage['name'] in ['主升期', '确认期', '发酵期']
        
        return {
            'is_main_line': is_main,
            'score': score,
            'factors': factors
        }
    
    def _generate_strategy(self, stage, main_line, metrics):
        """生成操作策略"""
        if main_line['is_main_line']:
            if stage['name'] == '主升期':
                return '重仓参与，持股待涨，不轻易下车'
            else:
                return '积极加仓，上核心标的'
        elif stage['name'] == '发酵期':
            if metrics['total_zt_amount'] < 30:
                return '⚠️ 可能一日游，资金深度不足，不参与'
            else:
                return '小仓试错，明日竞价确认后上车'
        else:
            return stage['strategy']

# ============ 报告生成 ============

def generate_report(date_str):
    """生成完整报告"""
    analyzer = SectorAnalyzer(date_str)
    data = analyzer.analyze_all()
    
    # 生成各板块内容
    main_content = generate_main_content(data['main'])
    ferment_content = generate_ferment_content(data['ferment'])
    risk_content = generate_risk_content(data['risk'])
    
    report = f"""# A股主流板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw

---

## 一、主线板块（重仓参与）

**判定标准**：资金深度+涨停梯队+封单强度达标，分数≥50，处于主升/确认/发酵期

{main_content}

---

## 二、发酵板块（小仓试错）

**判定标准**：有晋升主线可能，需判断持续性，避免一日游

{ferment_content}

---

## 三、风险板块（坚决回避）

**判定标准**：退潮期/分歧期，或跌幅>3%，或前期炒作充分

{risk_content}
"""
    return report

def generate_main_content(sectors):
    """生成主线板块内容"""
    if not sectors:
        return "当前无明显主线板块。"
    
    content = ""
    for i, item in enumerate(sectors, 1):
        s = item['sector']
        m = item['metrics']
        ml = item['main_line']
        
        # 龙头列表
        dragons = '、'.join([f"{z['name']}{z['boards']}板" for z in s['zt_list'][:3]]) if s['zt_list'] else '待识别'
        
        content += f"""### 1.{i} {s['name']}

**板块表现**：指数{m['change']:+.2f}%，成交{m['amount']:.0f}亿，换手{m['turnover']:.1f}%，影响力{m['influence']}/100

**涨停分析**：涨停{m['zt_count']}家，最高{m['max_boards']}板，涨停成交{m['total_zt_amount']:.0f}亿，平均封单{m['avg_seal']:.1f}亿

**龙头梯队**：{dragons}

**中军力量**：{m['mid_count']}只中军大涨（成交>{m['mid_total_amount']:.0f}亿），{', '.join([s['name'] for s in m['mid_stocks']]) if m['mid_stocks'] else '待识别'}

**主线判定**：分数{ml['score']}/100（{'、'.join(ml['factors']) if ml['factors'] else '待观察'}）

---

"""
    return content

def generate_ferment_content(sectors):
    """生成发酵板块内容"""
    if not sectors:
        return "当前无明显发酵板块。"
    
    content = ""
    for i, item in enumerate(sectors, 1):
        s = item['sector']
        m = item['metrics']
        
        # 一日游判断
        if m['total_zt_amount'] < 30:
            yry = "⚠️ 一日游风险（资金深度不足，板块容量小）→ 不参与"
        elif m['max_boards'] < 2:
            yry = "⚠️ 一日游风险（无高度龙头）→ 不参与"
        else:
            yry = "✓ 真发酵（资金深度好，有龙头）→ 明日竞价上车"
        
        content += f"""### 2.{i} {s['name']}

**板块表现**：指数{m['change']:+.2f}%，涨停{m['zt_count']}家，最高{m['max_boards']}板

**一日游判断**：{yry}

**晋升条件**：明日涨停≥5家且出现3板龙头，可确认晋升主线

**操作建议**：{item['strategy']}

---

"""
    return content

def generate_risk_content(sectors):
    """生成风险板块内容"""
    if not sectors:
        return "当前无明显风险板块。"
    
    content = ""
    for i, item in enumerate(sectors, 1):
        s = item['sector']
        stage = item['stage']
        
        content += f"""### 3.{i} {s['name']}

**风险特征**：{stage['desc']}

**板块表现**：指数{s['change_pct']:+.2f}%

---

"""
    return content

def generate_summary_strategy(data):
    """生成总结策略"""
    strategies = []
    
    if data['main']:
        main_names = '、'.join([item['sector']['name'] for item in data['main'][:2]])
        strategies.append(f"- 主线板块：{main_names}，重仓参与，去弱留强")
    
    if data['ferment']:
        strategies.append(f"- 发酵板块：关注{len(data['ferment'])}个潜在板块，明日竞价确认")
    
    if not data['main'] and not data['ferment']:
        strategies.append("- 当前无明显机会，控制仓位，等待主线出现")
    
    return '\n'.join(strategies)

def get_weekday(date_str):
    """获取星期几"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return weekdays[date.weekday()]

def main():
    """主函数"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    from data_provider import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM stock_kline WHERE date <= ?', (today,))
    latest_date = cursor.fetchone()[0]
    conn.close()
    
    if latest_date != today:
        print(f"今天({today})不是交易日，使用最近交易日({latest_date})的数据...")
        date_str = latest_date
    else:
        print(f"生成 {today} 的板块分析报告...")
        date_str = today
    
    report = generate_report(date_str)
    
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'sector_analysis_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    title = f"A股主流板块分析-{date_str[2:4]}/{date_str[5:7]}/{date_str[8:]}({get_weekday(date_str)})-Billy's Claw"
    result = publish_to_mowen(
        title=title,
        content=report,
        tags=["A股分析", "板块分析"],
        auto_publish=True
    )
    
    if result.get('success'):
        print(f"墨问链接: {result.get('url')}")
    else:
        print(f"发布失败: {result.get('error')}")

if __name__ == '__main__':
    main()
