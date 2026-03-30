"""
Stock Playground - 股票模拟交易核心模块
"""
__version__ = "2.0.0"

# 方便直接导入
from .data import EnhancedMockStockData, StockConfig, Industry
from .core import Portfolio, BacktestEngine
from .strategies import STRATEGIES

__all__ = [
    'EnhancedMockStockData',
    'StockConfig',
    'Industry',
    'Portfolio',
    'BacktestEngine',
    'STRATEGIES'
]
