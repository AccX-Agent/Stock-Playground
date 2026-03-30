"""
Streamlit Web 界面 V3 - 时间推进版
支持：时间推进系统、持仓分析、沪深300基准对比
"""
import streamlit as st
import sys
import os
from pathlib import Path

# 获取项目根目录（兼容 Windows/Linux）
PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_ROOT / 'src'

# 确保 src 在路径中
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Windows 兼容：切换工作目录到项目根目录
os.chdir(PROJECT_ROOT)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 尝试导入，失败时给出详细错误
try:
    from data.mock_data import EnhancedMockStockData, StockConfig, Industry
    from core.portfolio import Portfolio
    from core.backtest import BacktestEngine
    from core.time_manager import TimeManager
    from core.position_analyzer import PositionAnalyzer
    from strategies.examples import STRATEGIES
except ImportError as e:
    st.error(f"❌ 导入模块失败: {e}")
    st.error(f"📁 项目根目录: {PROJECT_ROOT}")
    st.error(f"📁 src 目录: {SRC_DIR}")
    st.error(f"📁 当前工作目录: {os.getcwd()}")
    st.error(f"📋 sys.path: {sys.path}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="股票模拟交易 V3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化 session state ====================
def init_session_state():
    """初始化 session state"""
    if 'data' not in st.session_state:
        st.session_state.data = EnhancedMockStockData()
        st.session_state.all_dates = st.session_state.data.get_all_dates()
    
    if 'time_manager' not in st.session_state:
        st.session_state.time_manager = TimeManager(st.session_state.all_dates)
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio()
    
    if 'selected_position_for_analysis' not in st.session_state:
        st.session_state.selected_position_for_analysis = None

init_session_state()

# 获取全局对象
data = st.session_state.data
tm = st.session_state.time_manager
pf = st.session_state.portfolio
current_date = tm.current_date

# ==================== 顶部时间控制栏 ====================
def render_time_header():
    """渲染顶部时间控制栏"""
    header_cols = st.columns([2, 1, 1, 1, 1])
    
    with header_cols[0]:
        st.markdown(f"### 📅 当前日期: **{current_date}**")
    
    with header_cols[1]:
        st.progress(tm.progress_pct / 100, text=f"进度: {tm.progress}")
    
    with header_cols[2]:
        if not tm.is_last_date:
            next_date = tm.next_date
            st.caption(f"下一交易日: {next_date}")
        else:
            st.caption("⚠️ 已是最后一天")
    
    with header_cols[3]:
        if st.button("➡️ 下一交易日", type="primary", disabled=tm.is_last_date):
            if tm.advance():
                # 日期推进后更新所有持仓价格
                current_date = tm.current_date
                prices = {}
                for code in pf.positions.keys():
                    if code in data.data:
                        row = data.data[data.data['date'] == current_date]
                        if not row.empty:
                            prices[code] = float(row['close'].iloc[0])
                pf.update_prices(prices)
                st.session_state.portfolio = pf
                st.rerun()
    
    with header_cols[4]:
        if st.button("🔄 重置数据"):
            st.session_state.data = EnhancedMockStockData()
            st.session_state.all_dates = st.session_state.data.get_all_dates()
            st.session_state.time_manager = TimeManager(st.session_state.all_dates)
            st.session_state.portfolio = Portfolio()
            st.rerun()

# 侧边栏导航
st.sidebar.title("📈 股票 Playground V3")

# 数据配置
with st.sidebar.expander("⚙️ 数据配置", expanded=False):
    years = st.slider("历史数据年限", 1, 10, 5, key="data_years")
    if st.button("应用年限"):
        with st.spinner("重新生成数据中..."):
            st.session_state.data = EnhancedMockStockData(days=252*years)
            st.session_state.all_dates = st.session_state.data.get_all_dates()
            st.session_state.time_manager = TimeManager(st.session_state.all_dates)
            st.session_state.portfolio = Portfolio()
        st.rerun()

page = st.sidebar.radio("导航", [
    "🏠 首页",
    "📊 行情中心",
    "🔍 个股详情",
    "💰 模拟交易",
    "💼 我的持仓",
    "📈 持仓回测",  # 新增页面
    "📊 股票对比",
    "🔄 策略回测",
    "📜 交易记录",
    "💾 数据导出"
])

# ==================== 页面内容 ====================

# ==================== 首页 ====================
if page == "🏠 首页":
    st.title("🚀 股票模拟交易 Playground V3")
    
    # 顶部时间控制
    render_time_header()
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("股票数量", len(data.stocks))
    with col2:
        st.metric("行业分类", len(data.get_industries()))
    with col3:
        st.metric("数据年限", f"{data.days // 252} 年")
    with col4:
        st.metric("当前交易日", f"{tm.current_index + 1}/{len(tm.all_dates)}")
    
    st.divider()
    
    st.markdown("""
    ### ✨ V3 新特性（时间推进版）
    
    - **⏰ 真实时间推进**：可以逐日推进，体验真实的交易时间线
    - **📊 持仓分析**：查看持仓的历史收益曲线、最大盈亏、最佳卖出点
    - **📈 沪深300对比**：持仓表现与大盘基准对比
    - **🔍 最大回撤分析**：识别持仓期间的最大回撤
    
    ### 🚀 快速开始
    
    1. **查看行情**：去"行情中心"看全市场股票
    2. **模拟交易**：在"模拟交易"页面买卖股票（按当前日期价格）
    3. **推进时间**：点击右上角「下一交易日」进入下一天
    4. **持仓分析**：在"持仓回测"页面分析持仓表现
    """)

# ==================== 行情中心 ====================
elif page == "📊 行情中心":
    st.title("📊 行情中心")
    render_time_header()
    st.divider()
    
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
    
    # 获取并筛选股票（使用当前日期的价格）
    stocks = data.get_stock_list(
        industry=None if selected_industry == "全部" else selected_industry
    )
    
    # 更新价格为当前日期的价格
    for stock in stocks:
        code = stock['code']
        if code in data.data:
            df = data.data[code]
            # 获取当前日期及之前的数据
            mask = df['date'] <= current_date
            filtered = df[mask]
            if len(filtered) >= 2:
                latest = filtered.iloc[-1]
                prev = filtered.iloc[-2]
                stock['price'] = round(latest['close'], 2)
                stock['change'] = round((latest['close'] - prev['close']) / prev['close'] * 100, 2)
    
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
    
    # 重命名列为中文
    df_display = df.rename(columns={
        'code': '代码',
        'name': '名称',
        'industry': '行业',
        'price': '现价',
        'change': '涨跌',
        'amount': '成交额',
        'turnover': '换手率',
        'pe_ratio': 'PE',
        'market_cap': '市值'
    })
    
    # 格式化显示
    df_display['涨跌'] = df['change'].apply(lambda x: f"{'🟢' if x >= 0 else '🔴'} {x:+.2f}%")
    df_display['成交额'] = df['amount'].apply(lambda x: f"{x:.2f}亿")
    df_display['市值'] = df['market_cap'].apply(lambda x: f"{x:.0f}亿")
    
    display_cols = ['代码', '名称', '行业', '现价', '涨跌', '成交额', '换手率', 'PE', '市值']
    
    st.dataframe(
        df_display[display_cols],
        width='stretch',
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
    st.plotly_chart(fig, width="stretch")

# ==================== 个股详情 ====================
elif page == "🔍 个股详情":
    st.title("🔍 个股详情")
    render_time_header()
    st.divider()
    
    stocks = data.get_stock_list()
    selected = st.selectbox(
        "选择股票",
        [s['code'] for s in stocks],
        format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}"
    )
    
    if selected:
        info = data.get_stock_info(selected)
        
        # 获取当前日期的价格
        df = data.data[selected]
        mask = df['date'] <= current_date
        filtered = df[mask]
        
        if len(filtered) >= 1:
            latest = filtered.iloc[-1]
            current_price = latest['close']
            
            # 基本信息卡片
            cols = st.columns(4)
            with cols[0]:
                if len(filtered) > 1:
                    prev = filtered.iloc[-2]
                    change = (latest['close'] - prev['close']) / prev['close'] * 100
                else:
                    change = 0
                st.metric("最新价", f"¥{latest['close']:.2f}", f"{change:+.2f}%")
            with cols[1]:
                st.metric("市盈率", f"{latest['pe_ratio']:.2f}")
            with cols[2]:
                st.metric("市值", f"{latest['market_cap']:.0f}亿")
            with cols[3]:
                st.metric("换手率", f"{latest['turnover']:.2f}%")
            
            # K线周期选择
            st.subheader("📈 K线图（截至当前日期）")
            kline_cols = st.columns([1, 1, 3])
            with kline_cols[0]:
                freq = st.selectbox("周期", ["D", "W", "M"], 
                                  format_func=lambda x: {"D": "日线", "W": "周线", "M": "月线"}[x])
            with kline_cols[1]:
                kline_days = st.slider("显示K线数", 20, min(252, len(filtered)), min(60, len(filtered)))
            
            # 获取K线数据
            kline = filtered.tail(kline_days).copy()
            
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
            
            st.plotly_chart(fig, width="stretch")

# ==================== 模拟交易 ====================
elif page == "💰 模拟交易":
    st.title("💰 模拟交易")
    render_time_header()
    st.divider()
    
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
            
            # 获取当前日期的价格
            buy_price = 10.0
            if buy_code in data.data:
                df = data.data[buy_code]
                mask = df['date'] <= current_date
                filtered = df[mask]
                if not filtered.empty:
                    buy_price = float(filtered.iloc[-1]['close'])
            
            buy_price_input = st.number_input("买入价格", min_value=0.01, value=round(buy_price, 2), step=0.01)
            buy_amount = st.number_input("买入数量", min_value=100, value=1000, step=100)
            
            if st.button("买入", type="primary", width="stretch"):
                stock = next(s for s in data.stocks if s.code == buy_code)
                result = pf.buy(buy_code, stock.name, buy_price_input, int(buy_amount), trade_date=current_date)
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
                - 当前日期: {current_date}
                - 当前价格: ¥{buy_price_input}
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
                
                # 获取当前日期的价格
                sell_price = pos['current_price']
                if sell_code in data.data:
                    df = data.data[sell_code]
                    mask = df['date'] <= current_date
                    filtered = df[mask]
                    if not filtered.empty:
                        sell_price = float(filtered.iloc[-1]['close'])
                
                sell_price_input = st.number_input("卖出价格", min_value=0.01, 
                                            value=round(sell_price, 2), step=0.01)
                sell_amount = st.number_input("卖出数量", min_value=100, 
                                             max_value=int(pos['amount']), 
                                             value=int(pos['amount']), step=100)
                
                if st.button("卖出", type="primary", width="stretch"):
                    stock = next(s for s in data.stocks if s.code == sell_code)
                    result = pf.sell(sell_code, stock.name, sell_price_input, int(sell_amount), trade_date=current_date)
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
                - 当前价: ¥{sell_price_input}
                - 买入日期: {pos.get('buy_date', '未知')}
                - 盈亏: {pos['profit']:+,.2f} ({pos['profit_pct']:+.2f}%)
                """)
        else:
            st.info("暂无持仓")

# ==================== 我的持仓 ====================
elif page == "💼 我的持仓":
    st.title("💼 我的持仓")
    render_time_header()
    st.divider()
    
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
        df['买入日期'] = df['buy_date']
        
        # 添加查看分析按钮
        def add_analysis_button(row):
            if st.button(f"📊 分析", key=f"analyze_{row['code']}"):
                st.session_state.selected_position_for_analysis = row['code']
                st.switch_page("📈 持仓回测")  # 这会触发导航
        
        display_cols = ['code', 'name', 'amount', '成本', '现价', '市值', '盈亏', '盈亏率', '买入日期']
        
        st.dataframe(
            df[display_cols],
            width="stretch"
        )
        
        # 持仓分布图
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=[p['name'] for p in positions],
                values=[p['market_value'] for p in positions],
                hole=0.4
            )])
            fig.update_layout(title="持仓市值分布", height=400)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # 盈亏分布
            fig = go.Figure(data=[go.Bar(
                x=[p['name'] for p in positions],
                y=[p['profit'] for p in positions],
                marker_color=['green' if p['profit'] >= 0 else 'red' for p in positions]
            )])
            fig.update_layout(title="持仓盈亏", height=400)
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("暂无持仓")

# ==================== 持仓回测（新增页面） ====================
elif page == "📈 持仓回测":
    st.title("📈 持仓回测分析")
    render_time_header()
    st.divider()
    
    positions = pf.get_positions()
    
    if not positions:
        st.warning("暂无持仓，请先买入股票后再进行分析")
    else:
        # 选择持仓
        selected_code = st.selectbox(
            "选择要分析的持仓",
            [p['code'] for p in positions],
            format_func=lambda x: f"{x} - {next(p['name'] for p in positions if p['code'] == x)}",
            key="analysis_select"
        )
        
        if selected_code:
            pos = next(p for p in positions if p['code'] == selected_code)
            
            # 创建分析器
            if selected_code in data.data:
                analyzer = PositionAnalyzer(
                    stock_data=data.data[selected_code],
                    hs300_data=data.hs300_data
                )
                
                # 执行分析
                result = analyzer.analyze(
                    code=pos['code'],
                    name=pos['name'],
                    buy_date=pos.get('buy_date', current_date),
                    buy_price=pos['avg_cost'],
                    amount=pos['amount'],
                    current_date=current_date,
                    current_price=pos['current_price']
                )
                
                # 显示基本信息
                st.subheader(f"📊 {result.name} ({result.code}) 持仓分析")
                
                info_cols = st.columns(4)
                with info_cols[0]:
                    st.metric("买入日期", result.buy_date)
                with info_cols[1]:
                    st.metric("持仓天数", len(result.daily_returns))
                with info_cols[2]:
                    st.metric("买入价格", f"¥{result.buy_price:.2f}")
                with info_cols[3]:
                    st.metric("当前价格", f"¥{result.current_price:.2f}")
                
                st.divider()
                
                # 收益指标
                st.subheader("📈 收益表现")
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    delta_color = "normal" if result.total_return_pct >= 0 else "inverse"
                    st.metric("总收益率", f"{result.total_return_pct:+.2f}%", 
                             delta_color=delta_color)
                with metrics_cols[1]:
                    st.metric("总盈亏额", f"¥{result.total_return_amount:+,.2f}")
                with metrics_cols[2]:
                    st.metric("同期沪深300", f"{result.hs300_return_pct:+.2f}%")
                with metrics_cols[3]:
                    alpha_color = "normal" if result.alpha >= 0 else "inverse"
                    st.metric("超额收益(α)", f"{result.alpha:+.2f}%", delta_color=alpha_color)
                
                # 历史极值
                st.subheader("📉 历史极值")
                extreme_cols = st.columns(4)
                with extreme_cols[0]:
                    st.metric("最大盈利", f"{result.max_profit_pct:+.2f}%", delta_color="normal")
                with extreme_cols[1]:
                    st.metric("最大亏损", f"{result.max_loss_pct:+.2f}%", delta_color="inverse")
                with extreme_cols[2]:
                    st.metric("最大回撤", f"{result.max_drawdown_pct:.2f}%", delta_color="inverse")
                with extreme_cols[3]:
                    st.metric("当前回撤", f"{(result.best_sell_return_pct - result.total_return_pct):.2f}%")
                
                # 最佳卖出点
                st.subheader("🎯 最佳卖出点分析")
                best_cols = st.columns(4)
                with best_cols[0]:
                    st.metric("最佳卖出日期", result.best_sell_date)
                with best_cols[1]:
                    st.metric("最佳卖出价格", f"¥{result.best_sell_price:.2f}")
                with best_cols[2]:
                    st.metric("最佳收益率", f"{result.best_sell_return_pct:+.2f}%")
                with best_cols[3]:
                    st.metric("错过收益", f"{result.missed_profit_pct:+.2f}%", delta_color="inverse")
                
                if result.missed_profit_pct > 5:
                    st.warning(f"⚠️ 您错过了 **{result.missed_profit_pct:.2f}%** 的潜在收益！建议在盈利时适时止盈。")
                
                st.divider()
                
                # 收益曲线图
                st.subheader("📊 收益曲线")
                
                if result.daily_returns:
                    df_returns = pd.DataFrame(result.daily_returns)
                    
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=("收益率对比", "价格走势")
                    )
                    
                    # 股票收益率
                    fig.add_trace(go.Scatter(
                        x=df_returns['date'],
                        y=df_returns['return_pct'],
                        mode='lines',
                        name=f"{result.name} 收益率",
                        line=dict(color='blue', width=2)
                    ), row=1, col=1)
                    
                    # 沪深300收益率
                    fig.add_trace(go.Scatter(
                        x=df_returns['date'],
                        y=df_returns['hs300_return_pct'],
                        mode='lines',
                        name="沪深300 收益率",
                        line=dict(color='orange', width=2, dash='dash')
                    ), row=1, col=1)
                    
                    # 零线
                    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)
                    
                    # 标注最佳卖出点
                    best_idx = df_returns['return_pct'].idxmax()
                    best_date = df_returns.iloc[best_idx]['date']
                    best_return = df_returns.iloc[best_idx]['return_pct']
                    
                    fig.add_trace(go.Scatter(
                        x=[best_date],
                        y=[best_return],
                        mode='markers',
                        name='最佳卖出点',
                        marker=dict(color='green', size=15, symbol='star')
                    ), row=1, col=1)
                    
                    # 价格走势
                    fig.add_trace(go.Scatter(
                        x=df_returns['date'],
                        y=df_returns['price'],
                        mode='lines',
                        name='股价',
                        line=dict(color='purple', width=2)
                    ), row=2, col=1)
                    
                    # 买入价线
                    fig.add_hline(y=result.buy_price, line_dash="dash", 
                                 line_color="red", annotation_text="买入价", row=2, col=1)
                    
                    fig.update_layout(height=700, showlegend=True)
                    st.plotly_chart(fig, width="stretch")
                    
                    # 每日详细数据表格
                    with st.expander("📋 查看每日详细数据"):
                        display_df = df_returns.copy()
                        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                        display_df.columns = ['日期', '价格', '收益率(%)', '盈亏额', '沪深300收益率(%)', '成交量']
                        display_df['收益率(%)'] = display_df['收益率(%)'].round(2)
                        display_df['沪深300收益率(%)'] = display_df['沪深300收益率(%)'].round(2)
                        display_df['盈亏额'] = display_df['盈亏额'].round(2)
                        st.dataframe(display_df, width="stretch", height=400)

# ==================== 股票对比 ====================
elif page == "📊 股票对比":
    st.title("📊 股票对比分析")
    render_time_header()
    st.divider()
    
    stocks = data.get_stock_list()
    selected_codes = st.multiselect(
        "选择要对比的股票（最多5只）",
        [s['code'] for s in stocks],
        default=[stocks[0]['code'], stocks[1]['code']],
        format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}",
        max_selections=5
    )
    
    if len(selected_codes) >= 2:
        max_days = min(len(data.data[code][data.data[code]['date'] <= current_date]) for code in selected_codes)
        days = st.slider("对比天数", 5, max(5, max_days), min(60, max_days))
        
        # 收益曲线对比
        st.subheader("📈 收益曲线对比")
        fig = go.Figure()
        
        for code in selected_codes:
            df = data.data[code]
            mask = df['date'] <= current_date
            filtered = df[mask].tail(days).copy()
            
            if not filtered.empty:
                filtered['normalized'] = filtered['close'] / filtered['close'].iloc[0] * 100
                info = data._stock_info[code]
                
                fig.add_trace(go.Scatter(
                    x=filtered['date'],
                    y=filtered['normalized'],
                    mode='lines',
                    name=f"{info['name']} ({code})"
                ))
        
        # 添加沪深300基准
        if data.hs300_data is not None:
            mask = data.hs300_data['date'] <= current_date
            hs300_filtered = data.hs300_data[mask].tail(days).copy()
            if not hs300_filtered.empty:
                hs300_filtered['normalized'] = hs300_filtered['close'] / hs300_filtered['close'].iloc[0] * 100
                fig.add_trace(go.Scatter(
                    x=hs300_filtered['date'],
                    y=hs300_filtered['normalized'],
                    mode='lines',
                    name="沪深300 (基准)",
                    line=dict(dash='dash', color='gray')
                ))
        
        fig.update_layout(
            title="收益率对比（归一化到100）",
            xaxis_title="日期",
            yaxis_title="收益率",
            height=500
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("请至少选择2只股票进行对比")

# ==================== 策略回测 ====================
elif page == "🔄 策略回测":
    st.title("🔄 策略回测")
    render_time_header()
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("参数设置")
        strategy_name = st.selectbox("选择策略", list(STRATEGIES.keys()))
        max_days = len(tm.all_dates) - 1
        backtest_days = st.slider("回测天数", 30, max_days, min(252, max_days))
        initial_cash = st.number_input("初始资金", min_value=10000, value=100000, step=10000)
        
        run_bt = st.button("开始回测", type="primary", width="stretch")
    
    with col2:
        if run_bt:
            with st.spinner("正在运行回测..."):
                # 使用历史数据回测
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
                st.plotly_chart(fig, width="stretch")

# ==================== 交易记录 ====================
elif page == "📜 交易记录":
    st.title("📜 交易记录")
    render_time_header()
    st.divider()
    
    trades = pf.get_trades(limit=100)
    if trades:
        df = pd.DataFrame(reversed(trades))
        df['操作'] = df['action'].apply(lambda x: '🟢 买入' if x == 'buy' else '🔴 卖出')
        df['金额'] = df['total'].apply(lambda x: f"¥{x:,.2f}")
        df['价格'] = df['price'].apply(lambda x: f"¥{x:.2f}")
        
        # 显示交易日期
        if 'trade_date' in df.columns:
            df['交易日期'] = df['trade_date']
            display_cols = ['trade_date', 'code', 'name', '操作', '价格', 'amount', '金额']
        else:
            display_cols = ['time', 'code', 'name', '操作', '价格', 'amount', '金额']
        
        st.dataframe(
            df[display_cols],
            width="stretch",
            height=600
        )
    else:
        st.info("暂无交易记录")

# ==================== 数据导出 ====================
elif page == "💾 数据导出":
    st.title("💾 数据导出")
    render_time_header()
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 导出设置")
        
        stocks = data.get_stock_list()
        export_options = ["全部股票", "沪深300"] + [s['code'] for s in stocks]
        export_stock = st.selectbox(
            "选择股票",
            export_options,
            format_func=lambda x: "全部股票" if x == "全部股票" else 
                                "沪深300" if x == "沪深300" else 
                                f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}"
        )
        
        export_format = st.radio("导出格式", ["CSV", "JSON"])
        max_export_days = len(tm.all_dates)
        export_days = st.slider("导出天数", 5, max_export_days, min(252, max_export_days))
        
        if st.button("生成导出文件", type="primary"):
            if export_stock == "沪深300":
                if data.hs300_data is not None:
                    ext = 'csv' if export_format == "CSV" else 'json'
                    filepath = f"/tmp/hs300_data.{ext}"
                    df = data.hs300_data.tail(export_days).copy()
                    if export_format == "CSV":
                        df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    else:
                        df.to_json(filepath, orient='records', force_ascii=False, indent=2)
                    
                    with open(filepath, 'rb') as f:
                        file_bytes = f.read()
                    
                    st.download_button(
                        label=f"⬇️ 下载 {export_format}",
                        data=file_bytes,
                        file_name=f"hs300_data.{ext}",
                        mime="text/csv" if export_format == "CSV" else "application/json"
                    )
                    st.success(f"✅ 沪深300数据已生成，包含 {len(df)} 条记录")
                else:
                    st.error("❌ 沪深300数据未生成")
            else:
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
