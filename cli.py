"""
CLI 入口
"""
import click
import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/stock-playground/src')

from data.mock_data import MockStockData
from core.portfolio import Portfolio
from core.backtest import BacktestEngine
from strategies.examples import STRATEGIES


@click.group()
def cli():
    """股票模拟交易 CLI"""
    pass


@cli.command()
def market():
    """查看行情"""
    data = MockStockData()
    stocks = data.get_stock_list()
    
    click.echo('\n📈 股票行情')
    click.echo('-' * 60)
    click.echo(f'{"代码":<15} {"名称":<10} {"价格":<10} {"涨跌幅":<10} {"成交量":<12}')
    click.echo('-' * 60)
    
    for s in stocks:
        change_color = '🟢' if s['change'] >= 0 else '🔴'
        click.echo(f"{s['code']:<15} {s['name']:<10} {s['price']:<10.2f} {change_color}{s['change']:<8.2f}% {s['volume']:<12,}")
    
    click.echo('-' * 60)


@cli.command()
@click.option('--code', prompt='股票代码', help='股票代码，如 000001.SZ')
def info(code):
    """查看股票详情"""
    data = MockStockData()
    try:
        info = data.get_stock_info(code)
        click.echo(f"\n📊 {info['name']} ({info['code']})")
        click.echo('-' * 40)
        click.echo(f"最新价: {info['price']:.2f}")
        click.echo(f"涨跌幅: {info['change']:+.2f}%")
        click.echo(f"今开: {info['open']:.2f}")
        click.echo(f"最高: {info['high']:.2f}")
        click.echo(f"最低: {info['low']:.2f}")
        click.echo(f"成交量: {info['volume']:,}")
    except ValueError as e:
        click.echo(f'❌ {e}')


@cli.command()
def portfolio():
    """查看持仓"""
    pf = Portfolio()
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
        click.echo(f'{"代码":<15} {"名称":<10} {"数量":<10} {"成本":<10} {"现价":<10} {"盈亏":<12}')
        click.echo('-' * 70)
        for p in positions:
            profit_color = '🟢' if p['profit'] >= 0 else '🔴'
            click.echo(f"{p['code']:<15} {p['name']:<10} {p['amount']:<10} {p['avg_cost']:<10.2f} {p['current_price']:<10.2f} {profit_color}{p['profit']:+,.2f} ({p['profit_pct']:+.2f}%)")


@cli.command()
@click.option('--code', prompt='股票代码', help='股票代码')
@click.option('--price', prompt='买入价格', type=float, help='买入价格')
@click.option('--amount', prompt='买入数量', type=int, help='买入数量（100的整数倍）')
def buy(code, price, amount):
    """买入股票"""
    data = MockStockData()
    pf = Portfolio()
    
    # 获取股票名称
    try:
        stock = next(s for s in data.MOCK_STOCKS if s['code'] == code)
        name = stock['name']
    except StopIteration:
        click.echo(f'❌ 股票代码 {code} 不存在')
        return
    
    result = pf.buy(code, name, price, amount)
    click.echo(f'\n{"✅" if result["success"] else "❌"} {result["message"]}')


@cli.command()
@click.option('--code', prompt='股票代码', help='股票代码')
@click.option('--price', prompt='卖出价格', type=float, help='卖出价格')
@click.option('--amount', prompt='卖出数量', type=int, help='卖出数量')
def sell(code, price, amount):
    """卖出股票"""
    data = MockStockData()
    pf = Portfolio()
    
    try:
        stock = next(s for s in data.MOCK_STOCKS if s['code'] == code)
        name = stock['name']
    except StopIteration:
        click.echo(f'❌ 股票代码 {code} 不存在')
        return
    
    result = pf.sell(code, name, price, amount)
    click.echo(f'\n{"✅" if result["success"] else "❌"} {result["message"]}')


@cli.command()
@click.option('--limit', default=10, help='显示多少条记录')
def history(limit):
    """查看交易记录"""
    pf = Portfolio()
    trades = pf.get_trades(limit=limit)
    
    click.echo(f'\n📜 最近 {len(trades)} 笔交易')
    click.echo(f'{"时间":<20} {"代码":<15} {"操作":<6} {"价格":<10} {"数量":<10} {"金额":<12}')
    click.echo('-' * 80)
    
    for t in reversed(trades):  # 最新的在前
        action_color = '🟢' if t['action'] == 'buy' else '🔴'
        action_text = '买入' if t['action'] == 'buy' else '卖出'
        click.echo(f"{t['time']:<20} {t['code']:<15} {action_color}{action_text:<4} {t['price']:<10.2f} {t['amount']:<10} ¥{t['total']:,.2f}")


@cli.command()
@click.option('--strategy', default='simple_ma', help='策略名称')
@click.option('--days', default=60, help='回测天数')
def backtest(strategy, days):
    """运行回测"""
    if strategy not in STRATEGIES:
        click.echo(f'❌ 策略 {strategy} 不存在，可用策略: {list(STRATEGIES.keys())}')
        return
    
    click.echo(f'\n🔄 正在运行回测: {strategy}')
    
    # 准备数据
    data = MockStockData(days=days)
    stock_data = {code: df for code, df in data.data.items()}
    
    # 运行回测
    engine = BacktestEngine(initial_cash=100000)
    result = engine.run(STRATEGIES[strategy], stock_data)
    
    click.echo('\n📊 回测结果')
    click.echo('-' * 40)
    click.echo(f"策略: {result.strategy_name}")
    click.echo(f"初始资金: ¥{result.initial_cash:,.2f}")
    click.echo(f"最终资产: ¥{result.final_value:,.2f}")
    
    profit_color = '🟢' if result.total_return >= 0 else '🔴'
    click.echo(f"总收益: {profit_color}¥{result.total_return:,.2f} ({result.total_return_pct:+.2f}%)")
    click.echo(f"交易次数: {len(result.trades)} 次")


if __name__ == '__main__':
    cli()
