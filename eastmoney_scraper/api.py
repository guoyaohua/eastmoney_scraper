"""
EastMoney Scraper API
东方财富数据爬虫接口

提供简洁的API接口供外部程序调用
"""

import pandas as pd
from typing import Optional, Dict, List, Callable
import threading
import time
from datetime import datetime
import logging

from .concept_sector_scraper import ConceptSectorScraper
from .eastmoney_capital_flow_scraper import CapitalFlowScraper

logger = logging.getLogger(__name__)


# ==================== 概念板块接口 ====================

def get_concept_sectors(
    include_capital_flow: bool = True,
    periods: List[str] = ['today', '5day', '10day'],
    save_to_file: bool = False,
    output_dir: str = "concept_sector_data"
) -> pd.DataFrame:
    """
    获取概念板块数据（一次性）
    
    Parameters:
        include_capital_flow (bool): 是否包含资金流向数据
        periods (List[str]): 资金流向周期 ['today', '5day', '10day']
        save_to_file (bool): 是否保存到文件
        output_dir (str): 输出目录
    
    Returns:
        pd.DataFrame: 概念板块数据
        
    Example:
        >>> df = get_concept_sectors()
        >>> print(df[['板块名称', '涨跌幅', '主力净流入']].head())
    """
    scraper = ConceptSectorScraper(output_dir=output_dir)
    df = scraper.scrape_all_data()
    
    if save_to_file and not df.empty:
        scraper.save_data(df)
    
    return df


def get_concept_sectors_realtime() -> pd.DataFrame:
    """
    仅获取概念板块实时行情（不含资金流向）
    
    Returns:
        pd.DataFrame: 概念板块实时行情数据
        
    Example:
        >>> df = get_concept_sectors_realtime()
        >>> print(df[['板块名称', '涨跌幅', '成交额']].head())
    """
    from .concept_sector_scraper import ConceptSectorConfig, ConceptSectorFetcher, ConceptSectorParser
    
    config = ConceptSectorConfig()
    fetcher = ConceptSectorFetcher(config)
    parser = ConceptSectorParser(config)
    
    quotes_data = fetcher.fetch_concept_quotes()
    df = parser.parse_concept_quotes(quotes_data)
    
    return df


def get_concept_capital_flow(period: str = 'today') -> pd.DataFrame:
    """
    获取概念板块资金流向数据
    
    Parameters:
        period (str): 时间周期 'today'/'5day'/'10day'
        
    Returns:
        pd.DataFrame: 资金流向数据
        
    Example:
        >>> df = get_concept_capital_flow('5day')
        >>> print(df[['板块名称', '5日主力净流入']].head())
    """
    from .concept_sector_scraper import ConceptSectorConfig, ConceptSectorFetcher, ConceptSectorParser
    
    config = ConceptSectorConfig()
    fetcher = ConceptSectorFetcher(config)
    parser = ConceptSectorParser(config)
    
    flow_data = fetcher.fetch_capital_flow(period)
    df = parser.parse_capital_flow(flow_data, period)
    
    return df


# ==================== 个股资金流向接口 ====================

def get_stock_capital_flow(
    max_pages: int = 10,
    save_to_file: bool = False,
    output_dir: str = "capital_flow_data"
) -> pd.DataFrame:
    """
    获取个股资金流向数据
    
    Parameters:
        max_pages (int): 最大页数
        save_to_file (bool): 是否保存到文件
        output_dir (str): 输出目录
        
    Returns:
        pd.DataFrame: 个股资金流向数据
        
    Example:
        >>> df = get_stock_capital_flow(max_pages=5)
        >>> print(df[['股票名称', '涨跌幅', '主力净流入']].head())
    """
    scraper = CapitalFlowScraper()
    scraper.storage.output_dir = output_dir
    
    df = scraper.scrape_once(save_to_file=save_to_file)
    return df if df is not None else pd.DataFrame()


# ==================== 监控器类 ====================

