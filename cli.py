"""
CLI 入口 V2 - 扩展版
"""
import click
import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/stock-playground/src')

from data.mock_data import EnhancedMockStockData
from core.portfolio import Portfolio
from core.backtest import BacktestEngine
from strategies.examples import STRATEGIES


@click.group()
@click.option('--data-years', default=5, help='历史数据年限')
@click.pass_context
def cli(ctx, data_years):
    """股票模拟交易 CLI V2"""
    ctx.ensure_object(dict)
    ctx.obj['data'] = EnhancedMockStockData(days=252*data_years)
    ctx.obj['portfolio'] = Portfolio()


@cli.command()
@click.option('--industry', help='按行业筛选')
@click.option('--sort', default='change', help='排序字段')
@click.option('--limit', default=20, help='显示数量')
@click.pass_context
def market(ctx, industry, sort, limit):
    """查看行情"""
    data = ctx.obj['data']
    stocks = data.get_stock_list(industry=industry)
    
    # 排序
    stocks = sorted(stocks, key=lambda x: x.get(sort, 0), reverse=True)
    stocks = stocks[:limit]
    
    click.echo('\n📈 股票行情')
    click.echo('-' * 90)
    click.echo(f'{"代码":<12} {"名称":<10} {"行业":<8} {"现价":<8} {"涨跌":<10} {"换手":<8} {"PE":<8} {"市值":<10}')
    click.echo('-' * 90)
    
    for s in stocks:
        change_color = '🟢' if s['change'] >= 0 else '🔴'
        click.echo(f"{s['code']:<12} {s['name']:<10} {s['industry']:<8} "
                  f"¥{s['price']:<7.2f} {change_color}{s['change']:<7.2f}% "
                  f"{s['turnover']:<7.2f}% {s['pe_ratio']:<7.2f} {s['market_cap']:<8.0f}亿")
    
    click.echo('-' * 90)
    click.echo(f"共 {len(stocks)} 只")


@cli.command()
@click.pass_context
def industries(ctx):
    """查看行业列表"""
    data = ctx.obj['data']
    industries = data.get_industries()
    
    click.echo('\n🏭 行业分类')
    click.echo('-' * 40)
    for i, ind in enumerate(industries, 1):
        count = len([s for s in data.stocks if s.industry.value == ind])
        click.echo(f"{i}. {ind} ({count}只)")


@cli.command()
@click.argument('code')
@click.option('--days', default=30, help='显示天数')
@click.option('--freq', default='D', type=click.Choice(['D', 'W', 'M']), help='周期')
@click.pass_context
def info(ctx, code, days, freq):
    """查看股票详情"""
    data = ctx.obj['data']
    try:
        info = data.get_stock_info(code)
        
        click.echo(f"\n📊 {info['name']} ({info['code']})")
        click.echo(f"行业: {info['industry']} | 波动率: {info['volatility']*100:.1f}%")
        click.echo('-' * 50)
        click.echo(f"最新价: ¥{info['price']:.2f}")
        click.echo(f"今开: ¥{info['open']:.2f} | 最高: ¥{info['high']:.2f} | 最低: ¥{info['low']:.2f}")
        click.echo(f"涨跌: {info['change']:+.2f}%")
        click.echo(f"振幅: {info['amplitude']:.2f}%")
        click.echo(f"成交量: {info['volume']:,}")
        click.echo(f"换手率: {info['turnover']:.2f}%")
        click.echo(f"市盈率: {info['pe_ratio']:.2f}")
        click.echo(f"市值: {info['market_cap']:.0f}亿")
        click.echo('-' * 50)
        click.echo(f"总回报: {info['total_return']:+.2f}%")
        click.echo(f"年化波动: {info['volatility_annual']:.2f}%")
        click.echo(f"最大回撤: {info['max_drawdown']:.2f}%")
        
        # 显示最近K线
        kline = data.get_kline(code, days=days, freq=freq)
        click.echo(f'\n📈 最近{days}根{ {"D": "日线", "W": "周线", "M": "月线"}[freq] }')
        click.echo(f'{"日期":<12} {"开盘":<10} {"最高":<10} {"最低":<10} {"收盘":<10} {"涨幅":<8}')
        click.echo('-' * 70)
        for _, row in kline.tail(5).iterrows():
            change = (row['close'] - row['open']) / row['open'] * 100
            click.echo(f"{row['date']:<12} ¥{row['open']:<9.2f} ¥{row['high']:<9.2f} "
                      f"¥{row['low']:<9.2f} ¥{row['close']:<9.2f} {change:+.2f}%")
        
    except ValueError as e:
        click.echo(f'❌ {e}')


