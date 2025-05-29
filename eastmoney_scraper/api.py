"""
东方财富数据爬虫API接口模块

本模块提供简洁易用的API接口，供外部程序调用爬虫功能。
包含概念板块数据获取、个股资金流向分析、实时监控、数据筛选等核心功能。

主要功能包括:
- 概念板块行情与资金流向数据获取
- 个股资金流向排行数据获取
- 实时数据监控器
- 数据分析与筛选工具
- 股票到概念板块映射关系
"""

import pandas as pd
from typing import Optional, Dict, List, Callable, Union
import threading
import time
from datetime import datetime, timedelta
import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from .sector_scraper import SectorScraper, SectorType
from .stock_capital_flow_scraper import StockCapitalFlowScraper, MarketType

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 获取日志记录器实例，使用模块名作为日志器名称
logger = logging.getLogger(__name__)


# ==================== 概念板块数据获取接口 ====================

def get_concept_sectors(
    include_capital_flow: bool = True,
    periods: List[str] = ['today', '5day', '10day'],
    save_to_file: bool = False,
    output_dir: str = "output/concept_sector_data"
) -> pd.DataFrame:
    """
    获取概念板块综合数据（行情+资金流向）
    
    这是最常用的接口，能够一次性获取概念板块的完整数据，包括实时行情和多周期资金流向信息。
    适用于需要全面分析概念板块表现的场景。
    
    Args:
        include_capital_flow (bool): 是否包含资金流向数据，默认为True
        periods (List[str]): 资金流向周期列表，可选值：'today', '5day', '10day'
        save_to_file (bool): 是否将获取的数据保存到文件，默认为False
        output_dir (str): 数据文件的输出目录，默认为"concept_sector_data"
    
    Returns:
        pd.DataFrame: 包含概念板块数据的Pandas DataFrame，字段包括：
            - 板块代码: 概念板块唯一标识符
            - 板块名称: 概念板块中文名称
            - 涨跌幅: 当日涨跌百分比
            - 最新价: 最新指数价格
            - 成交额: 成交金额
            - 主力净流入: 主力资金净流入金额
            - 5日主力净流入: 5日累计主力净流入
            - 10日主力净流入: 10日累计主力净流入
        
    Example:
        >>> # 获取所有概念板块数据
        >>> df = get_concept_sectors()
        >>> print(df[['板块名称', '涨跌幅', '主力净流入']].head())
        
        >>> # 仅获取今日资金流向，并保存到文件
        >>> df = get_concept_sectors(periods=['today'], save_to_file=True)
        >>> print(f"获取到 {len(df)} 个概念板块数据")
    """
    # 创建概念板块爬虫实例
    scraper = SectorScraper(sector_type=SectorType.CONCEPT, output_dir=output_dir)
    
    # 爬取所有数据（包括行情和资金流向）
    df = scraper.scrape_all_data()
    
    # 如果需要保存文件且数据不为空，则保存数据
    if save_to_file and not df.empty:
        scraper.save_data(df)
        logger.info(f"概念板块数据已保存到目录: {output_dir}")
    
    return df


