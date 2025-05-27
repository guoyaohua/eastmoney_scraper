"""
东方财富爬虫包版本信息模块
EastMoney Scraper Version Information Module

本模块定义了包的版本号、作者信息、描述信息等基本元数据。
这些信息被setup.py和__init__.py等模块引用，确保版本信息的一致性。

This module defines basic metadata such as package version number, author information,
and description. This information is referenced by setup.py and __init__.py to ensure
version information consistency.

版本更新历史 (Version Update History):
- v1.2.0: 优化代码结构，完善中文注释，增强API功能
- v1.1.0: 改进错误处理和日志记录，提升性能和稳定性
- v1.0.0: 初始版本发布，支持概念板块和个股数据爬取
"""

# 版本号 - 保持与setup.py一致 (Version number - keep consistent with setup.py)
__version__ = "1.2.0"

# 作者信息 (Author information)
__author__ = "Yaohua Guo"
__email__ = "guo.yaohua@foxmail.com"

# 包描述信息 (Package description)
__description__ = "东方财富数据爬虫包 - 提供概念板块和个股资金流向数据爬取与监控功能"
__description_en__ = "EastMoney data scraper package - provides concept sector and individual stock capital flow data scraping and monitoring"

# 项目链接 (Project links)
__url__ = "https://github.com/guoyaohua/eastmoney-scraper"
__license__ = "MIT"

# 包的关键字 (Package keywords)
__keywords__ = [
    # 中文关键词 (Chinese keywords)
    "东方财富", "数据爬虫", "股票", "资金流向", "概念板块",
    "实时监控", "投资分析", "金融数据", "量化交易",
    
    # 英文关键词 (English keywords)
    "eastmoney", "scraper", "stocks", "capital-flow", "concept-sector",
    "real-time", "monitoring", "investment", "analysis", "financial-data", "quantitative"
]

# 更新日志 (Changelog)
__changelog__ = {
    "1.2.0": [
        "优化代码结构和API设计",
        "添加详细的中文注释和文档",
        "完善数据分析和筛选功能",
        "增强错误处理和日志记录",
        "统一命名规范和代码风格"
    ],
    "1.1.0": [
        "改进错误处理和日志记录",
        "提升性能和稳定性",
        "完善文档和示例代码"
    ],
    "1.0.0": [
        "初始版本发布",
        "支持概念板块数据爬取",
        "支持个股资金流向爬取",
        "提供实时监控功能"
    ]
}