"""
东方财富数据爬虫API接口模块
EastMoney Scraper API Interface Module

本模块提供简洁易用的API接口，供外部程序调用爬虫功能。
包含概念板块数据获取、个股资金流向分析、实时监控、数据筛选等核心功能。

This module provides simple and easy-to-use API interfaces for external programs
to call scraper functions. Includes concept sector data fetching, individual stock
capital flow analysis, real-time monitoring, data filtering and other core features.

主要功能包括 (Main features include):
- 概念板块行情与资金流向数据获取 (Concept sector quotes and capital flow data fetching)
- 个股资金流向排行数据获取 (Individual stock capital flow ranking data fetching)
- 实时数据监控器 (Real-time data monitors)
- 数据分析与筛选工具 (Data analysis and filtering tools)
- 股票到概念板块映射关系 (Stock-to-concept sector mapping)
"""

import pandas as pd
from typing import Optional, Dict, List, Callable, Union
import threading
import time
from datetime import datetime
import logging
import os
from .concept_sector_scraper import ConceptSectorScraper
from .eastmoney_capital_flow_scraper import CapitalFlowScraper

# 获取日志记录器实例，使用模块名作为日志器名称
# (Get logger instance using module name as logger name)
logger = logging.getLogger(__name__)


# ==================== 概念板块数据获取接口 (Concept Sector Data Fetching APIs) ====================

def get_concept_sectors(
    include_capital_flow: bool = True,
    periods: List[str] = ['today', '5day', '10day'],
    save_to_file: bool = False,
    output_dir: str = "concept_sector_data"
) -> pd.DataFrame:
    """
    获取概念板块综合数据（行情+资金流向）。
    (Fetches comprehensive concept sector data including quotes and capital flow.)
    
    这是最常用的接口，能够一次性获取概念板块的完整数据，包括实时行情和多周期资金流向信息。
    适用于需要全面分析概念板块表现的场景。
    
    (This is the most commonly used interface that can fetch complete concept sector data
    in one call, including real-time quotes and multi-period capital flow information.
    Suitable for scenarios requiring comprehensive analysis of concept sector performance.)
    
    Args:
        include_capital_flow (bool): 是否包含资金流向数据。默认为 True。
            (Whether to include capital flow data. Default is True.)
        periods (List[str]): 资金流向周期列表，可选值：'today', '5day', '10day'。
            (Capital flow period list, options: 'today', '5day', '10day'.)
        save_to_file (bool): 是否将获取的数据保存到文件。默认为 False。
            (Whether to save fetched data to file. Default is False.)
        output_dir (str): 数据文件的输出目录。默认为 "concept_sector_data"。
            (Output directory for data files. Default is "concept_sector_data".)
    
    Returns:
        pd.DataFrame: 包含概念板块数据的Pandas DataFrame，字段包括：
            (Pandas DataFrame containing concept sector data with fields including:)
            - 板块代码 (Sector Code): 概念板块唯一标识符
            - 板块名称 (Sector Name): 概念板块中文名称
            - 涨跌幅 (Change %): 当日涨跌百分比
            - 最新价 (Latest Price): 最新指数价格
            - 成交额 (Volume): 成交金额
            - 主力净流入 (Main Net Inflow): 主力资金净流入金额
            - 5日主力净流入 (5-Day Main Net Inflow): 5日累计主力净流入
            - 10日主力净流入 (10-Day Main Net Inflow): 10日累计主力净流入
        
    Example:
        >>> # 获取所有概念板块数据
        >>> df = get_concept_sectors()
        >>> print(df[['板块名称', '涨跌幅', '主力净流入']].head())
        
        >>> # 仅获取今日资金流向，并保存到文件
        >>> df = get_concept_sectors(periods=['today'], save_to_file=True)
        >>> print(f"获取到 {len(df)} 个概念板块数据")
    """
    # 创建概念板块爬虫实例
    # (Create concept sector scraper instance)
    scraper = ConceptSectorScraper(output_dir=output_dir)
    
    # 爬取所有数据（包括行情和资金流向）
    # (Scrape all data including quotes and capital flow)
    df = scraper.scrape_all_data()
    
    # 如果需要保存文件且数据不为空，则保存数据
    # (Save data if requested and data is not empty)
    if save_to_file and not df.empty:
        scraper.save_data(df)
        logger.info(f"概念板块数据已保存到目录: {output_dir}")
    
    return df