def get_concept_sectors_realtime() -> pd.DataFrame:
    """
    获取概念板块实时行情数据（不包含资金流向）
    
    此接口只获取概念板块的实时行情信息，不包含资金流向数据，速度更快。
    适用于只需要查看板块涨跌情况，不需要资金流向分析的场景。
    
    Returns:
        pd.DataFrame: 包含概念板块实时行情数据的DataFrame，字段包括：
            - 板块代码: 概念板块唯一标识符
            - 板块名称: 概念板块中文名称
            - 涨跌幅: 当日涨跌百分比
            - 最新价: 最新指数价格
            - 成交额: 成交金额
            - 换手率: 换手率百分比
            - 领涨股: 板块内涨幅最大的股票
    
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
    scraper = SectorScraper(sector_type=SectorType.CONCEPT)
    
    # 只获取行情数据，不获取资金流向数据
    fetcher = scraper.fetcher
    quotes_data = fetcher.fetch_all_quotes()
    
    # 解析行情数据
    parser = scraper.parser
    df = parser.parse_quotes_data(quotes_data)
    
    logger.info(f"成功获取 {len(df)} 个概念板块的实时行情数据")
    return df


def get_concept_capital_flow(period: str = 'today') -> pd.DataFrame:
    """
    获取概念板块指定周期的资金流向数据
    
    此接口专门用于获取概念板块的资金流向数据，支持不同时间周期。
    适用于专门分析资金流向趋势和主力行为的场景。
    
    Args:
        period (str): 资金流向统计周期，可选值：
            - 'today': 今日资金流向
            - '5day': 5日资金流向
            - '10day': 10日资金流向
    
    Returns:
        pd.DataFrame: 包含指定周期资金流向数据的DataFrame，字段包括：
            - 板块代码: 概念板块唯一标识符
            - 板块名称: 概念板块中文名称
            - 主力净流入: 主力资金净流入金额
            - 主力净流入占比: 主力净流入占成交额比例
            - 超大单净流入: 超大单资金净流入
            - 大单净流入: 大单资金净流入
            - 中单净流入: 中单资金净流入
            - 小单净流入: 小单资金净流入
    
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
    valid_periods = ['today', '5day', '10day']
    if period not in valid_periods:
        raise ValueError(f"无效的周期参数: {period}。有效值为: {valid_periods}")
    
    # 创建概念板块爬虫实例
    scraper = SectorScraper(sector_type=SectorType.CONCEPT)
    
    # 获取综合数据（包含资金流向信息）
    df = scraper.scrape_all_data()
    
    # 根据period筛选相关的资金流向列
    if period == 'today':
        columns = ['板块代码', '板块名称', '主力净流入', '主力净流入占比', '超大单净流入']
    elif period == '5day':
        columns = ['板块代码', '板块名称', '5日主力净流入', '5日主力净流入占比', '5日超大单净流入']
    elif period == '10day':
        columns = ['板块代码', '板块名称', '10日主力净流入', '10日主力净流入占比', '10日超大单净流入']
    
    # 筛选存在的列
    existing_columns = [col for col in columns if col in df.columns]
    result_df = df[existing_columns] if existing_columns else pd.DataFrame()
    
    logger.info(f"成功获取 {len(result_df)} 个概念板块的{period}资金流向数据")
    return result_df


def get_stock_capital_flow(
    max_pages: int = 10,
    save_to_file: bool = False,
    output_dir: str = "output/capital_flow_data"
) -> pd.DataFrame:
    """
    获取个股资金流向排行数据
    
    此接口用于获取按资金流向排序的个股数据，包括主力资金、超大单、大单等各类资金的流向情况。
    数据按主力净流入金额从大到小排序，适用于寻找资金流入活跃的个股。
    
    Args:
        max_pages (int): 最大爬取页数，每页约100只股票，默认为10页（约1000只股票）
        save_to_file (bool): 是否将获取的数据保存到文件，默认为False
        output_dir (str): 数据文件的输出目录，默认为"capital_flow_data"
        
    Returns:
        pd.DataFrame: 包含个股资金流向数据的DataFrame，字段包括：
            - 股票代码: 6位股票代码
            - 股票名称: 股票中文名称
            - 最新价: 当前股价
            - 涨跌幅: 涨跌百分比
            - 主力净流入: 主力资金净流入金额
            - 主力净流入占比: 主力净流入占成交额比例
            - 超大单净流入: 超大单资金净流入
            - 大单净流入: 大单资金净流入
            - 中单净流入: 中单资金净流入
            - 小单净流入: 小单资金净流入
        
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
    scraper = StockCapitalFlowScraper(market_type=MarketType.ALL, output_dir=output_dir)
    
    # 爬取数据
    if save_to_file:
        df, filepath = scraper.run_once(max_pages=max_pages, save_format='csv')
    else:
        df = scraper.scrape_all_data(max_pages=max_pages)
    
    # 返回数据，如果为None则返回空DataFrame
    result_df = df if df is not None else pd.DataFrame()
    
    if not result_df.empty:
        logger.info(f"成功获取 {len(result_df)} 只股票的资金流向数据")
    else:
        logger.warning("未获取到股票资金流向数据")
    
    return result_df


def get_stock_to_concept_map(
    save_to_file: bool = False,
    output_dir: str = "output/concept_sector_data",
    max_workers: int = 10
) -> Dict[str, List[str]]:
    """
    获取个股到概念板块的映射关系
    
    此接口用于获取每只股票所属的概念板块信息，建立股票与概念板块之间的映射关系。
    这对于分析概念板块成分股、进行主题投资研究非常有用。
    
    Args:
        save_to_file (bool): 是否将映射关系保存到JSON文件，默认为False
        output_dir (str): 数据文件的输出目录，默认为"concept_sector_data"
        max_workers (int): 并行处理的最大线程数，默认为10
    
    Returns:
        Dict[str, List[str]]: 股票代码到概念板块列表的映射字典，格式为：
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
    scraper = SectorScraper(sector_type=SectorType.CONCEPT, output_dir=output_dir)
    
    # 爬取股票到概念板块的映射关系
    logger.info("开始获取股票到概念板块映射关系...")
    mapping = scraper.scrape_stock_to_sector_mapping(max_workers=max_workers)
    
    # 转换映射关系：从概念->股票列表 转为 股票->概念列表
    stock_to_concepts = {}
    for concept, stocks in mapping.items():
        for stock in stocks:
            if stock not in stock_to_concepts:
                stock_to_concepts[stock] = []
            stock_to_concepts[stock].append(concept)
    
    # 如果需要保存文件
    if save_to_file:
        scraper.save_mapping_data(stock_to_concepts)
        logger.info(f"股票到概念板块映射已保存到文件")
    
    logger.info(f"成功获取 {len(stock_to_concepts)} 只股票的概念板块映射关系")
