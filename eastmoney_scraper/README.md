# 东方财富个股资金流向爬虫

基于东方财富网(https://data.eastmoney.com/zjlx/detail.html)的个股资金流向数据爬虫，支持定时爬取、数据分析和实时监控。

## 功能特点

- 🔄 **定时爬取**: 支持每10秒自动爬取最新数据
- 📊 **数据分析**: 提供多维度的资金流向分析
- 📈 **实时监控**: 实时显示资金流向变化和TOP排行
- 💾 **数据存储**: 支持CSV、JSON和SQLite数据库存储
- 🔧 **模块化设计**: 代码结构清晰，易于扩展

## 项目结构

```
.
├── run_eastmoney_scraper.py          # 主入口文件
└── eastmoney_scraper/                # 爬虫模块目录
    ├── __init__.py                   # 包初始化文件
    ├── eastmoney_capital_flow_scraper.py  # 核心爬虫模块
    ├── capital_flow_monitor.py       # 监控和分析模块
    ├── example_usage.py              # 使用示例
    ├── quickstart.py                 # 快速开始
    ├── test_scraper.py               # 测试脚本
    ├── requirements.txt              # 依赖包列表
    ├── README.md                     # 项目说明
    └── capital_flow_data/            # 数据存储目录（自动创建）
        ├── capital_flow_*.csv        # CSV数据文件
        ├── capital_flow_*.json       # JSON数据文件
        └── capital_flow.db           # SQLite数据库
```

## 安装依赖

```bash
# 进入项目目录
cd eastmoney_scraper

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 运行主程序

```bash
# 在项目根目录运行
python run_eastmoney_scraper.py
```

### 2. 作为模块使用

```python
from eastmoney_scraper import CapitalFlowScraper

# 创建爬虫实例
scraper = CapitalFlowScraper()

# 执行单次爬取
df = scraper.scrape_once(save_to_file=True)

# 查看数据
print(df.head())
```

### 3. 定时爬取

```python
from eastmoney_scraper import CapitalFlowScraper

scraper = CapitalFlowScraper()
# 每10秒自动爬取
scraper.start_scheduled_scraping(interval=10)
```

### 4. 实时监控

```python
from eastmoney_scraper import CapitalFlowMonitor

monitor = CapitalFlowMonitor()
monitor.start_monitoring(interval=10, display_interval=30)
```

### 5. 运行示例程序

```bash
cd eastmoney_scraper
python -m example_usage
```

### 6. 运行测试

```bash
cd eastmoney_scraper
python -m test_scraper
```

## 核心模块说明

### eastmoney_capital_flow_scraper.py

#### CapitalFlowConfig
配置类，包含API地址、请求头、字段映射等配置信息。

#### DataFetcher
数据获取模块，负责从API获取原始数据。
- `fetch_data()`: 获取单页数据
- `fetch_all_pages()`: 多线程获取多页数据

#### DataParser
数据解析模块，负责解析和转换原始数据。
- `parse_stock_data()`: 解析单只股票数据
- `parse_batch_data()`: 批量解析并返回DataFrame

#### DataStorage
数据存储模块，支持多种存储格式。
- `save_to_csv()`: 保存为CSV文件
- `save_to_json()`: 保存为JSON文件
- `append_to_database()`: 追加到SQLite数据库

#### CapitalFlowScraper
主爬虫类，整合各个模块功能。
- `scrape_once()`: 执行一次完整的爬取流程
- `start_scheduled_scraping()`: 开始定时爬取

### capital_flow_monitor.py

#### CapitalFlowAnalyzer
数据分析器，提供各种分析功能。
- `get_latest_data()`: 获取最新数据
- `get_top_inflow_stocks()`: 获取主力净流入TOP股票
- `get_continuous_inflow_stocks()`: 获取连续流入股票
- `analyze_sector_flow()`: 分析板块资金流向

#### CapitalFlowMonitor
实时监控器，提供可视化监控界面。
- `display_realtime_data()`: 显示实时数据
- `plot_analysis()`: 生成分析图表
- `start_monitoring()`: 开始监控

## 数据字段说明

| 字段名 | 说明 | 单位 |
|--------|------|------|
| 股票代码 | 股票代码 | - |
| 股票名称 | 股票名称 | - |
| 最新价 | 当前股价 | 元 |
| 涨跌幅 | 涨跌百分比 | % |
| 主力净流入 | 主力资金净流入金额 | 万元 |
| 超大单净流入 | 超大单资金净流入 | 万元 |
| 大单净流入 | 大单资金净流入 | 万元 |
| 中单净流入 | 中单资金净流入 | 万元 |
| 小单净流入 | 小单资金净流入 | 万元 |
| 主力净流入占比 | 主力净流入占总成交额比例 | % |

## 注意事项

1. **频率限制**: 建议爬取间隔不少于10秒，避免对服务器造成压力
2. **数据准确性**: 数据来源于东方财富网，仅供参考
3. **异常处理**: 程序包含完整的异常处理，网络错误会自动重试
4. **存储空间**: 长时间运行会产生大量数据，注意磁盘空间

## 自定义扩展

### 添加新的分析维度

在 `CapitalFlowAnalyzer` 类中添加新方法：

```python
def your_custom_analysis(self):
    """您的自定义分析"""
    df = self.get_latest_data()
    # 添加您的分析逻辑
    return result
```

### 修改数据存储方式

在 `DataStorage` 类中添加新的存储方法：

```python
def save_to_your_format(self, data):
    """保存到您的格式"""
    # 实现您的存储逻辑
    pass
```

## 常见问题

1. **Q: 爬虫获取不到数据？**
   A: 检查网络连接，确认东方财富网API是否正常。

2. **Q: 如何修改爬取的股票范围？**
   A: 修改 `CapitalFlowConfig.DEFAULT_PARAMS` 中的 `fs` 参数。

3. **Q: 数据库文件在哪里？**
   A: 在 `capital_flow_data/capital_flow.db`。

## License

本项目仅供学习研究使用，请勿用于商业用途。使用本项目获取的数据时，请遵守东方财富网的相关协议。

## 贡献

欢迎提交Issue和Pull Request！