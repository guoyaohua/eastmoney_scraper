# 🎯 EastMoney Scraper - 东方财富数据爬虫

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.0-orange.svg)](https://github.com/guoyaohua/eastmoney-scraper)
[![Code Quality](https://img.shields.io/badge/code%20quality-optimized-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)]()

一个功能强大、高度优化的东方财富网数据爬虫包，提供概念板块、行业板块和个股资金流向数据的爬取、监控与智能分析功能。

## ✨ 核心特性

- 🚀 **板块数据**：支持概念板块和行业板块，实时行情、多周期资金流向分析（今日/5日/10日）
- 💰 **个股资金流向**：主力、超大单、大单、中单、小单资金流向追踪，支持多市场（全市场/创业板/科创板/主板）
- ⚡ **高性能设计**：支持并行爬取，智能分页，自动重试机制
- 📡 **实时监控**：内置监控器，支持定时更新和自定义回调通知
- 🔧 **简洁API**：提供函数式和面向对象两种编程接口
- 💾 **统一存储**：所有数据统一保存到output目录，支持CSV、JSON等格式
- 🔍 **智能分析**：内置数据筛选、排序、统计分析和图表生成功能
- 📊 **可视化友好**：与matplotlib、seaborn等可视化库完美集成

## 🆕 v1.4.0 重构亮点

### 包结构优化
- **精简模块**：只保留 `sector_scraper.py` 和 `stock_capital_flow_scraper.py` 两个核心模块
- **统一输出**：所有数据文件统一保存到 `output/` 目录，便于管理
- **功能整合**：监控和分析功能集成到 `api.py`，提供更强大的功能

### 新增功能
- 🆕 **StockCapitalFlowAnalyzer** - 专业的资金流向数据分析器
- 🆕 **增强监控器** - 支持实时显示、图表生成、连续流入分析
- 🆕 **市场情绪分析** - 计算市场整体情绪指标
- 🆕 **多市场支持** - 支持全市场、创业板、科创板、主板等不同市场

### 向后兼容
- ✅ 主要API接口保持不变
- ✅ 现有代码无需修改即可使用
- ✅ 自动适配新的输出目录结构

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

### 1️⃣ 个股资金流向数据（推荐）

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

### 2️⃣ 概念板块数据获取

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
```

### 3️⃣ 实时监控与分析（增强功能）

```python
from eastmoney_scraper import StockCapitalFlowMonitor, StockCapitalFlowAnalyzer, MarketType

# 🆕 创建增强的监控器
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

### 4️⃣ 数据分析与筛选

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

### 🏗️ 新的项目结构（v1.4.0）

```
eastmoney-scraper/
├── 📁 eastmoney_scraper/          # 核心包目录
│   ├── 📄 __init__.py             # 包初始化和API导出
│   ├── 📄 version.py              # 版本信息
│   ├── 📄 api.py                  # 用户友好的API接口（包含监控和分析功能）
│   ├── 📄 sector_scraper.py       # 通用板块爬虫（概念+行业）
│   └── 📄 stock_capital_flow_scraper.py  # 个股资金流向爬虫
├── 📁 tests/                      # 测试套件
│   └── 📄 test_stock_capital_flow_scraper.py  # 功能测试
├── 📁 examples/                   # 使用示例
│   ├── 📄 stock_capital_flow_usage.py  # 个股资金流向示例
│   ├── 📄 basic_usage.py          # 基础功能示例
│   ├── 📄 advanced_usage.py       # 高级功能示例
│   └── 📄 monitor_usage.py        # 监控功能示例
├── 📁 output/                     # 🆕 统一输出目录
│   ├── 📁 stock_capital_flow_data_all/    # 全市场数据
│   ├── 📁 stock_capital_flow_data_gem/    # 创业板数据
│   ├── 📁 stock_capital_flow_data_star/   # 科创板数据
│   ├── 📁 stock_capital_flow_data_main/   # 主板数据
│   ├── 📁 concept_sector_data/            # 概念板块数据
│   └── 📁 industry_sector_data/           # 行业板块数据
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

#### 板块数据接口

| 函数 | 说明 | 主要参数 |
|------|------|----------|
| `get_concept_sectors()` | 获取完整概念板块数据 | `include_capital_flow`, `periods`, `save_to_file` |
| `get_concept_sectors_realtime()` | 仅获取实时行情 | 无 |
| `get_industry_sectors()` | 🆕 获取行业板块数据 | `include_capital_flow`, `save_to_file` |
| `get_sectors()` | 🆕 通用板块数据获取 | `sector_type`, `include_capital_flow` |
| `get_stock_to_sector_mapping()` | 🆕 获取股票-板块映射 | `sector_type`, `save_to_file` |

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

### v1.4.0 (2025-05-29) - 当前版本 🆕
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

### v1.2.0 (2025-05-27)
- ✨ **代码优化**：全面优化代码结构和API设计，提升可维护性
- 📝 **中文注释**：为所有函数、类、方法添加详细的中文注释和文档
- 🔧 **功能增强**：完善数据分析和筛选工具函数，增加更多实用功能
- 📊 **API改进**：补全缺失的API函数，统一接口设计风格
- 🐛 **错误处理**：增强异常处理机制，提供更友好的错误信息
- 📚 **文档完善**：更新README文档，提供更详细的使用说明
- 🎯 **命名规范**：统一变量、函数、类的命名规范，提升代码可读性

### v1.1.0 (2024-12-26)
- ✨ 优化代码结构和API设计
- 📚 完善文档和示例代码
- 🔧 改进错误处理和日志记录
- 🚀 提升性能和稳定性

### v1.0.0 (2024-05-26)
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