# ==================== 通用板块数据获取接口 ====================

def get_sectors(
    sector_type: Union[str, SectorType],
    include_capital_flow: bool = True,
    save_to_file: bool = False,
    output_dir: str = None
) -> pd.DataFrame:
    """
    获取板块综合数据（行情+资金流向）- 支持概念板块和行业板块
    
    这是新的通用接口，能够获取概念板块或行业板块的完整数据，包括实时行情和资金流向信息。
    
    Args:
        sector_type (Union[str, SectorType]): 板块类型，可选值：
            - "concept" 或 SectorType.CONCEPT: 概念板块
            - "industry" 或 SectorType.INDUSTRY: 行业板块
        include_capital_flow (bool): 是否包含资金流向数据，默认为True
        save_to_file (bool): 是否将获取的数据保存到文件，默认为False
        output_dir (str): 数据文件的输出目录，如果为None则根据板块类型自动设置
    
    Returns:
        pd.DataFrame: 包含板块数据的Pandas DataFrame，字段包括：
            - 板块代码: 板块唯一标识符
            - 板块名称: 板块中文名称
            - 涨跌幅: 当日涨跌百分比
            - 最新价: 最新指数价格
            - 成交额: 成交金额
            - 主力净流入: 主力资金净流入金额
            - 5日主力净流入: 5日累计主力净流入
            - 10日主力净流入: 10日累计主力净流入
        
    Example:
        >>> # 获取所有概念板块数据
        >>> df_concept = get_sectors("concept")
        >>> print(df_concept[['板块名称', '涨跌幅', '主力净流入']].head())
        
        >>> # 获取所有行业板块数据并保存到文件
        >>> df_industry = get_sectors(SectorType.INDUSTRY, save_to_file=True)
        >>> print(f"获取到 {len(df_industry)} 个行业板块数据")
    """
    # 处理板块类型参数
    if isinstance(sector_type, str):
        sector_type_map = {
            "concept": SectorType.CONCEPT,
            "industry": SectorType.INDUSTRY
        }
        if sector_type not in sector_type_map:
            raise ValueError(f"无效的板块类型: {sector_type}。有效值为: {list(sector_type_map.keys())}")
        sector_type = sector_type_map[sector_type]
    
    # 创建板块爬虫实例
    scraper = SectorScraper(sector_type=sector_type, output_dir=output_dir)
    
    # 爬取所有数据（包括行情和资金流向）
    df = scraper.scrape_all_data()
    
    # 如果需要保存文件且数据不为空，则保存数据
    if save_to_file and not df.empty:
        scraper.save_data(df)
        logger.info(f"{sector_type.value}板块数据已保存到目录: {scraper.output_dir}")
    
    return df


