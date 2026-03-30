"""
回测引擎
"""
import pandas as pd
from typing import List, Dict, Callable
from dataclasses import dataclass


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    initial_cash: float
    final_value: float
    total_return: float
    total_return_pct: float
    trades: List[Dict]
    daily_values: List[Dict]  # 每日资产变化
    
    def to_dict(self):
        return {
            'strategy_name': self.strategy_name,
            'initial_cash': round(self.initial_cash, 2),
            'final_value': round(self.final_value, 2),
            'total_return': round(self.total_return, 2),
            'total_return_pct': round(self.total_return_pct, 2),
            'trades_count': len(self.trades),
            'trades': self.trades[-10:],  # 最后10笔交易
            'daily_values': self.daily_values
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, int] = {}  # 持仓数量
        self.trades: List[Dict] = []
        self.daily_values: List[Dict] = []
    
    def reset(self):
        """重置状态"""
        self.cash = self.initial_cash
        self.positions = {}
        self.trades = []
        self.daily_values = []
    
    def buy(self, date: str, code: str, name: str, price: float, amount: int):
        """回测中的买入"""
        cost = price * amount
        if cost <= self.cash:
            self.cash -= cost
            self.positions[code] = self.positions.get(code, 0) + amount
            self.trades.append({
                'date': date,
                'code': code,
                'name': name,
                'action': 'buy',
                'price': price,
                'amount': amount,
                'value': cost
            })
            return True
        return False
    
    def sell(self, date: str, code: str, name: str, price: float, amount: int):
        """回测中的卖出"""
        if code in self.positions and self.positions[code] >= amount:
            value = price * amount
            self.cash += value
            self.positions[code] -= amount
            if self.positions[code] == 0:
                del self.positions[code]
            self.trades.append({
                'date': date,
                'code': code,
                'name': name,
                'action': 'sell',
                'price': price,
                'amount': amount,
                'value': value
            })
            return True
        return False
    
    def get_portfolio_value(self, date: str, prices: Dict[str, float]) -> float:
        """计算当前资产价值"""
        positions_value = sum(
            self.positions.get(code, 0) * price
            for code, price in prices.items()
        )
        return self.cash + positions_value
    
    def record_daily_value(self, date: str, value: float):
        """记录每日资产"""
        self.daily_values.append({
            'date': date,
            'value': round(value, 2),
            'cash': round(self.cash, 2),
            'positions_value': round(value - self.cash, 2)
        })
    
    def run(
        self,
        strategy: Callable,
        data: Dict[str, pd.DataFrame],
        strategy_params: Dict = None
    ) -> BacktestResult:
        """
        运行回测
        
        Args:
            strategy: 策略函数，接收(engine, data, params)参数
            data: 股票数据 {code: DataFrame}
            strategy_params: 策略参数
        """
        self.reset()
        
        # 获取所有日期
        all_dates = set()
        for df in data.values():
            all_dates.update(df['date'].tolist())
        all_dates = sorted(list(all_dates))
        
        # 运行策略
        strategy(self, data, strategy_params or {})
        
        # 计算最终收益
        final_prices = {
            code: df.iloc[-1]['close']
            for code, df in data.items()
        }
        final_value = self.get_portfolio_value(all_dates[-1], final_prices)
        total_return = final_value - self.initial_cash
        total_return_pct = (total_return / self.initial_cash) * 100
        
        return BacktestResult(
            strategy_name=strategy.__name__,
            initial_cash=self.initial_cash,
            final_value=final_value,
            total_return=total_return,
            total_return_pct=total_return_pct,
            trades=self.trades,
            daily_values=self.daily_values
        )
