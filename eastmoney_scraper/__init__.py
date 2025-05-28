"""
东方财富数据爬虫包

提供东方财富网概念板块、行业板块和个股资金流向数据的爬取与监控功能。
包含实时数据获取、历史数据分析、资金流向追踪等核心功能。

主要功能:
- 概念板块和行业板块数据爬取与监控
- 个股资金流向数据获取
- 实时数据更新与回调通知
- 多种数据存储格式支持
- 并行数据获取与处理
- 板块成分股映射关系获取
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
from .concept_sector_scraper import ConceptSectorScraper  # 概念板块爬虫主类
from .sector_scraper import SectorScraper, SectorType  # 通用板块爬虫主类和类型枚举
from .eastmoney_capital_flow_scraper import CapitalFlowScraper  # 个股资金流向爬虫主类

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
    
    # 实时监控器类
    ConceptSectorMonitor,         # 概念板块实时数据监控器
    StockCapitalFlowMonitor,      # 个股资金流向实时数据监控器
    
    # 数据分析与筛选工具函数
    filter_sectors_by_change,     # 根据涨跌幅筛选板块数据
    filter_sectors_by_capital,    # 根据资金流向筛选板块数据
    get_top_sectors               # 获取表现最佳的板块数据
)

# 定义包的公开API接口列表，用于 `from eastmoney_scraper import *` 导入
__all__ = [
    # 核心爬虫类
    "ConceptSectorScraper",         # 概念板块数据爬虫主类
    "SectorScraper",                # 通用板块数据爬虫主类
    "SectorType",                   # 板块类型枚举
    "CapitalFlowScraper",           # 个股资金流向数据爬虫主类
    
    # 实时监控器类
    "ConceptSectorMonitor",         # 概念板块实时数据监控器类
    "StockCapitalFlowMonitor",      # 个股资金流向实时数据监控器类
    
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
    
    # 数据分析与筛选工具函数
    "filter_sectors_by_change",     # 根据涨跌幅筛选板块数据
    "filter_sectors_by_capital",    # 根据资金流向筛选板块数据
    "get_top_sectors",              # 获取表现最佳（或最差）的板块
]