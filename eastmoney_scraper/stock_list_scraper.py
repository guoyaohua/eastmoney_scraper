"""
东方财富股票列表数据爬虫模块

本模块提供获取全部股票代码和基本信息的功能，支持按市场类型筛选。
包含沪深A股、科创板、创业板等不同市场的股票信息获取。

主要功能:
- 获取全部A股股票代码列表
- 按市场类型筛选（沪市主板、深市主板、创业板、科创板等）
- 获取股票基本信息（代码、名称、市场类型等）
- 支持数据缓存和定期更新
- 高性能数据获取和解析
"""

import requests
import pandas as pd
import json
import time
import os
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
import logging

# 配置日志
logger = logging.getLogger(__name__)


class StockMarket(Enum):
    """股票市场类型枚举"""
    ALL = "all"           # 全部市场
    SH_MAIN = "sh_main"   # 沪市主板
    SZ_MAIN = "sz_main"   # 深市主板
    CHINEXT = "chinext"   # 创业板
    STAR = "star"         # 科创板
    BJ = "bj"            # 北交所


class StockListConfig:
    """股票列表爬虫配置类"""
    
    # 东方财富股票列表API端点
    STOCK_LIST_URL = "http://80.push2.eastmoney.com/api/qt/clist/get"
    
    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://quote.eastmoney.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }
    
    # 请求参数模板
    BASE_PARAMS = {
        'pn': 1,        # 页码
        'pz': 5000,     # 每页数量（设置较大值获取所有数据）
        'po': 1,        # 排序方式
        'np': 1,        # 未知参数
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',  # 固定参数
        'fltt': 2,      # 过滤参数
        'invt': 2,      # 投资者类型
        'wbp2u': '|0|0|0|web',  # 未知参数
        'fid': 'f3',    # 排序字段
        'fs': '',       # 市场筛选条件（动态设置）
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
    }
    
    # 市场筛选条件映射
    MARKET_FILTERS = {
        StockMarket.ALL: 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048',
        StockMarket.SH_MAIN: 'm:1+t:2,m:1+t:23',      # 沪市主板
        StockMarket.SZ_MAIN: 'm:0+t:6,m:0+t:80',      # 深市主板
        StockMarket.CHINEXT: 'm:0+t:80',               # 创业板
        StockMarket.STAR: 'm:1+t:23',                  # 科创板
        StockMarket.BJ: 'm:0+t:81+s:2048'              # 北交所
    }
    
    # 字段映射
    FIELD_MAPPING = {
        'f12': '股票代码',
        'f14': '股票名称',
        'f2': '最新价',
        'f3': '涨跌幅',
        'f4': '涨跌额',
        'f5': '成交量',
        'f6': '成交额',
        'f7': '振幅',
        'f15': '最高价',
        'f16': '最低价',
        'f17': '开盘价',
        'f18': '昨收价',
        'f20': '总市值',
        'f21': '流通市值',
        'f23': '市盈率',
        'f24': '市净率',
        'f25': '市销率',
        'f22': '换手率',
        'f11': '成交量_手',
        'f62': '主营业务',
        'f128': '领涨领跌',
        'f136': '上市时间',
        'f115': '市盈率_动态',
        'f152': '市净率_加权'
    }


