"""
股票列表数据获取使用示例

本示例展示如何使用eastmoney_scraper包获取股票列表数据，包括：
- 获取全部股票代码
- 按市场类型筛选股票
- 搜索特定股票
- 获取市场概况统计
- 数据分析和筛选
"""

import sys
import os

# 添加项目根目录到路径，以便导入包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import (
    get_all_stock_codes, get_stock_list, get_stock_basic_info,
    search_stocks, get_market_overview, StockListScraper, StockMarket,
    filter_stocks_by_market_cap, get_top_stocks_by_metric
)
import pandas as pd


def demo_basic_usage():
    """演示基本使用方法"""
    print("=" * 60)
    print("1. 基本使用演示")
    print("=" * 60)
    
    try:
        # 获取所有股票代码
        print("获取所有股票代码...")
        all_codes = get_all_stock_codes()
        print(f"✓ 总共获取到 {len(all_codes)} 只股票代码")
        print(f"前10只股票代码: {all_codes[:10]}")
        
        # 获取创业板股票代码
        print("\n获取创业板股票代码...")
        chinext_codes = get_all_stock_codes(market='chinext')
        print(f"✓ 创业板股票数量: {len(chinext_codes)}")
        print(f"前5只创业板股票: {chinext_codes[:5]}")
        
        # 获取科创板股票代码
        print("\n获取科创板股票代码...")
        star_codes = get_all_stock_codes(market='star')
        print(f"✓ 科创板股票数量: {len(star_codes)}")
        print(f"前5只科创板股票: {star_codes[:5]}")
        
    except Exception as e:
        print(f"✗ 基本使用演示出错: {e}")


def demo_stock_list_data():
    """演示获取股票列表完整数据"""
    print("\n" + "=" * 60)
    print("2. 股票列表完整数据演示")
    print("=" * 60)
    
    try:
        # 获取全部股票列表数据
        print("获取全部股票列表数据...")
        df = get_stock_list(save_to_file=False)  # 不保存文件以节省时间
        
        if not df.empty:
            print(f"✓ 获取到 {len(df)} 只股票的完整数据")
            print("\n数据字段:")
            print(df.columns.tolist())
            
            print("\n前5只股票数据:")
            display_columns = ['股票代码', '股票名称', '最新价', '涨跌幅', '总市值', '市场类型']
            available_columns = [col for col in display_columns if col in df.columns]
            print(df[available_columns].head())
            
            print("\n数据类型统计:")
            print(df.dtypes)
            
        else:
            print("⚠ 未获取到股票列表数据")
            
    except Exception as e:
        print(f"✗ 股票列表数据获取出错: {e}")