def get_industry_sectors(
    include_capital_flow: bool = True,
    save_to_file: bool = False,
    output_dir: str = "output/industry_sector_data"
) -> pd.DataFrame:
    """
    获取行业板块综合数据（行情+资金流向）
    
    此接口专门用于获取行业板块数据，是get_sectors的便捷封装。
    
    Args:
        include_capital_flow (bool): 是否包含资金流向数据，默认为True
        save_to_file (bool): 是否将获取的数据保存到文件，默认为False
        output_dir (str): 数据文件的输出目录，默认为"industry_sector_data"
    
    Returns:
        pd.DataFrame: 包含行业板块数据的Pandas DataFrame
        
    Example:
        >>> # 获取所有行业板块数据
        >>> df = get_industry_sectors()
        >>> print(df[['板块名称', '涨跌幅', '主力净流入']].head())
        
        >>> # 获取并保存行业板块数据
        >>> df = get_industry_sectors(save_to_file=True)
        >>> print(f"获取到 {len(df)} 个行业板块数据")
    """
    return get_sectors(
        sector_type=SectorType.INDUSTRY,
        include_capital_flow=include_capital_flow,
        save_to_file=save_to_file,
        output_dir=output_dir
    )


def get_stock_to_sector_mapping(
    sector_type: Union[str, SectorType],
    save_to_file: bool = False,
    output_dir: str = None,
    max_workers: int = 10
) -> Dict[str, List[str]]:
    """
    获取个股到板块的映射关系（支持概念板块和行业板块）
    
    此接口用于获取每只股票所属的板块信息，建立股票与板块之间的映射关系。
    
    Args:
        sector_type (Union[str, SectorType]): 板块类型，可选值：
            - "concept" 或 SectorType.CONCEPT: 概念板块
            - "industry" 或 SectorType.INDUSTRY: 行业板块
        save_to_file (bool): 是否将映射关系保存到JSON文件，默认为False
        output_dir (str): 数据文件的输出目录，如果为None则根据板块类型自动设置
        max_workers (int): 并行处理的最大线程数，默认为10
    
    Returns:
        Dict[str, List[str]]: 股票代码到板块列表的映射字典，格式为：
            {
                "000001": ["银行", "金融改革", "深圳本地股"],
                "000002": ["房地产", "粤港澳大湾区", "深圳本地股"],
                ...
            }
    
    Example:
        >>> # 获取股票到概念板块映射
        >>> concept_mapping = get_stock_to_sector_mapping("concept")
        >>> print(f"获取到 {len(concept_mapping)} 只股票的概念板块映射")
        
        >>> # 获取股票到行业板块映射
        >>> industry_mapping = get_stock_to_sector_mapping(SectorType.INDUSTRY, save_to_file=True)
        >>> print(f"获取到 {len(industry_mapping)} 只股票的行业板块映射")
    """
    # 处理板块类型参数
    if isinstance(sector_type, str):
        sector_type_map = {
            "concept": SectorType.CONCEPT,
            "industry": SectorType.INDUSTRY
        }
        if sector_type not in sector_type_map:
            raise ValueError(f"无效的板块类型: {sector_type}。有效值为: {list(sector_type_map.keys())}")
        sector_type = sector_type_map[sector_type]
    
    # 创建板块爬虫实例
    scraper = SectorScraper(sector_type=sector_type, output_dir=output_dir)
    
    # 爬取股票到板块的映射关系
    logger.info(f"开始获取股票到{sector_type.value}板块映射关系...")
    mapping = scraper.scrape_stock_to_sector_mapping(max_workers=max_workers)
    
    # 如果需要保存文件
    if save_to_file:
        scraper.save_mapping_data(mapping)
        logger.info(f"股票到{sector_type.value}板块映射已保存到文件")
    
    logger.info(f"成功获取 {len(mapping)} 只股票的{sector_type.value}板块映射关系")
    return mapping
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
    
    def __init__(self, output_dir: str = "output/concept_sector_data"):
        """
        初始化概念板块监控器。
        (Initialize concept sector monitor.)
        
        Args:
            output_dir (str): 数据文件输出目录。默认为 "concept_sector_data"。
                (Output directory for data files. Default is "concept_sector_data".)
        """
        # 创建概念板块爬虫实例
        # (Create concept sector scraper instance)
        self.scraper = SectorScraper(sector_type=SectorType.CONCEPT, output_dir=output_dir)
        
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


