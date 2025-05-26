"""
东方财富个股资金流向爬虫 - 快速开始
Quick start guide for EastMoney Capital Flow Scraper
"""

try:
    from .eastmoney_capital_flow_scraper import CapitalFlowScraper
except ImportError:
    from eastmoney_capital_flow_scraper import CapitalFlowScraper
import time

def quickstart():
    """快速开始示例"""
    print("=" * 60)
    print("东方财富个股资金流向爬虫 - 快速开始")
    print("=" * 60)
    print()
    
    # 创建爬虫实例
    scraper = CapitalFlowScraper()
    
    print("1. 执行单次爬取...")
    print("-" * 40)
    
    # 执行单次爬取
    df = scraper.scrape_once(save_to_file=True)
    
    if df is not None and not df.empty:
        print(f"\n✓ 成功爬取 {len(df)} 条数据")
        
        # 显示主力净流入TOP5
        print("\n主力净流入TOP5:")
        print("-" * 60)
        top5 = df.nlargest(5, '主力净流入')
        for idx, row in top5.iterrows():
            print(f"{row['股票代码']} {row['股票名称']:<8} "
                  f"最新价: {row['最新价']:>8.2f} "
                  f"涨跌幅: {row['涨跌幅']:>6.2f}% "
                  f"主力净流入: {row['主力净流入']:>10.2f}万")
        
        # 显示主力净流出TOP5
        print("\n主力净流出TOP5:")
        print("-" * 60)
        bottom5 = df.nsmallest(5, '主力净流入')
        for idx, row in bottom5.iterrows():
            print(f"{row['股票代码']} {row['股票名称']:<8} "
                  f"最新价: {row['最新价']:>8.2f} "
                  f"涨跌幅: {row['涨跌幅']:>6.2f}% "
                  f"主力净流入: {row['主力净流入']:>10.2f}万")
        
        # 基本统计
        print("\n基本统计信息:")
        print("-" * 40)
        print(f"主力净流入总额: {df['主力净流入'].sum():,.2f}万")
        print(f"平均主力净流入: {df['主力净流入'].mean():.2f}万")
        print(f"流入股票数量: {len(df[df['主力净流入'] > 0])}")
        print(f"流出股票数量: {len(df[df['主力净流入'] < 0])}")
        print(f"平均涨跌幅: {df['涨跌幅'].mean():.2f}%")
        
        print("\n数据已保存到 capital_flow_data 目录")
        
        # 询问是否继续定时爬取
        print("\n" + "=" * 60)
        user_input = input("是否开始定时爬取？(每10秒更新一次) [y/N]: ")
        
        if user_input.lower() == 'y':
            print("\n开始定时爬取，按 Ctrl+C 停止...")
            print("-" * 40)
            scraper.start_scheduled_scraping(interval=10)
        else:
            print("\n程序结束。")
    else:
        print("\n✗ 爬取失败，请检查网络连接或API状态")


def test_connection():
    """测试连接"""
    print("\n测试API连接...")
    try:
        from .eastmoney_capital_flow_scraper import DataFetcher, CapitalFlowConfig
    except ImportError:
        from eastmoney_capital_flow_scraper import DataFetcher, CapitalFlowConfig
    
    config = CapitalFlowConfig()
    fetcher = DataFetcher(config)
    
    try:
        result = fetcher.fetch_data(page=1, page_size=1)
        if result and 'data' in result:
            print("✓ API连接正常")
            return True
        else:
            print("✗ API返回数据异常")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


if __name__ == "__main__":
    # 先测试连接
    if test_connection():
        # 运行快速开始
        quickstart()
    else:
        print("\n请检查网络连接后重试")