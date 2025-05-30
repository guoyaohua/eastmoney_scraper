# 🎯 EastMoney Scraper - 东方财富数据爬虫

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.7.0-orange.svg)](https://github.com/guoyaohua/eastmoney-scraper)
[![Code Quality](https://img.shields.io/badge/code%20quality-optimized-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)]()

一个功能强大、高度优化的东方财富网数据爬虫包，提供概念板块、行业板块、个股资金流向、K线历史数据和股票列表的爬取、监控与智能分析功能。

## ✨ 核心特性

- 🚀 **板块数据**：支持概念板块和行业板块，实时行情、多周期资金流向分析（今日/5日/10日）
- 💰 **个股资金流向**：主力、超大单、大单、中单、小单资金流向追踪，支持多市场（全市场/创业板/科创板/主板）
- 📈 **K线历史数据**：支持多周期K线（日/周/月/分钟线），多复权类型（前复权/后复权/不复权）
- 📊 **股票列表获取**：全市场股票代码和基本信息，支持按市场类型筛选和搜索
- ⚡ **高性能设计**：支持并行爬取，智能分页，自动重试机制，智能缓存
- 📡 **实时监控**：内置监控器，支持定时更新和自定义回调通知
- 🔧 **简洁API**：提供函数式和面向对象两种编程接口
- 💾 **统一存储**：所有数据统一保存到output目录，支持CSV、JSON等格式
- 🔍 **智能分析**：内置数据筛选、排序、统计分析和图表生成功能
- 📊 **可视化友好**：与matplotlib、seaborn等可视化库完美集成

## 🆕 v1.7.0 重大更新

### 核心架构升级
- 🏗️ **板块监控重构** - 全新的模块化监控架构设计
- 🔄 **统一监控接口** - 支持概念板块和行业板块的统一接口
- 🎯 **专业监控器** - 提供专门的概念板块和行业板块监控器
- 🛠️ **灵活扩展性** - 支持自定义回调和数据处理

### 监控功能增强
- 📊 **实时数据更新** - 支持自定义更新间隔和数据处理
- 🔔 **智能通知** - 支持自定义回调函数处理数据更新
- 📈 **数据分析** - 内置市场趋势和板块表现分析
- 🎨 **可视化** - 支持实时数据可视化展示

## v1.6.0 更新

### 核心功能扩展
- 🆕 **股票列表获取** - 全市场股票代码和基本信息，支持市场筛选和搜索
- 🆕 **市场统计分析** - 完整的市场概况和统计分析功能
- 🆕 **智能搜索功能** - 支持按股票名称、代码等关键词搜索
- 🆕 **数据分析增强** - 新增市值筛选、表现排名等分析工具

### 数据覆盖
- 📊 **股票列表**：沪市主板、深市主板、创业板、科创板、北交所
- 🔍 **智能缓存**：支持数据缓存机制，提升获取效率
- 📈 **数据筛选**：支持按市场类型、市值等条件筛选股票
- 🛠️ **API扩展**：新增get_all_stock_codes、search_stocks等接口

### 向后兼容
- ✅ 主要API接口保持不变
- ✅ 现有代码无需修改即可使用
- ✅ 自动适配新的输出目录结构
- ✅ 新增功能不影响原有功能

## 📦 安装

### 基础安装

```bash
pip install eastmoney-scraper
```

### 带可选依赖安装

```bash
# 完整功能安装（推荐）
pip install eastmoney-scraper[full]

# 仅可视化功能
pip install eastmoney-scraper[visualization]

# 仅存储功能
pip install eastmoney-scraper[storage]

# 仅调度功能
pip install eastmoney-scraper[scheduling]

# 开发环境安装
pip install eastmoney-scraper[dev]
```

### 从源码安装

```bash
git clone https://github.com/guoyaohua/eastmoney-scraper.git
cd eastmoney-scraper
pip install -e .[dev]
```

## 🚀 快速开始

### 1️⃣ K线历史数据获取（新功能⭐）

```python
from eastmoney_scraper import get_stock_kline, get_multiple_stocks_kline

# 获取单只股票日K线数据
df = get_stock_kline('000001', period='daily', limit=100)
print(f"获取到平安银行 {len(df)} 条K线数据")
print(df[['日期', '开盘价', '收盘价', '涨跌幅']].head())

# 获取多周期K线数据
weekly_df = get_stock_kline('600000', period='weekly', limit=50)
minute_df = get_stock_kline('000858', period='min_60', limit=200)

# 批量获取多只股票K线数据
stock_codes = ['000001', '600000', '000858', '002415']
data_dict = get_multiple_stocks_kline(stock_codes, save_to_file=True)
print(f"批量获取 {len(data_dict)} 只股票的K线数据")

# K线数据技术分析
from eastmoney_scraper import analyze_kline_data
analysis = analyze_kline_data(df)
print(f"价格区间: {analysis['price_min']} - {analysis['price_max']}")
print(f"平均涨跌幅: {analysis['avg_change']}%")
```

### 2️⃣ 股票列表获取（新功能⭐）

```python
from eastmoney_scraper import get_all_stock_codes, get_stock_list, search_stocks

# 获取所有股票代码
all_codes = get_all_stock_codes()
print(f"全市场共 {len(all_codes)} 只股票")

# 获取创业板股票代码
chinext_codes = get_all_stock_codes(market='chinext')
print(f"创业板共 {len(chinext_codes)} 只股票")

# 获取股票完整信息
df = get_stock_list()
print(df[['股票代码', '股票名称', '最新价', '总市值']].head(10))

# 搜索银行股
bank_stocks = search_stocks('银行')
print(f"找到 {len(bank_stocks)} 只银行股")

# 市场概况统计
from eastmoney_scraper import get_market_overview
overview = get_market_overview()
print(f"市场总股票数: {overview['总股票数']}")
print(f"平均股价: {overview['平均股价']:.2f}元")
```
### 3️⃣ 个股资金流向数据

```python
from eastmoney_scraper import StockCapitalFlowScraper, MarketType

# 创建爬虫实例（全市场）
scraper = StockCapitalFlowScraper(market_type=MarketType.ALL)

# 执行一次爬取，获取前5页数据，保存为CSV
df, filepath = scraper.run_once(max_pages=5, save_format='csv')

print(f"✅ 成功爬取 {len(df)} 条数据")
print(f"📁 数据已保存到: {filepath}")

# 显示市场概况
summary = scraper.analyze_market_summary(df)
for key, value in summary.items():
    print(f"{key}: {value}")

# 显示主力净流入前10名
top_inflow = scraper.get_top_inflow_stocks(df, 10)
print("🔥 主力净流入前10名:")
print(top_inflow[['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入']])

# 不同市场的数据
gem_scraper = StockCapitalFlowScraper(market_type=MarketType.GEM)  # 创业板
star_scraper = StockCapitalFlowScraper(market_type=MarketType.STAR)  # 科创板
main_scraper = StockCapitalFlowScraper(market_type=MarketType.MAIN_BOARD)  # 主板
```

### 4️⃣ 概念板块数据获取

```python
from eastmoney_scraper import get_concept_sectors, get_sectors, SectorType

# 获取完整概念板块数据（行情+资金流向）
df = get_concept_sectors()
print(df[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']].head(10))

# 仅获取实时行情（更快）
from eastmoney_scraper import get_concept_sectors_realtime
df_quotes = get_concept_sectors_realtime()
print(f"获取到 {len(df_quotes)} 个板块的实时行情")

# 🆕 获取行业板块数据（新功能）
from eastmoney_scraper import get_industry_sectors

df_industry = get_industry_sectors(save_to_file=True)
print(f"获取到 {len(df_industry)} 个行业板块")
print(df_industry[['板块名称', '涨跌幅', '主力净流入']].head())

# 🆕 获取板块成分股映射（新功能）
from eastmoney_scraper import get_stock_to_sector_mapping

# 获取股票到概念板块的映射
concept_mapping = get_stock_to_sector_mapping("concept", save_to_file=True)
print(f"获取到 {len(concept_mapping)} 只股票的概念板块映射")

# 获取股票到行业板块的映射
industry_mapping = get_stock_to_sector_mapping(SectorType.INDUSTRY)
print(f"获取到 {len(industry_mapping)} 只股票的行业板块映射")

# 🆕 获取板块成分股（新功能）
from eastmoney_scraper import get_sector_stocks

# 获取"人工智能"概念板块的成分股
ai_stocks = get_sector_stocks('BK0800', sector_type='concept')
print(f"人工智能板块包含 {len(ai_stocks)} 只成分股")
print(ai_stocks[['股票代码', '股票名称', '涨跌幅', '最新价']].head())

# 🆕 获取板块历史走势（新功能）
from eastmoney_scraper import get_sector_history

# 获取板块近30天历史数据
history_df = get_sector_history('BK0800', days=30)
print(f"获取到 {len(history_df)} 天的历史数据")
print(history_df[['日期', '收盘价', '涨跌幅', '成交额']].tail())

# 🆕 获取板块实时资金流向（新功能）
from eastmoney_scraper import get_sector_capital_flow_realtime

# 获取板块实时资金流向明细
flow_df = get_sector_capital_flow_realtime('BK0800')
print("板块资金流向：")
print(f"主力净流入: {flow_df['主力净流入']}万元")
print(f"散户净流入: {flow_df['散户净流入']}万元")

# 🆕 板块对比分析（新功能）
from eastmoney_scraper import compare_sectors

# 对比多个板块表现
sectors_to_compare = ['BK0800', 'BK0493', 'BK1037']  # AI、新能源、芯片
comparison_df = compare_sectors(sectors_to_compare)
print("板块对比分析：")
print(comparison_df[['板块名称', '涨跌幅', '5日涨幅', '主力净流入']])

# 🆕 获取板块资金流向历史（新功能）
from eastmoney_scraper import get_sector_capital_flow_history

# 获取板块近5日资金流向
flow_history = get_sector_capital_flow_history('BK0800', days=5)
print("近5日资金流向：")
for _, row in flow_history.iterrows():
    print(f"{row['日期']}: 主力净流入 {row['主力净流入']:.2f}万元")
```

### 5️⃣ 板块实时监控（v1.7.0新架构）

```python
from eastmoney_scraper import SectorMonitor, ConceptSectorMonitor, IndustrySectorMonitor

# 🆕 使用基类SectorMonitor灵活监控（支持概念/行业板块）
monitor = SectorMonitor(sector_type="concept")  # 或 "industry"

# 🆕 使用专门的概念板块监控器
concept_monitor = ConceptSectorMonitor()

# 🆕 使用专门的行业板块监控器
industry_monitor = IndustrySectorMonitor()

# 设置数据更新回调
def on_sector_update(df):
    print(f"板块数据更新：{len(df)} 个板块")
    # 显示涨幅前5的板块
    top5 = df.nlargest(5, '涨跌幅')
    for _, sector in top5.iterrows():
        print(f"{sector['板块名称']}: {sector['涨跌幅']:+.2f}%")

# 启动监控
monitor.set_callback(on_sector_update)
monitor.start(interval=30)  # 每30秒更新一次

# 获取最新数据
latest_data = monitor.get_latest_data()

# 记得停止监控
monitor.stop()
```

### 6️⃣ 个股资金流向监控与分析

```python
from eastmoney_scraper import StockCapitalFlowMonitor, StockCapitalFlowAnalyzer, MarketType

# 创建增强的监控器
monitor = StockCapitalFlowMonitor(market_type=MarketType.ALL)

# 🆕 创建数据分析器
analyzer = StockCapitalFlowAnalyzer()

# 数据更新回调函数
def on_data_update(df):
    print(f"📊 数据更新：{len(df)} 只股票")
    
    # 计算市场情绪
    sentiment = analyzer.calculate_market_sentiment(df)
    print(f"📈 市场情绪：{sentiment}")
    
    # 获取热门股票
    top_stocks = analyzer.get_top_inflow_stocks(df, 5)
    print("🔥 资金流入TOP5:")
    for _, stock in top_stocks.iterrows():
        print(f"  {stock['股票名称']}: {stock['主力净流入']:.2f}万元")

# 设置回调并启动监控
monitor.set_callback(on_data_update)
monitor.start(interval=30)  # 每30秒更新

# 或使用高级监控功能
monitor.start_monitoring(
    scrape_interval=60,      # 数据爬取间隔60秒
    display_interval=30,     # 显示更新间隔30秒
    max_pages=5,             # 每次爬取5页数据
    save_format='csv'        # 保存为CSV格式
)
```

### 6️⃣ 数据分析与筛选

```python
from eastmoney_scraper import (
    get_concept_sectors, 
    filter_sectors_by_change, 
    get_top_sectors,
    StockCapitalFlowAnalyzer
)

# 获取数据
df = get_concept_sectors()

# 筛选强势板块（涨幅>3%）
strong_sectors = filter_sectors_by_change(df, min_change=3.0)
print(f"💪 强势板块：{len(strong_sectors)} 个")

# 获取主力资金流入前10的板块
top_inflow = get_top_sectors(df, n=10, by='主力净流入', ascending=False)
print("💰 资金流入排行：")
print(top_inflow[['板块名称', '涨跌幅', '主力净流入']].to_string(index=False))

# 🆕 使用分析器进行深度分析
analyzer = StockCapitalFlowAnalyzer()

# 加载最新数据
latest_data = analyzer.load_latest_data()
if not latest_data.empty:
    # 分析连续流入的股票
    historical_data = analyzer.load_historical_data(days=3)
    continuous_inflow = analyzer.analyze_continuous_inflow_stocks(historical_data, days=3)
    print(f"🎯 连续3日流入股票：{len(continuous_inflow)} 只")
    
    # 生成分析图表
    scraper = StockCapitalFlowScraper(market_type=MarketType.ALL)
    chart_path = monitor.generate_analysis_charts(latest_data)
    print(f"📊 分析图表已保存：{chart_path}")
```

## 📚 详细文档

### 🏗️ 项目结构（v1.7.0）

```
eastmoney-scraper/
├── 📁 eastmoney_scraper/          # 核心包目录
│   ├── 📄 __init__.py             # 包初始化和API导出
│   ├── 📄 version.py              # 版本信息
│   ├── 📄 api.py                  # 用户友好的API接口
│   ├── 📄 sector_scraper.py       # 🆕 重构后的板块爬虫（概念+行业）
│   ├── 📄 stock_capital_flow_scraper.py  # 个股资金流向爬虫
│   ├── 📄 stock_kline_scraper.py  # K线历史数据爬虫
│   └── 📄 stock_list_scraper.py   # 股票列表数据爬虫
├── 📁 tests/                      # 测试套件
│   ├── 📄 test_sector_monitor.py  # 🆕 板块监控测试
│   ├── 📄 test_stock_capital_flow_scraper.py  # 资金流向测试
│   ├── 📄 test_stock_kline_scraper.py         # K线数据测试
│   └── 📄 test_stock_list_scraper.py          # 股票列表测试
├── 📁 examples/                   # 使用示例
│   ├── 📄 monitor_usage.py        # 🆕 板块监控示例
│   ├── 📄 stock_capital_flow_usage.py  # 个股资金流向示例
│   ├── 📄 stock_kline_usage.py         # K线数据使用示例
│   └── 📄 stock_list_usage.py          # 股票列表使用示例
├── 📁 output/                     # 统一输出目录
│   ├── 📁 stock_capital_flow_data/     # 资金流向数据
│   ├── 📁 stock_kline_data/            # K线历史数据
│   ├── 📁 stock_list_data/             # 股票列表数据
│   ├── 📁 concept_sector_data/         # 概念板块数据
│   └── 📁 industry_sector_data/        # 行业板块数据
├── 📄 README.md                   # 项目文档
├── 📄 setup.py                    # 安装配置
└── 📄 requirements.txt            # 依赖清单
```

### 🔧 API 参考

#### 个股资金流向接口（核心功能）

| 类/函数 | 说明 | 主要参数 |
|---------|------|----------|
| `StockCapitalFlowScraper` | 个股资金流向爬虫 | `market_type`, `output_dir` |
| `StockCapitalFlowMonitor` | 🆕 增强监控器 | `market_type`, `output_dir` |
| `StockCapitalFlowAnalyzer` | 🆕 数据分析器 | `data_dir` |
| `get_stock_capital_flow()` | 获取个股资金流向排行 | `max_pages`, `save_to_file` |

#### K线数据接口（新增）

| 类/函数 | 说明 | 主要参数 |
|---------|------|----------|
| `StockKlineScraper` | 🆕 K线历史数据爬虫 | `output_dir` |
| `get_stock_kline()` | 🆕 获取单只股票K线数据 | `stock_code`, `period`, `limit`, `adjust_type` |
| `get_multiple_stocks_kline()` | 🆕 批量获取多只股票K线数据 | `stock_codes`, `save_to_file` |
| `analyze_kline_data()` | 🆕 K线数据技术分析 | `df` |
| `StockKlineMonitor` | 🆕 K线数据实时监控器 | `stock_codes`, `interval` |

#### 股票列表接口（新增）

| 类/函数 | 说明 | 主要参数 |
|---------|------|----------|
| `StockListScraper` | 🆕 股票列表数据爬虫 | `output_dir` |
| `get_all_stock_codes()` | 🆕 获取所有股票代码 | `market`, `use_cache` |
| `get_stock_list()` | 🆕 获取股票列表完整数据 | `market`, `save_to_file` |
| `get_stock_basic_info()` | 🆕 获取股票基本信息字典 | `market`, `use_cache` |
| `search_stocks()` | 🆕 搜索股票 | `keyword`, `market` |
| `get_market_overview()` | 🆕 获取市场概况统计 | `market`, `use_cache` |

#### 板块数据接口

| 函数/类 | 说明 | 主要参数 |
|---------|------|----------|
| `get_concept_sectors()` | 获取完整概念板块数据 | `include_capital_flow`, `periods`, `save_to_file` |
| `get_concept_sectors_realtime()` | 仅获取实时行情 | 无 |
| `get_industry_sectors()` | 🆕 获取行业板块数据 | `include_capital_flow`, `save_to_file` |
| `get_sectors()` | 🆕 通用板块数据获取 | `sector_type`, `include_capital_flow` |
| `get_stock_to_sector_mapping()` | 🆕 获取股票-板块映射 | `sector_type`, `save_to_file` |
| `get_sector_stocks()` | 🆕 获取板块成分股 | `sector_code`, `sector_type` |
| `get_sector_history()` | 🆕 获取板块历史走势 | `sector_code`, `days` |
| `get_sector_capital_flow_realtime()` | 🆕 获取板块实时资金流向 | `sector_code` |
| `get_sector_capital_flow_history()` | 🆕 获取板块资金流向历史 | `sector_code`, `days` |
| `compare_sectors()` | 🆕 板块对比分析 | `sector_codes`, `metrics` |

#### 板块监控接口（v1.7.0新架构）

| 类 | 说明 | 主要参数 |
|----|------|----------|
| `SectorMonitor` | 🆕 板块监控器基类（支持概念/行业） | `sector_type`, `output_dir` |
| `ConceptSectorMonitor` | 概念板块专用监控器 | `output_dir` |
| `IndustrySectorMonitor` | 🆕 行业板块专用监控器 | `output_dir` |

#### 数据分析工具

| 函数 | 说明 | 主要参数 |
|------|------|----------|
| `filter_sectors_by_change()` | 按涨跌幅筛选板块 | `min_change`, `max_change` |
| `filter_sectors_by_capital()` | 按资金流向筛选板块 | `min_capital`, `flow_type` |
| `get_top_sectors()` | 获取排名前N的板块 | `n`, `by`, `ascending` |

### 📊 数据字段说明

#### 个股资金流向数据字段

| 字段名 | 说明 | 单位 | 示例 |
|--------|------|------|------|
| 股票代码 | 6位股票代码 | - | `000001` |
| 股票名称 | 股票中文名称 | - | `平安银行` |
| 最新价 | 当前股价 | 元 | `12.34` |
| 涨跌幅 | 涨跌百分比 | % | `2.51` |
| 主力净流入 | 主力资金净流入 | 万元 | `5678` |
| 主力净流入占比 | 主力净流入占成交额比例 | % | `8.75` |
| 超大单净流入 | 超大单资金净流入 | 万元 | `3456` |
| 大单净流入 | 大单资金净流入 | 万元 | `2222` |
| 中单净流入 | 中单资金净流入 | 万元 | `-1111` |
| 小单净流入 | 小单资金净流入 | 万元 | `-4567` |

#### 概念板块数据字段

| 字段名 | 说明 | 单位 | 示例 |
|--------|------|------|------|
| 板块代码 | 板块唯一标识 | - | `BK0477` |
| 板块名称 | 板块中文名称 | - | `人工智能` |
| 涨跌幅 | 当日涨跌百分比 | % | `3.45` |
| 最新价 | 最新指数价格 | 点 | `1234.56` |
| 成交额 | 总成交金额 | 万元 | `1234567` |
| 主力净流入 | 主力资金净流入 | 万元 | `12345` |
| 5日主力净流入 | 5日累计主力净流入 | 万元 | `67890` |
| 10日主力净流入 | 10日累计主力净流入 | 万元 | `123456` |

#### K线历史数据字段（新增）

| 字段名 | 说明 | 单位 | 示例 |
|--------|------|------|------|
| 股票代码 | 6位股票代码 | - | `000001` |
| 日期 | 交易日期 | - | `2025-05-29` |
| 开盘价 | 开盘价格 | 元 | `12.34` |
| 收盘价 | 收盘价格 | 元 | `12.56` |
| 最高价 | 最高价格 | 元 | `12.78` |
| 最低价 | 最低价格 | 元 | `12.20` |
| 成交量(手) | 成交量 | 手 | `123456` |
| 成交额(万元) | 成交金额 | 万元 | `15432.1` |
| 振幅 | 价格振幅 | % | `4.71` |
| 涨跌幅 | 涨跌百分比 | % | `1.79` |
| 涨跌额 | 涨跌金额 | 元 | `0.22` |
| 换手率 | 换手率 | % | `0.89` |

#### 股票列表数据字段（新增）

| 字段名 | 说明 | 单位 | 示例 |
|--------|------|------|------|
| 股票代码 | 6位股票代码 | - | `000001` |
| 股票名称 | 股票中文名称 | - | `平安银行` |
| 市场类型 | 所属市场类型 | - | `深市主板` |
| 最新价 | 当前股价 | 元 | `12.34` |
| 涨跌幅 | 涨跌百分比 | % | `2.51` |
| 总市值 | 总市值 | 万元 | `1234567.89` |
| 流通市值 | 流通市值 | 万元 | `987654.32` |
| 市盈率 | 市盈率 | 倍 | `15.6` |
| 市净率 | 市净率 | 倍 | `1.2` |
| 换手率 | 换手率 | % | `0.89` |
| 成交量 | 成交量 | 手 | `123456` |
| 成交额 | 成交额 | 万元 | `15432.1` |

## 💡 高级用法

### 🆕 多市场数据对比分析

```python
from eastmoney_scraper import StockCapitalFlowScraper, MarketType
import pandas as pd

# 获取不同市场的数据
markets = {
    '全市场': MarketType.ALL,
    '创业板': MarketType.GEM,
    '科创板': MarketType.STAR,
    '主板': MarketType.MAIN_BOARD
}

market_data = {}
for name, market_type in markets.items():
    scraper = StockCapitalFlowScraper(market_type=market_type)
    df, _ = scraper.run_once(max_pages=2, save_format='csv')
    
    if not df.empty:
        summary = scraper.analyze_market_summary(df)
        market_data[name] = summary
        print(f"📊 {name}：{summary['总股票数']}只股票，"
              f"上涨{summary['上涨股票数']}只，"
              f"主力净流入{summary['市场主力净流入总额(万元)']/10000:.1f}亿")

# 对比不同市场表现
comparison_df = pd.DataFrame(market_data).T
print("\n🔍 市场对比分析：")
print(comparison_df[['总股票数', '上涨股票数', '市场主力净流入总额(万元)']])
```

### 🆕 连续流入股票挖掘

```python
from eastmoney_scraper import StockCapitalFlowAnalyzer

# 创建分析器
analyzer = StockCapitalFlowAnalyzer()

# 加载历史数据
historical_data = analyzer.load_historical_data(days=7)

# 寻找连续3日流入的股票
continuous_inflow = analyzer.analyze_continuous_inflow_stocks(historical_data, days=3)

if not continuous_inflow.empty:
    print("🎯 连续3日主力净流入股票：")
    for _, stock in continuous_inflow.head(10).iterrows():
        print(f"  {stock['股票名称']}({stock['股票代码']})：")
        print(f"    累计流入: {stock['累计流入']:.2f}万元")
        print(f"    平均每日: {stock['平均每日流入']:.2f}万元")
        print(f"    最新涨幅: +{stock['涨跌幅']:.2f}%")
```

### 🆕 实时市场监控仪表板

```python
from eastmoney_scraper import StockCapitalFlowMonitor, MarketType
import time

class MarketDashboard:
    """市场实时监控仪表板"""
    
    def __init__(self):
        self.monitor = StockCapitalFlowMonitor(market_type=MarketType.ALL)
        self.start_time = time.time()
        
    def display_callback(self, df):
        """实时显示回调"""
        runtime = int(time.time() - self.start_time)
        
        print(f"\n" + "="*80)
        print(f"📊 市场实时监控 - 运行时间: {runtime//60}分{runtime%60}秒")
        print("="*80)
        
        if df.empty:
            print("⚠️ 暂无数据")
            return
            
        # 市场概况
        summary = self.monitor.scraper.analyze_market_summary(df)
        print(f"📈 市场概况：")
        print(f"   总计: {summary['总股票数']}只 | "
              f"上涨: {summary['上涨股票数']}只({summary['上涨股票数']/summary['总股票数']*100:.1f}%) | "
              f"下跌: {summary['下跌股票数']}只")
        print(f"   主力净流入: {summary['市场主力净流入总额(万元)']/10000:.2f}亿元 | "
              f"流入股票: {summary['主力净流入股票数']}只")
        
        # TOP5流入股票
        top_inflow = self.monitor.analyzer.get_top_inflow_stocks(df, 5)
        print(f"\n🔥 主力净流入TOP5：")
        for i, (_, stock) in enumerate(top_inflow.iterrows(), 1):
            print(f"   {i}. {stock['股票名称']}({stock['股票代码']})：")
            print(f"      {stock['主力净流入']:.0f}万元 | +{stock['涨跌幅']:.2f}% | ¥{stock['最新价']}")
        
        # TOP3流出股票
        top_outflow = self.monitor.analyzer.get_top_outflow_stocks(df, 3)
        print(f"\n❄️ 主力净流出TOP3：")
        for i, (_, stock) in enumerate(top_outflow.iterrows(), 1):
            print(f"   {i}. {stock['股票名称']}({stock['股票代码']})：")
            print(f"      {stock['主力净流入']:.0f}万元 | {stock['涨跌幅']:+.2f}% | ¥{stock['最新价']}")
    
    def start_monitoring(self):
        """启动监控"""
        self.monitor.set_callback(self.display_callback)
        self.monitor.start(interval=30)  # 30秒更新一次
        
        print("🚀 市场监控仪表板已启动")
        print("⏹️ 按 Ctrl+C 停止监控")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ 正在停止监控...")
            self.monitor.stop()
            print("✅ 监控已停止")

# 使用示例
dashboard = MarketDashboard()
dashboard.start_monitoring()
```

## 🧪 测试与示例

### 运行测试

```bash
# 运行主要功能测试
python tests/test_stock_capital_flow_scraper.py

# 运行示例代码
python examples/stock_capital_flow_usage.py
```

### 测试输出示例

```
🚀 开始测试 - 2025-05-29 20:43:40
🧪 测试个股资金流向爬虫
============================================================
✅ 爬虫实例创建成功
📡 开始爬取数据...
✅ 成功爬取 100 条数据
📁 数据已保存到: output\stock_capital_flow_all_20250529_204342.csv

📊 数据列信息:
   - 股票代码、股票名称、最新价、涨跌幅
   - 成交量、成交额、主力净流入、主力净流入占比
   - 超大单净流入、大单净流入、中单净流入、小单净流入

🔍 市场概况分析:
   总股票数: 100
   主力净流入股票数: 100
   上涨股票数: 98
   市场主力净流入总额(万元): 2001990.2

🔥 主力净流入TOP5:
   山子高科(000981): 70563.60万元
   四方精创(300468): 65772.71万元
   中超控股(002471): 58095.77万元
```

## ⚠️ 注意事项

### 使用建议

1. **🕒 请求频率**：建议请求间隔不少于10秒，避免对服务器造成压力
2. **📊 数据准确性**：数据仅供参考，投资决策请以官方数据为准
3. **🔒 资源管理**：使用监控器后务必调用`stop()`方法释放资源
4. **💾 存储空间**：长期运行会产生大量数据，注意磁盘空间管理
5. **🌐 网络环境**：确保网络连接稳定，程序包含自动重试机制

### 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 获取不到数据 | 网络连接/API变化 | 检查网络，更新包版本 |
| 数据格式错误 | API接口变化 | 提交Issue报告问题 |
| 内存占用过高 | 数据量过大 | 减少`max_pages`参数 |
| 监控器无响应 | 回调函数异常 | 检查回调函数逻辑 |
| 文件保存失败 | 权限/空间不足 | 检查output目录权限和磁盘空间 |

## 📈 版本历史

### v1.7.0 (2025-05-30) - 当前版本 🆕
- 🏗️ **架构升级**：全新的板块监控架构，支持更灵活的监控方案
- 🔄 **统一接口**：提供统一的板块监控接口，支持概念和行业板块
- 🎯 **监控器增强**：新增专业概念和行业板块监控器
- 📊 **数据分析**：增强数据分析功能，支持市场趋势分析
- 🔔 **智能通知**：支持自定义回调函数处理数据更新
- 📈 **可视化**：支持实时数据可视化展示
- 🧪 **测试完善**：新增完整的监控功能测试用例
- 📚 **文档更新**：更新监控相关文档和使用示例

### v1.6.0 (2025-05-29)
- 🎯 **新增功能**：全部股票代码和基本信息获取模块
- 📊 **市场覆盖**：支持沪市主板、深市主板、创业板、科创板、北交所
- 🔍 **智能缓存**：支持数据缓存机制，提升获取效率
- 📈 **数据筛选**：支持按市场类型、市值等条件筛选股票
- 🔎 **搜索功能**：支持按股票名称、代码等关键词搜索
- 📊 **市场统计**：提供完整的市场概况和统计分析功能
- 🛠️ **API扩展**：新增get_all_stock_codes、search_stocks等接口
- 📚 **数据分析**：新增filter_stocks_by_market_cap等分析工具
- 🧪 **完善测试**：新增股票列表功能的完整测试用例
- 📝 **使用示例**：提供详细的股票列表使用示例和演示代码

### v1.5.0 (2025-05-29)
- 🎯 **新增功能**：完整的个股K线历史数据爬虫模块
- 📈 **支持多周期**：日K、周K、月K、1/5/15/30/60分钟K线
- 🔄 **复权支持**：前复权、后复权、不复权三种类型
- ⚡ **高性能**：支持并行获取多只股票数据
- 🛠️ **技术分析**：内置移动平均线、价格统计等技术指标计算
- 📡 **监控器**：新增StockKlineMonitor实时K线数据监控
- 🔧 **API扩展**：新增get_stock_kline等便捷接口函数
- 🧪 **完善测试**：新增comprehensive K线数据测试用例
- 📝 **使用示例**：提供详细的K线数据使用示例代码

### v1.4.0 (2025-05-28)
- 🎯 **重大重构**：精简包结构，删除冗余模块，保留核心功能
- 📁 **统一输出**：所有数据文件统一保存到`output/`目录，便于管理
- 🔧 **监控整合**：将监控器和分析器功能集成到`api.py`，功能更强大
- 📊 **新增分析器**：`StockCapitalFlowAnalyzer`提供专业数据分析功能
- 🎨 **增强监控**：支持实时显示、图表生成、连续流入分析、市场情绪计算
- 🌟 **多市场支持**：个股资金流向支持全市场、创业板、科创板、主板
- 🧪 **测试优化**：测试文件移动到`tests/`目录，示例代码更新
- 📚 **文档完善**：整合重构信息，更新API文档和使用示例
- ✅ **向后兼容**：保持主要API接口不变，现有代码无需修改

### v1.3.0 (2025-05-28)
- 🎯 **重大重构**：完全重构 `concept_sector_scraper.py` 核心模块，优化代码结构和可读性
- 🌐 **去英文化**：移除所有英文注释和双语注释，统一使用中文注释
- 🔧 **API优化**：简化类名和方法名，去掉冗余前缀，提升开发体验
- 📝 **类名更新**：`ConceptSectorFetcher` → `ConceptSectorDataFetcher`，`ConceptSectorParser` → `ConceptSectorDataParser`
- ⚡ **方法简化**：`fetch_concept_quotes` → `fetch_all_quotes`，`parse_concept_quotes` → `parse_quotes_data` 等
- 📚 **文档更新**：更新所有API接口、示例文件和测试文件，统一文档字符串格式
- 🎨 **代码优化**：统一注释风格，简化文档字符串，提高代码可维护性

### v1.2.0 (2025-05-26)
- ✨ **代码优化**：全面优化代码结构和API设计，提升可维护性
- 📝 **中文注释**：为所有函数、类、方法添加详细的中文注释和文档
- 🔧 **功能增强**：完善数据分析和筛选工具函数，增加更多实用功能
- 📊 **API改进**：补全缺失的API函数，统一接口设计风格
- 🐛 **错误处理**：增强异常处理机制，提供更友好的错误信息
- 📚 **文档完善**：更新README文档，提供更详细的使用说明
- 🎯 **命名规范**：统一变量、函数、类的命名规范，提升代码可读性

### v1.1.0 (2025-05-25)
- ✨ 优化代码结构和API设计
- 📚 完善文档和示例代码
- 🔧 改进错误处理和日志记录
- 🚀 提升性能和稳定性

### v1.0.0 (2025-05-24)
- 🎉 初始版本发布
- 📊 支持概念板块数据爬取
- 💰 支持个股资金流向爬取
- 📡 提供实时监控功能

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. 🍴 Fork 项目
2. 🌿 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔀 开启 Pull Request

### 开发环境设置

```bash
git clone https://github.com/guoyaohua/eastmoney-scraper.git
cd eastmoney-scraper
pip install -e .[dev]

# 运行测试
python tests/test_stock_capital_flow_scraper.py

# 代码格式化
black eastmoney_scraper/

# 代码质量检查
flake8 eastmoney_scraper/
```

## 📄 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢东方财富网提供的数据服务，本项目仅用于学习和研究目的。

## ⭐ 支持项目

如果这个项目对你有帮助，请给它一个⭐️！

---

<div align="center">

**🎯 EastMoney Scraper - 让数据获取变得简单**

Made with ❤️ by [Yaohua Guo](https://github.com/guoyaohua)

</div>