def get_concept_sectors_realtime() -> pd.DataFrame:
    """
    获取概念板块实时行情数据（不包含资金流向）。
    (Fetches real-time concept sector quote data without capital flow.)
    
    此接口只获取概念板块的实时行情信息，不包含资金流向数据，速度更快。
    适用于只需要查看板块涨跌情况，不需要资金流向分析的场景。
    
    (This interface only fetches real-time quote information for concept sectors,
    excluding capital flow data, making it faster. Suitable for scenarios where
    only sector price movements are needed without capital flow analysis.)
    
    Returns:
        pd.DataFrame: 包含概念板块实时行情数据的DataFrame，字段包括：
            (DataFrame containing real-time concept sector quote data with fields:)
            - 板块代码 (Sector Code): 概念板块唯一标识符
            - 板块名称 (Sector Name): 概念板块中文名称
            - 涨跌幅 (Change %): 当日涨跌百分比
            - 最新价 (Latest Price): 最新指数价格
            - 成交额 (Volume): 成交金额
            - 换手率 (Turnover Rate): 换手率百分比
            - 领涨股 (Leading Stock): 板块内涨幅最大的股票
    
    Example:
        >>> # 快速获取概念板块行情
        >>> df = get_concept_sectors_realtime()
        >>> print(f"获取到 {len(df)} 个板块的实时行情")
        >>>
        >>> # 查看涨幅前10的板块
        >>> top_gainers = df.nlargest(10, '涨跌幅')
        >>> print(top_gainers[['板块名称', '涨跌幅', '领涨股']])
    """
    # 创建概念板块爬虫实例
    # (Create concept sector scraper instance)
    scraper = ConceptSectorScraper()
    
    # 只获取行情数据，不获取资金流向数据
    # (Only fetch quote data, no capital flow data)
    fetcher = scraper.fetcher
    quotes_data = fetcher.fetch_concept_quotes()
    
    # 解析行情数据
    # (Parse quote data)
    parser = scraper.parser
    df = parser.parse_concept_quotes(quotes_data)
    
    logger.info(f"成功获取 {len(df)} 个概念板块的实时行情数据")
    return df


def get_concept_capital_flow(period: str = 'today') -> pd.DataFrame:
    """
    获取概念板块指定周期的资金流向数据。
    (Fetches concept sector capital flow data for a specified period.)
    
    此接口专门用于获取概念板块的资金流向数据，支持不同时间周期。
    适用于专门分析资金流向趋势和主力行为的场景。
    
    (This interface is specifically for fetching concept sector capital flow data
    with support for different time periods. Suitable for analyzing capital flow
    trends and institutional behavior.)
    
    Args:
        period (str): 资金流向统计周期，可选值：
            (Capital flow statistics period, options:)
            - 'today': 今日资金流向 (Today's capital flow)
            - '5day': 5日资金流向 (5-day capital flow)
            - '10day': 10日资金流向 (10-day capital flow)
    
    Returns:
        pd.DataFrame: 包含指定周期资金流向数据的DataFrame，字段包括：
            (DataFrame containing capital flow data for specified period with fields:)
            - 板块代码 (Sector Code): 概念板块唯一标识符
            - 板块名称 (Sector Name): 概念板块中文名称
            - 主力净流入 (Main Net Inflow): 主力资金净流入金额
            - 主力净流入占比 (Main Net Inflow Ratio): 主力净流入占成交额比例
            - 超大单净流入 (Super Large Order Net Inflow): 超大单资金净流入
            - 大单净流入 (Large Order Net Inflow): 大单资金净流入
            - 中单净流入 (Medium Order Net Inflow): 中单资金净流入
            - 小单净流入 (Small Order Net Inflow): 小单资金净流入
    
    Example:
        >>> # 获取今日概念板块资金流向
        >>> df_today = get_concept_capital_flow('today')
        >>> print(df_today[['板块名称', '主力净流入', '主力净流入占比']].head())
        
        >>> # 获取5日概念板块资金流向
        >>> df_5day = get_concept_capital_flow('5day')
        >>> inflow_sectors = df_5day[df_5day['主力净流入'] > 0]
        >>> print(f"5日主力净流入板块数量: {len(inflow_sectors)}")
    """
    # 验证周期参数
    # (Validate period parameter)
    valid_periods = ['today', '5day', '10day']
    if period not in valid_periods:
        raise ValueError(f"无效的周期参数: {period}。有效值为: {valid_periods}")
    
    # 创建概念板块爬虫实例
    # (Create concept sector scraper instance)
    scraper = ConceptSectorScraper()
    
    # 获取指定周期的资金流向数据
    # (Fetch capital flow data for specified period)
    fetcher = scraper.fetcher
    flow_data = fetcher.fetch_capital_flow(period=period)
    
    # 解析资金流向数据
    # (Parse capital flow data)
    parser = scraper.parser
    df = parser.parse_capital_flow(flow_data, period=period)
    
    logger.info(f"成功获取 {len(df)} 个概念板块的{period}资金流向数据")
    return df


