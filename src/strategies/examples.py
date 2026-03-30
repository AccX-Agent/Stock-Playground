"""
示例策略
"""
import pandas as pd
from typing import Dict


def simple_ma_strategy(engine, data: Dict[str, pd.DataFrame], params: Dict):
    """
    简单均线策略
    
    逻辑：
    - 当短期均线（5日）上穿长期均线（20日）时买入
    - 当短期均线下穿长期均线（20日）时卖出
    
    参数：
    - short_window: 短期均线窗口（默认5）
    - long_window: 长期均线窗口（默认20）
    """
    short_window = params.get('short_window', 5)
    long_window = params.get('long_window', 20)
    
    # 只取第一只股票做示例
    code = list(data.keys())[0]
    df = data[code].copy()
    name = code  # 简化处理
    
    # 计算均线
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()
    
    # 生成买卖信号
    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1  # 买入信号
    df.loc[df['ma_short'] <= df['ma_long'], 'signal'] = -1  # 卖出信号
    
    # 执行交易
    position = 0  # 当前持仓
    for _, row in df.iterrows():
        date = row['date']
        price = row['close']
        signal = row['signal']
        
        # 买入信号且无持仓
        if signal == 1 and position == 0:
            # 全仓买入
            amount = int(engine.cash / price / 100) * 100  # 买100的整数倍
            if amount >= 100:
                if engine.buy(date, code, name, price, amount):
                    position = amount
        
        # 卖出信号且有持仓
        elif signal == -1 and position > 0:
            if engine.sell(date, code, name, price, position):
                position = 0
        
        # 记录每日资产
        prices = {code: price}
        value = engine.get_portfolio_value(date, prices)
        engine.record_daily_value(date, value)


def random_strategy(engine, data: Dict[str, pd.DataFrame], params: Dict):
    """
    随机策略（用于测试）
    
    每天随机决定买入、卖出或持有
    """
    import random
    
    code = list(data.keys())[0]
    df = data[code].copy()
    name = code
    
    position = 0
    for _, row in df.iterrows():
        date = row['date']
        price = row['close']
        
        action = random.choice(['buy', 'sell', 'hold'])
        
        if action == 'buy' and position == 0 and engine.cash > price * 100:
            amount = int(engine.cash / price / 100) * 100
            if amount >= 100:
                if engine.buy(date, code, name, price, amount):
                    position = amount
        
        elif action == 'sell' and position > 0:
            if engine.sell(date, code, name, price, position):
                position = 0
        
        prices = {code: price}
        value = engine.get_portfolio_value(date, prices)
        engine.record_daily_value(date, value)


STRATEGIES = {
    'simple_ma': simple_ma_strategy,
    'random': random_strategy,
}