def demo_basic_info():
    """演示获取股票基本信息"""
    print("\n" + "=" * 60)
    print("3. 股票基本信息演示")
    print("=" * 60)
    
    try:
        # 获取股票基本信息
        print("获取股票基本信息...")
        stock_info = get_stock_basic_info()
        
        if stock_info:
            print(f"✓ 获取到 {len(stock_info)} 只股票的基本信息")
            
            # 显示前5只股票的信息
            print("\n前5只股票基本信息:")
            count = 0
            for code, info in stock_info.items():
                if count >= 5:
                    break
                print(f"{code}: {info.get('股票名称', 'N/A')} - {info.get('市场类型', 'N/A')}")
                print(f"  最新价: {info.get('最新价', 'N/A')}, 总市值: {info.get('总市值', 'N/A')}")
                count += 1
            
            # 按市场类型统计
            print("\n按市场类型统计:")
            market_count = {}
            for code, info in stock_info.items():
                market = info.get('市场类型', '未知')
                market_count[market] = market_count.get(market, 0) + 1
            
            for market, count in sorted(market_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {market}: {count} 只")
                
        else:
            print("⚠ 未获取到股票基本信息")
            
    except Exception as e:
        print(f"✗ 股票基本信息获取出错: {e}")


def demo_search_stocks():
    """演示搜索股票功能"""
    print("\n" + "=" * 60)
    print("4. 股票搜索功能演示")
    print("=" * 60)
    
    try:
        # 搜索银行股
        print("搜索名称包含'银行'的股票...")
        bank_stocks = search_stocks("银行")
        
        if not bank_stocks.empty:
            print(f"✓ 找到 {len(bank_stocks)} 只银行股")
            display_columns = ['股票代码', '股票名称', '最新价', '市场类型']
            available_columns = [col for col in display_columns if col in bank_stocks.columns]
            print(bank_stocks[available_columns].head(10))
        else:
            print("⚠ 未找到银行股")
        
        # 搜索特定股票代码
        print("\n搜索股票代码 '000001'...")
        search_result = search_stocks("000001")
        
        if not search_result.empty:
            stock_info = search_result.iloc[0]
            print(f"✓ 找到股票: {stock_info.get('股票代码', 'N/A')} - {stock_info.get('股票名称', 'N/A')}")
            print(f"  最新价: {stock_info.get('最新价', 'N/A')}")
            print(f"  市场类型: {stock_info.get('市场类型', 'N/A')}")
        else:
            print("⚠ 未找到股票 000001")
        
        # 在创业板中搜索科技股
        print("\n在创业板中搜索包含'科技'的股票...")
        tech_stocks = search_stocks("科技", market='chinext')
        
        if not tech_stocks.empty:
            print(f"✓ 在创业板找到 {len(tech_stocks)} 只科技股")
            available_columns = [col for col in ['股票代码', '股票名称', '最新价'] if col in tech_stocks.columns]
            print(tech_stocks[available_columns].head(5))
        else:
            print("⚠ 在创业板未找到科技股")
            
    except Exception as e:
        print(f"✗ 股票搜索演示出错: {e}")


def demo_market_overview():
    """演示市场概况统计"""
    print("\n" + "=" * 60)
    print("5. 市场概况统计演示")
    print("=" * 60)
    
    try:
        # 获取全市场概况
        print("获取全市场概况...")
        overview = get_market_overview()
        
        if overview:
            print("✓ 全市场概况:")
            key_metrics = [
                '总股票数', '平均股价', '总市值', '上涨股票数', '下跌股票数',
                '上涨股票比例', '平均涨跌幅', '平均市值'
            ]
            
            for metric in key_metrics:
                if metric in overview:
                    value = overview[metric]
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.2f}")
                    else:
                        print(f"  {metric}: {value}")
            
            # 显示市场分布
            if '市场分布' in overview:
                print("\n  市场分布:")
                for market, count in overview['市场分布'].items():
                    print(f"    {market}: {count} 只")
        
        # 获取创业板概况
        print("\n获取创业板概况...")
        chinext_overview = get_market_overview('chinext')
        
        if chinext_overview:
            print("✓ 创业板概况:")
            for metric in ['总股票数', '平均股价', '上涨股票比例']:
                if metric in chinext_overview:
                    value = chinext_overview[metric]
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.2f}")
                    else:
                        print(f"  {metric}: {value}")
        
    except Exception as e:
        print(f"✗ 市场概况统计出错: {e}")


