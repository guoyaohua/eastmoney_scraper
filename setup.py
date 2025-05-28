"""
东方财富数据爬虫包安装配置

本文件配置了eastmoney_scraper包的安装参数，包括：
- 基本包信息和依赖
- 入口点和命令行工具
- 分类器和兼容性信息
- 可选依赖和开发工具
"""

import os
from setuptools import setup, find_packages

# 读取版本信息从version.py文件
def get_version():
    """从version.py文件获取版本信息"""
    version_file = os.path.join(os.path.dirname(__file__), 'eastmoney_scraper', 'version.py')
    version_info = {}
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            exec(f.read(), version_info)
        return version_info
    except Exception:
        # 如果读取失败，使用默认值
        return {
            '__version__': '1.3.0',
            '__author__': 'Yaohua Guo',
            '__email__': 'guo.yaohua@foxmail.com',
            '__description__': '东方财富数据爬虫包',
            '__url__': 'https://github.com/guoyaohua/eastmoney-scraper',
            '__license__': 'MIT'
        }

# 读取README文件作为长描述
def get_long_description():
    """获取长描述文本"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "东方财富数据爬虫包 - 提供概念板块和个股资金流向数据爬取功能"

# 获取版本信息
version_info = get_version()
long_description = get_long_description()

setup(
    # 基本包信息
    name="eastmoney-scraper",
    version=version_info['__version__'],
    author=version_info['__author__'],
    author_email=version_info['__email__'],
    description=version_info['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=version_info['__url__'],
    license=version_info['__license__'],
    
    # 包发现和包含
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    include_package_data=True,
    
    # PyPI分类器
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Environment :: Console",
    ],
    
    # Python版本要求
    python_requires=">=3.7",
    
    # 核心依赖
    install_requires=[
        "requests>=2.28.0",      # HTTP请求库，用于API调用
        "pandas>=1.5.0",         # 数据处理和分析
        "numpy>=1.23.0",         # 数值计算支持
    ],
    
    # 可选依赖
    extras_require={
        # 开发依赖
        "dev": [
            "pytest>=6.0.0",        # 测试框架
            "pytest-cov>=2.0.0",    # 测试覆盖率
            "black>=21.0.0",         # 代码格式化
            "flake8>=3.9.0",         # 代码质量检查
            "mypy>=0.900",           # 类型检查
        ],
        
        # 可视化依赖
        "visualization": [
            "matplotlib>=3.5.0",    # 基础绘图
            "seaborn>=0.12.0",       # 统计绘图
            "plotly>=5.0.0",         # 交互式图表
        ],
        
        # 数据存储依赖
        "storage": [
            "openpyxl>=3.0.0",       # Excel文件支持
            "xlsxwriter>=3.0.0",     # Excel写入优化
            "sqlalchemy>=1.4.0",     # 数据库抽象层
        ],
        
        # 调度和监控依赖
        "scheduling": [
            "schedule>=1.1.0",       # 任务调度
            "apscheduler>=3.9.0",    # 高级调度器
        ],
        
        # 完整安装（所有可选依赖）
        "full": [
            "matplotlib>=3.5.0",
            "seaborn>=0.12.0",
            "plotly>=5.0.0",
            "openpyxl>=3.0.0",
            "xlsxwriter>=3.0.0",
            "sqlalchemy>=1.4.0",
            "schedule>=1.1.0",
            "apscheduler>=3.9.0",
        ],
    },
    
    # 包数据
    package_data={
        'eastmoney_scraper': [
            '*.json',
            '*.yaml',
            '*.yml',
        ],
    },
    
    # 入口点（暂时注释掉，因为CLI模块不存在）
    # entry_points={
    #     "console_scripts": [
    #         "eastmoney-concept=eastmoney_scraper.cli:run_concept_scraper",
    #         "eastmoney-stock=eastmoney_scraper.cli:run_stock_scraper",
    #         "eastmoney-monitor=eastmoney_scraper.cli:run_monitor",
    #     ],
    # },
    
    # 项目URLs
    project_urls={
        "Documentation": "https://github.com/guoyaohua/eastmoney-scraper#readme",
        "Bug Reports": "https://github.com/guoyaohua/eastmoney-scraper/issues",
        "Feature Requests": "https://github.com/guoyaohua/eastmoney-scraper/issues",
        "Source Code": "https://github.com/guoyaohua/eastmoney-scraper",
        "Download": "https://github.com/guoyaohua/eastmoney-scraper/releases",
    },
    
    # 关键词
    keywords=[
        "eastmoney", "scraper", "financial", "stock", "capital-flow",
        "concept-sector", "investment", "trading", "market-data",
        "东方财富", "数据爬虫", "股票", "资金流向", "概念板块"
    ],
    
    # Zip安全
    zip_safe=False,
)