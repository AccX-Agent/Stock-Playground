"""
Streamlit Web 界面 V2 - 扩展版
支持：更多数据维度、多周期K线、股票对比、数据导出
"""
import streamlit as st
import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/stock-playground/src')

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.mock_data import EnhancedMockStockData
from core.portfolio import Portfolio
from core.backtest import BacktestEngine
from strategies.examples import STRATEGIES

# 页面配置
st.set_page_config(
    page_title="股票模拟交易 V2",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'data' not in st.session_state:
    st.session_state.data = EnhancedMockStockData()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = Portfolio()

# 侧边栏导航
st.sidebar.title("📈 股票 Playground V2")

# 数据配置
with st.sidebar.expander("⚙️ 数据配置", expanded=False):
    if st.button("🔄 重新生成数据"):
        st.session_state.data = EnhancedMockStockData()
        st.rerun()
    
    years = st.slider("历史数据年限", 1, 10, 5)
    if st.button("应用年限"):
        st.session_state.data = EnhancedMockStockData(days=252*years)
        st.rerun()

page = st.sidebar.radio("导航", [
    "🏠 首页",
    "📊 行情中心",
    "🔍 个股详情",
    "💰 模拟交易",
    "💼 我的持仓",
    "📈 股票对比",
    "🔄 策略回测",
    "📜 交易记录",
    "💾 数据导出"
])

data = st.session_state.data
pf = st.session_state.portfolio

# ==================== 首页 ====================
if page == "🏠 首页":
    st.title("🚀 股票模拟交易 Playground V2")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("股票数量", len(data.stocks))
    with col2:
        st.metric("行业分类", len(data.get_industries()))
    with col3:
        st.metric("数据年限", f"{data.days // 252} 年")
    
    st.divider()
    
    st.markdown("""
    ### ✨ V2 新特性
    
    - **📊 更多股票**：50+ 只 A 股，覆盖 10 大行业
    - **📈 更多维度**：市盈率、换手率、市值、振幅
    - **🕐 多周期支持**：日线、周线、月线切换
    - **📊 股票对比**：多只票收益对比分析
    - **💾 数据导出**：CSV/JSON 格式导出
    - **⚙️ 可定制**：支持自定义股票生成
    
    ### 🚀 快速开始
    
    1. **查看行情**：去"行情中心"看全市场股票
    2. **模拟交易**：在"模拟交易"页面买卖股票
    3. **分析对比**：使用"股票对比"功能比较不同标的
    4. **策略回测**：测试你的交易策略
    """)

# ==================== 行情中心 ====================
elif page == "📊 行情中心":
    st.title("📊 行情中心")
    
    # 筛选条件
    cols = st.columns(3)
    with cols[0]:
        industries = ["全部"] + data.get_industries()
        selected_industry = st.selectbox("行业筛选", industries)
    with cols[1]:
        sort_by = st.selectbox("排序方式", [
            "涨跌幅", "成交额", "换手率", "市盈率", "市值"
        ])
    with cols[2]:
        sort_order = st.radio("排序", ["降序", "升序"], horizontal=True)
    
    # 获取并筛选股票
    stocks = data.get_stock_list(
        industry=None if selected_industry == "全部" else selected_industry
    )
    
    # 排序
    sort_map = {
        "涨跌幅": "change",
        "成交额": "amount",
        "换手率": "turnover",
        "市盈率": "pe_ratio",
        "市值": "market_cap"
    }
    stocks = sorted(stocks, key=lambda x: x[sort_map[sort_by]], 
                   reverse=(sort_order == "降序"))
    
    # 显示表格
    df = pd.DataFrame(stocks)
    df['涨跌'] = df['change'].apply(lambda x: f"{'🟢' if x >= 0 else '🔴'} {x:+.2f}%")
    df['成交额'] = df['amount'].apply(lambda x: f"{x:.2f}亿")
    df['市值'] = df['market_cap'].apply(lambda x: f"{x:.0f}亿")
    df['PE'] = df['pe_ratio']
    
    display_cols = ['code', 'name', 'industry', 'price', '涨跌', 
                   '成交额', '换手率', 'PE', '市值']
    rename_map = {
        'code': '代码', 'name': '名称', 'industry': '行业',
        'price': '现价', 'turnover': '换手率'
    }
    
    st.dataframe(
        df[display_cols].rename(columns=rename_map),
        use_container_width=True,
        height=600
    )
    
    # 行业分布图
    st.subheader("📊 行业分布")
    industry_counts = df['industry'].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=industry_counts.index,
        values=industry_counts.values,
        hole=0.4
    )])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==================== 个股详情 ====================