def get_stock_capital_flow(
    max_pages: int = 10,
    save_to_file: bool = False,
    output_dir: str = "capital_flow_data"
) -> pd.DataFrame:
    """
    获取个股资金流向排行数据。
    (Fetches individual stock capital flow ranking data.)
    
    此接口用于获取按资金流向排序的个股数据，包括主力资金、超大单、大单等各类资金的流向情况。
    数据按主力净流入金额从大到小排序，适用于寻找资金流入活跃的个股。
    
    (This interface fetches individual stock data sorted by capital flow, including
    institutional funds, super large orders, large orders and other types of capital flows.
    Data is sorted by main net inflow amount in descending order, suitable for finding
    stocks with active capital inflows.)
    
    Args:
        max_pages (int): 最大爬取页数，每页约100只股票。默认为 10页（约1000只股票）。
            (Maximum pages to scrape, about 100 stocks per page. Default is 10 pages (~1000 stocks).)
        save_to_file (bool): 是否将获取的数据保存到文件。默认为 False。
            (Whether to save fetched data to file. Default is False.)
        output_dir (str): 数据文件的输出目录。默认为 "capital_flow_data"。
            (Output directory for data files. Default is "capital_flow_data".)
        
    Returns:
        pd.DataFrame: 包含个股资金流向数据的DataFrame，字段包括：
            (DataFrame containing individual stock capital flow data with fields:)
            - 股票代码 (Stock Code): 6位股票代码
            - 股票名称 (Stock Name): 股票中文名称
            - 最新价 (Latest Price): 当前股价
            - 涨跌幅 (Change %): 涨跌百分比
            - 主力净流入 (Main Net Inflow): 主力资金净流入金额
            - 主力净流入占比 (Main Net Inflow Ratio): 主力净流入占成交额比例
            - 超大单净流入 (Super Large Order Net Inflow): 超大单资金净流入
            - 大单净流入 (Large Order Net Inflow): 大单资金净流入
            - 中单净流入 (Medium Order Net Inflow): 中单资金净流入
            - 小单净流入 (Small Order Net Inflow): 小单资金净流入
        
    Example:
        >>> # 获取资金流向排行前500名的股票
        >>> df = get_stock_capital_flow(max_pages=5)
        >>> print(df[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']].head(10))
        
        >>> # 获取所有数据并保存到文件
        >>> df = get_stock_capital_flow(max_pages=20, save_to_file=True)
        >>> print(f"获取到 {len(df)} 只股票的资金流向数据")
        
        >>> # 筛选主力净流入超过1亿的股票
        >>> big_inflow = df[df['主力净流入'] > 10000]  # 单位：万元
        >>> print(f"主力净流入超1亿的股票：{len(big_inflow)} 只")
    """
    # 创建个股资金流向爬虫实例
    # (Create individual stock capital flow scraper instance)
    scraper = CapitalFlowScraper()
    
    # 设置输出目录
    # (Set output directory)
    scraper.storage.output_dir = output_dir
    
    # 爬取数据
    # (Scrape data)
    df = scraper.scrape_once(save_to_file=save_to_file)
    
    # 返回数据，如果为None则返回空DataFrame
    # (Return data, if None return empty DataFrame)
    result_df = df if df is not None else pd.DataFrame()
    
    if not result_df.empty:
        logger.info(f"成功获取 {len(result_df)} 只股票的资金流向数据")
    else:
        logger.warning("未获取到股票资金流向数据")
    
    return result_df


def get_stock_to_concept_map(
    save_to_file: bool = False,
    output_dir: str = "concept_sector_data",
    max_workers: int = 10
) -> Dict[str, List[str]]:
    """
    获取个股到概念板块的映射关系。
    (Fetches mapping relationship from individual stocks to concept sectors.)
    
    此接口用于获取每只股票所属的概念板块信息，建立股票与概念板块之间的映射关系。
    这对于分析概念板块成分股、进行主题投资研究非常有用。
    
    (This interface fetches information about which concept sectors each stock belongs to,
    establishing mapping relationships between stocks and concept sectors. This is very
    useful for analyzing concept sector constituents and thematic investment research.)
    
    Args:
        save_to_file (bool): 是否将映射关系保存到JSON文件。默认为 False。
            (Whether to save mapping to JSON file. Default is False.)
        output_dir (str): 数据文件的输出目录。默认为 "concept_sector_data"。
            (Output directory for data files. Default is "concept_sector_data".)
        max_workers (int): 并行处理的最大线程数。默认为 10。
            (Maximum number of threads for parallel processing. Default is 10.)
    
    Returns:
        Dict[str, List[str]]: 股票代码到概念板块列表的映射字典，格式为：
            (Dictionary mapping stock codes to list of concept sectors, format:)
            {
                "000001": ["银行", "金融改革", "深圳本地股"],
                "000002": ["房地产", "粤港澳大湾区", "深圳本地股"],
                ...
            }
    
    Example:
        >>> # 获取股票到概念板块映射
        >>> mapping = get_stock_to_concept_map()
        >>> print(f"获取到 {len(mapping)} 只股票的概念板块映射")
        
        >>> # 查看某只股票的概念板块
        >>> stock_code = "000001"
        >>> if stock_code in mapping:
        >>>     print(f"{stock_code} 所属概念板块: {mapping[stock_code]}")
        
        >>> # 保存映射关系到文件
        >>> mapping = get_stock_to_concept_map(save_to_file=True)
        >>>
        >>> # 统计概念板块包含的股票数量
        >>> concept_count = {}
        >>> for stock, concepts in mapping.items():
        >>>     for concept in concepts:
        >>>         concept_count[concept] = concept_count.get(concept, 0) + 1
        >>> print("概念板块股票数量排行:")
        >>> for concept, count in sorted(concept_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        >>>     print(f"  {concept}: {count}只股票")
    """
    # 创建概念板块爬虫实例
    # (Create concept sector scraper instance)
    scraper = ConceptSectorScraper(output_dir=output_dir)
    
    # 爬取股票到概念板块的映射关系
    # (Scrape stock-to-concept sector mapping)
    logger.info("开始获取股票到概念板块映射关系...")
    mapping = scraper.scrape_concept_to_stock_mapping(max_workers=max_workers)
    
    # 转换映射关系：从概念->股票列表 转为 股票->概念列表
    # (Convert mapping: from concept->stock_list to stock->concept_list)
    stock_to_concepts = {}
    for concept, stocks in mapping.items():
        for stock in stocks:
            if stock not in stock_to_concepts:
                stock_to_concepts[stock] = []
            stock_to_concepts[stock].append(concept)
    
    # 如果需要保存文件
    # (Save to file if requested)
    if save_to_file:
        filename = "stock_to_concept_mapping.json"
        scraper.save_stock_to_concept_mapping(stock_to_concepts, filename)
        logger.info(f"股票到概念板块映射已保存到文件: {filename}")
    
    logger.info(f"成功获取 {len(stock_to_concepts)} 只股票的概念板块映射关系")
    return stock_to_concepts