class StockCapitalFlowAnalyzer:
    """个股资金流向分析器"""
    
    def __init__(self, data_dir: str = "output/stock_capital_flow_data_all"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_latest_data(self, filename_pattern: str = "stock_capital_flow") -> pd.DataFrame:
        """
        加载最新的资金流向数据
        
        Args:
            filename_pattern (str): 文件名模式
            
        Returns:
            pd.DataFrame: 最新的数据
        """
        try:
            # 查找最新的CSV文件
            csv_files = [f for f in os.listdir(self.data_dir)
                        if f.startswith(filename_pattern) and f.endswith('.csv')]
            
            if not csv_files:
                logger.warning(f"在目录 {self.data_dir} 中未找到资金流向数据文件")
                return pd.DataFrame()
            
            # 按文件名排序，获取最新文件
            latest_file = sorted(csv_files)[-1]
            filepath = os.path.join(self.data_dir, latest_file)
            
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            logger.info(f"成功加载数据文件: {latest_file}, 数据条数: {len(df)}")
            
            return df
            
        except Exception as e:
            logger.error(f"加载数据时发生错误: {e}")
            return pd.DataFrame()
    
    def load_historical_data(self, days: int = 7, filename_pattern: str = "stock_capital_flow") -> List[pd.DataFrame]:
        """
        加载历史数据
        
        Args:
            days (int): 加载最近几天的数据
            filename_pattern (str): 文件名模式
            
        Returns:
            List[pd.DataFrame]: 历史数据列表
        """
        try:
            csv_files = [f for f in os.listdir(self.data_dir)
                        if f.startswith(filename_pattern) and f.endswith('.csv')]
            
            if not csv_files:
                return []
            
            # 按时间排序，获取最近的文件
            csv_files.sort()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            historical_data = []
            for filename in csv_files[-days*10:]:  # 取更多文件以防有些时间段没有数据
                try:
                    # 从文件名提取时间信息
                    time_part = filename.split('_')[-2] + '_' + filename.split('_')[-1].replace('.csv', '')
                    file_time = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
                    
                    if file_time >= cutoff_date:
                        filepath = os.path.join(self.data_dir, filename)
                        df = pd.read_csv(filepath, encoding='utf-8-sig')
                        if not df.empty:
                            df['文件时间'] = file_time
                            historical_data.append(df)
                            
                except Exception as e:
                    logger.warning(f"解析文件 {filename} 时出错: {e}")
                    continue
            
            logger.info(f"成功加载 {len(historical_data)} 个历史数据文件")
            return historical_data
            
        except Exception as e:
            logger.error(f"加载历史数据时发生错误: {e}")
            return []
    
    def get_top_inflow_stocks(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """获取主力净流入最多的股票"""
        if df.empty or '主力净流入' not in df.columns:
            return pd.DataFrame()
        
        return df.nlargest(top_n, '主力净流入')[
            ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比', '数据获取时间']
        ]
    
    def get_top_outflow_stocks(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """获取主力净流出最多的股票"""
        if df.empty or '主力净流入' not in df.columns:
            return pd.DataFrame()
        
        return df.nsmallest(top_n, '主力净流入')[
            ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比', '数据获取时间']
        ]
    
    def analyze_continuous_inflow_stocks(self, historical_data: List[pd.DataFrame], days: int = 3) -> pd.DataFrame:
        """
        分析连续多日主力净流入的股票
        
        Args:
            historical_data (List[pd.DataFrame]): 历史数据列表
            days (int): 连续天数
            
        Returns:
            pd.DataFrame: 连续流入的股票
        """
        if not historical_data or len(historical_data) < days:
            return pd.DataFrame()
        
        try:
            # 合并历史数据
            all_data = pd.concat(historical_data, ignore_index=True)
            
            # 按股票代码分组分析
            continuous_stocks = []
            
            for stock_code, group in all_data.groupby('股票代码'):
                # 按时间排序
                group_sorted = group.sort_values('文件时间')
                
                # 获取最近几天的数据
                recent_data = group_sorted.tail(days)
                
                if len(recent_data) >= days:
                    # 检查是否连续流入
                    inflow_values = recent_data['主力净流入'].values
                    if all(val > 0 for val in inflow_values):
                        latest_data = recent_data.iloc[-1]
                        continuous_stocks.append({
                            '股票代码': stock_code,
                            '股票名称': latest_data['股票名称'],
                            '最新价': latest_data['最新价'],
                            '涨跌幅': latest_data['涨跌幅'],
                            '连续流入天数': days,
                            '累计流入': inflow_values.sum(),
                            '平均每日流入': inflow_values.mean(),
                            '最新流入': latest_data['主力净流入']
                        })
            
            result_df = pd.DataFrame(continuous_stocks)
            if not result_df.empty:
                result_df = result_df.sort_values('累计流入', ascending=False)
            
            return result_df
            
        except Exception as e:
            logger.error(f"分析连续流入股票时发生错误: {e}")
            return pd.DataFrame()
    
    def calculate_market_sentiment(self, df: pd.DataFrame) -> Dict:
        """
        计算市场情绪指标
        
        Args:
            df (pd.DataFrame): 股票数据
            
        Returns:
            Dict: 市场情绪指标
        """
        if df.empty:
            return {}
        
        try:
            total_stocks = len(df)
            inflow_stocks = len(df[df['主力净流入'] > 0]) if '主力净流入' in df.columns else 0
            outflow_stocks = len(df[df['主力净流入'] < 0]) if '主力净流入' in df.columns else 0
            
            up_stocks = len(df[df['涨跌幅'] > 0]) if '涨跌幅' in df.columns else 0
            down_stocks = len(df[df['涨跌幅'] < 0]) if '涨跌幅' in df.columns else 0
            
            total_inflow = df['主力净流入'].sum() if '主力净流入' in df.columns else 0
            
            sentiment = {
                '总股票数': total_stocks,
                '主力净流入股票数': inflow_stocks,
                '主力净流出股票数': outflow_stocks,
                '上涨股票数': up_stocks,
                '下跌股票数': down_stocks,
                '资金流入比例': round(inflow_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0,
                '上涨股票比例': round(up_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0,
                '市场总流入(万元)': round(total_inflow, 2),
                '平均流入(万元)': round(total_inflow / total_stocks, 2) if total_stocks > 0 else 0,
                '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return sentiment
            
        except Exception as e:
            logger.error(f"计算市场情绪时发生错误: {e}")
            return {}


class StockCapitalFlowMonitor:
    """个股资金流向监控器"""
    
    def __init__(self, market_type: MarketType = MarketType.ALL, output_dir: str = None):
        self.market_type = market_type
        self.scraper = StockCapitalFlowScraper(market_type=market_type, output_dir=output_dir)
        self.analyzer = StockCapitalFlowAnalyzer(self.scraper.output_dir)
        self.is_monitoring = False
        
        # 监控状态控制
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        
        # 回调函数和数据存储
        self.callback: Optional[Callable[[pd.DataFrame], None]] = None
        self.interval = 10
        self.last_data: Optional[pd.DataFrame] = None
    
    def set_callback(self, callback: Callable[[pd.DataFrame], None]) -> None:
        """设置数据更新回调函数"""
        self.callback = callback
        logger.debug("数据更新回调函数已设置")
        
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """获取最新的个股资金流向数据"""
        return self.last_data
    
    def display_realtime_data(self):
        """显示实时数据"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 100)
        print(f"个股资金流向实时监控 ({self.market_type.value}市场) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        
        # 加载最新数据
        latest_data = self.analyzer.load_latest_data()
        
        if latest_data.empty:
            print("暂无数据")
            return
        
        # 市场情绪指标
        sentiment = self.analyzer.calculate_market_sentiment(latest_data)
        if sentiment:
            print(f"\n【市场概况】")
            print("-" * 100)
            print(f"总股票数: {sentiment['总股票数']} | "
                  f"上涨: {sentiment['上涨股票数']}({sentiment['上涨股票比例']}%) | "
                  f"下跌: {sentiment['下跌股票数']} | "
                  f"资金流入股票: {sentiment['主力净流入股票数']}({sentiment['资金流入比例']}%)")
            print(f"市场总流入: {sentiment['市场总流入(万元)']}万元 | "
                  f"平均流入: {sentiment['平均流入(万元)']}万元")
        
        # 主力净流入TOP20
        top_inflow = self.analyzer.get_top_inflow_stocks(latest_data, 20)
        if not top_inflow.empty:
            print(f"\n【主力净流入TOP20】")
            print("-" * 100)
            print(f"{'股票代码':<10} {'股票名称':<12} {'最新价':<10} {'涨跌幅':<10} {'主力净流入(万)':<15} {'流入占比(%)':<12}")
            print("-" * 100)
            
            for _, row in top_inflow.iterrows():
                print(f"{row['股票代码']:<10} {row['股票名称']:<12} "
                      f"{row['最新价']:<10.2f} {row['涨跌幅']:<10.2f} "
                      f"{row['主力净流入']:<15.2f} {row['主力净流入占比']:<12.2f}")
        
        # 主力净流出TOP10
        top_outflow = self.analyzer.get_top_outflow_stocks(latest_data, 10)
        if not top_outflow.empty:
            print(f"\n【主力净流出TOP10】")
            print("-" * 100)
            print(f"{'股票代码':<10} {'股票名称':<12} {'最新价':<10} {'涨跌幅':<10} {'主力净流出(万)':<15} {'流出占比(%)':<12}")
            print("-" * 100)
            
            for _, row in top_outflow.iterrows():
                print(f"{row['股票代码']:<10} {row['股票名称']:<12} "
                      f"{row['最新价']:<10.2f} {row['涨跌幅']:<10.2f} "
                      f"{row['主力净流入']:<15.2f} {row['主力净流入占比']:<12.2f}")
    
    def generate_analysis_charts(self, df: pd.DataFrame) -> str:
        """
        生成分析图表
        
        Args:
            df (pd.DataFrame): 数据
            
        Returns:
            str: 图表保存路径
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'个股资金流向分析报告 ({self.market_type.value}市场)', fontsize=16)
            
            # 1. 主力净流入TOP15柱状图
            top_stocks = self.analyzer.get_top_inflow_stocks(df, 15)
            if not top_stocks.empty:
                ax1 = axes[0, 0]
                colors = ['red' if x > 0 else 'green' for x in top_stocks['主力净流入']]
                ax1.bar(range(len(top_stocks)), top_stocks['主力净流入'], color=colors)
                ax1.set_xticks(range(len(top_stocks)))
                ax1.set_xticklabels(top_stocks['股票名称'], rotation=45, ha='right')
                ax1.set_title('主力净流入TOP15')
                ax1.set_ylabel('净流入金额(万元)')
                ax1.grid(True, alpha=0.3)
            
            # 2. 涨跌幅与资金流入散点图
            if not df.empty and '涨跌幅' in df.columns and '主力净流入' in df.columns:
                ax2 = axes[0, 1]
                scatter = ax2.scatter(df['涨跌幅'],
                                     df['主力净流入'],
                                     c=df['主力净流入'],
                                     cmap='RdYlGn',
                                     alpha=0.6,
                                     s=30)
                ax2.set_xlabel('涨跌幅(%)')
                ax2.set_ylabel('主力净流入(万元)')
                ax2.set_title('涨跌幅与主力净流入关系')
                ax2.grid(True, alpha=0.3)
                plt.colorbar(scatter, ax=ax2)
            
            # 3. 资金流入占比分布
            if not df.empty and '主力净流入占比' in df.columns:
                ax3 = axes[1, 0]
                valid_data = df['主力净流入占比'].dropna()
                if not valid_data.empty:
                    ax3.hist(valid_data, bins=30, alpha=0.7, color='blue', edgecolor='black')
                    ax3.set_xlabel('主力净流入占比(%)')
                    ax3.set_ylabel('股票数量')
                    ax3.set_title('主力净流入占比分布')
                    ax3.grid(True, alpha=0.3)
            
            # 4. 市场情绪指标
            ax4 = axes[1, 1]
            sentiment = self.analyzer.calculate_market_sentiment(df)
            if sentiment:
                labels = ['流入股票', '流出股票']
                sizes = [sentiment['主力净流入股票数'], sentiment['主力净流出股票数']]
                colors = ['red', 'green']
                ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax4.set_title('资金流向分布')
            
            plt.tight_layout()
            
            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_path = os.path.join(self.scraper.output_dir, f'analysis_chart_{timestamp}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"分析图表已保存到: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"生成分析图表时发生错误: {e}")
            return ""
    
    def start(self, interval: int = 10) -> None:
        """启动个股资金流向监控器"""
        if self.is_running:
            logger.warning("个股资金流向监控器已在运行中，无法重复启动")
            return
            
        self.interval = interval
        self.is_running = True
        
        # 创建并启动监控线程
        self.thread = threading.Thread(
            target=self._run,
            name="StockCapitalFlowMonitorThread",
            daemon=True
        )
        self.thread.start()
        
        logger.info(f"个股资金流向监控器已启动，数据更新间隔: {interval}秒")
        
    def stop(self) -> None:
        """停止个股资金流向监控器"""
        if not self.is_running:
            logger.info("个股资金流向监控器未在运行")
            return
            
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("监控线程在5秒内未能正常结束")
            else:
                logger.info("监控线程已正常结束")
        
        self.thread = None
        logger.info("个股资金流向监控器已停止")
        
    def _run(self) -> None:
        """监控器主循环（内部方法）"""
        logger.info("个股资金流向监控循环已开始")
        
        while self.is_running:
            try:
                # 获取个股资金流向数据
                df, filepath = self.scraper.run_once(max_pages=10, save_format='csv')
                
                if not df.empty:
                    # 更新最新数据
                    self.last_data = df
                    
                    # 调用回调函数
                    if self.callback:
                        try:
                            self.callback(df)
                        except Exception as e:
                            logger.error(f"回调函数执行出错: {e}")
                    
                    logger.debug(f"成功获取 {len(df)} 只股票的资金流向数据，保存到: {filepath}")
                else:
                    logger.warning("获取到的个股资金流向数据为空")
                        
                # 等待下次更新
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("监控器收到键盘中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"监控过程发生异常: {e}", exc_info=True)
                time.sleep(min(self.interval, 30))
        
        logger.info("个股资金流向监控循环已结束")
    
    def start_monitoring(self,
                        scrape_interval: int = 60,
                        display_interval: int = 30,
                        max_pages: int = 10,
                        save_format: str = 'csv'):
        """
        开始监控
        
        Args:
            scrape_interval (int): 数据爬取间隔(秒)
            display_interval (int): 显示更新间隔(秒)
            max_pages (int): 每次爬取的最大页数
            save_format (str): 保存格式
        """
        self.is_monitoring = True
        last_display_time = time.time()
        last_chart_time = time.time()
        
        print(f"开始监控{self.market_type.value}市场个股资金流向...")
        print(f"数据爬取间隔: {scrape_interval}秒")
        print(f"显示刷新间隔: {display_interval}秒")
        print(f"数据保存格式: {save_format}")
        print("按 Ctrl+C 停止监控\n")
        
        while self.is_monitoring:
            try:
                # 爬取数据
                df, filepath = self.scraper.run_once(max_pages=max_pages, save_format=save_format)
                
                if not df.empty:
                    logger.info(f"成功爬取数据，共 {len(df)} 条记录，保存到: {filepath}")
                
                # 更新显示
                current_time = time.time()
                if current_time - last_display_time >= display_interval:
                    self.display_realtime_data()
                    last_display_time = current_time
                
                # 每小时生成一次分析图表
                if current_time - last_chart_time >= 3600:  # 3600秒 = 1小时
                    if not df.empty:
                        chart_path = self.generate_analysis_charts(df)
                        if chart_path:
                            logger.info(f"已生成分析图表: {chart_path}")
                    last_chart_time = current_time
                
                time.sleep(scrape_interval)
                
            except KeyboardInterrupt:
                print("\n停止监控...")
                self.stop_monitoring()
                break
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                time.sleep(scrape_interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.scraper.stop()
        logger.info("个股资金流向监控已停止")


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