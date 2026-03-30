"""
Mock A股数据生成器 V2 - 扩展版
支持：更多股票、更多维度、更长历史、自定义配置
"""
import random
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Industry(Enum):
    """行业分类"""
    BANK = "银行"
    REAL_ESTATE = "房地产"
    LIQUOR = "白酒"
    NEW_ENERGY = "新能源"
    TECH = "科技"
    MEDICINE = "医药"
    CONSUMER = "消费"
    MANUFACTURING = "制造业"
    ENERGY = "能源"
    MATERIALS = "材料"


@dataclass
class StockConfig:
    """股票配置"""
    code: str
    name: str
    base_price: float
    industry: Industry
    volatility: float = 0.02  # 日波动率
    market_cap: float = 100e8  # 市值（亿）
    pe_ratio: float = 15.0     # 初始市盈率


class EnhancedMockStockData:
    """增强版 Mock 股票数据生成器"""
    
    # 默认股票池 - 50只，分行业
    DEFAULT_STOCKS = [
        # 银行 (5只)
        StockConfig("000001.SZ", "平安银行", 10.5, Industry.BANK, 0.015, 2500e8, 6.5),
        StockConfig("600000.SH", "浦发银行", 7.8, Industry.BANK, 0.012, 2200e8, 5.2),
        StockConfig("600036.SH", "招商银行", 32.0, Industry.BANK, 0.018, 8000e8, 6.8),
        StockConfig("601398.SH", "工商银行", 4.5, Industry.BANK, 0.008, 18000e8, 4.5),
        StockConfig("601288.SH", "农业银行", 3.8, Industry.BANK, 0.007, 12000e8, 4.2),
        
        # 白酒 (5只)
        StockConfig("600519.SH", "贵州茅台", 1680.0, Industry.LIQUOR, 0.018, 21000e8, 28.5),
        StockConfig("000858.SZ", "五粮液", 145.0, Industry.LIQUOR, 0.022, 5600e8, 22.0),
        StockConfig("000568.SZ", "泸州老窖", 185.0, Industry.LIQUOR, 0.025, 2700e8, 24.5),
        StockConfig("600809.SH", "山西汾酒", 240.0, Industry.LIQUOR, 0.028, 2900e8, 32.0),
        StockConfig("002304.SZ", "洋河股份", 95.0, Industry.LIQUOR, 0.020, 1400e8, 18.5),
        
        # 新能源 (8只)
        StockConfig("002594.SZ", "比亚迪", 240.0, Industry.NEW_ENERGY, 0.035, 7000e8, 35.0),
        StockConfig("300750.SZ", "宁德时代", 185.0, Industry.NEW_ENERGY, 0.040, 8000e8, 28.0),
        StockConfig("601012.SH", "隆基绿能", 22.0, Industry.NEW_ENERGY, 0.038, 1600e8, 15.0),
        StockConfig("002460.SZ", "赣锋锂业", 38.0, Industry.NEW_ENERGY, 0.045, 760e8, 18.0),
        StockConfig("300014.SZ", "亿纬锂能", 42.0, Industry.NEW_ENERGY, 0.042, 860e8, 32.0),
        StockConfig("002812.SZ", "恩捷股份", 55.0, Industry.NEW_ENERGY, 0.040, 540e8, 25.0),
        StockConfig("603659.SH", "璞泰来", 35.0, Industry.NEW_ENERGY, 0.038, 480e8, 22.0),
        StockConfig("300124.SZ", "汇川技术", 58.0, Industry.NEW_ENERGY, 0.032, 1550e8, 35.0),
        
        # 科技 (8只)
        StockConfig("000063.SZ", "中兴通讯", 28.0, Industry.TECH, 0.030, 1300e8, 22.0),
        StockConfig("002415.SZ", "海康威视", 32.0, Industry.TECH, 0.025, 3000e8, 25.0),
        StockConfig("600570.SH", "恒生电子", 68.0, Industry.TECH, 0.040, 1300e8, 45.0),
        StockConfig("300033.SZ", "同花顺", 158.0, Industry.TECH, 0.050, 850e8, 55.0),
        StockConfig("002230.SZ", "科大讯飞", 48.0, Industry.TECH, 0.038, 1100e8, 180.0),
        StockConfig("000938.SZ", "中芯国际", 52.0, Industry.TECH, 0.035, 4100e8, 85.0),
        StockConfig("600584.SH", "长电科技", 32.0, Industry.TECH, 0.042, 580e8, 42.0),
        StockConfig("002371.SZ", "北方华创", 285.0, Industry.TECH, 0.048, 1500e8, 65.0),
        
        # 医药 (6只)
        StockConfig("600276.SH", "恒瑞医药", 45.0, Industry.MEDICINE, 0.028, 2850e8, 65.0),
        StockConfig("000538.SZ", "云南白药", 55.0, Industry.MEDICINE, 0.020, 980e8, 22.0),
        StockConfig("300760.SZ", "迈瑞医疗", 285.0, Industry.MEDICINE, 0.025, 3450e8, 32.0),
        StockConfig("603259.SH", "药明康德", 48.0, Industry.MEDICINE, 0.035, 1400e8, 28.0),
        StockConfig("000999.SZ", "华润三九", 58.0, Industry.MEDICINE, 0.022, 570e8, 18.0),
        StockConfig("300003.SZ", "乐普医疗", 12.5, Industry.MEDICINE, 0.030, 235e8, 15.0),
        
        # 消费 (6只)
        StockConfig("000333.SZ", "美的集团", 58.0, Industry.CONSUMER, 0.022, 4000e8, 14.0),
        StockConfig("000651.SZ", "格力电器", 35.0, Industry.CONSUMER, 0.020, 1950e8, 8.5),
        StockConfig("600887.SH", "伊利股份", 26.5, Industry.CONSUMER, 0.018, 1680e8, 18.0),
        StockConfig("002714.SZ", "牧原股份", 42.0, Industry.CONSUMER, 0.040, 2300e8, 25.0),
        StockConfig("603288.SH", "海天味业", 38.0, Industry.CONSUMER, 0.018, 2100e8, 32.0),
        StockConfig("600690.SH", "海尔智家", 25.0, Industry.CONSUMER, 0.022, 2350e8, 15.0),
        
        # 房地产 (4只)
        StockConfig("000002.SZ", "万科A", 15.2, Industry.REAL_ESTATE, 0.030, 1800e8, 12.0),
        StockConfig("600048.SH", "保利发展", 12.5, Industry.REAL_ESTATE, 0.028, 1500e8, 8.5),
        StockConfig("001979.SZ", "招商蛇口", 10.8, Industry.REAL_ESTATE, 0.032, 960e8, 15.0),
        StockConfig("600606.SH", "绿地控股", 3.2, Industry.REAL_ESTATE, 0.035, 450e8, 35.0),
        
        # 制造业 (4只)
        StockConfig("600031.SH", "三一重工", 18.0, Industry.MANUFACTURING, 0.030, 1520e8, 25.0),
        StockConfig("000425.SZ", "徐工机械", 7.5, Industry.MANUFACTURING, 0.032, 880e8, 18.0),
        StockConfig("601766.SH", "中国中车", 6.8, Industry.MANUFACTURING, 0.018, 1950e8, 15.0),
        StockConfig("600893.SH", "航发动力", 38.0, Industry.MANUFACTURING, 0.035, 1010e8, 65.0),
        
        # 能源 (4只)
        StockConfig("601088.SH", "中国神华", 38.0, Industry.ENERGY, 0.018, 7500e8, 10.0),
        StockConfig("601857.SH", "中国石油", 8.5, Industry.ENERGY, 0.015, 15500e8, 12.0),
        StockConfig("600028.SH", "中国石化", 6.2, Industry.ENERGY, 0.012, 7500e8, 15.0),
        StockConfig("601225.SH", "陕西煤业", 25.0, Industry.ENERGY, 0.020, 2400e8, 8.5),
    ]
    
    def __init__(
        self,
        days: int = 252 * 5,  # 默认5年
        custom_stocks: Optional[List[StockConfig]] = None,
        start_date: Optional[datetime] = None
    ):
        """
        Args:
            days: 生成多少天的数据（默认5年）
            custom_stocks: 自定义股票列表，不传则使用默认50只
            start_date: 数据起始日期，默认从今天往前推
        """
        self.days = days
        self.stocks = custom_stocks or self.DEFAULT_STOCKS
        self.start_date = start_date or (datetime.now() - timedelta(days=days*1.5))
        self.data: Dict[str, pd.DataFrame] = {}
        self._stock_info: Dict[str, Dict] = {}
        self._generate_all()
    
    def _generate_price_series(self, config: StockConfig) -> pd.DataFrame:
        """生成单只股票的完整数据（增强版）"""
        days = self.days
        
        # 根据波动率生成收益率（每个股票有自己的特性）
        daily_returns = np.random.normal(0.0002, config.volatility, days)
        
        # 计算价格序列（几何布朗运动）
        prices = [config.base_price]
        for ret in daily_returns:
            new_price = prices[-1] * (1 + ret)
            # 限制价格不能为负，保持在合理范围
            new_price = max(0.5, min(new_price, config.base_price * 5))
            prices.append(new_price)
        prices = prices[1:]
        
        # 生成交易日序列（跳过周末和节假日模拟）
        dates = []
        current = self.start_date
        while len(dates) < days:
            weekday = current.weekday()
            # 跳过周末 (5=周六, 6=周日)
            if weekday < 5:
                # 模拟节假日（随机跳过一些交易日，约5%）
                if random.random() > 0.05:
                    dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        # 确保日期和价格数量一致
        dates = dates[:len(prices)]
        
        # 生成 OHLCV
        df = pd.DataFrame({'date': dates, 'close': prices})
        
        # 根据收盘价生成开高低（更真实的波动）
        df['prev_close'] = df['close'].shift(1)
        df.loc[0, 'prev_close'] = config.base_price
        
        # 开盘价（前收盘 +/- 随机跳空）
        gap = np.random.normal(0, config.volatility * 0.5, len(df))
        df['open'] = df['prev_close'] * (1 + gap)
        
        # 最高价和最低价（基于日内波动）
        intraday_volatility = np.abs(np.random.normal(0, config.volatility * 1.5, len(df)))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + intraday_volatility)
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - intraday_volatility)
        
        # 成交量（与价格波动相关）
        price_change = df['close'].pct_change().abs().fillna(0)
        base_volume = config.market_cap / config.base_price / 1000  # 基于市值估算
        volume_noise = np.random.lognormal(0, 0.5, len(df))
        df['volume'] = (base_volume * (1 + price_change * 10) * volume_noise).astype(int)
        df['volume'] = df['volume'].clip(lower=int(base_volume * 0.1))
        
        # 计算额外指标
        df['amount'] = (df['close'] * df['volume']).round(2)  # 成交额
        df['amplitude'] = ((df['high'] - df['low']) / df['low'] * 100).round(2)  # 振幅
        df['change_pct'] = (df['close'] - df['open']) / df['open'] * 100  # 涨跌幅
        
        # 换手率（基于流通股估算）
        float_shares = config.market_cap / config.base_price * 0.4  # 假设40%流通股
        df['turnover'] = (df['volume'] / float_shares * 100).round(2)
        df['turnover'] = df['turnover'].clip(upper=25.0)  # 限制最高25%
        
        # PE 动态变化（基于价格变化）
        base_earnings = config.base_price / config.pe_ratio  # 每股盈利
        df['pe_ratio'] = (df['close'] / base_earnings).round(2)
        df['pe_ratio'] = df['pe_ratio'].clip(lower=3.0, upper=200.0)
        
        # 市值动态变化
        total_shares = config.market_cap / config.base_price
        df['market_cap'] = (df['close'] * total_shares / 1e8).round(2)  # 亿
        
        # 删除临时列
        df = df.drop(columns=['prev_close'])
        
        return df
    
    def _generate_all(self):
        """生成所有股票数据"""
        for config in self.stocks:
            self.data[config.code] = self._generate_price_series(config)
            # 保存股票静态信息
            self._stock_info[config.code] = {
                'code': config.code,
                'name': config.name,
                'industry': config.industry.value,
                'volatility': config.volatility,
                'market_cap': config.market_cap,
                'pe_ratio': config.pe_ratio
            }
    
    def get_stock_list(self, industry: Optional[str] = None) -> List[Dict]:
        """获取股票列表，支持按行业筛选"""
        result = []
        for config in self.stocks:
            if industry and config.industry.value != industry:
                continue
            
            latest = self.data[config.code].iloc[-1]
            prev = self.data[config.code].iloc[-2] if len(self.data[config.code]) > 1 else latest
            
            result.append({
                'code': config.code,
                'name': config.name,
                'industry': config.industry.value,
                'price': round(latest['close'], 2),
                'change': round((latest['close'] - prev['close']) / prev['close'] * 100, 2),
                'change_amount': round(latest['close'] - prev['close'], 2),
                'volume': int(latest['volume']),
                'amount': round(latest['amount'] / 1e8, 2),  # 成交额亿
                'turnover': round(latest['turnover'], 2),
                'pe_ratio': round(latest['pe_ratio'], 2),
                'market_cap': round(latest['market_cap'], 2),
                'amplitude': round(latest['amplitude'], 2)
            })
        return result
    
    def get_industries(self) -> List[str]:
        """获取所有行业列表"""
        return list(set(s.industry.value for s in self.stocks))
    
    def get_kline(
        self,
        code: str,
        days: int = 30,
        freq: str = 'D'  # 'D'=日线, 'W'=周线, 'M'=月线
    ) -> pd.DataFrame:
        """
        获取K线数据，支持多周期
        
        Args:
            code: 股票代码
            days: 返回多少根K线
            freq: 周期，D=日 W=周 M=月
        """
        if code not in self.data:
            raise ValueError(f"股票代码 {code} 不存在")
        
        df = self.data[code].copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        if freq == 'D':
            result = df.tail(days)
        elif freq == 'W':
            # 周线重采样
            weekly = df.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum',
                'turnover': 'mean',
                'pe_ratio': 'last',
                'market_cap': 'last'
            }).dropna()
            result = weekly.tail(days)
        elif freq == 'M':
            # 月线重采样
            monthly = df.resample('M').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum',
                'turnover': 'mean',
                'pe_ratio': 'last',
                'market_cap': 'last'
            }).dropna()
            result = monthly.tail(days)
        else:
            raise ValueError(f"不支持的周期: {freq}")
        
        result = result.reset_index()
        result['date'] = result['date'].dt.strftime('%Y-%m-%d')
        return result
    
    def get_stock_info(self, code: str) -> Dict:
        """获取股票完整信息"""
        if code not in self.data:
            raise ValueError(f"股票代码 {code} 不存在")
        
        config = self._stock_info[code]
        df = self.data[code]
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # 计算更多统计指标
        returns = df['close'].pct_change().dropna()
        
        return {
            **config,
            'price': round(latest['close'], 2),
            'open': round(latest['open'], 2),
            'high': round(latest['high'], 2),
            'low': round(latest['low'], 2),
            'volume': int(latest['volume']),
            'amount': round(latest['amount'], 2),
            'turnover': round(latest['turnover'], 2),
            'pe_ratio': round(latest['pe_ratio'], 2),
            'market_cap': round(latest['market_cap'], 2),
            'amplitude': round(latest['amplitude'], 2),
            'change': round((latest['close'] - prev['close']) / prev['close'] * 100, 2) if len(df) > 1 else 0,
            'history': df,
            # 统计指标
            'total_return': round((latest['close'] / df.iloc[0]['close'] - 1) * 100, 2),
            'volatility_annual': round(returns.std() * np.sqrt(252) * 100, 2),
            'max_drawdown': self._calc_max_drawdown(df['close']),
            'avg_volume': int(df['volume'].mean()),
            'avg_turnover': round(df['turnover'].mean(), 2)
        }
    
    def _calc_max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        return round(drawdown.min() * 100, 2)
    
    def compare_stocks(self, codes: List[str], days: int = 30) -> pd.DataFrame:
        """多股票对比"""
        data = []
        for code in codes:
            if code in self.data:
                df = self.data[code].tail(days)
                info = self._stock_info[code]
                data.append({
                    'code': code,
                    'name': info['name'],
                    'industry': info['industry'],
                    'start_price': df.iloc[0]['close'],
                    'end_price': df.iloc[-1]['close'],
                    'return': round((df.iloc[-1]['close'] / df.iloc[0]['close'] - 1) * 100, 2),
                    'avg_volume': int(df['volume'].mean()),
                    'avg_turnover': round(df['turnover'].mean(), 2),
                    'volatility': round(df['close'].pct_change().std() * 100, 2)
                })
        return pd.DataFrame(data)
    
    def export_data(
        self,
        code: str,
        filepath: str,
        format: str = 'csv',
        days: Optional[int] = None
    ):
        """
        导出数据到文件
        
        Args:
            code: 股票代码，传 'all' 导出所有
            filepath: 文件路径
            format: 'csv' 或 'json'
            days: 导出多少天，None表示全部
        """
        if code == 'all':
            # 导出所有股票
            all_data = []
            for c, df in self.data.items():
                df_copy = df.copy()
                df_copy['code'] = c
                df_copy['name'] = self._stock_info[c]['name']
                if days:
                    df_copy = df_copy.tail(days)
                all_data.append(df_copy)
            df = pd.concat(all_data, ignore_index=True)
        else:
            if code not in self.data:
                raise ValueError(f"股票代码 {code} 不存在")
            df = self.data[code].copy()
            df['code'] = code
            df['name'] = self._stock_info[code]['name']
            if days:
                df = df.tail(days)
        
        if format == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format == 'json':
            df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        return filepath
    
    @classmethod
    def create_custom_stock(
        cls,
        code: str,
        name: str,
        base_price: float,
        industry: str = "其他",
        volatility: float = 0.02,
        market_cap: float = 100e8
    ) -> StockConfig:
        """
        创建自定义股票配置
        
        示例：
            custom = EnhancedMockStockData.create_custom_stock(
                code="999999.SZ",
                name="测试股份",
                base_price=50.0,
                industry="科技",
                volatility=0.05,  # 高波动
                market_cap=500e8
            )
            data = EnhancedMockStockData(custom_stocks=[custom])
        """
        industry_enum = Industry.OTHER
        for ind in Industry:
            if ind.value == industry:
                industry_enum = ind
                break
        
        return StockConfig(
            code=code,
            name=name,
            base_price=base_price,
            industry=industry_enum,
            volatility=volatility,
            market_cap=market_cap,
            pe_ratio=random.uniform(10, 50)
        )