elif page == "🔍 个股详情":
    st.title("🔍 个股详情")
    
    stocks = data.get_stock_list()
    selected = st.selectbox(
        "选择股票",
        [s['code'] for s in stocks],
        format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}"
    )
    
    if selected:
        info = data.get_stock_info(selected)
        
        # 基本信息卡片
        cols = st.columns(4)
        with cols[0]:
            st.metric("最新价", f"¥{info['price']}", f"{info['total_return']:.2f}%")
        with cols[1]:
            st.metric("市盈率", f"{info['pe_ratio']}")
        with cols[2]:
            st.metric("市值", f"{info['market_cap']:.0f}亿")
        with cols[3]:
            st.metric("换手率", f"{info['turnover']}%")
        
        # K线周期选择
        st.subheader("📈 K线图")
        kline_cols = st.columns([1, 1, 3])
        with kline_cols[0]:
            freq = st.selectbox("周期", ["D", "W", "M"], 
                              format_func=lambda x: {"D": "日线", "W": "周线", "M": "月线"}[x])
        with kline_cols[1]:
            kline_days = st.slider("显示K线数", 20, 252, 60)
        
        # 获取K线数据
        kline = data.get_kline(selected, days=kline_days, freq=freq)
        
        # 绘制K线
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
        
        # K线
        fig.add_trace(go.Candlestick(
            x=kline['date'],
            open=kline['open'],
            high=kline['high'],
            low=kline['low'],
            close=kline['close'],
            name="K线"
        ), row=1, col=1)
        
        # 成交量
        colors = ['red' if c >= o else 'green' 
                 for c, o in zip(kline['close'], kline['open'])]
        fig.add_trace(go.Bar(
            x=kline['date'],
            y=kline['volume'],
            marker_color=colors,
            name="成交量"
        ), row=2, col=1)
        
        fig.update_layout(
            title=f"{info['name']} ({selected}) - { {'D': '日线', 'W': '周线', 'M': '月线'}[freq] }",
            height=600,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细数据
        st.subheader("📋 详细数据")
        detail_cols = st.columns(4)
        details = [
            ("今开", f"¥{info['open']}"),
            ("最高", f"¥{info['high']}"),
            ("最低", f"¥{info['low']}"),
            ("振幅", f"{info['amplitude']}%"),
            ("成交量", f"{info['volume']:,}"),
            ("成交额", f"¥{info['amount']/1e8:.2f}亿"),
            ("总回报", f"{info['total_return']}%"),
            ("年化波动", f"{info['volatility_annual']}%"),
            ("最大回撤", f"{info['max_drawdown']}%"),
            ("平均换手", f"{info['avg_turnover']}%"),
            ("平均成交", f"{info['avg_volume']:,}"),
            ("行业", info['industry'])
        ]
        for i, (label, value) in enumerate(details):
            with detail_cols[i % 4]:
                st.metric(label, value)

# ==================== 模拟交易 ====================
elif page == "💰 模拟交易":
    st.title("💰 模拟交易")
    
    stocks = data.get_stock_list()
    
    tab1, tab2 = st.tabs(["🟢 买入", "🔴 卖出"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            buy_code = st.selectbox(
                "选择股票",
                [s['code'] for s in stocks],
                format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}"
            )
            buy_price = st.number_input("买入价格", min_value=0.01, value=10.0, step=0.01)
            buy_amount = st.number_input("买入数量", min_value=100, value=1000, step=100)
            
            if st.button("买入", type="primary", use_container_width=True):
                stock = next(s for s in data.stocks if s.code == buy_code)
                result = pf.buy(buy_code, stock.name, buy_price, int(buy_amount))
                if result['success']:
                    st.success(result['message'])
                    st.session_state.portfolio = pf
                else:
                    st.error(result['message'])
        
        with col2:
            # 显示选中股票信息
            if buy_code:
                info = data.get_stock_info(buy_code)
                st.info(f"""
                **{info['name']}** ({buy_code})
                - 现价: ¥{info['price']}
                - 涨跌: {info['change']:.2f}%
                - 市值: {info['market_cap']:.0f}亿
                - PE: {info['pe_ratio']}
                """)
    
    with tab2:
        positions = pf.get_positions()
        if positions:
            col1, col2 = st.columns(2)
            with col1:
                sell_code = st.selectbox(
                    "选择持仓",
                    [p['code'] for p in positions],
                    format_func=lambda x: f"{x} - {next(p['name'] for p in positions if p['code'] == x)}"
                )
                pos = next(p for p in positions if p['code'] == sell_code)
                sell_price = st.number_input("卖出价格", min_value=0.01, 
                                            value=float(pos['current_price']), step=0.01)
                sell_amount = st.number_input("卖出数量", min_value=100, 
                                             max_value=int(pos['amount']), 
                                             value=int(pos['amount']), step=100)
                
                if st.button("卖出", type="primary", use_container_width=True):
                    stock = next(s for s in data.stocks if s.code == sell_code)
                    result = pf.sell(sell_code, stock.name, sell_price, int(sell_amount))
                    if result['success']:
                        st.success(result['message'])
                        st.session_state.portfolio = pf
                    else:
                        st.error(result['message'])
            
            with col2:
                st.info(f"""
                **{pos['name']}** ({sell_code})
                - 持仓: {pos['amount']} 股
                - 成本: ¥{pos['avg_cost']}
                - 现价: ¥{pos['current_price']}
                - 盈亏: {pos['profit']:+.2f} ({pos['profit_pct']:+.2f}%)
                """)
        else:
            st.info("暂无持仓")

# ==================== 我的持仓 ====================
elif page == "💼 我的持仓":
    st.title("💼 我的持仓")
    
    summary = pf.get_summary()
    positions = pf.get_positions()
    
    # 账户概览
    st.subheader("📊 账户概览")
    cols = st.columns(4)
    with cols[0]:
        delta_color = "normal" if summary['total_profit'] >= 0 else "inverse"
        st.metric("总资产", f"¥{summary['total_value']:,.2f}", 
                 f"{summary['total_profit_pct']:+.2f}%", delta_color=delta_color)
    with cols[1]:
        st.metric("可用资金", f"¥{summary['cash']:,.2f}")
    with cols[2]:
        st.metric("持仓市值", f"¥{summary['positions_value']:,.2f}")
    with cols[3]:
        st.metric("总盈亏", f"¥{summary['total_profit']:,.2f}")
    
    st.divider()
    
    # 持仓明细
    st.subheader("📋 持仓明细")
    if positions:
        df = pd.DataFrame(positions)
        df['盈亏'] = df['profit'].apply(lambda x: f"{'🟢' if x >= 0 else '🔴'} {x:+,.2f}")
        df['盈亏率'] = df['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        df['市值'] = df['market_value'].apply(lambda x: f"¥{x:,.2f}")
        df['成本'] = df['avg_cost'].apply(lambda x: f"¥{x:.2f}")
        df['现价'] = df['current_price'].apply(lambda x: f"¥{x:.2f}")
        
        st.dataframe(
            df[['code', 'name', 'amount', '成本', '现价', '市值', '盈亏', '盈亏率']],
            use_container_width=True
        )
        
        # 持仓分布图
        fig = go.Figure(data=[go.Pie(
            labels=[p['name'] for p in positions],
            values=[p['market_value'] for p in positions],
            hole=0.4
        )])
        fig.update_layout(title="持仓分布", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无持仓")

# ==================== 股票对比 ====================
elif page == "📈 股票对比":
    st.title("📈 股票对比分析")
    
    stocks = data.get_stock_list()
    selected_codes = st.multiselect(
        "选择要对比的股票（最多5只）",
        [s['code'] for s in stocks],
        default=[stocks[0]['code'], stocks[1]['code']],
        format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}",
        max_selections=5
    )
    
    if len(selected_codes) >= 2:
        days = st.slider("对比天数", 5, 252, 60)
        
        # 对比表格
        comparison = data.compare_stocks(selected_codes, days)
        st.subheader("📊 对比数据")
        st.dataframe(comparison, use_container_width=True)
        
        # 收益曲线对比
        st.subheader("📈 收益曲线对比")
        fig = go.Figure()
        
        for code in selected_codes:
            df = data.data[code].tail(days).copy()
            df['normalized'] = df['close'] / df['close'].iloc[0] * 100
            info = data._stock_info[code]
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['normalized'],
                mode='lines',
                name=f"{info['name']} ({code})"
            ))
        
        fig.update_layout(
            title="收益率对比（归一化到100）",
            xaxis_title="日期",
            yaxis_title="收益率",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 柱状图对比
        st.subheader("📊 关键指标对比")
        metrics = ['return', 'volatility', 'avg_turnover']
        metric_names = ['收益率(%)', '波动率(%)', '平均换手率(%)']
        
        fig = go.Figure()
        for i, metric in enumerate(metrics):
            fig.add_trace(go.Bar(
                name=metric_names[i],
                x=comparison['name'],
                y=comparison[metric],
                offsetgroup=i
            ))
        
        fig.update_layout(
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请至少选择2只股票进行对比")

# ==================== 策略回测 ====================
elif page == "🔄 策略回测":
    st.title("🔄 策略回测")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("参数设置")
        strategy_name = st.selectbox("选择策略", list(STRATEGIES.keys()))
        backtest_days = st.slider("回测天数", 30, 252*3, 252)
        initial_cash = st.number_input("初始资金", min_value=10000, value=100000, step=10000)
        
        run_bt = st.button("开始回测", type="primary", use_container_width=True)
    
    with col2:
        if run_bt:
            with st.spinner("正在运行回测..."):
                backtest_data = EnhancedMockStockData(days=backtest_days)
                stock_data = {code: df for code, df in backtest_data.data.items()}
                
                engine = BacktestEngine(initial_cash=initial_cash)
                result = engine.run(STRATEGIES[strategy_name], stock_data)
            
            st.subheader("📊 回测结果")
            
            cols = st.columns(4)
            with cols[0]:
                st.metric("初始资金", f"¥{result.initial_cash:,.2f}")
            with cols[1]:
                st.metric("最终资产", f"¥{result.final_value:,.2f}")
            with cols[2]:
                delta_color = "normal" if result.total_return >= 0 else "inverse"
                st.metric("总收益", f"¥{result.total_return:,.2f}",
                         f"{result.total_return_pct:+.2f}%", delta_color=delta_color)
            with cols[3]:
                st.metric("交易次数", len(result.trades))
            
            if result.daily_values:
                df = pd.DataFrame(result.daily_values)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                  vertical_spacing=0.1,
                                  subplot_titles=("资产曲线", "持仓市值"))
                
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['value'],
                    mode='lines', name='总资产', line=dict(color='blue')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df['date'], y=[initial_cash]*len(df),
                    mode='lines', name='初始资金',
                    line=dict(dash='dash', color='gray')
                ), row=1, col=1)
                
                fig.add_trace(go.Bar(
                    x=df['date'], y=df['positions_value'],
                    name='持仓市值', marker_color='green'
                ), row=2, col=1)
                
                fig.update_layout(height=600, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

# ==================== 交易记录 ====================
elif page == "📜 交易记录":
    st.title("📜 交易记录")
    
    trades = pf.get_trades(limit=100)
    if trades:
        df = pd.DataFrame(reversed(trades))
        df['操作'] = df['action'].apply(lambda x: '🟢 买入' if x == 'buy' else '🔴 卖出')
        df['金额'] = df['total'].apply(lambda x: f"¥{x:,.2f}")
        df['价格'] = df['price'].apply(lambda x: f"¥{x:.2f}")
        
        st.dataframe(
            df[['time', 'code', 'name', '操作', '价格', 'amount', '金额']],
            use_container_width=True,
            height=600
        )
    else:
        st.info("暂无交易记录")

# ==================== 数据导出 ====================
elif page == "💾 数据导出":
    st.title("💾 数据导出")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 导出设置")
        
        stocks = data.get_stock_list()
        export_options = ["全部股票"] + [s['code'] for s in stocks]
        export_stock = st.selectbox(
            "选择股票",
            export_options,
            format_func=lambda x: "全部股票" if x == "全部股票" else f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}"
        )
        
        export_format = st.radio("导出格式", ["CSV", "JSON"])
        export_days = st.slider("导出天数", 5, data.days, 252)
        
        if st.button("生成导出文件", type="primary"):
            code = 'all' if export_stock == "全部股票" else export_stock
            ext = 'csv' if export_format == "CSV" else 'json'
            filepath = f"/tmp/stock_data_{code.replace('.', '_')}.{ext}"
            
            try:
                data.export_data(code, filepath, ext.lower(), export_days)
                
                with open(filepath, 'rb') as f:
                    file_bytes = f.read()
                
                st.download_button(
                    label=f"⬇️ 下载 {export_format}",
                    data=file_bytes,
                    file_name=f"stock_data_{code.replace('.', '_')}.{ext}",
                    mime="text/csv" if export_format == "CSV" else "application/json"
                )
                
                st.success(f"✅ 文件已生成，包含 {export_days} 天数据")
            except Exception as e:
                st.error(f"❌ 导出失败: {e}")
    
    with col2:
        st.subheader("📋 数据说明")
        st.markdown("""
        **导出字段说明：**
        
        | 字段 | 说明 |
        |------|------|
        | date | 交易日期 |
        | open | 开盘价 |
        | high | 最高价 |
        | low | 最低价 |
        | close | 收盘价 |
        | volume | 成交量 |
        | amount | 成交额 |
        | turnover | 换手率(%) |
        | pe_ratio | 市盈率 |
        | market_cap | 市值(亿) |
        | amplitude | 振幅(%) |
        | change_pct | 涨跌幅(%) |
        """)