@cli.command()
@click.pass_context
def portfolio(ctx):
    """查看持仓"""
    pf = ctx.obj['portfolio']
    summary = pf.get_summary()
    positions = pf.get_positions()
    
    click.echo('\n💼 账户概览')
    click.echo('-' * 50)
    click.echo(f"初始资金: ¥{summary['initial_cash']:,.2f}")
    click.echo(f"可用资金: ¥{summary['cash']:,.2f}")
    click.echo(f"持仓市值: ¥{summary['positions_value']:,.2f}")
    click.echo(f"总资产:   ¥{summary['total_value']:,.2f}")
    
    profit_color = '🟢' if summary['total_profit'] >= 0 else '🔴'
    click.echo(f"总盈亏:   {profit_color}¥{summary['total_profit']:,.2f} ({summary['total_profit_pct']:+.2f}%)")
    click.echo(f"持仓数量: {summary['positions_count']} 只")
    click.echo(f"交易次数: {summary['trades_count']} 次")
    
    if positions:
        click.echo('\n📋 持仓明细')
        click.echo(f'{"代码":<12} {"名称":<10} {"数量":<10} {"成本":<10} {"现价":<10} {"盈亏":<12} {"盈亏率":<8}')
        click.echo('-' * 80)
        for p in positions:
            profit_color = '🟢' if p['profit'] >= 0 else '🔴'
            click.echo(f"{p['code']:<12} {p['name']:<10} {p['amount']:<10} "
                      f"¥{p['avg_cost']:<9.2f} ¥{p['current_price']:<9.2f} "
                      f"{profit_color}¥{p['profit']:+,.2f} ({p['profit_pct']:+.2f}%)")


@cli.command()
@click.option('--code', prompt='股票代码', help='股票代码')
@click.option('--price', prompt='买入价格', type=float, help='买入价格')
@click.option('--amount', prompt='买入数量', type=int, help='买入数量（100的整数倍）')
@click.pass_context
def buy(ctx, code, price, amount):
    """买入股票"""
    data = ctx.obj['data']
    pf = ctx.obj['portfolio']
    
    try:
        stock = next(s for s in data.stocks if s.code == code)
        result = pf.buy(code, stock.name, price, amount)
        click.echo(f'\n{"✅" if result["success"] else "❌"} {result["message"]}')
    except StopIteration:
        click.echo(f'❌ 股票代码 {code} 不存在')


@cli.command()
@click.option('--code', prompt='股票代码', help='股票代码')
@click.option('--price', prompt='卖出价格', type=float, help='卖出价格')
@click.option('--amount', prompt='卖出数量', type=int, help='卖出数量')
@click.pass_context
def sell(ctx, code, price, amount):
    """卖出股票"""
    data = ctx.obj['data']
    pf = ctx.obj['portfolio']
    
    try:
        stock = next(s for s in data.stocks if s.code == code)
        result = pf.sell(code, stock.name, price, amount)
        click.echo(f'\n{"✅" if result["success"] else "❌"} {result["message"]}')
    except StopIteration:
        click.echo(f'❌ 股票代码 {code} 不存在')


@cli.command()
@click.option('--limit', default=10, help='显示记录数')
@click.pass_context
def history(ctx, limit):
    """查看交易记录"""
    pf = ctx.obj['portfolio']
    trades = pf.get_trades(limit=limit)
    
    click.echo(f'\n📜 最近 {len(trades)} 笔交易')
    click.echo(f'{"时间":<20} {"代码":<12} {"操作":<6} {"价格":<10} {"数量":<10} {"金额":<12}')
    click.echo('-' * 80)
    
    for t in reversed(trades):
        action_color = '🟢' if t['action'] == 'buy' else '🔴'
        action_text = '买入' if t['action'] == 'buy' else '卖出'
        click.echo(f"{t['time']:<20} {t['code']:<12} {action_color}{action_text:<4} "
                  f"¥{t['price']:<9.2f} {t['amount']:<10} ¥{t['total']:,.2f}")


@cli.command()
@click.argument('codes', nargs=-1, required=True)
@click.option('--days', default=60, help='对比天数')
@click.pass_context
def compare(ctx, codes, days):
    """对比多只股票，示例：python cli.py compare 000001.SZ 600519.SH --days 60"""
    data = ctx.obj['data']
    
    if len(codes) < 2:
        click.echo('❌ 请至少提供2只股票代码')
        return
    
    click.echo(f'\n📊 {len(codes)} 只股票对比（{days}天）')
    click.echo('-' * 80)
    
    comparison = data.compare_stocks(list(codes), days)
    
    click.echo(f'{"名称":<12} {"行业":<10} {"收益率":<10} {"波动率":<10} {"换手率":<10}')
    click.echo('-' * 80)
    
    for _, row in comparison.iterrows():
        change_color = '🟢' if row['return'] >= 0 else '🔴'
        click.echo(f"{row['name']:<12} {row['industry']:<10} "
                  f"{change_color}{row['return']:+.2f}%    {row['volatility']:.2f}%    {row['avg_turnover']:.2f}%")