class ConceptSectorMonitor:
    """
    概念板块监控器
    
    提供实时监控概念板块行情和资金流向的功能
    
    Example:
        >>> monitor = ConceptSectorMonitor()
        >>> 
        >>> # 设置回调函数
        >>> def on_data(df):
        ...     print(f"收到数据更新: {len(df)} 个板块")
        ...     print(df[['板块名称', '涨跌幅']].head())
        >>> 
        >>> monitor.set_callback(on_data)
        >>> monitor.start(interval=30)  # 每30秒更新一次
        >>> 
        >>> # 停止监控
        >>> monitor.stop()
    """
    
    def __init__(self, output_dir: str = "concept_sector_data"):
        self.scraper = ConceptSectorScraper(output_dir=output_dir)
        self.is_running = False
        self.thread = None
        self.callback = None
        self.interval = 10
        self.last_data = None
        
    def set_callback(self, callback: Callable[[pd.DataFrame], None]):
        """设置数据更新回调函数"""
        self.callback = callback
        
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """获取最新数据"""
        return self.last_data
        
    def start(self, interval: int = 10):
        """
        开始监控
        
        Parameters:
            interval (int): 更新间隔（秒）
        """
        if self.is_running:
            logger.warning("监控器已在运行中")
            return
            
        self.interval = interval
        self.is_running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"概念板块监控器已启动，更新间隔: {interval}秒")
        
    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("概念板块监控器已停止")
        
    def _run(self):
        """运行监控循环"""
        while self.is_running:
            try:
                df = self.scraper.scrape_all_data()
                if not df.empty:
                    self.last_data = df
                    if self.callback:
                        self.callback(df)
                    self.scraper.save_data(df)
                    
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"监控过程出错: {e}")
                time.sleep(self.interval)


class StockCapitalFlowMonitor:
    """
    个股资金流向监控器
    
    Example:
        >>> monitor = StockCapitalFlowMonitor()
        >>> 
        >>> def on_data(df):
        ...     print(f"收到数据更新: {len(df)} 只股票")
        >>> 
        >>> monitor.set_callback(on_data)
        >>> monitor.start(interval=60)
        >>> monitor.stop()
    """
    
    def __init__(self, output_dir: str = "capital_flow_data"):
        self.scraper = CapitalFlowScraper()
        self.scraper.storage.output_dir = output_dir
        self.is_running = False
        self.thread = None
        self.callback = None
        self.interval = 10
        self.last_data = None
        
    def set_callback(self, callback: Callable[[pd.DataFrame], None]):
        """设置数据更新回调函数"""
        self.callback = callback
        
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """获取最新数据"""
        return self.last_data
        
    def start(self, interval: int = 10):
        """开始监控"""
        if self.is_running:
            logger.warning("监控器已在运行中")
            return
            
        self.interval = interval
        self.is_running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"个股资金流监控器已启动，更新间隔: {interval}秒")
        
    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("个股资金流监控器已停止")
        
    def _run(self):
        """运行监控循环"""
        while self.is_running:
            try:
                df = self.scraper.scrape_once(save_to_file=True)
                if df is not None and not df.empty:
                    self.last_data = df
                    if self.callback:
                        self.callback(df)
                        
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"监控过程出错: {e}")
                time.sleep(self.interval)


# ==================== 高级功能 ====================

def filter_sectors_by_change(df: pd.DataFrame, min_change: float = None, max_change: float = None) -> pd.DataFrame:
    """
    根据涨跌幅筛选板块
    
    Parameters:
        df (pd.DataFrame): 板块数据
        min_change (float): 最小涨跌幅
        max_change (float): 最大涨跌幅
        
    Returns:
        pd.DataFrame: 筛选后的数据
    """
    result = df.copy()
    if min_change is not None:
        result = result[result['涨跌幅'] >= min_change]
    if max_change is not None:
        result = result[result['涨跌幅'] <= max_change]
    return result


def filter_sectors_by_capital(df: pd.DataFrame, min_capital: float = None, flow_type: str = '主力净流入') -> pd.DataFrame:
    """
    根据资金流向筛选板块
    
    Parameters:
        df (pd.DataFrame): 板块数据
        min_capital (float): 最小资金流入（万元）
        flow_type (str): 资金类型
        
    Returns:
        pd.DataFrame: 筛选后的数据
    """
    if flow_type in df.columns and min_capital is not None:
        return df[df[flow_type] >= min_capital]
    return df


def get_top_sectors(df: pd.DataFrame, n: int = 10, by: str = '涨跌幅', ascending: bool = False) -> pd.DataFrame:
    """
    获取排名前N的板块
    
    Parameters:
        df (pd.DataFrame): 板块数据
        n (int): 数量
        by (str): 排序字段
        ascending (bool): 是否升序
        
    Returns:
        pd.DataFrame: 前N个板块
    """
    if by in df.columns:
        return df.sort_values(by, ascending=ascending).head(n)
    return df.head(n)