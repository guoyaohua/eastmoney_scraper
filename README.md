# 🎯 EastMoney Scraper - 东方财富数据爬虫

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/guoyaohua/eastmoney-scraper)
[![Code Quality](https://img.shields.io/badge/code%20quality-optimized-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)]()

一个功能强大、高度优化的东方财富网数据爬虫包，提供概念板块和个股资金流向数据的爬取、监控与智能分析功能。

A powerful and highly optimized EastMoney data scraper package that provides scraping, monitoring and intelligent analysis functionality for concept sectors and individual stock capital flow data.

## ✨ 核心特性

- 🚀 **概念板块数据**：实时行情、多周期资金流向分析（今日/5日/10日）
- 💰 **个股资金流向**：主力、超大单、大单、中单、小单资金流向追踪
- ⚡ **高性能设计**：支持并行爬取，智能分页，自动重试机制
- 📡 **实时监控**：内置监控器，支持定时更新和自定义回调通知
- 🔧 **简洁API**：提供函数式和面向对象两种编程接口
- 💾 **多格式存储**：支持CSV、JSON、SQLite等多种数据存储格式
- 🔍 **智能分析**：内置数据筛选、排序、统计分析功能
- 📊 **可视化友好**：与matplotlib、seaborn等可视化库完美集成

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

### 1️⃣ 概念板块数据获取

```python
from eastmoney_scraper import get_concept_sectors

# 获取完整概念板块数据（行情+资金流向）
df = get_concept_sectors()
print(df[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']].head(10))

# 仅获取实时行情（更快）
from eastmoney_scraper import get_concept_sectors_realtime
df_quotes = get_concept_sectors_realtime()
print(f"获取到 {len(df_quotes)} 个板块的实时行情")
```

### 2️⃣ 个股资金流向数据

```python
from eastmoney_scraper import get_stock_capital_flow

# 获取个股资金流向排行数据
df = get_stock_capital_flow(max_pages=2)  # 获取前2页约200只股票
print(df[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']].head(10))

# 使用高级爬虫类进行精确控制
from eastmoney_scraper import CapitalFlowScraper

scraper = CapitalFlowScraper()
df = scraper.scrape_once(save_to_file=True)  # 自动保存到文件
```

### 3️⃣ 实时监控系统

```python
from eastmoney_scraper import ConceptSectorMonitor
import time

# 创建概念板块监控器
monitor = ConceptSectorMonitor()

# 定义数据更新回调函数
def on_data_update(df):
    print(f"📊 数据更新：{len(df)} 个板块")
    if not df.empty:
        leading = df.iloc[0]
        print(f"🔥 领涨板块：{leading['板块名称']} (+{leading['涨跌幅']:.2f}%)")

# 设置回调并启动监控
monitor.set_callback(on_data_update)
monitor.start(interval=30)  # 每30秒更新

# 运行监控
try:
    time.sleep(300)  # 监控5分钟
finally:
    monitor.stop()  # 停止监控
```

### 4️⃣ 数据分析与筛选

```python
from eastmoney_scraper import (
    get_concept_sectors, 
    filter_sectors_by_change, 
    get_top_sectors
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

# 自定义复合筛选
hot_sectors = df[
    (df['涨跌幅'] > 2) & 
    (df['主力净流入'] > 10000) &  # 超过1亿
    (df['成交额'] > 100000)       # 成交额超过10亿
]
print(f"🎯 优质热门板块：{len(hot_sectors)} 个")
```

## 📚 详细文档

### 🏗️ 项目结构

```
eastmoney-scraper/
├── 📁 eastmoney_scraper/          # 核心包目录
│   ├── 📄 __init__.py             # 包初始化和API导出
│   ├── 📄 version.py              # 版本信息
│   ├── 📄 api.py                  # 用户友好的API接口
│   ├── 📄 concept_sector_scraper.py  # 概念板块爬虫
│   ├── 📄 eastmoney_capital_flow_scraper.py  # 个股资金流爬虫
│   └── 📄 capital_flow_monitor.py # 监控和分析模块
├── 📁 examples/                   # 使用示例
│   ├── 📄 basic_usage.py          # 基础功能示例
│   ├── 📄 advanced_usage.py       # 高级功能示例
│   ├── 📄 monitor_usage.py        # 监控功能示例
│   └── 📄 quickstart_capital_flow.py  # 快速入门指南
├── 📁 tests/                      # 测试套件
│   └── 📄 test_capital_flow_scraper.py  # 功能测试
├── 📄 README.md                   # 项目文档
├── 📄 setup.py                    # 安装配置
└── 📄 requirements.txt            # 依赖清单
```

### 🔧 API 参考

#### 概念板块数据接口

| 函数 | 说明 | 主要参数 |
|------|------|----------|
| `get_concept_sectors()` | 获取完整概念板块数据 | `include_capital_flow`, `periods`, `save_to_file` |
| `get_concept_sectors_realtime()` | 仅获取实时行情 | 无 |
| `get_concept_capital_flow()` | 获取指定周期资金流向 | `period` ('today'/'5day'/'10day') |

#### 个股资金流向接口

| 函数 | 说明 | 主要参数 |
|------|------|----------|
| `get_stock_capital_flow()` | 获取个股资金流向排行 | `max_pages`, `save_to_file` |
| `get_stock_to_concept_map()` | 获取股票-概念映射关系 | `save_to_file`, `max_workers` |

#### 数据分析工具

| 函数 | 说明 | 主要参数 |
|------|------|----------|
| `filter_sectors_by_change()` | 按涨跌幅筛选板块 | `min_change`, `max_change` |
| `filter_sectors_by_capital()` | 按资金流向筛选板块 | `min_capital`, `flow_type` |
| `get_top_sectors()` | 获取排名前N的板块 | `n`, `by`, `ascending` |

#### 监控器类

| 类 | 说明 | 主要方法 |
|----|------|----------|
| `ConceptSectorMonitor` | 概念板块实时监控 | `start()`, `stop()`, `set_callback()` |
| `StockCapitalFlowMonitor` | 个股资金流监控 | `start()`, `stop()`, `set_callback()` |

### 📊 数据字段说明

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

#### 个股资金流向数据字段

| 字段名 | 说明 | 单位 | 示例 |
|--------|------|------|------|
| 股票代码 | 6位股票代码 | - | `000001` |
| 股票名称 | 股票中文名称 | - | `平安银行` |
| 最新价 | 当前股价 | 元 | `12.34` |
| 涨跌幅 | 涨跌百分比 | % | `2.51` |
| 主力净流入 | 主力资金净流入 | 万元 | `5678` |
| 超大单净流入 | 超大单资金净流入 | 万元 | `3456` |
| 大单净流入 | 大单资金净流入 | 万元 | `2222` |
| 中单净流入 | 中单资金净流入 | 万元 | `-1111` |
| 小单净流入 | 小单资金净流入 | 万元 | `-4567` |
| 主力净流入占比 | 主力净流入占成交额比例 | % | `8.75` |

## 💡 高级用法

### 智能投资机会筛选

```python
from eastmoney_scraper import get_concept_sectors, get_stock_capital_flow

# 1. 寻找强势概念板块
concept_df = get_concept_sectors()
strong_concepts = concept_df[
    (concept_df['涨跌幅'] > 3) &           # 涨幅超过3%
    (concept_df['主力净流入'] > 20000) &    # 主力流入超过2亿
    (concept_df['5日主力净流入'] > 0)       # 5日持续流入
]

print(f"🎯 发现 {len(strong_concepts)} 个强势概念：")
for _, concept in strong_concepts.head(5).iterrows():
    print(f"  • {concept['板块名称']}：+{concept['涨跌幅']:.2f}%，"
          f"主力流入{concept['主力净流入']/10000:.1f}亿")

# 2. 寻找资金流入活跃个股
stock_df = get_stock_capital_flow(max_pages=3)
active_stocks = stock_df[
    (stock_df['主力净流入'] > 10000) &      # 主力流入超过1亿
    (stock_df['主力净流入占比'] > 5) &       # 占比超过5%
    (stock_df['涨跌幅'] > 1)                # 上涨超过1%
]

print(f"\n💎 发现 {len(active_stocks)} 只活跃个股：")
for _, stock in active_stocks.head(5).iterrows():
    print(f"  • {stock['股票名称']}({stock['股票代码']})：+{stock['涨跌幅']:.2f}%，"
          f"主力流入{stock['主力净流入']/10000:.2f}亿")
```

### 多监控器协同运行

```python
from eastmoney_scraper import ConceptSectorMonitor, StockCapitalFlowMonitor
import time

class MarketMonitor:
    """市场综合监控器"""
    
    def __init__(self):
        self.concept_monitor = ConceptSectorMonitor()
        self.stock_monitor = StockCapitalFlowMonitor()
        self.latest_concept_data = None
        self.latest_stock_data = None
    
    def concept_callback(self, df):
        """概念板块数据回调"""
        self.latest_concept_data = df
        print(f"📊 概念板块更新：{len(df)}个板块")
        self.analyze_market()
    
    def stock_callback(self, df):
        """个股数据回调"""
        self.latest_stock_data = df
        print(f"💰 个股数据更新：{len(df)}只股票")
        self.analyze_market()
    
    def analyze_market(self):
        """市场综合分析"""
        if self.latest_concept_data is None or self.latest_stock_data is None:
            return
        
        # 分析概念板块热度
        hot_concepts = len(self.latest_concept_data[self.latest_concept_data['涨跌幅'] > 3])
        
        # 分析个股资金活跃度
        active_stocks = len(self.latest_stock_data[self.latest_stock_data['主力净流入'] > 5000])
        
        print(f"🔥 市场热度：热门概念{hot_concepts}个，活跃个股{active_stocks}只")
    
    def start(self):
        """启动监控"""
        self.concept_monitor.set_callback(self.concept_callback)
        self.stock_monitor.set_callback(self.stock_callback)
        
        self.concept_monitor.start(interval=30)
        self.stock_monitor.start(interval=60)
        
        print("🚀 市场监控系统已启动")
    
    def stop(self):
        """停止监控"""
        self.concept_monitor.stop()
        self.stock_monitor.stop()
        print("⏹️ 市场监控系统已停止")

# 使用示例
monitor = MarketMonitor()
try:
    monitor.start()
    time.sleep(180)  # 运行3分钟
finally:
    monitor.stop()
```

### 定时任务调度

```python
import schedule
import time
from datetime import datetime
from eastmoney_scraper import get_concept_sectors, get_stock_capital_flow

def market_snapshot():
    """市场快照任务"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取概念板块数据
    concept_df = get_concept_sectors(save_to_file=True)
    rising_concepts = len(concept_df[concept_df['涨跌幅'] > 0])
    
    # 获取个股数据
    stock_df = get_stock_capital_flow(max_pages=1, save_to_file=True)
    rising_stocks = len(stock_df[stock_df['涨跌幅'] > 0])
    
    print(f"📸 [{timestamp}] 市场快照：")
    print(f"   概念板块：{len(concept_df)}个（上涨{rising_concepts}个）")
    print(f"   个股样本：{len(stock_df)}只（上涨{rising_stocks}只）")

# 调度任务
schedule.every(5).minutes.do(market_snapshot)      # 每5分钟执行
schedule.every().hour.at(":00").do(market_snapshot) # 每小时整点执行

print("⏰ 定时任务已设置，按Ctrl+C停止")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n📋 定时任务已停止")
```

## 🧪 测试与示例

### 运行示例代码

```bash
# 基础功能示例
python examples/basic_usage.py

# 高级功能示例
python examples/advanced_usage.py

# 监控功能示例
python examples/monitor_usage.py

# 快速入门指南
python examples/quickstart_capital_flow.py
```

### 运行测试套件

```bash
# 运行完整测试
python tests/test_capital_flow_scraper.py

# 使用pytest运行（需要安装pytest）
pytest tests/ -v
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

## 📈 版本历史

### v1.2.0 (2025-05-27) - 当前版本
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
python tests/test_capital_flow_scraper.py

# 代码格式化
black eastmoney_scraper/

# 代码质量检查
flake8 eastmoney_scraper/
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## ⚖️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。使用本项目获取的数据进行投资决策，风险自负。请遵守东方财富网的服务条款和数据使用政策。

## 📞 联系方式

- 📧 邮箱：guo.yaohua@foxmail.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/guoyaohua/eastmoney-scraper/issues)
- 📖 项目主页：[GitHub Repository](https://github.com/guoyaohua/eastmoney-scraper)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

Made with ❤️ by [Yaohua Guo](https://github.com/guoyaohua)

</div>