@cli.command()
@click.option('--strategy', default='simple_ma', help='策略名称')
@click.option('--days', default=252, help='回测天数')
@click.option('--cash', default=100000, help='初始资金')
@click.pass_context
def backtest(ctx, strategy, days, cash):
    """运行回测"""
    if strategy not in STRATEGIES:
        click.echo(f'❌ 策略 {strategy} 不存在，可用: {list(STRATEGIES.keys())}')
        return
    
    click.echo(f'\n🔄 正在运行回测: {strategy}')
    click.echo(f'回测周期: {days}天 | 初始资金: ¥{cash:,}')
    
    # 准备数据
    data = EnhancedMockStockData(days=days)
    stock_data = {code: df for code, df in data.data.items()}
    
    # 运行回测
    engine = BacktestEngine(initial_cash=cash)
    result = engine.run(STRATEGIES[strategy], stock_data)
    
    click.echo('\n' + '=' * 50)
    click.echo('📊 回测结果')
    click.echo('=' * 50)
    click.echo(f"策略: {result.strategy_name}")
    click.echo(f"初始资金: ¥{result.initial_cash:,.2f}")
    click.echo(f"最终资产: ¥{result.final_value:,.2f}")
    
    profit_color = '🟢' if result.total_return >= 0 else '🔴'
    click.echo(f"总收益: {profit_color}¥{result.total_return:,.2f} ({result.total_return_pct:+.2f}%)")
    click.echo(f"交易次数: {len(result.trades)} 次")
    
    if result.trades:
        click.echo(f'\n最近5笔交易:')
        click.echo(f'{"日期":<12} {"操作":<6} {"价格":<10} {"数量":<8} {"金额":<12}')
        for t in result.trades[-5:]:
            action = '买入' if t['action'] == 'buy' else '卖出'
            click.echo(f"{t['date']:<12} {action:<6} ¥{t['price']:<9.2f} {t['amount']:<8} ¥{t['value']:,.2f}")


@cli.command()
@click.argument('code')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--format', 'fmt', default='csv', type=click.Choice(['csv', 'json']), help='导出格式')
@click.option('--days', default=252, help='导出天数')
@click.pass_context
def export(ctx, code, output, fmt, days):
    """导出股票数据，示例：python cli.py export 000001.SZ -o data.csv --format csv --days 252"""
    data = ctx.obj['data']
    
    try:
        filepath = data.export_data(code, output, fmt, days)
        click.echo(f'✅ 数据已导出到: {filepath}')
        click.echo(f'   格式: {fmt.upper()} | 天数: {days}')
    except Exception as e:
        click.echo(f'❌ 导出失败: {e}')


@cli.command()
@click.option('--name', prompt='股票名称', help='股票名称')
@click.option('--code', prompt='股票代码', help='股票代码（如 999999.SZ）')
@click.option('--price', prompt='基准价格', type=float, help='基准价格')
@click.option('--industry', default='其他', help='行业')
@click.option('--volatility', default=0.03, type=float, help='波动率（0.01-0.1）')
@click.option('--marketcap', default=100.0, type=float, help='市值（亿）')
def create_stock(name, code, price, industry, volatility, marketcap):
    """创建自定义股票配置"""
    from data.mock_data import StockConfig, Industry
    
    # 找到对应的行业枚举
    industry_enum = Industry.OTHER
    for ind in Industry:
        if ind.value == industry:
            industry_enum = ind
            break
    
    custom = StockConfig(
        code=code,
        name=name,
        base_price=price,
        industry=industry_enum,
        volatility=volatility,
        market_cap=marketcap * 1e8
    )
    
    click.echo(f'\n✅ 自定义股票已创建:')
    click.echo(f'   代码: {custom.code}')
    click.echo(f'   名称: {custom.name}')
    click.echo(f'   行业: {custom.industry.value}')
    click.echo(f'   波动率: {custom.volatility*100:.1f}%')
    click.echo(f'\n💡 使用方式:')
    click.echo(f'   data = EnhancedMockStockData(custom_stocks=[custom])')


if __name__ == '__main__':
    cli()
