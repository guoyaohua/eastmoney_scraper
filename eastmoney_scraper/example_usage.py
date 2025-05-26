"""
东方财富个股资金流向爬虫使用示例
"""

from .eastmoney_capital_flow_scraper import CapitalFlowScraper
from .capital_flow_monitor import CapitalFlowMonitor, CapitalFlowAnalyzer
import pandas as pd

def example_single_scrape():
    """单次爬取示例"""
    print("=== 单次爬取示例 ===")
    
    # 创建爬虫实例
    scraper = CapitalFlowScraper()
    
    # 执行单次爬取
    df = scraper.scrape_once(save_to_file=True)
    
    if df is not None:
        print(f"\n成功爬取 {len(df)} 条数据")
        print("\n主力净流入TOP10:")
        print("-" * 80)
        top10 = df.nlargest(10, '主力净流入')[['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比']]
        print(top10.to_string(index=False))
        
        print("\n主力净流出TOP10:")
        print("-" * 80)
        bottom10 = df.nsmallest(10, '主力净流入')[['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比']]
        print(bottom10.to_string(index=False))


def example_scheduled_scraping():
    """定时爬取示例"""
    print("\n=== 定时爬取示例 ===")
    print("每10秒执行一次爬取，按Ctrl+C停止")
    
    scraper = CapitalFlowScraper()
    # 开始定时爬取（每10秒）
    scraper.start_scheduled_scraping(interval=10)


def example_data_analysis():
    """数据分析示例"""
    print("\n=== 数据分析示例 ===")
    
    # 创建分析器实例
    analyzer = CapitalFlowAnalyzer()
    
    # 获取最新数据
    latest_data = analyzer.get_latest_data(limit=100)
    if not latest_data.empty:
        print(f"\n数据库中有 {len(latest_data)} 条最新记录")
        
        # 获取主力净流入最多的股票
        top_inflow = analyzer.get_top_inflow_stocks(top_n=10)
        if not top_inflow.empty:
            print("\n主力净流入TOP10:")
            print(top_inflow.to_string(index=False))
        
        # 获取连续流入的股票
        continuous = analyzer.get_continuous_inflow_stocks(days=3)
        if not continuous.empty:
            print("\n连续3日主力净流入的股票:")
            print(continuous.head(10).to_string(index=False))
        
        # 分析板块资金流向
        sector_flow = analyzer.analyze_sector_flow()
        if not sector_flow.empty:
            print("\n板块资金流向:")
            print(sector_flow.to_string())
    else:
        print("数据库中暂无数据，请先运行爬虫获取数据")


def example_realtime_monitor():
    """实时监控示例"""
    print("\n=== 实时监控示例 ===")
    print("启动实时监控面板...")
    print("数据每10秒更新，显示每30秒刷新")
    print("按Ctrl+C停止监控")
    
    # 创建监控器实例
    monitor = CapitalFlowMonitor()
    
    # 开始监控
    monitor.start_monitoring(interval=10, display_interval=30)


def example_custom_analysis():
    """自定义分析示例"""
    print("\n=== 自定义分析示例 ===")
    
    # 直接读取CSV文件进行分析
    import os
    import glob
    
    # 查找最新的CSV文件
    csv_files = glob.glob("capital_flow_data/capital_flow_*.csv")
    if csv_files:
        latest_csv = max(csv_files, key=os.path.getctime)
        print(f"读取文件: {latest_csv}")
        
        df = pd.read_csv(latest_csv)
        
        # 自定义分析1: 找出主力净流入占比超过10%的股票
        high_ratio_stocks = df[df['主力净流入占比'] > 10].sort_values('主力净流入占比', ascending=False)
        print(f"\n主力净流入占比超过10%的股票 ({len(high_ratio_stocks)}只):")
        if not high_ratio_stocks.empty:
            print(high_ratio_stocks[['股票代码', '股票名称', '涨跌幅', '主力净流入', '主力净流入占比']].head(20).to_string(index=False))
        
        # 自定义分析2: 统计各个涨跌幅区间的平均主力净流入
        print("\n各涨跌幅区间的平均主力净流入:")
        df['涨跌幅区间'] = pd.cut(df['涨跌幅'], 
                              bins=[-11, -5, -2, 0, 2, 5, 11],
                              labels=['跌停区', '大跌区', '小跌区', '小涨区', '大涨区', '涨停区'])
        
        stats = df.groupby('涨跌幅区间')['主力净流入'].agg(['mean', 'count'])
        stats.columns = ['平均净流入(万)', '股票数量']
        print(stats.to_string())
        
        # 自定义分析3: 相关性分析
        print("\n相关性分析:")
        correlation = df[['涨跌幅', '主力净流入', '超大单净流入', '大单净流入', '中单净流入', '小单净流入']].corr()
        print(correlation['涨跌幅'].sort_values(ascending=False).to_string())
    else:
        print("未找到CSV文件，请先运行爬虫")


def main():
    """主函数 - 选择运行模式"""
    print("东方财富个股资金流向爬虫")
    print("=" * 50)
    print("请选择运行模式:")
    print("1. 单次爬取")
    print("2. 定时爬取（每10秒）")
    print("3. 数据分析")
    print("4. 实时监控")
    print("5. 自定义分析")
    print("0. 退出")
    
    while True:
        choice = input("\n请输入选项 (0-5): ")
        
        if choice == '1':
            example_single_scrape()
        elif choice == '2':
            example_scheduled_scraping()
            break
        elif choice == '3':
            example_data_analysis()
        elif choice == '4':
            example_realtime_monitor()
            break
        elif choice == '5':
            example_custom_analysis()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()