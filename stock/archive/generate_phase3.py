#!/usr/bin/env python3
"""
生成 Phase 3 版本 - 只添加模块化重构，不改变页面结构和初始化逻辑
"""

import re

def generate_phase3():
    # 读取稳定版本
    with open('/tmp/old_index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 在 </script> 前添加模块化代码（在原有代码之后）
    module_code = '''
        
        // Phase 3: 模块化重构（不改变原有逻辑，只添加模块）
        const EventBus = {
            events: {},
            on(e, t) { (this.events[e] ||= []).push(t); },
            emit(e, d) { this.events[e]?.forEach(t => t(d)); }
        };

        const DataManager = {
            getCurrentDate() { return reportDates[currentReportIndex]; },
            getCurrentReport() { return dailyReports[this.getCurrentDate()]; },
            getCurrentMarketData() { return marketData.find(d => d.date === this.getCurrentDate()); }
        };

        const ChartManager = {
            charts: { kline: null, sentiment: null, strength: null },
            get(name) { return this.charts[name]; },
            set(name, chart) { this.charts[name] = chart; }
        };
    '''
    
    # 在最后一个 </script> 前插入模块代码
    html = html.replace('    </script>', module_code + '    </script>')
    
    # 保存
    output_path = '/root/.openclaw/workspace/stock/web/index-local.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ Phase 3 版本已生成: {output_path}')
    print(f'   文件大小: {len(html) / 1024:.1f} KB')
    return output_path

if __name__ == '__main__':
    generate_phase3()
