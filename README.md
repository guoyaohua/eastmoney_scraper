# EastMoney Scraper - 东方财富数据爬虫

一个用于爬取东方财富网概念板块和个股资金流向数据的Python包。

## 功能特性

- 🚀 **概念板块数据**：实时行情、资金流向（今日/5日/10日）
- 📊 **个股资金流向**：主力、超大单、大单、中单、小单资金流向
- ⚡ **高性能**：支持并行爬取，自动分页获取全量数据
- 🔄 **实时监控**：内置监控器，支持定时更新和回调通知
- 📦 **简洁API**：提供易用的函数接口和类接口

## 安装

```bash
git clone https://github.com/guoyaohua/eastmoney-scraper.git
cd eastmoney-scraper
pip install -e .
```

## 快速开始

### 1. 获取概念板块数据

```python
from eastmoney_scraper import get_concept_sectors

# 获取所有概念板块数据（包含行情和资金流向）
df = get_concept_sectors()
print(df[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']].head(10))
```

### 2. 实时监控概念板块

```python
from eastmoney_scraper import ConceptSectorMonitor

# 创建监控器
monitor = ConceptSectorMonitor()

# 设置数据更新回调
def on_update(df):
    print(f"更新时间: {df['更新时间'].iloc[0]}")
    print(f"领涨板块: {df.iloc[0]['板块名称']} ({df.iloc[0]['涨跌幅']}%)")
    
monitor.set_callback(on_update)

# 开始监控（每30秒更新一次）
monitor.start(interval=30)

# 运行一段时间后停止
import time
time.sleep(300)  # 运行5分钟
monitor.stop()
```

### 3. 获取个股资金流向

```python
from eastmoney_scraper import get_stock_capital_flow

# 获取个股资金流向排行
df = get_stock_capital_flow(max_pages=5)
print(df[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']].head(10))
```

## API 文档

### 概念板块相关

#### `get_concept_sectors()`
获取概念板块完整数据（行情+资金流向）

参数：
- `include_capital_flow` (bool): 是否包含资金流向数据，默认True
- `periods` (list): 资金流向周期，默认['today', '5day', '10day']
- `save_to_file` (bool): 是否保存到文件，默认False
- `output_dir` (str): 输出目录，默认"concept_sector_data"

返回：`pd.DataFrame` - 概念板块数据

#### `get_concept_sectors_realtime()`
仅获取概念板块实时行情（不含资金流向）

返回：`pd.DataFrame` - 实时行情数据

#### `get_concept_capital_flow(period='today')`
获取概念板块资金流向数据

参数：
- `period` (str): 时间周期 'today'/'5day'/'10day'

返回：`pd.DataFrame` - 资金流向数据

### 个股资金流向相关

#### `get_stock_capital_flow()`
获取个股资金流向数据

参数：
- `max_pages` (int): 最大页数，默认10
- `save_to_file` (bool): 是否保存到文件，默认False
- `output_dir` (str): 输出目录，默认"capital_flow_data"

返回：`pd.DataFrame` - 个股资金流向数据

### 监控器类

#### `ConceptSectorMonitor`
概念板块实时监控器

方法：
- `set_callback(callback)`: 设置数据更新回调函数
- `start(interval)`: 开始监控
- `stop()`: 停止监控
- `get_latest_data()`: 获取最新数据

#### `StockCapitalFlowMonitor`
个股资金流向监控器

方法：
- `set_callback(callback)`: 设置数据更新回调函数
- `start(interval)`: 开始监控
- `stop()`: 停止监控
- `get_latest_data()`: 获取最新数据

### 工具函数

#### `filter_sectors_by_change(df, min_change, max_change)`
根据涨跌幅筛选板块

#### `filter_sectors_by_capital(df, min_capital, flow_type)`
根据资金流向筛选板块

#### `get_top_sectors(df, n, by, ascending)`
获取排名前N的板块

## 数据字段说明

### 概念板块数据字段

| 字段名 | 说明 | 单位 |
|--------|------|------|
| 板块代码 | 板块唯一标识 | - |
| 板块名称 | 板块中文名称 | - |
| 涨跌幅 | 当日涨跌百分比 | % |
| 最新价 | 最新指数价格 | 点 |
| 成交额 | 成交金额 | 万元 |
| 主力净流入 | 主力资金净流入 | 万元 |
| 5日主力净流入 | 5日累计主力净流入 | 万元 |
| 10日主力净流入 | 10日累计主力净流入 | 万元 |

## 高级用法

### 1. 数据筛选和分析

```python
from eastmoney_scraper import get_concept_sectors, filter_sectors_by_change, get_top_sectors

# 获取数据
df = get_concept_sectors()

# 筛选涨幅超过3%的板块
rising_sectors = filter_sectors_by_change(df, min_change=3.0)

# 获取主力净流入前10的板块
top_inflow = get_top_sectors(df, n=10, by='主力净流入', ascending=False)

# 自定义分析
strong_sectors = df[(df['涨跌幅'] > 2) & (df['主力净流入'] > 10000)]
print(f"强势板块数量: {len(strong_sectors)}")
```

### 2. 定时任务

```python
import schedule
import time
from eastmoney_scraper import get_concept_sectors

def job():
    df = get_concept_sectors(save_to_file=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 更新完成，共{len(df)}个板块")

# 每5分钟执行一次
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### 3. 数据导出

```python
from eastmoney_scraper import get_concept_sectors

# 获取数据
df = get_concept_sectors()

# 导出为Excel
df.to_excel('concept_sectors.xlsx', index=False)

# 导出为JSON
df.to_json('concept_sectors.json', orient='records', force_ascii=False)

# 导出为CSV（默认）
df.to_csv('concept_sectors.csv', index=False, encoding='utf-8-sig')
```

## 注意事项

1. **请求频率**：建议请求间隔不少于10秒，避免对服务器造成压力
2. **数据准确性**：数据仅供参考，以东方财富官网为准
3. **异常处理**：网络异常时会自动重试，建议添加异常处理逻辑
4. **资源清理**：使用监控器后记得调用`stop()`方法释放资源

## 更新日志

### v1.0.0 (2024-05-26)
- 初始版本发布
- 支持概念板块数据爬取
- 支持个股资金流向爬取
- 提供监控器和API接口

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 免责声明

本项目仅供学习和研究使用，不构成投资建议。使用本项目获取的数据进行投资决策，风险自负。