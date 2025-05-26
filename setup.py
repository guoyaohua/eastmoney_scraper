"""
EastMoney Scraper Package Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eastmoney-scraper",
    version="1.0.0",
    author="Yaohua Guo",
    author_email="guo.yaohua@example.com",
    description="东方财富数据爬虫包 - 提供概念板块和个股资金流向数据",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guoyaohua/eastmoney-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "eastmoney-concept=eastmoney_scraper.cli:run_concept_scraper",
            "eastmoney-stock=eastmoney_scraper.cli:run_stock_scraper",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/guoyaohua/eastmoney-scraper/issues",
        "Source": "https://github.com/guoyaohua/eastmoney-scraper",
    },
)