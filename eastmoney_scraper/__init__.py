"""
东方财富数据爬虫包

提供东方财富网概念板块、行业板块、个股资金流向、K线历史数据和股票列表的爬取与监控功能。
包含实时数据获取、历史数据分析、资金流向追踪、技术分析、市场统计等核心功能。

主要功能:
- 概念板块和行业板块数据爬取与监控
- 个股资金流向数据获取与分析
- 个股K线历史数据获取（支持多周期、多复权类型）
- 全市场股票列表获取（支持按市场类型筛选）
- 实时数据更新与回调通知
- 多种数据存储格式支持
- 高性能并行数据获取与处理
- 板块成分股映射关系获取
- 技术指标计算与数据分析
- 股票搜索与市场统计分析
"""

# 从版本模块导入版本信息
from .version import (
    __version__,
    __author__,
    __email__,
    __description__,
    __url__,
    __license__
)

# 核心爬虫类导入
from .sector_scraper import SectorScraper, SectorType  # 通用板块爬虫主类和类型枚举
from .stock_capital_flow_scraper import StockCapitalFlowScraper, MarketType  # 个股资金流向爬虫主类
from .stock_kline_scraper import StockKlineScraper, KlinePeriod, AdjustType  # 个股K线历史数据爬虫主类
from .stock_list_scraper import StockListScraper, StockMarket  # 股票列表数据爬虫主类

# 从API模块导入用户友好的接口函数和监控器类
from .api import (
    # 数据获取函数
    get_concept_sectors,          # 获取概念板块综合数据（行情+资金流向）
    get_concept_sectors_realtime, # 获取概念板块实时行情数据
    get_concept_capital_flow,     # 获取概念板块指定周期资金流向数据
    get_stock_capital_flow,       # 获取个股资金流向排行数据
    get_stock_to_concept_map,     # 获取个股到概念板块的映射关系
    
    # 通用板块数据获取函数
    get_sectors,                  # 获取板块综合数据（支持概念板块和行业板块）
    get_industry_sectors,         # 获取行业板块综合数据
    get_stock_to_sector_mapping,  # 获取个股到板块的映射关系（支持概念和行业板块）
    
    # K线数据获取函数
    get_stock_kline,              # 获取单只股票K线数据
    get_multiple_stocks_kline,    # 批量获取多只股票K线数据
    analyze_kline_data,           # 分析K线数据
    
    # 股票列表数据获取函数
    get_all_stock_codes,          # 获取所有股票代码
    get_stock_list,               # 获取股票列表完整数据
    get_stock_basic_info,         # 获取股票基本信息
    search_stocks,                # 搜索股票
    get_market_overview,          # 获取市场概况统计
    
    # 实时监控器类
    SectorMonitor,                # 板块实时数据监控器基类（支持概念和行业板块）
    ConceptSectorMonitor,         # 概念板块实时数据监控器
    IndustrySectorMonitor,        # 行业板块实时数据监控器
    StockCapitalFlowMonitor,      # 个股资金流向实时数据监控器
    StockCapitalFlowAnalyzer,     # 个股资金流向数据分析器
    StockKlineMonitor,            # 个股K线数据监控器
    
    # 数据分析与筛选工具函数
    filter_sectors_by_change,     # 根据涨跌幅筛选板块数据
    filter_sectors_by_capital,    # 根据资金流向筛选板块数据
    get_top_sectors,              # 获取表现最佳的板块数据
    filter_stocks_by_price_change, # 根据价格变化筛选股票
    get_top_performing_stocks,    # 获取表现最佳的股票
    filter_stocks_by_market_cap,  # 根据市值筛选股票
    get_top_stocks_by_metric      # 按指标获取排名前N的股票
)

# 定义包的公开API接口列表，用于 `from eastmoney_scraper import *` 导入
__all__ = [
    # 核心爬虫类
    "SectorScraper",                # 通用板块数据爬虫主类
    "SectorType",                   # 板块类型枚举
    "StockCapitalFlowScraper",      # 个股资金流向数据爬虫主类
    "MarketType",                   # 市场类型枚举
    "StockKlineScraper",            # 个股K线历史数据爬虫主类
    "KlinePeriod",                  # K线周期枚举
    "AdjustType",                   # 复权类型枚举
    "StockListScraper",             # 股票列表数据爬虫主类
    "StockMarket",                  # 股票市场类型枚举
    
    # 实时监控器类和分析器类
    "SectorMonitor",                # 板块实时数据监控器基类（支持概念和行业板块）
    "ConceptSectorMonitor",         # 概念板块实时数据监控器类
    "IndustrySectorMonitor",        # 行业板块实时数据监控器类
    "StockCapitalFlowMonitor",      # 个股资金流向实时数据监控器类
    "StockCapitalFlowAnalyzer",     # 个股资金流向数据分析器类
    "StockKlineMonitor",            # 个股K线数据监控器类
    
    # 主要功能函数
    "get_concept_sectors",          # 获取概念板块完整数据
    "get_concept_sectors_realtime", # 获取概念板块实时行情
    "get_concept_capital_flow",     # 获取概念板块指定周期的资金流向
    "get_stock_capital_flow",       # 获取个股资金流向排行数据
    "get_stock_to_concept_map",     # 获取个股与其所属概念板块的映射关系
    
    # 通用板块功能函数
    "get_sectors",                  # 获取板块综合数据（支持概念板块和行业板块）
    "get_industry_sectors",         # 获取行业板块综合数据
    "get_stock_to_sector_mapping",  # 获取个股到板块的映射关系（支持概念和行业板块）
    
    # K线数据功能函数
    "get_stock_kline",              # 获取单只股票K线数据
    "get_multiple_stocks_kline",    # 批量获取多只股票K线数据
    "analyze_kline_data",           # 分析K线数据
    
    # 股票列表数据功能函数
    "get_all_stock_codes",          # 获取所有股票代码
    "get_stock_list",               # 获取股票列表完整数据
    "get_stock_basic_info",         # 获取股票基本信息
    "search_stocks",                # 搜索股票
    "get_market_overview",          # 获取市场概况统计
    
    # 数据分析与筛选工具函数
    "filter_sectors_by_change",     # 根据涨跌幅筛选板块数据
    "filter_sectors_by_capital",    # 根据资金流向筛选板块数据
    "get_top_sectors",              # 获取表现最佳（或最差）的板块
    "filter_stocks_by_price_change", # 根据价格变化筛选股票
    "get_top_performing_stocks",    # 获取表现最佳的股票
    "filter_stocks_by_market_cap",  # 根据市值筛选股票
    "get_top_stocks_by_metric",     # 按指标获取排名前N的股票
]