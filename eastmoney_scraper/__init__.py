"""
EastMoney Scraper Package
东方财富数据爬虫包

提供东方财富网概念板块和个股资金流向数据的爬取功能
"""

from .concept_sector_scraper import ConceptSectorScraper
from .eastmoney_capital_flow_scraper import CapitalFlowScraper

# 主要接口
from .api import (
    get_concept_sectors,
    get_concept_sectors_realtime,
    get_concept_capital_flow,
    get_stock_capital_flow,
    ConceptSectorMonitor,
    StockCapitalFlowMonitor,
    filter_sectors_by_change,
    filter_sectors_by_capital,
    get_top_sectors
)

__version__ = "1.0.0"
__author__ = "Yaohua Guo"
__email__ = "guo.yaohua@foxmail.com"

__all__ = [
    # 类
    "ConceptSectorScraper",
    "CapitalFlowScraper",
    "ConceptSectorMonitor",
    "StockCapitalFlowMonitor",
    
    # 函数
    "get_concept_sectors",
    "get_concept_sectors_realtime",
    "get_concept_capital_flow",
    "get_stock_capital_flow",
    
    # 工具函数
    "filter_sectors_by_change",
    "filter_sectors_by_capital",
    "get_top_sectors",
]