def demo_data_analysis():
    """演示数据分析功能"""
    print("\n" + "=" * 60)
    print("6. 数据分析功能演示")
    print("=" * 60)
    
    try:
        # 获取股票数据
        print("获取股票数据进行分析...")
        df = get_stock_list(save_to_file=False)
        
        if df.empty:
            print("⚠ 无法获取股票数据，跳过分析演示")
            return
        
        print(f"✓ 获取到 {len(df)} 只股票数据")
        
        # 按市值筛选大盘股（市值>1000亿）
        if '总市值' in df.columns:
            print("\n筛选大盘股（市值>1000亿）...")
            big_caps = filter_stocks_by_market_cap(df, min_cap=10000000)  # 1000亿 = 10000000万
            print(f"✓ 找到 {len(big_caps)} 只大盘股")
            
            if not big_caps.empty:
                display_columns = ['股票代码', '股票名称', '总市值', '市场类型']
                available_columns = [col for col in display_columns if col in big_caps.columns]
                print("前5只大盘股:")
                print(big_caps[available_columns].head())
        
        # 获取市值最大的20只股票
        if '总市值' in df.columns:
            print("\n获取市值最大的20只股票...")
            top_by_cap = get_top_stocks_by_metric(df, '总市值', 20)
            
            if not top_by_cap.empty:
                print(f"✓ 市值前20名:")
                display_columns = ['股票代码', '股票名称', '总市值', '市盈率']
                available_columns = [col for col in display_columns if col in top_by_cap.columns]
                print(top_by_cap[available_columns].head(10))
        
        # 获取涨幅最大的股票
        if '涨跌幅' in df.columns:
            print("\n获取涨幅最大的10只股票...")
            top_gainers = get_top_stocks_by_metric(df, '涨跌幅', 10)
            
            if not top_gainers.empty:
                print(f"✓ 涨幅前10名:")
                display_columns = ['股票代码', '股票名称', '涨跌幅', '最新价']
                available_columns = [col for col in display_columns if col in top_gainers.columns]
                print(top_gainers[available_columns])
                
    except Exception as e:
        print(f"✗ 数据分析演示出错: {e}")


def demo_scraper_direct_usage():
    """演示直接使用爬虫类"""
    print("\n" + "=" * 60)
    print("7. 直接使用爬虫类演示")
    print("=" * 60)
    
    try:
        # 创建爬虫实例
        scraper = StockListScraper()
        
        print("爬虫配置信息:")
        print(f"  支持的市场类型: {scraper.get_supported_markets()}")
        print(f"  输出目录: {scraper.output_dir}")
        print(f"  API URL: {scraper.config.STOCK_LIST_URL}")
        
        # 获取支持的市场类型
        print("\n支持的市场类型详情:")
        for market in StockMarket:
            print(f"  {market.value}: {scraper.config.MARKET_FILTERS[market]}")
        
        print("\n字段映射示例:")
        field_samples = list(scraper.config.FIELD_MAPPING.items())[:5]
        for field_key, field_name in field_samples:
            print(f"  {field_key} -> {field_name}")
        
        print("\n✓ 爬虫类直接使用演示完成")
        
    except Exception as e:
        print(f"✗ 爬虫类使用演示出错: {e}")


def main():
    """主函数"""
    print("东方财富股票列表数据获取使用示例")
    print("=" * 60)
    print("本示例将演示股票列表数据获取的各种功能")
    print("注意: 部分功能需要网络连接，请确保网络正常")
    print("=" * 60)
    
    # 运行各个演示
    demo_basic_usage()
    demo_stock_list_data()
    demo_basic_info()
    demo_search_stocks()
    demo_market_overview()
    demo_data_analysis()
    demo_scraper_direct_usage()
    
    print("\n" + "=" * 60)
    print("股票列表数据获取使用示例演示完成！")
    print("=" * 60)
    
    print("\n快速开始代码片段:")
    print("```python")
    print("from eastmoney_scraper import get_all_stock_codes, get_stock_list, search_stocks")
    print("")
    print("# 获取所有股票代码")
    print("codes = get_all_stock_codes()")
    print("print(f'总共 {len(codes)} 只股票')")
    print("")
    print("# 获取创业板股票")
    print("chinext_codes = get_all_stock_codes(market='chinext')")
    print("print(f'创业板 {len(chinext_codes)} 只股票')")
    print("")
    print("# 搜索银行股")
    print("bank_stocks = search_stocks('银行')")
    print("print(f'找到 {len(bank_stocks)} 只银行股')")
    print("```")


if __name__ == "__main__":
    main()