class StockListFetcher:
    """股票列表数据获取器"""
    
    def __init__(self, config: StockListConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        
    def fetch_stock_list(self, market: StockMarket = StockMarket.ALL, timeout: int = 30) -> Optional[Dict]:
        """
        获取股票列表数据
        
        Args:
            market (StockMarket): 市场类型
            timeout (int): 请求超时时间
            
        Returns:
            Optional[Dict]: 返回的JSON数据，失败时返回None
        """
        try:
            # 设置市场筛选条件
            params = self.config.BASE_PARAMS.copy()
            params['fs'] = self.config.MARKET_FILTERS[market]
            
            logger.debug(f"正在获取{market.value}市场股票列表数据...")
            
            response = self.session.get(
                self.config.STOCK_LIST_URL,
                params=params,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # 解析JSON数据
            data = response.json()
            
            if data and 'data' in data and data['data']:
                logger.debug(f"成功获取{market.value}市场股票列表原始数据")
                return data
            else:
                logger.warning(f"获取{market.value}市场股票列表数据为空或格式错误")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"获取{market.value}市场股票列表时网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析{market.value}市场股票列表JSON数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取{market.value}市场股票列表时发生未知错误: {e}")
            return None


class StockListParser:
    """股票列表数据解析器"""
    
    def __init__(self, config: StockListConfig):
        self.config = config
        
    def parse_stock_list(self, data: Dict, market: StockMarket) -> pd.DataFrame:
        """
        解析股票列表数据
        
        Args:
            data (Dict): 原始JSON数据
            market (StockMarket): 市场类型
            
        Returns:
            pd.DataFrame: 解析后的股票列表数据
        """
        try:
            if not data or 'data' not in data or not data['data']:
                logger.warning("股票列表数据为空")
                return pd.DataFrame()
            
            # 提取股票列表数据
            stock_data = data['data'].get('diff', [])
            
            if not stock_data:
                logger.warning("股票列表中没有股票数据")
                return pd.DataFrame()
            
            # 解析每只股票的数据
            parsed_stocks = []
            for stock in stock_data:
                if not isinstance(stock, dict):
                    continue
                
                parsed_stock = {}
                
                # 映射字段
                for field_key, field_name in self.config.FIELD_MAPPING.items():
                    value = stock.get(field_key)
                    if value is not None:
                        parsed_stock[field_name] = value
                    else:
                        parsed_stock[field_name] = None
                
                # 添加市场类型
                parsed_stock['市场类型'] = self._determine_market_type(
                    parsed_stock.get('股票代码', ''), market
                )
                
                # 添加获取时间
                parsed_stock['数据获取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                parsed_stocks.append(parsed_stock)
            
            # 创建DataFrame
            df = pd.DataFrame(parsed_stocks)
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功解析{len(df)}只{market.value}市场股票数据")
            return df
            
        except Exception as e:
            logger.error(f"解析{market.value}市场股票列表数据时发生错误: {e}")
            return pd.DataFrame()
    
    def _determine_market_type(self, stock_code: str, market: StockMarket) -> str:
        """根据股票代码确定详细市场类型"""
        if not stock_code:
            return "未知"
        
        if market != StockMarket.ALL:
            return market.value
        
        # 根据股票代码前缀判断市场类型
        if stock_code.startswith('60'):
            return '沪市主板'
        elif stock_code.startswith('00'):
            return '深市主板'
        elif stock_code.startswith('30'):
            return '创业板'
        elif stock_code.startswith('68'):
            return '科创板'
        elif stock_code.startswith('8') or stock_code.startswith('4'):
            return '北交所'
        else:
            return '其他'
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        if df.empty:
            return df
        
        try:
            # 数值类型字段
            numeric_fields = [
                '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅',
                '最高价', '最低价', '开盘价', '昨收价', '总市值', '流通市值',
                '市盈率', '市净率', '市销率', '换手率', '成交量_手', '市盈率_动态', '市净率_加权'
            ]
            
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
            
            # 字符串类型字段
            string_fields = ['股票代码', '股票名称', '主营业务', '市场类型']
            for field in string_fields:
                if field in df.columns:
                    df[field] = df[field].astype(str)
            
            return df
            
        except Exception as e:
            logger.warning(f"数据类型转换时发生错误: {e}")
            return df


class StockListScraper:
    """股票列表爬虫主类"""
    
    def __init__(self, output_dir: str = "output/stock_list_data"):
        """
        初始化股票列表爬虫
        
        Args:
            output_dir (str): 输出目录路径
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化配置和组件
        self.config = StockListConfig()
        self.fetcher = StockListFetcher(self.config)
        self.parser = StockListParser(self.config)
        
        # 缓存相关
        self.cache_file = os.path.join(output_dir, "stock_list_cache.csv")
        self.cache_duration = timedelta(hours=6)  # 缓存6小时
        
        logger.debug(f"股票列表爬虫已初始化，输出目录: {output_dir}")
    
    def get_all_stocks(
        self,
        market: Union[str, StockMarket] = StockMarket.ALL,
        use_cache: bool = True,
        save_to_file: bool = True
    ) -> pd.DataFrame:
        """
        获取所有股票列表
        
        Args:
            market (Union[str, StockMarket]): 市场类型
            use_cache (bool): 是否使用缓存
            save_to_file (bool): 是否保存到文件
            
        Returns:
            pd.DataFrame: 股票列表数据
        """
        # 处理市场类型参数
        if isinstance(market, str):
            market_map = {
                'all': StockMarket.ALL,
                'sh_main': StockMarket.SH_MAIN,
                'sz_main': StockMarket.SZ_MAIN,
                'chinext': StockMarket.CHINEXT,
                'star': StockMarket.STAR,
                'bj': StockMarket.BJ
            }
            market = market_map.get(market.lower(), StockMarket.ALL)
        
        # 检查缓存
        if use_cache and market == StockMarket.ALL:
            cached_data = self._load_cache()
            if cached_data is not None:
                logger.info(f"从缓存加载股票列表，共{len(cached_data)}只股票")
                return cached_data
        
        # 获取新数据
        logger.info(f"正在获取{market.value}市场股票列表...")
        
        # 获取原始数据
        raw_data = self.fetcher.fetch_stock_list(market)
        if not raw_data:
            logger.error(f"获取{market.value}市场股票列表失败")
            return pd.DataFrame()
        
        # 解析数据
        df = self.parser.parse_stock_list(raw_data, market)
        
        if df.empty:
            logger.warning(f"解析{market.value}市场股票列表数据为空")
            return df
        
        # 保存数据
        if save_to_file:
            filepath = self.save_stock_list(df, market)
            logger.info(f"股票列表已保存到: {filepath}")
        
        # 更新缓存
        if market == StockMarket.ALL:
            self._save_cache(df)
        
        logger.info(f"成功获取{len(df)}只{market.value}市场股票")
        return df
    
    def get_stock_codes(
        self,
        market: Union[str, StockMarket] = StockMarket.ALL,
        use_cache: bool = True
    ) -> List[str]:
        """
        获取股票代码列表
        
        Args:
            market (Union[str, StockMarket]): 市场类型
            use_cache (bool): 是否使用缓存
            
        Returns:
            List[str]: 股票代码列表
        """
        df = self.get_all_stocks(market=market, use_cache=use_cache, save_to_file=False)
        
        if df.empty or '股票代码' not in df.columns:
            return []
        
        stock_codes = df['股票代码'].tolist()
        logger.info(f"获取到{len(stock_codes)}个{market}市场股票代码")
        
        return stock_codes
    
    def get_stock_basic_info(
        self,
        market: Union[str, StockMarket] = StockMarket.ALL,
        use_cache: bool = True
    ) -> Dict[str, Dict]:
        """
        获取股票基本信息字典
        
        Args:
            market (Union[str, StockMarket]): 市场类型
            use_cache (bool): 是否使用缓存
            
        Returns:
            Dict[str, Dict]: 股票代码到基本信息的映射
        """
        df = self.get_all_stocks(market=market, use_cache=use_cache, save_to_file=False)
        
        if df.empty:
            return {}
        
        # 转换为字典格式
        stock_info = {}
        for _, row in df.iterrows():
            stock_code = row.get('股票代码')
            if stock_code:
                stock_info[stock_code] = {
                    '股票名称': row.get('股票名称'),
                    '市场类型': row.get('市场类型'),
                    '最新价': row.get('最新价'),
                    '总市值': row.get('总市值'),
                    '流通市值': row.get('流通市值'),
                    '上市时间': row.get('上市时间')
                }
        
        logger.info(f"获取到{len(stock_info)}只股票的基本信息")
        return stock_info
    
    def save_stock_list(self, df: pd.DataFrame, market: StockMarket, format: str = 'csv') -> str:
        """
        保存股票列表数据
        
        Args:
            df (pd.DataFrame): 股票列表数据
            market (StockMarket): 市场类型
            format (str): 保存格式
            
        Returns:
            str: 保存文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_list_{market.value}_{timestamp}"
        
        if format.lower() == 'csv':
            filepath = os.path.join(self.output_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format.lower() == 'json':
            filepath = os.path.join(self.output_dir, f"{filename}.json")
            df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的保存格式: {format}")
        
        return filepath
    
    def _load_cache(self) -> Optional[pd.DataFrame]:
        """加载缓存数据"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            # 检查缓存时间
            cache_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
            if datetime.now() - cache_time > self.cache_duration:
                logger.debug("缓存已过期")
                return None
            
            # 加载缓存数据
            df = pd.read_csv(self.cache_file, encoding='utf-8-sig')
            logger.debug(f"加载缓存成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
            return None
    
    def _save_cache(self, df: pd.DataFrame) -> None:
        """保存缓存数据"""
        try:
            df.to_csv(self.cache_file, index=False, encoding='utf-8-sig')
            logger.debug("缓存保存成功")
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    def clear_cache(self) -> None:
        """清除缓存"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                logger.info("缓存已清除")
        except Exception as e:
            logger.warning(f"清除缓存失败: {e}")
    
    def get_supported_markets(self) -> List[str]:
        """获取支持的市场类型"""
        return [market.value for market in StockMarket]


# 便捷函数
def get_all_stock_codes(market: str = 'all', use_cache: bool = True) -> List[str]:
    """
    获取所有股票代码（便捷函数）
    
    Args:
        market (str): 市场类型
        use_cache (bool): 是否使用缓存
        
    Returns:
        List[str]: 股票代码列表
    """
    scraper = StockListScraper()
    return scraper.get_stock_codes(market=market, use_cache=use_cache)


def get_stock_basic_info(market: str = 'all', use_cache: bool = True) -> Dict[str, Dict]:
    """
    获取股票基本信息（便捷函数）
    
    Args:
        market (str): 市场类型
        use_cache (bool): 是否使用缓存
        
    Returns:
        Dict[str, Dict]: 股票基本信息字典
    """
    scraper = StockListScraper()
    return scraper.get_stock_basic_info(market=market, use_cache=use_cache)


if __name__ == "__main__":
    # 简单测试
    scraper = StockListScraper()
    
    # 获取所有股票代码
    print("获取所有股票代码...")
    codes = scraper.get_stock_codes()
    print(f"总共获取到 {len(codes)} 只股票")
    print(f"前10只股票代码: {codes[:10]}")
    
    # 获取创业板股票
    print("\n获取创业板股票...")
    chinext_codes = scraper.get_stock_codes(market='chinext')
    print(f"创业板股票数量: {len(chinext_codes)}")
    
    # 获取股票基本信息
    print("\n获取前5只股票的基本信息...")
    info = scraper.get_stock_basic_info()
    for i, (code, data) in enumerate(info.items()):
        if i >= 5:
            break
        print(f"{code}: {data['股票名称']} - {data['市场类型']}")