# ==================== 实时监控器类 (Real-time Monitor Classes) ====================

class ConceptSectorMonitor:
    """
    概念板块实时数据监控器。
    (Real-time concept sector data monitor.)
    
    此监控器能够定时获取概念板块数据，支持自定义回调函数来处理更新的数据。
    适用于需要实时跟踪概念板块表现、资金流向变化的应用场景。
    
    (This monitor can periodically fetch concept sector data and supports custom
    callback functions to process updated data. Suitable for applications that need
    real-time tracking of concept sector performance and capital flow changes.)
    
    主要功能 (Main Features):
    - 定时自动获取概念板块数据 (Automatic periodic fetching of concept sector data)
    - 支持自定义数据更新回调 (Support for custom data update callbacks)
    - 线程安全的启停控制 (Thread-safe start/stop control)
    - 异常处理和错误恢复 (Exception handling and error recovery)
    - 数据自动保存功能 (Automatic data saving functionality)
    """
    
    def __init__(self, output_dir: str = "concept_sector_data"):
        """
        初始化概念板块监控器。
        (Initialize concept sector monitor.)
        
        Args:
            output_dir (str): 数据文件输出目录。默认为 "concept_sector_data"。
                (Output directory for data files. Default is "concept_sector_data".)
        """
        # 创建概念板块爬虫实例
        # (Create concept sector scraper instance)
        self.scraper = ConceptSectorScraper(output_dir=output_dir)
        
        # 监控状态控制
        # (Monitor status control)
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        
        # 回调函数和数据存储
        # (Callback function and data storage)
        self.callback: Optional[Callable[[pd.DataFrame], None]] = None
        self.interval = 10
        self.last_data: Optional[pd.DataFrame] = None
        
        logger.debug(f"概念板块监控器已初始化，输出目录: {output_dir}")
        
    def set_callback(self, callback: Callable[[pd.DataFrame], None]) -> None:
        """
        设置数据更新回调函数。
        (Set data update callback function.)
        
        回调函数将在每次获取到新数据时被调用，接收DataFrame作为参数。
        (Callback function will be called every time new data is fetched,
        receiving DataFrame as parameter.)
        
        Args:
            callback (Callable[[pd.DataFrame], None]): 数据更新回调函数。
                (Data update callback function.)
        
        Example:
            >>> def my_callback(df):
            >>>     print(f"获取到 {len(df)} 个板块数据")
            >>>     top_gainer = df.iloc[0]
            >>>     print(f"领涨板块: {top_gainer['板块名称']}")
            >>>
            >>> monitor = ConceptSectorMonitor()
            >>> monitor.set_callback(my_callback)
        """
        self.callback = callback
        logger.debug("数据更新回调函数已设置")
        
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """
        获取最新的概念板块数据。
        (Get the latest concept sector data.)
        
        Returns:
            Optional[pd.DataFrame]: 最新的概念板块数据，如果还没有数据则返回None。
                (Latest concept sector data, returns None if no data available yet.)
        """
        return self.last_data
        
    def start(self, interval: int = 10) -> None:
        """
        启动概念板块监控器。
        (Start the concept sector monitor.)
        
        Args:
            interval (int): 数据更新间隔（秒）。默认为 10秒。
                (Data update interval in seconds. Default is 10 seconds.)
        
        Note:
            如果监控器已经在运行，此方法会发出警告并直接返回。
            (If monitor is already running, this method will issue a warning and return.)
        """
        if self.is_running:
            logger.warning("概念板块监控器已在运行中，无法重复启动")
            return
            
        self.interval = interval
        self.is_running = True
        
        # 创建并启动监控线程
        # (Create and start monitoring thread)
        self.thread = threading.Thread(
            target=self._run,
            name="ConceptSectorMonitorThread",
            daemon=True  # 设置为守护线程，主程序退出时自动结束
        )
        self.thread.start()
        
        logger.info(f"概念板块监控器已启动，数据更新间隔: {interval}秒")
        
    def stop(self) -> None:
        """
        停止概念板块监控器。
        (Stop the concept sector monitor.)
        
        此方法会安全地停止监控线程，等待当前操作完成后再退出。
        (This method safely stops the monitoring thread, waiting for current
        operations to complete before exiting.)
        """
        if not self.is_running:
            logger.info("概念板块监控器未在运行")
            return
            
        # 设置停止标志
        # (Set stop flag)
        self.is_running = False
        
        # 等待线程结束
        # (Wait for thread to finish)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("监控线程在5秒内未能正常结束")
            else:
                logger.info("监控线程已正常结束")
        
        self.thread = None
        logger.info("概念板块监控器已停止")
        
    def _run(self) -> None:
        """
        监控器主循环（内部方法）。
        (Monitor main loop - internal method.)
        
        此方法在独立线程中运行，负责定时获取数据、调用回调函数和处理异常。
        (This method runs in a separate thread, responsible for periodic data fetching,
        callback invocation, and exception handling.)
        """
        logger.info("概念板块监控循环已开始")
        
        while self.is_running:
            try:
                # 获取概念板块数据
                # (Fetch concept sector data)
                df = self.scraper.scrape_all_data()
                
                if not df.empty:
                    # 更新最新数据
                    # (Update latest data)
                    self.last_data = df
                    
                    # 调用回调函数
                    # (Call callback function)
                    if self.callback:
                        try:
                            self.callback(df)
                        except Exception as e:
                            logger.error(f"回调函数执行出错: {e}")
                else:
                    logger.warning("获取到的概念板块数据为空")
                    
                # 等待下次更新
                # (Wait for next update)
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("监控器收到键盘中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"监控过程发生异常: {e}", exc_info=True)
                # 发生异常后等待一段时间再继续，避免频繁出错
                # (Wait after exception before continuing to avoid frequent errors)
                time.sleep(min(self.interval, 30))
        
        logger.info("概念板块监控循环已结束")


class StockCapitalFlowMonitor:
    """
    个股资金流向实时数据监控器。
    (Real-time individual stock capital flow data monitor.)
    
    此监控器能够定时获取个股资金流向排行数据，支持自定义回调函数来处理更新的数据。
    适用于需要实时跟踪个股资金流向变化、寻找热门股票的应用场景。
    
    (This monitor can periodically fetch individual stock capital flow ranking data
    and supports custom callback functions to process updated data. Suitable for
    applications that need real-time tracking of individual stock capital flow changes
    and finding hot stocks.)
    
    主要功能 (Main Features):
    - 定时自动获取个股资金流向数据 (Automatic periodic fetching of stock capital flow data)
    - 支持自定义数据更新回调 (Support for custom data update callbacks)
    - 线程安全的启停控制 (Thread-safe start/stop control)
    - 异常处理和错误恢复 (Exception handling and error recovery)
    - 数据自动保存功能 (Automatic data saving functionality)
    """
    
    def __init__(self, output_dir: str = "capital_flow_data"):
        """
        初始化个股资金流向监控器。
        (Initialize individual stock capital flow monitor.)
        
        Args:
            output_dir (str): 数据文件输出目录。默认为 "capital_flow_data"。
                (Output directory for data files. Default is "capital_flow_data".)
        """
        # 创建个股资金流向爬虫实例
        # (Create individual stock capital flow scraper instance)
        self.scraper = CapitalFlowScraper()
        self.scraper.storage.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True) # 创建输出目录 (如果不存在) (Create output directory if it doesn't exist)
        
        # 监控状态控制
        # (Monitor status control)
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        
        # 回调函数和数据存储
        # (Callback function and data storage)
        self.callback: Optional[Callable[[pd.DataFrame], None]] = None
        self.interval = 10
        self.last_data: Optional[pd.DataFrame] = None
        
        logger.debug(f"个股资金流向监控器已初始化，输出目录: {output_dir}")
        
    def set_callback(self, callback: Callable[[pd.DataFrame], None]) -> None:
        """
        设置数据更新回调函数。
        (Set data update callback function.)
        
        回调函数将在每次获取到新数据时被调用，接收DataFrame作为参数。
        (Callback function will be called every time new data is fetched,
        receiving DataFrame as parameter.)
        
        Args:
            callback (Callable[[pd.DataFrame], None]): 数据更新回调函数。
                (Data update callback function.)
        
        Example:
            >>> def my_callback(df):
            >>>     print(f"获取到 {len(df)} 只股票数据")
            >>>     top_stock = df.iloc[0]
            >>>     print(f"资金流入最多: {top_stock['股票名称']}")
            >>>
            >>> monitor = StockCapitalFlowMonitor()
            >>> monitor.set_callback(my_callback)
        """
        self.callback = callback
        logger.debug("数据更新回调函数已设置")
        
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """
        获取最新的个股资金流向数据。
        (Get the latest individual stock capital flow data.)
        
        Returns:
            Optional[pd.DataFrame]: 最新的个股资金流向数据，如果还没有数据则返回None。
                (Latest individual stock capital flow data, returns None if no data available yet.)
        """
        return self.last_data
        
    def start(self, interval: int = 10) -> None:
        """
        启动个股资金流向监控器。
        (Start the individual stock capital flow monitor.)
        
        Args:
            interval (int): 数据更新间隔（秒）。默认为 10秒。
                (Data update interval in seconds. Default is 10 seconds.)
        
        Note:
            如果监控器已经在运行，此方法会发出警告并直接返回。
            (If monitor is already running, this method will issue a warning and return.)
        """
        if self.is_running:
            logger.warning("个股资金流向监控器已在运行中，无法重复启动")
            return
            
        self.interval = interval
        self.is_running = True
        
        # 创建并启动监控线程
        # (Create and start monitoring thread)
        self.thread = threading.Thread(
            target=self._run,
            name="StockCapitalFlowMonitorThread",
            daemon=True  # 设置为守护线程，主程序退出时自动结束
        )
        self.thread.start()
        
        logger.info(f"个股资金流向监控器已启动，数据更新间隔: {interval}秒")
        
    def stop(self) -> None:
        """
        停止个股资金流向监控器。
        (Stop the individual stock capital flow monitor.)
        
        此方法会安全地停止监控线程，等待当前操作完成后再退出。
        (This method safely stops the monitoring thread, waiting for current
        operations to complete before exiting.)
        """
        if not self.is_running:
            logger.info("个股资金流向监控器未在运行")
            return
            
        # 设置停止标志
        # (Set stop flag)
        self.is_running = False
        
        # 等待线程结束
        # (Wait for thread to finish)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("监控线程在5秒内未能正常结束")
            else:
                logger.info("监控线程已正常结束")
        
        self.thread = None
        logger.info("个股资金流向监控器已停止")
        
    def _run(self) -> None:
        """
        监控器主循环（内部方法）。
        (Monitor main loop - internal method.)
        
        此方法在独立线程中运行，负责定时获取数据、调用回调函数和处理异常。
        (This method runs in a separate thread, responsible for periodic data fetching,
        callback invocation, and exception handling.)
        """
        logger.info("个股资金流向监控循环已开始")
        
        while self.is_running:
            try:
                # 获取个股资金流向数据
                # (Fetch individual stock capital flow data)
                df = self.scraper.scrape_once(save_to_file=True)
                
                if df is not None and not df.empty:
                    # 更新最新数据
                    # (Update latest data)
                    self.last_data = df
                    
                    # 调用回调函数
                    # (Call callback function)
                    if self.callback:
                        try:
                            self.callback(df)
                        except Exception as e:
                            logger.error(f"回调函数执行出错: {e}")
                    
                    logger.debug(f"成功获取 {len(df)} 只股票的资金流向数据")
                else:
                    logger.warning("获取到的个股资金流向数据为空")
                        
                # 等待下次更新
                # (Wait for next update)
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("监控器收到键盘中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"监控过程发生异常: {e}", exc_info=True)
                # 发生异常后等待一段时间再继续，避免频繁出错
                # (Wait after exception before continuing to avoid frequent errors)
                time.sleep(min(self.interval, 30))
        
        logger.info("个股资金流向监控循环已结束")


# ==================== 数据分析与筛选工具函数 (Data Analysis and Filtering Utility Functions) ====================

def filter_sectors_by_change(
    df: pd.DataFrame,
    min_change: Optional[float] = None,
    max_change: Optional[float] = None
) -> pd.DataFrame:
    """
    根据涨跌幅筛选概念板块数据。
    (Filter concept sector data by price change percentage.)
    
    此函数用于根据涨跌幅条件筛选概念板块，可以设置最小涨幅、最大涨幅或涨跌幅区间。
    适用于寻找强势板块、弱势板块或特定涨跌幅范围的板块。
    
    (This function filters concept sectors based on price change conditions,
    allowing setting minimum gains, maximum gains, or specific gain/loss ranges.
    Suitable for finding strong sectors, weak sectors, or sectors within specific ranges.)
    
    Args:
        df (pd.DataFrame): 包含概念板块数据的DataFrame。
            (DataFrame containing concept sector data.)
        min_change (Optional[float]): 最小涨跌幅（百分比），例如 3.0 表示3%。
            (Minimum change percentage, e.g., 3.0 means 3%.)
        max_change (Optional[float]): 最大涨跌幅（百分比），例如 -2.0 表示-2%。
            (Maximum change percentage, e.g., -2.0 means -2%.)
    
    Returns:
        pd.DataFrame: 筛选后的概念板块数据。
            (Filtered concept sector data.)
    
    Example:
        >>> # 筛选涨幅超过3%的强势板块
        >>> strong_sectors = filter_sectors_by_change(df, min_change=3.0)
        >>> print(f"强势板块数量: {len(strong_sectors)}")
        
        >>> # 筛选跌幅超过2%的弱势板块
        >>> weak_sectors = filter_sectors_by_change(df, max_change=-2.0)
        >>> print(f"弱势板块数量: {len(weak_sectors)}")
        
        >>> # 筛选涨跌幅在-1%到1%之间的平稳板块
        >>> stable_sectors = filter_sectors_by_change(df, min_change=-1.0, max_change=1.0)
        >>> print(f"平稳板块数量: {len(stable_sectors)}")
    """
    # 复制数据以避免修改原始DataFrame
    # (Copy data to avoid modifying original DataFrame)
    result = df.copy()
    
    # 检查必要的列是否存在
    # (Check if required columns exist)
    if '涨跌幅' not in result.columns:
        logger.warning("筛选失败：DataFrame中缺少 '涨跌幅' 列")
        return df

    # 应用最小涨跌幅筛选条件
    # (Apply minimum change filter condition)
    if min_change is not None:
        result = result[result['涨跌幅'] >= min_change]
        logger.debug(f"应用最小涨跌幅筛选 >= {min_change}%，剩余 {len(result)} 个板块")
    
    # 应用最大涨跌幅筛选条件
    # (Apply maximum change filter condition)
    if max_change is not None:
        result = result[result['涨跌幅'] <= max_change]
        logger.debug(f"应用最大涨跌幅筛选 <= {max_change}%，剩余 {len(result)} 个板块")
    
    logger.info(f"涨跌幅筛选完成：从 {len(df)} 个板块筛选出 {len(result)} 个板块")
    return result


def filter_sectors_by_capital(
    df: pd.DataFrame,
    min_capital: Optional[float] = None,
    capital_flow_column: Optional[str] = None
) -> pd.DataFrame:
    """
    根据资金流向筛选概念板块数据。
    (Filter concept sector data by capital flow.)
    
    此函数用于根据资金流向条件筛选概念板块，可以设置最小资金流入金额。
    支持自动检测不同周期的资金流向列，适用于寻找资金流入活跃的热门板块。
    
    (This function filters concept sectors based on capital flow conditions,
    allowing setting minimum capital inflow amounts. Supports auto-detection of
    capital flow columns for different periods, suitable for finding hot sectors
    with active capital inflows.)
    
    Args:
        df (pd.DataFrame): 包含概念板块数据的DataFrame。
            (DataFrame containing concept sector data.)
        min_capital (Optional[float]): 最小资金流入金额（万元），例如 10000 表示1亿元。
            (Minimum capital inflow amount in 10k yuan, e.g., 10000 means 100 million yuan.)
        capital_flow_column (Optional[str]): 指定资金流向列名，如果不指定则自动检测。
            (Specify capital flow column name, auto-detect if not specified.)
    
    Returns:
        pd.DataFrame: 筛选后的概念板块数据。
            (Filtered concept sector data.)
    
    Example:
        >>> # 筛选主力净流入超过1亿的板块
        >>> hot_sectors = filter_sectors_by_capital(df, min_capital=10000)
        >>> print(f"热门板块数量: {len(hot_sectors)}")
        
        >>> # 筛选5日主力净流入超过5亿的板块
        >>> trending_sectors = filter_sectors_by_capital(df, min_capital=50000, capital_flow_column='5日主力净流入')
        >>> print(f"持续热门板块数量: {len(trending_sectors)}")
    """
    # 复制数据以避免修改原始DataFrame
    # (Copy data to avoid modifying original DataFrame)
    result_df = df.copy()
    
    # 如果未指定列名，自动检测资金流向列
    # (Auto-detect capital flow column if not specified)
    if capital_flow_column is None:
        potential_columns = [
            '主力净流入_x', '主力净流入_y', '主力净流入',
            '5日主力净流入', '10日主力净流入', '今日主力净流入'
        ]
        
        for col in potential_columns:
            if col in result_df.columns:
                capital_flow_column = col
                logger.debug(f"自动检测到资金流向列: {capital_flow_column}")
                break
                
        if capital_flow_column is None:
            logger.warning("筛选失败：DataFrame中未找到任何主力净流入相关列")
            return df
    
    # 检查指定的列是否存在
    # (Check if specified column exists)
    if capital_flow_column not in result_df.columns:
        logger.warning(f"筛选失败：DataFrame中缺少 '{capital_flow_column}' 列")
        return df
    
    # 应用资金流向筛选条件
    # (Apply capital flow filter condition)
    if min_capital is not None:
        result_df = result_df[result_df[capital_flow_column] >= min_capital]
        logger.debug(f"应用资金流向筛选 {capital_flow_column} >= {min_capital}万元，剩余 {len(result_df)} 个板块")
    
    logger.info(f"资金流向筛选完成：从 {len(df)} 个板块筛选出 {len(result_df)} 个板块")
    return result_df


def get_top_sectors(
    df: pd.DataFrame,
    n: int = 10,
    sort_by: str = '涨跌幅',
    ascending: bool = False
) -> pd.DataFrame:
    """
    获取按指定字段排序后的前N个概念板块。
    (Get top N concept sectors sorted by specified field.)
    
    此函数用于对概念板块数据进行排序并获取前N个结果，支持按各种字段排序。
    适用于寻找涨幅榜、资金流入榜、成交额榜等排行数据。
    
    (This function sorts concept sector data and gets top N results, supporting
    sorting by various fields. Suitable for finding gainers list, capital inflow
    list, trading volume list and other rankings.)
    
    Args:
        df (pd.DataFrame): 包含概念板块数据的DataFrame。
            (DataFrame containing concept sector data.)
        n (int): 返回的板块数量。默认为 10。
            (Number of sectors to return. Default is 10.)
        sort_by (str): 排序字段名。默认为 '涨跌幅'。
            (Field name for sorting. Default is '涨跌幅'.)
        ascending (bool): 是否升序排列。默认为 False（降序）。
            (Whether to sort in ascending order. Default is False (descending).)
    
    Returns:
        pd.DataFrame: 排序后的前N个概念板块数据。
            (Top N concept sector data after sorting.)
    
    Example:
        >>> # 获取涨幅前10的板块
        >>> top_gainers = get_top_sectors(df, n=10, sort_by='涨跌幅', ascending=False)
        >>> print("涨幅榜前10:")
        >>> print(top_gainers[['板块名称', '涨跌幅']].to_string(index=False))
        
        >>> # 获取资金流入前5的板块
        >>> top_inflow = get_top_sectors(df, n=5, sort_by='主力净流入', ascending=False)
        >>> print("资金流入榜前5:")
        >>> print(top_inflow[['板块名称', '主力净流入']].to_string(index=False))
        
        >>> # 获取跌幅最大的5个板块
        >>> top_losers = get_top_sectors(df, n=5, sort_by='涨跌幅', ascending=True)
        >>> print("跌幅榜前5:")
        >>> print(top_losers[['板块名称', '涨跌幅']].to_string(index=False))
    """
    # 检查排序字段是否存在
    # (Check if sort field exists)
    if sort_by in df.columns:
        result = df.sort_values(by=sort_by, ascending=ascending).head(n)
        order_text = "升序" if ascending else "降序"
        logger.info(f"按 '{sort_by}' {order_text}排序，返回前 {n} 个板块")
        return result
    else:
        logger.warning(f"排序字段 '{sort_by}' 不存在于DataFrame中，返回前 {n} 行原始数据")
        return df.head(n)


def analyze_sector_data(df: pd.DataFrame) -> Dict[str, Union[int, float, str]]:
    """
    分析概念板块数据，提供统计信息摘要。
    (Analyze concept sector data and provide statistical summary.)
    
    此函数对概念板块数据进行综合分析，计算各种统计指标和市场概况。
    适用于快速了解市场整体情况、板块分布、资金流向趋势等。
    
    (This function performs comprehensive analysis of concept sector data, calculating
    various statistical indicators and market overview. Suitable for quickly understanding
    overall market conditions, sector distribution, capital flow trends, etc.)
    
    Args:
        df (pd.DataFrame): 包含概念板块数据的DataFrame。
            (DataFrame containing concept sector data.)
    
    Returns:
        Dict[str, Union[int, float, str]]: 包含统计分析结果的字典，包括：
            (Dictionary containing statistical analysis results, including:)
            - total_sectors: 板块总数 (Total number of sectors)
            - avg_change: 平均涨跌幅 (Average change percentage)
            - positive_sectors: 上涨板块数 (Number of gaining sectors)
            - negative_sectors: 下跌板块数 (Number of declining sectors)
            - neutral_sectors: 平盘板块数 (Number of flat sectors)
            - avg_capital_flow: 平均资金流向 (Average capital flow)
            - capital_inflow_sectors: 资金流入板块数 (Number of sectors with capital inflow)
            - capital_outflow_sectors: 资金流出板块数 (Number of sectors with capital outflow)
    
    Example:
        >>> # 分析概念板块数据
        >>> analysis = analyze_sector_data(df)
        >>> print(f"市场概况分析:")
        >>> print(f"  总板块数: {analysis['total_sectors']}")
        >>> print(f"  平均涨跌幅: {analysis.get('avg_change', 'N/A'):.2f}%")
        >>> print(f"  上涨板块: {analysis.get('positive_sectors', 'N/A')} 个")
        >>> print(f"  下跌板块: {analysis.get('negative_sectors', 'N/A')} 个")
        >>> print(f"  资金净流入板块: {analysis.get('capital_inflow_sectors', 'N/A')} 个")
    """
    # 检查数据是否为空
    # (Check if data is empty)
    if df.empty:
        logger.warning("分析失败：输入数据为空")
        return {"error": "空数据集"}
        
    analysis = {}
    
    # 基本统计信息
    # (Basic statistics)
    analysis['total_sectors'] = len(df)
    logger.debug(f"开始分析 {len(df)} 个概念板块数据")
    
    # 涨跌幅分析
    # (Change percentage analysis)
    if '涨跌幅' in df.columns:
        analysis['avg_change'] = round(df['涨跌幅'].mean(), 4)
        analysis['positive_sectors'] = len(df[df['涨跌幅'] > 0])
        analysis['negative_sectors'] = len(df[df['涨跌幅'] < 0])
        analysis['neutral_sectors'] = len(df[df['涨跌幅'] == 0])
        
        # 计算涨跌分布比例
        # (Calculate gain/loss distribution ratio)
        total = len(df)
        analysis['positive_ratio'] = round(analysis['positive_sectors'] / total * 100, 2)
        analysis['negative_ratio'] = round(analysis['negative_sectors'] / total * 100, 2)
        
        logger.debug(f"涨跌幅分析：上涨{analysis['positive_sectors']}个，下跌{analysis['negative_sectors']}个")
    else:
        logger.debug("未找到涨跌幅数据列")
        
    # 资金流向分析
    # (Capital flow analysis)
    capital_flow_columns = [col for col in df.columns if '主力净流入' in col]
    if capital_flow_columns:
        main_capital_col = capital_flow_columns[0]
        analysis['main_capital_column'] = main_capital_col
        analysis['avg_capital_flow'] = round(df[main_capital_col].mean(), 2)
        analysis['capital_inflow_sectors'] = len(df[df[main_capital_col] > 0])
        analysis['capital_outflow_sectors'] = len(df[df[main_capital_col] < 0])
        
        # 计算资金流向分布比例
        # (Calculate capital flow distribution ratio)
        total = len(df)
        analysis['inflow_ratio'] = round(analysis['capital_inflow_sectors'] / total * 100, 2)
        analysis['outflow_ratio'] = round(analysis['capital_outflow_sectors'] / total * 100, 2)
        
        logger.debug(f"资金流向分析：流入{analysis['capital_inflow_sectors']}个，流出{analysis['capital_outflow_sectors']}个")
    else:
        logger.debug("未找到资金流向数据列")
        
    # 成交额分析（如果存在）
    # (Trading volume analysis if exists)
    if '成交额' in df.columns:
        analysis['total_volume'] = round(df['成交额'].sum(), 2)
        analysis['avg_volume'] = round(df['成交额'].mean(), 2)
        logger.debug(f"成交额分析：总成交额{analysis['total_volume']}万元")
    
    logger.info(f"概念板块数据分析完成，共分析 {analysis['total_sectors']} 个板块")
    return analysis