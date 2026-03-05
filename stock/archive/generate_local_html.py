#!/usr/bin/env python3
"""
生成本地预览版 HTML - 内嵌所有数据，可直接双击打开
"""

import json
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('/root/.openclaw/workspace/stock/duanxianxia_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_kline_data():
    """获取K线数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {}
    for code in ['000001', '000985', '399006']:
        cursor.execute('''
            SELECT date, open, close, high, low, volume, amount, ma50
            FROM index_kline
            WHERE index_code = ? AND date >= '2026-01-01'
            ORDER BY date ASC
        ''', (code,))
        rows = cursor.fetchall()
        
        code_names = {
            '000001': ('上证指数', '上证'),
            '000985': ('东财全A', '东财全A'),
            '399006': ('创业板指', '创业板')
        }
        name, display = code_names[code]
        
        result[code] = {
            'name': name,
            'display': display,
            'data': [dict(row) for row in rows]
        }
    
    conn.close()
    return result

def get_market_data():
    """获取市场数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM market_sentiment 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    market_data = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT date, phase, action, summary, mowen_link 
        FROM daily_reports 
        WHERE date >= '2026-01-01'
        ORDER BY date DESC
    ''')
    daily_reports = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return market_data, daily_reports

def generate_local_html():
    """生成本地预览版HTML - 内嵌所有数据"""
    
    # 获取数据
    kline_data = get_kline_data()
    market_data, daily_reports = get_market_data()
    
    # 转换为JSON
    kline_json = json.dumps(kline_data, ensure_ascii=False)
    market_json = json.dumps(market_data, ensure_ascii=False)
    reports_json = json.dumps(daily_reports, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>A股市场短线情绪走势 - 本地预览</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh;padding:12px}}
        .container{{max-width:1400px;margin:0 auto}}
        .header{{text-align:center;margin-bottom:16px;padding:12px 0;border-bottom:1px solid #30363d}}
        .header h1{{font-size:20px;color:#58a6ff;font-weight:600}}
        .local-badge{{display:inline-block;background:#238636;color:#fff;font-size:12px;padding:2px 8px;border-radius:4px;margin-left:10px}}
        .chart-container{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px;margin-bottom:16px}}
        .chart-title{{font-size:15px;color:#c9d1d9;font-weight:600;margin-bottom:12px;padding-left:8px;border-left:3px solid #58a6ff;display:flex;justify-content:space-between;align-items:center}}
        .index-selector{{background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer}}
        .date-switcher{{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:16px}}
        .date-arrow{{width:32px;height:32px;border-radius:50%;background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}}
        .date-arrow:hover{{background:#30363d;color:#58a6ff}}
        .date-arrow:disabled{{opacity:.3;cursor:not-allowed}}
        .date-display{{font-size:15px;font-weight:600;color:#c9d1d9;min-width:140px;text-align:center}}
        .card-container{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px}}
        .card-title{{font-size:16px;color:#c9d1d9;font-weight:600;margin-bottom:15px;padding-left:8px;border-left:3px solid #58a6ff}}
        .report-card{{background:#161b22;border-radius:8px;padding:16px}}
        .report-section{{margin-bottom:16px}}
        .report-section h4{{color:#58a6ff;font-size:14px;margin-bottom:8px}}
        .report-section p{{color:#c9d1d9;font-size:13px;line-height:1.6}}
        .report-section .highlight{{color:#f0883e;font-weight:600}}
        .report-link{{display:inline-block;font-size:12px;color:#8b949e;text-decoration:none;margin-top:8px;transition:color .2s}}
        .report-link:hover{{color:#58a6ff}}
        .data-table{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px;overflow-x:auto;-webkit-overflow-scrolling:touch}}
        .data-table h3{{font-size:15px;color:#c9d1d9;margin-bottom:12px;font-weight:600;padding-left:8px;border-left:3px solid #58a6ff}}
        table{{width:100%;border-collapse:collapse;font-size:11px;min-width:700px}}
        th,td{{padding:8px 6px;text-align:center;border-bottom:1px solid #30363d;white-space:nowrap}}
        th{{background:#21262d;color:#8b949e;font-weight:600;position:sticky;top:0}}
        tr:hover{{background:#21262d}}
        .emotion-hot{{color:#f85149;font-weight:600}}
        .emotion-good{{color:#f0883e;font-weight:600}}
        .emotion-normal{{color:#58a6ff;font-weight:600}}
        .emotion-ice{{color:#238636;font-weight:600}}
        .up-red{{color:#f85149}}
        .down-green{{color:#238636}}
        .footer{{text-align:center;padding:16px;margin-top:16px;font-size:12px;color:#6e7681}}
        @media(min-width:1024px){{
            .row{{display:flex;gap:20px;margin-bottom:20px}}
            .row .chart-container{{flex:2;margin-bottom:0}}
            .row .card-container{{flex:1}}
        }}
        @media(min-width:768px)and(max-width:1023px){{
            body{{padding:20px}}
            .header h1{{font-size:24px}}
        }}
        @media(max-width:375px){{body{{padding:8px}}.header h1{{font-size:18px}}}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>A股市场短线情绪走势<span class="local-badge">本地预览</span></h1>
        </div>
        <div class="row">
            <div class="chart-container">
                <div class="chart-title">短线情绪</div>
                <div id="sentimentChart" style="width:100%;height:260px"></div>
            </div>
            <div class="card-container">
                <div class="card-title">情绪研判</div>
                <div id="dailyReport"><div class="loading">加载中...</div></div>
            </div>
        </div>
        <div class="row">
            <div class="chart-container">
                <div class="chart-title">
                    <span>指数K线</span>
                    <select id="indexSelector" class="index-selector">
                        <option value="000001">上证指数</option>
                        <option value="000985">东财全A</option>
                        <option value="399006">创业板指</option>
                    </select>
                </div>
                <div id="klineChart" style="width:100%;height:320px"></div>
            </div>
            <div class="card-container">
                <div class="card-title">数据详情</div>
                <div id="dataDetails"><div class="loading">加载中...</div></div>
            </div>
        </div>
        <div class="row">
            <div class="chart-container">
                <div class="chart-title">中期趋势</div>
                <div id="strengthChart" style="width:100%;height:260px"></div>
            </div>
            <div class="card-container">
                <div class="card-title">板块分析</div>
                <div style="color:#6e7681;font-size:14px;text-align:center;padding:40px 20px">敬请期待</div>
            </div>
        </div>
        <div id="fullTableContainer" class="data-table" style="display:none">
            <h3>历史数据明细<button onclick="UIManager.hideFullTable()" style="float:right;background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:12px">收起</button></h3>
            <table id="dataTable">
                <thead><tr><th>日期</th><th>情绪</th><th>量能</th><th>上涨</th><th>下跌</th><th>涨停</th><th>跌停</th><th>大幅回撤</th><th>连板高度</th><th>连板表现</th><th>连板晋级率</th><th>涨停表现</th><th>封板率</th><th>MA50占比</th><th>强势股</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="footer">Powered by Billy's Claw | WeChat: tianbao</div>
    </div>

    <script>
        // 内嵌数据 - 本地预览版
        const KLINE_DATA = {kline_json};
        const EMBEDDED_MARKET_DATA = {market_json};
        const EMBEDDED_DAILY_REPORTS = {reports_json};
        
        // 处理研判数据
        const EMBEDDED_DAILY_REPORTS_MAP = {{}};
        EMBEDDED_DAILY_REPORTS.forEach(report => {{
            EMBEDDED_DAILY_REPORTS_MAP[report.date] = report;
        }});
        
        /* Config */
        const CONFIG = {{API_URL:"api/data.json",DEFAULT_INDEX:"000001",START_DATE:"2026-01-01"}};
        const INDEX_CONFIG = {{"000001":{{name:"上证指数",display:"上证"}},"000985":{{name:"东财全A",display:"东财全A"}},"399006":{{name:"创业板指",display:"创业板"}}}};
        const EMOTION_STATUS = [{{threshold:75,color:"#f85149",text:"火爆"}},{{threshold:50,color:"#f0883e",text:"良好"}},{{threshold:25,color:"#58a6ff",text:"一般"}},{{threshold:0,color:"#238636",text:"冰点"}}];
        
        /* EventBus */
        const EventBus = {{events:{{}},on(e,t){{this.events[e]||(this.events[e]=[]),this.events[e].push(t)}},emit(e,t){{this.events[e]&&this.events[e].forEach(e=>e(t))}}}};
        
        /* DataManager - 本地预览版（使用内嵌数据） */
        const DataManager = {{
            marketData: [],
            dailyReports: {{}},
            reportDates: [],
            currentReportIndex: 0,
            klineData: null,
            init(e) {{this.klineData = e}},
            async load() {{
                // 本地预览版：直接使用内嵌数据
                this.marketData = EMBEDDED_MARKET_DATA;
                this.dailyReports = EMBEDDED_DAILY_REPORTS_MAP;
                this.reportDates = Object.keys(this.dailyReports).sort();
                this.currentReportIndex = this.reportDates.length - 1;
                EventBus.emit("data:loaded", {{fromCache: false}});
                return {{updated: true}};
            }},
            getCurrentDate() {{return this.reportDates[this.currentReportIndex]}},
            getCurrentReport() {{return this.dailyReports[this.getCurrentDate()]}},
            getCurrentMarketData() {{return this.marketData.find(e => e.date === this.getCurrentDate())}},
            switchReport(e) {{
                const t = this.currentReportIndex + e;
                return t >= 0 && t < this.reportDates.length && (this.currentReportIndex = t, EventBus.emit("report:changed", {{date: this.getCurrentDate(), index: this.currentReportIndex}}), !0)
            }},
            getSharedDates() {{return this.marketData.filter(e => e.date >= CONFIG.START_DATE).map(e => e.date.substring(5)).reverse()}},
            getKlineData(e) {{const t = this.klineData[e]; return t && t.data ? t.data.filter(e => e.date >= CONFIG.START_DATE) : []}}
        }};
        
        /* ChartManager */
        const ChartManager = {{
            charts: {{}},
            currentIndex: CONFIG.DEFAULT_INDEX,
            init() {{this._initSentimentChart(), this._initKlineChart(), this._initStrengthChart(), this._connectCharts(), this._setupResizeHandler()}},
            _isMobile: () => window.innerWidth < 768,
            _initSentimentChart() {{const e = document.getElementById("sentimentChart"); e && (this.charts.sentiment = echarts.init(e, null, {{renderer: "canvas"}}), this.renderSentiment())}},
            renderSentiment() {{
                if (!this.charts.sentiment) return;
                const e = DataManager.getSharedDates(), t = DataManager.marketData.filter(e => e.date >= CONFIG.START_DATE).reverse(), a = [], n = [];
                e.forEach(a => {{const n = "2026-" + a, r = t.find(e => e.date === n); r ? (a.push(r.sentiment_index), n.push(r.up_count)) : (a.push(null), n.push(null))}});
                const s = this._isMobile(), i = a.map(e => ({{value: e, itemStyle: {{color: this._getEmotionColor(e)}}}}));
                this.charts.sentiment.setOption({{
                    backgroundColor: "transparent",
                    grid: {{left: s ? "12%" : "10%", right: "4%", bottom: s ? "15%" : "10%", top: "5%"}},
                    xAxis: {{type: "category", data: e, axisLine: {{lineStyle: {{color: "#30363d"}}}}, axisLabel: {{color: "#8b949e", fontSize: s ? 9 : 11, rotate: s ? 60 : 45}}}},
                    yAxis: [{{type: "value", min: 0, max: 100, axisLine: {{lineStyle: {{color: "#30363d"}}}}, axisLabel: {{color: "#8b949e", fontSize: s ? 10 : 12}}, splitLine: {{lineStyle: {{color: "#21262d", type: "dashed"}}}}}}, {{type: "value", show: !1, min: 0}}],
                    series: [{{name: "情绪指标", data: i, type: "line", smooth: !0, lineStyle: {{width: s ? 1.5 : 2, color: "#8b949e"}}, symbol: "circle", symbolSize: s ? 5 : 8, areaStyle: {{color: {{type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{offset: 0, color: "rgba(248,81,73,0.2)"}}, {{offset: .33, color: "rgba(240,136,62,0.15)"}}, {{offset: .66, color: "rgba(88,166,255,0.1)"}}, {{offset: 1, color: "rgba(35,134,54,0.05)"}}]}}}}, markLine: {{silent: !0, symbol: "none", lineStyle: {{type: "dashed", width: 1}}, label: {{position: "end", fontSize: s ? 10 : 12, color: "#8b949e"}}, data: [{{yAxis: 75, lineStyle: {{color: "#f0883e"}}}}, {{yAxis: 50, lineStyle: {{color: "#58a6ff"}}}}, {{yAxis: 25, lineStyle: {{color: "#238636"}}}}]}}}}, {{name: "上涨家数", data: n, type: "line", smooth: !0, yAxisIndex: 1, lineStyle: {{width: 1, color: "rgba(248,81,73,0.4)"}}, symbol: "none"}}],
                    tooltip: {{trigger: "axis", backgroundColor: "#161b22", borderColor: "#30363d", textStyle: {{color: "#c9d1d9", fontSize: s ? 12 : 14}}, formatter: e => {{const t = e[0].value, a = this._getEmotionStatus(t); let n = "2026-" + e[0].axisValue + "<br/>情绪值: <span style=\"color:" + a.color + ";font-weight:bold;\">" + t + "</span> (" + a.text + ")"; return e[1] && (n += "<br/>上涨家数: <span style=\"color:#f85149\">" + e[1].value + "</span>"), n}}}}
                }});
            }},
            _initKlineChart() {{const e = document.getElementById("klineChart"); e && (this.charts.kline = echarts.init(e, null, {{renderer: "canvas"}}), this.renderKline())}},
            renderKline() {{
                if (!this.charts.kline) return;
                const e = DataManager.getKlineData(this.currentIndex);
                if (!e || 0 === e.length) return;
                const t = DataManager.getSharedDates(), a = this._isMobile(), n = [], r = [], s = [], i = [];
                t.forEach((t, a) => {{const n = "2026-" + t, r = e.find(e => e.date === n); if (r) {{n.push([r.open, r.close, r.low, r.high]), r.push(r.amount), s.push(r.ma50); const e = a > 0 ? e.find(e => e.date === "2026-" + t[a-1]) : null; i.push(e ? (r.close >= e.close ? "#f85149" : "#238636") : (r.close >= r.open ? "#f85149" : "#238636"))}} else {{n.push([null, null, null, null]), r.push(0), s.push(null), i.push("#30363d")}}}});
                this.charts.kline.setOption({{
                    backgroundColor: "transparent", animation: !1,
                    tooltip: {{trigger: "axis", backgroundColor: "#161b22", borderColor: "#30363d", textStyle: {{color: "#c9d1d9", fontSize: a ? 11 : 12}}, formatter: e => {{const t = e.find(e => "K线" === e.seriesName), n = e.find(e => "成交额" === e.seriesName); let r = "2026-" + e[0].axisValue + "<br/>"; return t && (r += "开: " + t.data[1] + " 收: " + t.data[2] + "<br/>低: " + t.data[3] + " 高: " + t.data[4] + "<br/>"), n && (r += "额: " + (n.value / 1e8).toFixed(2) + "亿"), r}}}},
                    grid: [{{left: a ? "12%" : "10%", right: a ? "4%" : "8%", top: "10%", height: "55%"}}, {{left: a ? "12%" : "10%", right: a ? "4%" : "8%", top: "70%", height: "20%"}}],
                    xAxis: [{{type: "category", data: t, axisLine: {{lineStyle: {{color: "#30363d"}}}}, axisLabel: {{color: "#8b949e", fontSize: a ? 9 : 11, rotate: a ? 60 : 45}}}}, {{type: "category", gridIndex: 1, data: t, axisLabel: {{show: !1}}}}],
                    yAxis: [{{scale: !0, position: "right", axisLine: {{lineStyle: {{color: "#30363d"}}}}, axisLabel: {{color: "#8b949e", fontSize: a ? 9 : 10}}, splitLine: {{lineStyle: {{color: "#21262d", type: "dashed"}}}}}}, {{scale: !0, gridIndex: 1, splitNumber: 2, axisLabel: {{show: !1}}, splitLine: {{show: !1}}}}],
                    dataZoom: [{{type: "inside", xAxisIndex: [0, 1], start: 0, end: 100}}],
                    series: [{{name: "K线", type: "candlestick", data: n, itemStyle: {{color: "#f85149", color0: "#238636", borderColor: "#f85149", borderColor0: "#238636"}}, barWidth: a ? "60%" : "50%"}}, {{name: "MA50", type: "line", data: s, smooth: !0, lineStyle: {{width: 1.5, color: "#58a6ff"}}, symbol: "none"}}, {{name: "成交额", type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: r, itemStyle: {{color: e => i[e.dataIndex]}}, barWidth: a ? "60%" : "50%"}}]
                }});
            }},
            _initStrengthChart() {{const e = document.getElementById("strengthChart"); e && (this.charts.strength = echarts.init(e, null, {{renderer: "canvas"}}), this.renderStrength())}},
            renderStrength() {{
                if (!this.charts.strength) return;
                const e = DataManager.getSharedDates(), t = DataManager.marketData.filter(e => e.date >= CONFIG.START_DATE).reverse(), a = [], n = [];
                e.forEach(e => {{const a = "2026-" + e, n = t.find(e => e.date === a); a.push(n ? n.ma50_percent || 0 : null), n.push(n ? n.strong_percent || 0 : null)}});
                const r = this._isMobile(), s = a[a.length - 1], i = n[n.length - 1];
                this.charts.strength.setOption({{
                    backgroundColor: "transparent", grid: {{left: r ? "12%" : "10%", right: r ? "4%" : "8%", bottom: r ? "15%" : "10%", top: "10%"}},
                    xAxis: {{type: "category", data: e, axisLine: {{lineStyle: {{color: "#30363d"}}}}, axisLabel: {{color: "#8b949e", fontSize: r ? 9 : 11, rotate: r ? 60 : 45}}}},
                    yAxis: [{{type: "value", name: "MA50占比", min: 0, max: 100, position: "left", axisLine: {{lineStyle: {{color: "#58a6ff"}}}}, axisLabel: {{color: "#58a6ff", fontSize: r ? 10 : 12, formatter: "{{value}}%"}}, splitLine: {{lineStyle: {{color: "#21262d", type: "dashed"}}}}}}, {{type: "value", name: "强势股占比", min: 0, max: 50, position: "right", axisLine: {{lineStyle: {{color: "#f0883e"}}}}, axisLabel: {{color: "#f0883e", fontSize: r ? 10 : 12, formatter: "{{value}}%"}}, splitLine: {{show: !1}}}}],
                    series: [{{name: "MA50占比", data: a.map(e => ({{value: e, itemStyle: {{color: e >= 75 ? "#f85149" : e <= 25 ? "#238636" : "#58a6ff"}}}})), type: "line", smooth: !0, yAxisIndex: 0, lineStyle: {{width: r ? 1.5 : 2, color: "#58a6ff"}}, symbol: "circle", symbolSize: r ? 4 : 5, areaStyle: {{color: {{type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{offset: 0, color: "rgba(88,166,255,0.25)"}}, {{offset: 1, color: "rgba(88,166,255,0.03)"}}]}}}}, markLine: {{silent: !0, symbol: "none", lineStyle: {{type: "dashed", width: 1, color: "#58a6ff"}}, label: {{position: "end", formatter: "{{c}}%", fontSize: r ? 10 : 11}}, data: [{{yAxis: s}}]}}}}, {{name: "强势股占比", data: n, type: "line", smooth: !0, yAxisIndex: 1, lineStyle: {{width: r ? 1.5 : 2, color: "#f0883e"}}, symbol: "circle", symbolSize: r ? 4 : 5, areaStyle: {{color: {{type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{offset: 0, color: "rgba(240,136,62,0.25)"}}, {{offset: 1, color: "rgba(240,136,62,0.03)"}}]}}}}, markLine: {{silent: !0, symbol: "none", lineStyle: {{type: "dashed", width: 1, color: "#f0883e"}}, label: {{position: "end", formatter: "{{c}}%", fontSize: r ? 10 : 11}}, data: [{{yAxis: i}}]}}}}],
                    tooltip: {{trigger: "axis", backgroundColor: "#161b22", borderColor: "#30363d", textStyle: {{color: "#c9d1d9", fontSize: r ? 12 : 14}}, formatter: e => {{let t = "2026-" + e[0].axisValue + "<br/>"; return e.forEach(e => {{const a = "MA50占比" === e.seriesName ? "#58a6ff" : "#f0883e"; t += "<span style=\"color:" + a + "\">" + e.seriesName + ": " + e.value + "%</span><br/>"}}), t}}}}
                }});
            }},
            _connectCharts() {{const e = []; this.charts.kline && e.push(this.charts.kline), this.charts.sentiment && e.push(this.charts.sentiment), this.charts.strength && e.push(this.charts.strength), e.length > 1 && echarts.connect(e)}},
            switchIndex(e) {{this.currentIndex = e, this.charts.kline && (this.charts.kline.dispose(), this._initKlineChart(), this._connectCharts()), EventBus.emit("index:changed", {{indexCode: e}})}},
            refresh() {{this.renderSentiment(), this.renderKline(), this.renderStrength()}},
            _setupResizeHandler() {{let e; window.addEventListener("resize", () => {{clearTimeout(e), e = setTimeout(() => {{Object.values(this.charts).forEach(e => e && e.resize())}}, 250)}})}},
            _getEmotionColor: e => (EMOTION_STATUS.find(t => e >= t.threshold) || {{color: "#238636"}}).color,
            _getEmotionStatus: e => EMOTION_STATUS.find(t => e >= t.threshold) || {{color: "#238636", text: "冰点"}}
        }};
        
        /* UIManager */
        const UIManager = {{
            init() {{EventBus.on("report:changed", () => {{this.renderReportCard(), this.renderDataDetails()}}), EventBus.on("data:loaded", () => {{this.renderReportCard(), this.renderDataDetails(), ChartManager.init()}}), EventBus.on("data:updated", () => {{ChartManager.refresh(), this.renderReportCard(), this.renderDataDetails()}}); const e = document.getElementById("indexSelector"); e && e.addEventListener("change", e => {{ChartManager.switchIndex(e.target.value)}})}},
            renderReportCard() {{
                const e = document.getElementById("dailyReport"); if (!e) return;
                const t = DataManager.getCurrentDate(), a = DataManager.getCurrentReport();
                if (!a) return void(e.innerHTML = '<div class="loading">暂无数据</div>');
                const n = 0 === DataManager.currentReportIndex, r = DataManager.currentReportIndex === DataManager.reportDates.length - 1;
                e.innerHTML = '<div class="report-card"><div class="date-switcher"><button class="date-arrow" onclick="DataManager.switchReport(-1)" ' + (n ? "disabled" : "") + '>‹</button><span class="date-display">' + t + '</span><button class="date-arrow" onclick="DataManager.switchReport(1)" ' + (r ? "disabled" : "") + '>›</button></div><div class="report-content"><div class="report-section"><h4>周期定位</h4><p>' + a.phase + '</p></div><div class="report-section"><h4>操作方向</h4><p>' + a.action + '</p></div><div class="report-section"><h4>一句话总结</h4><p class="highlight">' + a.summary + '</p></div><a href="' + a.mowen_link + '" target="_blank" class="report-link">查看完整内容&gt;&gt;</a></div></div>';
            }},
            renderDataDetails() {{
                const e = document.getElementById("dataDetails"); if (!e) return;
                const t = DataManager.getCurrentDate(), a = DataManager.getCurrentMarketData(), n = DataManager.getKlineData("000001"), r = n.find(e => e.date === t);
                let s = '<div class="loading">暂无数据</div>';
                if (r) {{const e = n.findIndex(e => e.date === t), t = e > 0 ? n[e - 1] : null, a = t ? (r.close - t.close) / t.close * 100 : 0, n = a >= 0 ? "up-red" : "down-green", i = a >= 0 ? "+" : ""; s = r.close.toFixed(2) + ' <span class="' + n + '">(' + i + a.toFixed(2) + '%)</span>'}}
                let i = "-", l = "-", o = "-", c = "-";
                if (a) {{const e = DataManager.marketData.find(e => e.date < t), n = e ? (a.volume - e.volume) / e.volume * 100 : 0, r = n >= 0 ? "up-red" : "down-green", s = n >= 0 ? "+" : ""; i = Math.round(a.volume).toLocaleString() + '亿 <span class="' + r + '">(' + s + n.toFixed(1) + '%)</span>'; const d = a.down_count > 0 ? (a.up_count / a.down_count).toFixed(2) : "N/A"; l = '上涨: <span class="up-red">' + a.up_count.toLocaleString() + '</span> / 下跌: <span class="down-green">' + a.down_count.toLocaleString() + '</span> (' + d + ":1)", o = '涨停: <span class="up-red">' + a.limit_up + '</span> / 跌停: <span class="down-green">' + a.limit_down + "</span>", c = a.consecutive_height + "板"}}
                e.innerHTML = '<div class="report-section"><h4>上证指数</h4><p>' + s + '</p></div><div class="report-section"><h4>成交额</h4><p>' + i + '</p></div><div class="report-section"><h4>涨跌家数</h4><p>' + l + '</p></div><div class="report-section"><h4>涨停/跌停</h4><p>' + o + '</p></div><div class="report-section"><h4>连板高度</h4><p>' + c + '</p></div><a href="#" onclick="UIManager.showFullTable(); return false;" class="report-link" style="margin-top: 12px;">全部数据&gt;&gt;</a>';
            }},
            showFullTable() {{const e = document.getElementById("fullTableContainer"); e && (e.style.display = "block", this.renderTable(), e.scrollIntoView({{behavior: "smooth"}}))}},
            hideFullTable() {{const e = document.getElementById("fullTableContainer"); e && (e.style.display = "none")}},
            renderTable() {{const e = document.querySelector("#dataTable tbody"); e && (e.innerHTML = DataManager.marketData.map(e => {{let t = "emotion-ice"; return e.sentiment_index >= 75 ? t = "emotion-hot" : e.sentiment_index >= 50 ? t = "emotion-good" : e.sentiment_index >= 25 && (t = "emotion-normal"), "<tr><td>" + e.date + "</td><td class=\"" + t + "\">" + e.sentiment_index + "</td><td>" + Math.round(e.volume).toLocaleString() + "</td><td class=\"up-red\">" + e.up_count.toLocaleString() + "</td><td class=\"down-green\">" + e.down_count.toLocaleString() + "</td><td class=\"up-red\">" + e.limit_up + "</td><td class=\"down-green\">" + e.limit_down + "</td><td>" + e.major_pullback + "</td><td>" + e.consecutive_height + "</td><td>" + e.consecutive_performance + "</td><td>" + e.consecutive_promotion_rate + "</td><td>" + e.limit_up_performance + "</td><td>" + e.seal_rate + "</td><td>" + (e.ma50_percent ? e.ma50_percent.toFixed(2) + "%" : "-") + "</td><td>" + (e.strong_percent ? e.strong_percent.toFixed(2) + "%" : "-") + "</td></tr>"}}).join(""))}}
        }};
        
        /* App */
        const App = {{async init() {{console.log("App initializing..."), DataManager.init(KLINE_DATA), UIManager.init(), await DataManager.load(), console.log("App initialized")}}}};
        document.addEventListener("DOMContentLoaded", () => App.init());
    </script>
</body>
</html>'''
    
    # 保存文件
    output_path = '/root/.openclaw/workspace/stock/web/index-local.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ 本地预览版已生成: {output_path}')
    print(f'   文件大小: {len(html) / 1024:.1f} KB')
    print(f'   可直接双击打开，无需服务器')
    return output_path

if __name__ == '__main__':
    generate_local_html()
