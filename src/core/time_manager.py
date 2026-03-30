"""
时间管理系统 - 管理当前日期状态
"""
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


class TimeManager:
    """时间推进管理器
    
    负责管理当前日期状态，支持日期推进到下一交易日
    保证不会穿越到数据最后一天之后
    """
    
    def __init__(self, all_dates: list[str], start_date: Optional[str] = None):
        """
        初始化时间管理器
        
        Args:
            all_dates: 所有可用交易日列表（已排序）
            start_date: 初始日期，默认取第一个交易日
        """
        self.all_dates = sorted(set(all_dates))
        self.date_index_map = {date: i for i, date in enumerate(self.all_dates)}
        
        if start_date and start_date in self.date_index_map:
            self.current_index = self.date_index_map[start_date]
        else:
            # 默认从第二天开始（第一天没有前收盘价）
            self.current_index = min(1, len(self.all_dates) - 1)
        
        self._max_index = len(self.all_dates) - 1
    
    @property
    def current_date(self) -> str:
        """获取当前日期"""
        if 0 <= self.current_index <= self._max_index:
            return self.all_dates[self.current_index]
        return self.all_dates[-1] if self.all_dates else None
    
    @property
    def next_date(self) -> Optional[str]:
        """获取下一交易日"""
        next_idx = self.current_index + 1
        if next_idx <= self._max_index:
            return self.all_dates[next_idx]
        return None
    
    @property
    def is_last_date(self) -> bool:
        """是否已经是最后一天"""
        return self.current_index >= self._max_index
    
    @property
    def progress(self) -> str:
        """获取进度信息"""
        return f"{self.current_index + 1} / {len(self.all_dates)}"
    
    @property
    def progress_pct(self) -> float:
        """获取进度百分比"""
        return (self.current_index + 1) / len(self.all_dates) * 100 if self.all_dates else 0
    
    def advance(self) -> bool:
        """
        推进到下一交易日
        
        Returns:
            bool: 是否成功推进，False表示已到最后一交易日
        """
        if self.is_last_date:
            return False
        self.current_index += 1
        return True
    
    def go_to_date(self, target_date: str) -> bool:
        """
        跳转到指定日期
        
        Args:
            target_date: 目标日期字符串
            
        Returns:
            bool: 是否成功跳转
        """
        if target_date in self.date_index_map:
            idx = self.date_index_map[target_date]
            if idx <= self._max_index:
                self.current_index = idx
                return True
        return False
    
    def reset(self, start_date: Optional[str] = None):
        """重置时间到初始状态"""
        if start_date and start_date in self.date_index_map:
            self.current_index = self.date_index_map[start_date]
        else:
            self.current_index = min(1, len(self.all_dates) - 1)
    
    def get_date_range(self, days: int = 30) -> list[str]:
        """
        获取当前日期往前N天的日期列表
        
        Args:
            days: 天数
            
        Returns:
            日期列表
        """
        start_idx = max(0, self.current_index - days + 1)
        return self.all_dates[start_idx:self.current_index + 1]
    
    def get_date_index(self, date: str) -> int:
        """获取日期对应的索引"""
        return self.date_index_map.get(date, -1)
    
    def get_price_for_date(self, code: str, data: pd.DataFrame, date: str) -> Optional[dict]:
        """
        获取指定日期的股票数据
        
        Args:
            code: 股票代码
            data: 股票DataFrame
            date: 日期字符串
            
        Returns:
            该日期的股票数据字典，如果日期不存在则返回None
        """
        if date not in self.date_index_map:
            return None
        
        row = data[data['date'] == date]
        if row.empty:
            return None
        
        return {
            'code': code,
            'date': date,
            'open': float(row['open'].iloc[0]),
            'high': float(row['high'].iloc[0]),
            'low': float(row['low'].iloc[0]),
            'close': float(row['close'].iloc[0]),
            'volume': int(row['volume'].iloc[0]),
            'turnover': float(row['turnover'].iloc[0]),
            'pe_ratio': float(row['pe_ratio'].iloc[0]),
            'market_cap': float(row['market_cap'].iloc[0])
        }
