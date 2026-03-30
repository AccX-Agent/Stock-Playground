"""
交易核心模块 - V3 增强版
支持：记录买入日期、配合时间推进系统
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class Trade:
    """单笔交易记录"""
    id: str
    code: str
    name: str
    action: str  # 'buy' 或 'sell'
    price: float
    amount: int
    total: float
    time: str
    trade_date: str = ""  # 交易日期（用于时间推进系统）
    
    def to_dict(self):
        return asdict(self)


@dataclass 
class Position:
    """持仓"""
    code: str
    name: str
    amount: int              # 持仓数量
    avg_cost: float          # 平均成本
    current_price: float     # 当前价格
    buy_date: str = ""       # 首次买入日期
    buy_trades: List[Dict] = field(default_factory=list)  # 买入记录（记录每次买入的日期、价格、数量）
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.amount * self.current_price
    
    @property
    def profit(self) -> float:
        """盈亏金额"""
        return self.amount * (self.current_price - self.avg_cost)
    
    @property
    def profit_pct(self) -> float:
        """盈亏比例"""
        if self.avg_cost == 0:
            return 0
        return (self.current_price - self.avg_cost) / self.avg_cost * 100
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'amount': self.amount,
            'avg_cost': round(self.avg_cost, 2),
            'current_price': round(self.current_price, 2),
            'market_value': round(self.market_value, 2),
            'profit': round(self.profit, 2),
            'profit_pct': round(self.profit_pct, 2),
            'buy_date': self.buy_date,
            'buy_trades': self.buy_trades
        }


class Portfolio:
    """投资组合（账户）- V3 增强版"""
    
    def __init__(self, initial_cash: float = 1000000.0, data_dir: str = './data'):
        self.initial_cash = initial_cash
        self.cash = initial_cash  # 可用资金
        self.positions: Dict[str, Position] = {}  # 持仓
        self.trades: List[Trade] = []  # 交易历史
        self.data_dir = data_dir
        self._load()
    
    def _portfolio_file(self) -> str:
        return os.path.join(self.data_dir, 'portfolio.json')
    
    def _trades_file(self) -> str:
        return os.path.join(self.data_dir, 'trades.json')
    
    def _load(self):
        """从文件加载账户数据"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 加载持仓
        if os.path.exists(self._portfolio_file()):
            with open(self._portfolio_file(), 'r') as f:
                data = json.load(f)
                self.cash = data.get('cash', self.initial_cash)
                for code, pos_data in data.get('positions', {}).items():
                    self.positions[code] = Position(
                        code=pos_data['code'],
                        name=pos_data['name'],
                        amount=pos_data['amount'],
                        avg_cost=pos_data['avg_cost'],
                        current_price=pos_data.get('current_price', pos_data['avg_cost']),
                        buy_date=pos_data.get('buy_date', ''),
                        buy_trades=pos_data.get('buy_trades', [])
                    )
        
        # 加载交易记录
        if os.path.exists(self._trades_file()):
            with open(self._trades_file(), 'r') as f:
                trades_data = json.load(f)
                self.trades = [Trade(**t) for t in trades_data]
    
    def _save(self):
        """保存账户数据到文件"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 保存持仓
        portfolio_data = {
            'cash': self.cash,
            'positions': {
                code: {
                    'code': pos.code,
                    'name': pos.name,
                    'amount': pos.amount,
                    'avg_cost': pos.avg_cost,
                    'current_price': pos.current_price,
                    'buy_date': pos.buy_date,
                    'buy_trades': pos.buy_trades
                }
                for code, pos in self.positions.items()
            }
        }
        with open(self._portfolio_file(), 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        # 保存交易记录
        trades_data = [t.to_dict() for t in self.trades]
        with open(self._trades_file(), 'w') as f:
            json.dump(trades_data, f, indent=2)
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓的最新价格"""
        for code, price in prices.items():
            if code in self.positions:
                self.positions[code].current_price = price
    
    def buy(self, code: str, name: str, price: float, amount: int, trade_date: str = None) -> Dict:
        """
        买入股票
        
        Args:
            code: 股票代码
            name: 股票名称
            price: 买入价格
            amount: 买入数量
            trade_date: 交易日期（用于时间推进系统，不传则使用当前时间）
            
        Returns:
            {'success': bool, 'message': str}
        """
        total_cost = price * amount
        
        # 检查资金
        if total_cost > self.cash:
            return {
                'success': False,
                'message': f'资金不足，需要 {total_cost:.2f}，可用 {self.cash:.2f}'
            }
        
        # 执行买入
        self.cash -= total_cost
        
        # 获取当前日期
        current_date = trade_date or datetime.now().strftime('%Y-%m-%d')
        
        if code in self.positions:
            # 加仓，更新平均成本
            pos = self.positions[code]
            total_amount = pos.amount + amount
            pos.avg_cost = (pos.amount * pos.avg_cost + amount * price) / total_amount
            pos.amount = total_amount
            pos.current_price = price
            # 记录买入
            pos.buy_trades.append({
                'date': current_date,
                'price': price,
                'amount': amount
            })
        else:
            # 新建持仓
            self.positions[code] = Position(
                code=code,
                name=name,
                amount=amount,
                avg_cost=price,
                current_price=price,
                buy_date=current_date,
                buy_trades=[{
                    'date': current_date,
                    'price': price,
                    'amount': amount
                }]
            )
        
        # 记录交易
        trade = Trade(
            id=f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            code=code,
            name=name,
            action='buy',
            price=price,
            amount=amount,
            total=total_cost,
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            trade_date=current_date
        )
        self.trades.append(trade)
        self._save()
        
        return {
            'success': True,
            'message': f'买入成功：{name}({code}) {amount}股 @ {price:.2f}，花费 {total_cost:.2f}'
        }
    
    def sell(self, code: str, name: str, price: float, amount: int, trade_date: str = None) -> Dict:
        """
        卖出股票
        
        Args:
            code: 股票代码
            name: 股票名称
            price: 卖出价格
            amount: 卖出数量
            trade_date: 交易日期（用于时间推进系统）
            
        Returns:
            {'success': bool, 'message': str}
        """
        if code not in self.positions:
            return {'success': False, 'message': f'没有持仓 {code}'}
        
        pos = self.positions[code]
        if amount > pos.amount:
            return {
                'success': False,
                'message': f'持仓不足，持有 {pos.amount}股，尝试卖出 {amount}股'
            }
        
        # 执行卖出
        total_value = price * amount
        self.cash += total_value
        pos.amount -= amount
        pos.current_price = price
        
        # 清仓则删除持仓
        if pos.amount == 0:
            del self.positions[code]
        
        # 记录交易
        current_date = trade_date or datetime.now().strftime('%Y-%m-%d')
        trade = Trade(
            id=f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            code=code,
            name=name,
            action='sell',
            price=price,
            amount=amount,
            total=total_value,
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            trade_date=current_date
        )
        self.trades.append(trade)
        self._save()
        
        return {
            'success': True,
            'message': f'卖出成功：{name}({code}) {amount}股 @ {price:.2f}，获得 {total_value:.2f}'
        }
    
    @property
    def total_value(self) -> float:
        """总资产"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_profit(self) -> float:
        """总盈亏"""
        return self.total_value - self.initial_cash
    
    @property
    def total_profit_pct(self) -> float:
        """总盈亏比例"""
        return (self.total_value - self.initial_cash) / self.initial_cash * 100
    
    def get_summary(self) -> Dict:
        """获取账户概览"""
        return {
            'initial_cash': round(self.initial_cash, 2),
            'cash': round(self.cash, 2),
            'positions_value': round(sum(pos.market_value for pos in self.positions.values()), 2),
            'total_value': round(self.total_value, 2),
            'total_profit': round(self.total_profit, 2),
            'total_profit_pct': round(self.total_profit_pct, 2),
            'positions_count': len(self.positions),
            'trades_count': len(self.trades)
        }
    
    def get_positions(self) -> List[Dict]:
        """获取持仓列表"""
        return [pos.to_dict() for pos in self.positions.values()]
    
    def get_position(self, code: str) -> Optional[Position]:
        """获取单个持仓"""
        return self.positions.get(code)
    
    def get_trades(self, limit: int = 50) -> List[Dict]:
        """获取交易记录"""
        return [t.to_dict() for t in self.trades[-limit:]]
    
    def get_trades_by_code(self, code: str) -> List[Dict]:
        """获取某只股票的交易记录"""
        return [t.to_dict() for t in self.trades if t.code == code]
    
    def reset(self):
        """重置账户"""
        self.cash = self.initial_cash
        self.positions = {}
        self.trades = []
        self._save()
