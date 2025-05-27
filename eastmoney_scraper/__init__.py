"""
东方财富数据爬虫包
EastMoney Scraper Package

提供东方财富网概念板块和个股资金流向数据的爬取与监控功能。
包含实时数据获取、历史数据分析、资金流向追踪等核心功能。

Provides scraping and monitoring functionality for EastMoney concept sector 
and individual stock capital flow data. Includes real-time data fetching, 
historical data analysis, and capital flow tracking features.

主要功能 (Main Features):
- 概念板块数据爬取与监控 (Concept sector data scraping and monitoring)
- 个股资金流向数据获取 (Individual stock capital flow data fetching)
- 实时数据更新与回调通知 (Real-time data updates with callback notifications)
- 多种数据存储格式支持 (Multiple data storage format support)
- 并行数据获取与处理 (Parallel data fetching and processing)
"""

# 从版本模块导入版本信息 (Import version info from version module)
from .version import (
    __version__,
    __author__, 
    __email__,
    __description__,
    __url__,
    __license__
)

# 核心爬虫类导入 (Import core scraper classes)
from .concept_sector_scraper import ConceptSectorScraper  # 概念板块爬虫主类 (Main concept sector scraper class)
from .eastmoney_capital_flow_scraper import CapitalFlowScraper  # 个股资金流向爬虫主类 (Main individual stock capital flow scraper class)

# 从API模块导入用户友好的接口函数和监控器类 (Import user-friendly interface functions and monitor classes from API module)
from .api import (
    # 数据获取函数 (Data fetching functions)
    get_concept_sectors,          # 获取概念板块综合数据（行情+资金流向）(Get comprehensive concept sector data)
    get_concept_sectors_realtime, # 获取概念板块实时行情数据 (Get real-time concept sector quote data)
    get_concept_capital_flow,     # 获取概念板块指定周期资金流向数据 (Get concept sector capital flow data for specified period)
    get_stock_capital_flow,       # 获取个股资金流向排行数据 (Get individual stock capital flow ranking data)
    get_stock_to_concept_map,     # 获取个股到概念板块的映射关系 (Get stock-to-concept sector mapping)
    
    # 实时监控器类 (Real-time monitor classes)
    ConceptSectorMonitor,         # 概念板块实时数据监控器 (Concept sector real-time data monitor)
    StockCapitalFlowMonitor,      # 个股资金流向实时数据监控器 (Individual stock capital flow real-time data monitor)
    
    # 数据分析与筛选工具函数 (Data analysis and filtering utility functions)
    filter_sectors_by_change,     # 根据涨跌幅筛选板块数据 (Filter sector data by price change percentage)
    filter_sectors_by_capital,    # 根据资金流向筛选板块数据 (Filter sector data by capital flow)
    get_top_sectors               # 获取表现最佳的板块数据 (Get top-performing sector data)
)

# 定义包的公开API接口列表，用于 `from eastmoney_scraper import *` 导入
# (Define the package's public API interface list for `from eastmoney_scraper import *` imports)
__all__ = [
    # 核心爬虫类 (Core scraper classes)
    "ConceptSectorScraper",         # 概念板块数据爬虫主类 (Main class for concept sector data scraping)
    "CapitalFlowScraper",           # 个股资金流向数据爬虫主类 (Main class for individual stock capital flow data scraping)
    
    # 实时监控器类 (Real-time monitor classes)
    "ConceptSectorMonitor",         # 概念板块实时数据监控器类 (Class for monitoring real-time concept sector data)
    "StockCapitalFlowMonitor",      # 个股资金流向实时数据监控器类 (Class for monitoring real-time individual stock capital flow data)
    
    # 主要功能函数 (Main functional interfaces)
    "get_concept_sectors",          # 获取概念板块完整数据 (Get complete concept sector data)
    "get_concept_sectors_realtime", # 获取概念板块实时行情 (Get real-time quotes for concept sectors)
    "get_concept_capital_flow",     # 获取概念板块指定周期的资金流向 (Get capital flow for concept sectors for a specified period)
    "get_stock_capital_flow",       # 获取个股资金流向排行数据 (Get ranked data for individual stock capital flow)
    "get_stock_to_concept_map",     # 获取个股与其所属概念板块的映射关系 (Get mapping of stocks to their associated concept sectors)
    
    # 数据分析与筛选工具函数 (Data analysis and filtering utility functions)
    "filter_sectors_by_change",     # 根据涨跌幅筛选板块数据 (Filter sector data by price change percentage)
    "filter_sectors_by_capital",    # 根据资金流向筛选板块数据 (Filter sector data by capital flow)
    "get_top_sectors",              # 获取表现最佳（或最差）的板块 (Get top (or bottom) performing sectors)
]