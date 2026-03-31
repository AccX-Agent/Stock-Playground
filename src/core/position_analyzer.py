"""
持仓分析器 - 分析持仓的历史表现
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PositionAnalysisResult:
    """持仓分析结果"""
    # 基本信息
    code: str
    name: str
    buy_date: str
    current_date: str
    buy_price: float
    current_price: float
    amount: int
    
    # 收益指标
    total_return_pct: float
    total_return_amount: float
    
    # 历史统计
    max_profit_pct: float  # 持仓期间最大盈利百分比
    max_loss_pct: float    # 持仓期间最大亏损百分比
    max_drawdown_pct: float  # 最大回撤
    
    # 最佳卖出点
    best_sell_date: str
    best_sell_price: float
    best_sell_return_pct: float
    missed_profit_pct: float  # 错过收益 = 最佳收益 - 当前收益
    
    # 对比基准
    hs300_return_pct: float  # 同期沪深300收益
    alpha: float             # 超额收益
    
    # 时间序列数据（用于绘制收益曲线）
    daily_returns: List[Dict]  # 每日收益数据


class PositionAnalyzer:
    """持仓分析器
    
    分析单个持仓的历史表现，包括：
    - 从买入日到当前日期的收益曲线
    - 持仓期间的最大盈利/最大亏损
    - 最佳卖出点（如果提前卖出能赚更多）
    - 最大回撤
    - 对比同期沪深300
    """
    
    def __init__(self, stock_data: pd.DataFrame, hs300_data: Optional[pd.DataFrame] = None):
        """
        初始化分析器
        
        Args:
            stock_data: 股票历史数据DataFrame
            hs300_data: 沪深300历史数据DataFrame（可选）
        """
        self.stock_data = stock_data.copy()
        self.hs300_data = hs300_data.copy() if hs300_data is not None else None
        
        # 确保日期列为datetime类型
        if 'date' in self.stock_data.columns:
            self.stock_data['date'] = pd.to_datetime(self.stock_data['date'])
        if self.hs300_data is not None and 'date' in self.hs300_data.columns:
            self.hs300_data['date'] = pd.to_datetime(self.hs300_data['date'])
    
    def analyze(
        self,
        code: str,
        name: str,
        buy_date: str,
        buy_price: float,
        amount: int,
        current_date: str,
        current_price: float
    ) -> PositionAnalysisResult:
        """
        分析持仓表现
        
        Args:
            code: 股票代码
            name: 股票名称
            buy_date: 买入日期
            buy_price: 买入价格
            amount: 持仓数量
            current_date: 当前日期
            current_price: 当前价格
            
        Returns:
            PositionAnalysisResult: 分析结果
        """
        # 获取持仓期间的历史数据
        buy_dt = pd.to_datetime(buy_date)
        current_dt = pd.to_datetime(current_date)
        
        # 筛选持仓期间的数据
        mask = (self.stock_data['date'] >= buy_dt) & (self.stock_data['date'] <= current_dt)
        period_data = self.stock_data[mask].copy()
        
        if period_data.empty:
            return self._create_empty_result(code, name, buy_date, current_date, buy_price, amount)
        
        # 计算每日收益率（相对于买入价）
        period_data['return_pct'] = (period_data['close'] - buy_price) / buy_price * 100
        period_data['return_amount'] = (period_data['close'] - buy_price) * amount
        
        # 计算最大盈利和最大亏损
        max_profit_pct = period_data['return_pct'].max()
        max_loss_pct = period_data['return_pct'].min()
        
        # 计算最大回撤
        cummax = period_data['close'].cummax()
        drawdown = (period_data['close'] - cummax) / cummax * 100
        max_drawdown_pct = drawdown.min()
        
        # 找到最佳卖出点
        best_idx = period_data['close'].idxmax()
        best_row = period_data.loc[best_idx]
        best_sell_date = best_row['date'].strftime('%Y-%m-%d')
        best_sell_price = float(best_row['close'])
        best_sell_return_pct = float(best_row['return_pct'])
        
        # 当前收益
        current_return_pct = (current_price - buy_price) / buy_price * 100
        current_return_amount = (current_price - buy_price) * amount
        
        # 错过的收益
        missed_profit_pct = best_sell_return_pct - current_return_pct
        
        # 计算同期沪深300表现
        hs300_return_pct = 0.0
        alpha = current_return_pct
        
        if self.hs300_data is not None:
            hs300_mask = (self.hs300_data['date'] >= buy_dt) & (self.hs300_data['date'] <= current_dt)
            hs300_period = self.hs300_data[hs300_mask]
            
            if not hs300_period.empty:
                hs300_start = hs300_period['close'].iloc[0]
                hs300_end = hs300_period['close'].iloc[-1]
                hs300_return_pct = (hs300_end - hs300_start) / hs300_start * 100
                alpha = current_return_pct - hs300_return_pct
        
        # 生成每日收益数据（用于绘图）
        daily_returns = []
        for _, row in period_data.iterrows():
            hs300_value = 0.0
            if self.hs300_data is not None:
                date_mask = self.hs300_data['date'] == row['date']
                if date_mask.any():
                    hs300_row = self.hs300_data[date_mask].iloc[0]
                    # 修复：添加空值检查，避免 .iloc[0] 报错
                    hs300_period_data = self.hs300_data[
                        (self.hs300_data['date'] >= buy_dt) & 
                        (self.hs300_data['date'] <= row['date'])
                    ]
                    if not hs300_period_data.empty and len(hs300_period_data) > 0:
                        hs300_start = hs300_period_data['close'].iloc[0]
                        hs300_value = (hs300_row['close'] - hs300_start) / hs300_start * 100
                    else:
                        hs300_value = 0.0
            
            daily_returns.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'price': float(row['close']),
                'return_pct': float(row['return_pct']),
                'return_amount': float(row['return_amount']),
                'hs300_return_pct': round(hs300_value, 2),
                'volume': int(row['volume'])
            })
        
        return PositionAnalysisResult(
            code=code,
            name=name,
            buy_date=buy_date,
            current_date=current_date,
            buy_price=buy_price,
            current_price=current_price,
            amount=amount,
            total_return_pct=round(current_return_pct, 2),
            total_return_amount=round(current_return_amount, 2),
            max_profit_pct=round(max_profit_pct, 2),
            max_loss_pct=round(max_loss_pct, 2),
            max_drawdown_pct=round(max_drawdown_pct, 2),
            best_sell_date=best_sell_date,
            best_sell_price=round(best_sell_price, 2),
            best_sell_return_pct=round(best_sell_return_pct, 2),
            missed_profit_pct=round(missed_profit_pct, 2),
            hs300_return_pct=round(hs300_return_pct, 2),
            alpha=round(alpha, 2),
            daily_returns=daily_returns
        )
    
    def _create_empty_result(
        self,
        code: str,
        name: str,
        buy_date: str,
        current_date: str,
        buy_price: float,
        amount: int
    ) -> PositionAnalysisResult:
        """创建空的分析结果（数据不足时）"""
        return PositionAnalysisResult(
            code=code,
            name=name,
            buy_date=buy_date,
            current_date=current_date,
            buy_price=buy_price,
            current_price=buy_price,
            amount=amount,
            total_return_pct=0.0,
            total_return_amount=0.0,
            max_profit_pct=0.0,
            max_loss_pct=0.0,
            max_drawdown_pct=0.0,
            best_sell_date=buy_date,
            best_sell_price=buy_price,
            best_sell_return_pct=0.0,
            missed_profit_pct=0.0,
            hs300_return_pct=0.0,
            alpha=0.0,
            daily_returns=[]
        )
    
    def calculate_sharpe_ratio(self, daily_returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        计算夏普比率
        
        Args:
            daily_returns: 每日收益率列表
            risk_free_rate: 无风险利率（年化）
            
        Returns:
            夏普比率
        """
        if len(daily_returns) < 2:
            return 0.0
        
        returns = np.array(daily_returns)
        excess_returns = returns - risk_free_rate / 252  # 转换为日无风险利率
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        return round(sharpe, 2)
    
    def calculate_volatility(self, prices: pd.Series) -> float:
        """
        计算波动率（年化）
        
        Args:
            prices: 价格序列
            
        Returns:
            年化波动率（%）
        """
        if len(prices) < 2:
            return 0.0
        
        returns = prices.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        return round(volatility, 2)
