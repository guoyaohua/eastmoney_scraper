"""
个股资金流向爬虫使用示例
展示重构后的StockCapitalFlowScraper的各种用法
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import StockCapitalFlowScraper, MarketType, StockCapitalFlowMonitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'stock_capital_flow_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

def example_single_scrape():
    """示例1: 单次爬取全市场数据"""
    print("=" * 80)
    print("示例1: 单次爬取全市场个股资金流向数据")
    print("=" * 80)
    
    # 创建爬虫实例（全市场）
    scraper = StockCapitalFlowScraper(market_type=MarketType.ALL, output_dir="output")
    
    # 执行一次爬取，获取前5页数据，保存为CSV
    df, filepath = scraper.run_once(max_pages=5, save_format='csv')
    
    if not df.empty:
        print(f"✅ 成功爬取 {len(df)} 条数据")
        print(f"📁 数据已保存到: {filepath}")
        
        # 显示一些统计信息
        summary = scraper.analyze_market_summary(df)
        print(f"\n📊 市场概况:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # 显示主力净流入前10名
        top_inflow = scraper.get_top_inflow_stocks(df, 10)
        print(f"\n🔥 主力净流入前10名:")
        print(top_inflow[['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比']])
        
    else:
        print("❌ 未获取到数据")


def example_market_specific_scrape():
    """示例2: 爬取特定市场数据"""
    print("\n" + "=" * 80)
    print("示例2: 爬取创业板个股资金流向数据")
    print("=" * 80)
    
    # 创建创业板爬虫实例
    scraper = StockCapitalFlowScraper(
        market_type=MarketType.GEM,
        output_dir="output"
    )
    
    # 爬取数据并保存为JSON格式
    df, filepath = scraper.run_once(max_pages=3, save_format='json')
    
    if not df.empty:
        print(f"✅ 成功爬取创业板 {len(df)} 条数据")
        print(f"📁 JSON数据已保存到: {filepath}")
        
        # 分析创业板市场情况
        summary = scraper.analyze_market_summary(df)
        print(f"\n📊 创业板市场概况:")
        print(f"   总股票数: {summary.get('总股票数', 0)}")
        print(f"   主力净流入股票数: {summary.get('主力净流入股票数', 0)}")
        print(f"   市场主力净流入总额: {summary.get('市场主力净流入总额(万元)', 0)} 万元")
        print(f"   上涨股票数: {summary.get('上涨股票数', 0)}")
        
    else:
        print("❌ 未获取到创业板数据")


def example_scheduled_scraping():
    """示例3: 定时爬取（演示模式，运行30秒后停止）"""
    print("\n" + "=" * 80)
    print("示例3: 定时爬取演示（运行30秒）")
    print("=" * 80)
    
    # 创建科创板爬虫实例
    scraper = StockCapitalFlowScraper(
        market_type=MarketType.STAR,
        output_dir="output"
    )
    
    print("开始定时爬取科创板数据，每20秒爬取一次...")
    print("(演示模式，30秒后自动停止)")
    
    import threading
    import time
    
    # 启动定时爬取（在新线程中运行）
    def run_scraping():
        scraper.start_scheduled_scraping(interval_seconds=20, max_pages=2, save_format='both')
    
    scrape_thread = threading.Thread(target=run_scraping, daemon=True)
    scrape_thread.start()
    
    # 等待30秒后停止
    time.sleep(30)
    scraper.stop()
    print("✅ 定时爬取演示结束")


def example_monitoring():
    """示例4: 实时监控（演示模式，运行1分钟后停止）"""
    print("\n" + "=" * 80)
    print("示例4: 实时监控演示（运行1分钟）")
    print("=" * 80)
    
    # 创建监控器
    monitor = StockCapitalFlowMonitor(
        market_type=MarketType.MAIN_BOARD,
        output_dir="output"
    )
    
    print("开始实时监控主板资金流向...")
    print("(演示模式，1分钟后自动停止)")
    
    import threading
    import time
    
    # 启动监控（在新线程中运行）
    def run_monitoring():
        monitor.start_monitoring(
            scrape_interval=30,  # 30秒爬取一次
            display_interval=15,  # 15秒刷新显示一次
            max_pages=2,
            save_format='csv'
        )
    
    monitor_thread = threading.Thread(target=run_monitoring, daemon=True)
    monitor_thread.start()
    
    # 等待60秒后停止
    time.sleep(60)
    monitor.stop_monitoring()
    print("✅ 实时监控演示结束")


def example_data_analysis():
    """示例5: 数据分析功能演示"""
    print("\n" + "=" * 80)
    print("示例5: 数据分析功能演示")
    print("=" * 80)
    
    # 先爬取一些数据
    scraper = StockCapitalFlowScraper(market_type=MarketType.ALL, output_dir="output")
    df, _ = scraper.run_once(max_pages=3, save_format='csv')
    
    if df.empty:
        print("❌ 无法获取数据进行分析")
        return
    
    print(f"📊 基于 {len(df)} 条数据进行分析:")
    
    # 获取主力净流入最多的股票
    top_inflow = scraper.get_top_inflow_stocks(df, 5)
    print(f"\n🔥 主力净流入TOP5:")
    for _, row in top_inflow.iterrows():
        print(f"   {row['股票名称']}({row['股票代码']}): {row['主力净流入']:.2f}万元 ({row['主力净流入占比']:.2f}%)")
    
    # 获取主力净流出最多的股票
    top_outflow = scraper.get_top_outflow_stocks(df, 5)
    print(f"\n❄️ 主力净流出TOP5:")
    for _, row in top_outflow.iterrows():
        print(f"   {row['股票名称']}({row['股票代码']}): {row['主力净流入']:.2f}万元 ({row['主力净流入占比']:.2f}%)")
    
    # 市场概况分析
    summary = scraper.analyze_market_summary(df)
    print(f"\n📈 市场概况:")
    print(f"   主力净流入股票数: {summary.get('主力净流入股票数', 0)} / {summary.get('总股票数', 0)}")
    print(f"   上涨股票数: {summary.get('上涨股票数', 0)} / {summary.get('总股票数', 0)}")
    print(f"   市场总净流入: {summary.get('市场主力净流入总额(万元)', 0):.2f} 万元")


def main():
    """主函数 - 运行所有示例"""
    print("🚀 个股资金流向爬虫使用示例")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 运行各个示例
        example_single_scrape()
        example_market_specific_scrape()
        example_data_analysis()
        
        # 询问是否运行定时任务示例
        print("\n" + "=" * 80)
        response = input("是否运行定时爬取和监控示例？(y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            example_scheduled_scraping()
            example_monitoring()
        else:
            print("⏭️ 跳过定时任务示例")
        
        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成!")
        print("💡 提示: 查看生成的数据文件和日志以了解更多详情")
        print("📁 数据文件保存在各自的输出目录中")
        
    except KeyboardInterrupt:
        print("\n⚡ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()