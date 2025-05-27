"""
东方财富个股资金流向数据快速入门指南
EastMoney Individual Stock Capital Flow Quick Start Guide

本文件提供个股资金流向功能的快速入门示例，包括：
- 快速数据获取和展示
- 基础统计分析
- 连接测试和错误处理
- 定时监控入门

This file provides a quick start guide for individual stock capital flow features, including:
- Quick data fetching and display
- Basic statistical analysis
- Connection testing and error handling
- Scheduled monitoring introduction
"""

import sys
import os
import time
from datetime import datetime
from typing import Optional

# 添加父目录到Python路径以便导入eastmoney_scraper包
# (Add parent directory to Python path for importing eastmoney_scraper package)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入eastmoney_scraper的接口函数和类
# (Import interface functions and classes from eastmoney_scraper)
from eastmoney_scraper import (
    get_stock_capital_flow,    # 获取个股资金流向数据的便捷函数
    CapitalFlowScraper,        # 个股资金流向爬虫核心类
    StockCapitalFlowMonitor    # 个股资金流向监控器类
)
import pandas as pd

# 设置pandas显示选项
# (Configure pandas display options)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def test_api_connection() -> bool:
    """
    测试API连接是否正常
    Test if API connection is working properly
    
    Returns:
        bool: 连接成功返回True，失败返回False
    """
    print("🔗 测试API连接...")
    
    try:
        # 尝试获取少量数据进行连接测试
        # (Try to fetch a small amount of data for connection testing)
        test_df = get_stock_capital_flow(max_pages=1, save_to_file=False)
        
        if test_df is not None and not test_df.empty:
            print("✅ API连接正常")
            print(f"   测试获取到 {len(test_df)} 条数据")
            return True
        else:
            print("❌ API返回数据异常或为空")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


def quickstart_data_fetching():
    """
    快速开始：个股资金流向数据获取
    Quick start: Individual stock capital flow data fetching
    
    展示如何快速获取和分析个股资金流向数据
    """
    print("=" * 80)
    print("📊 快速开始：个股资金流向数据获取")
    print("=" * 80)
    
    print("⏳ 正在获取个股资金流向数据...")
    print("   提示：首次运行可能需要10-30秒，请耐心等待")
    
    # 获取个股资金流向数据（前2页，约200只股票）
    # (Get individual stock capital flow data - first 2 pages, about 200 stocks)
    df = get_stock_capital_flow(
        max_pages=2,          # 限制页数以加快速度
        save_to_file=True     # 保存数据到文件
    )
    
    if df is None or df.empty:
        print("❌ 未能获取到数据，请检查网络连接或稍后重试")
        return None
    
    print(f"✅ 成功获取 {len(df)} 只股票的资金流向数据")
    
    # 1. 显示主力净流入TOP10
    # (Display top 10 stocks by main capital inflow)
    print(f"\n💎 主力净流入TOP10：")
    print("─" * 80)
    top_10_inflow = df.nlargest(10, '主力净流入')
    
    print(f"{'排名':<4} {'股票代码':<8} {'股票名称':<10} {'最新价':<8} {'涨跌幅':<8} {'主力净流入':<12} {'占比':<8}")
    print("─" * 80)
    
    for idx, (_, stock) in enumerate(top_10_inflow.iterrows(), 1):
        print(f"{idx:<4} {stock['股票代码']:<8} {stock['股票名称']:<10} "
              f"{stock['最新价']:>7.2f} {stock['涨跌幅']:>+6.2f}% "
              f"{stock['主力净流入']:>10.0f}万 {stock['主力净流入占比']:>6.1f}%")
    
    # 2. 显示主力净流出TOP5
    # (Display top 5 stocks by main capital outflow)
    print(f"\n💸 主力净流出TOP5：")
    print("─" * 80)
    top_5_outflow = df.nsmallest(5, '主力净流入')
    
    print(f"{'排名':<4} {'股票代码':<8} {'股票名称':<10} {'最新价':<8} {'涨跌幅':<8} {'主力净流出':<12}")
    print("─" * 80)
    
    for idx, (_, stock) in enumerate(top_5_outflow.iterrows(), 1):
        print(f"{idx:<4} {stock['股票代码']:<8} {stock['股票名称']:<10} "
              f"{stock['最新价']:>7.2f} {stock['涨跌幅']:>+6.2f}% "
              f"{abs(stock['主力净流入']):>10.0f}万")
    
    # 3. 基础统计分析
    # (Basic statistical analysis)
    print(f"\n📊 基础统计分析：")
    print("─" * 50)
    
    # 资金流向统计
    inflow_stocks = df[df['主力净流入'] > 0]
    outflow_stocks = df[df['主力净流入'] < 0]
    
    total_inflow = inflow_stocks['主力净流入'].sum()
    total_outflow = abs(outflow_stocks['主力净流入'].sum())
    net_inflow = total_inflow - total_outflow
    
    print(f"• 主力净流入股票数量：{len(inflow_stocks)} 只 ({len(inflow_stocks)/len(df)*100:.1f}%)")
    print(f"• 主力净流出股票数量：{len(outflow_stocks)} 只 ({len(outflow_stocks)/len(df)*100:.1f}%)")
    print(f"• 主力总流入：{total_inflow:,.0f} 万元")
    print(f"• 主力总流出：{total_outflow:,.0f} 万元")
    print(f"• 主力净流入：{net_inflow:+,.0f} 万元")
    
    # 涨跌幅统计
    rising_stocks = df[df['涨跌幅'] > 0]
    falling_stocks = df[df['涨跌幅'] < 0]
    
    print(f"• 上涨股票数量：{len(rising_stocks)} 只 ({len(rising_stocks)/len(df)*100:.1f}%)")
    print(f"• 下跌股票数量：{len(falling_stocks)} 只 ({len(falling_stocks)/len(df)*100:.1f}%)")
    print(f"• 平均涨跌幅：{df['涨跌幅'].mean():+.2f}%")
    
    # 4. 投资机会筛选
    # (Investment opportunity screening)
    print(f"\n🎯 投资机会筛选：")
    print("─" * 50)
    
    # 筛选条件：主力净流入>5000万 且 涨幅>2% 且 主力净流入占比>5%
    investment_opportunities = df[
        (df['主力净流入'] > 5000) & 
        (df['涨跌幅'] > 2) & 
        (df['主力净流入占比'] > 5)
    ]
    
    if not investment_opportunities.empty:
        print(f"发现 {len(investment_opportunities)} 只潜在投资机会股票：")
        print("筛选条件：主力净流入>5000万 + 涨幅>2% + 占比>5%")
        print()
        
        for _, stock in investment_opportunities.head(5).iterrows():
            print(f"⭐ {stock['股票名称']} ({stock['股票代码']})：")
            print(f"   涨幅 {stock['涨跌幅']:+.2f}%，主力流入 {stock['主力净流入']:,.0f}万 ({stock['主力净流入占比']:.1f}%)")
    else:
        print("当前未发现符合条件的投资机会股票")
        print("建议调整筛选条件或稍后再试")
    
    # 5. 数据保存提示
    # (Data save notification)
    print(f"\n💾 数据保存信息：")
    print("─" * 50)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(current_dir, "capital_flow_data")
    print(f"数据已保存到：{data_dir}")
    print("包含格式：CSV文件、JSON文件、SQLite数据库")
    
    return df


def quickstart_advanced_scraper():
    """
    快速开始：使用高级爬虫类
    Quick start: Using advanced scraper class
    
    展示如何使用CapitalFlowScraper类进行更精细的控制
    """
    print(f"\n" + "=" * 80)
    print("🔧 快速开始：使用高级爬虫类")
    print("=" * 80)
    
    # 创建爬虫实例
    # (Create scraper instance)
    scraper = CapitalFlowScraper()
    
    print("⚙️ 使用 CapitalFlowScraper 类可以获得更多控制权：")
    print("  • 自定义数据存储路径")
    print("  • 精确控制爬取参数")
    print("  • 定时自动爬取")
    print("  • 更详细的日志记录")
    
    print(f"\n⏳ 执行高级爬取...")
    
    # 执行爬取并保存
    df = scraper.scrape_once(save_to_file=True)
    
    if df is not None and not df.empty:
        print(f"✅ 高级爬虫成功获取 {len(df)} 只股票数据")
        
        # 显示数据概览
        print(f"\n📋 数据概览：")
        high_inflow_count = len(df[df['主力净流入'] > 10000])  # >1亿
        high_ratio_count = len(df[df['主力净流入占比'] > 10])   # >10%
        
        print(f"  • 主力流入超1亿的股票：{high_inflow_count} 只")
        print(f"  • 主力流入占比超10%的股票：{high_ratio_count} 只")
        
        return scraper
    else:
        print("❌ 高级爬虫获取数据失败")
        return None


def quickstart_monitoring_demo(scraper: Optional[CapitalFlowScraper] = None):
    """
    快速开始：监控演示
    Quick start: Monitoring demonstration
    
    展示如何使用监控功能
    """
    print(f"\n" + "=" * 80)
    print("📡 快速开始：实时监控演示")
    print("=" * 80)
    
    print("🔄 实时监控功能可以：")
    print("  • 定时自动获取最新数据")
    print("  • 发现异常股票和投资机会")
    print("  • 提供实时数据更新回调")
    print("  • 自动保存历史数据")
    
    # 询问用户是否要启动监控演示
    user_choice = input(f"\n是否启动30秒监控演示？(y/N): ").strip().lower()
    
    if user_choice == 'y':
        print(f"\n🚀 启动监控演示（30秒）...")
        
        # 创建监控器
        monitor = StockCapitalFlowMonitor()
        
        # 定义简单的回调函数
        def simple_callback(df_update):
            current_time = datetime.now().strftime("%H:%M:%S")
            if not df_update.empty:
                top_stock = df_update.iloc[0]
                print(f"[{current_time}] 数据更新：{len(df_update)}只股票，"
                      f"最大流入 {top_stock['股票名称']} {top_stock['主力净流入']:.0f}万")
        
        # 设置回调并启动监控
        monitor.set_callback(simple_callback)
        monitor.start(interval=15)  # 15秒间隔
        
        try:
            print("📊 监控运行中...")
            time.sleep(30)  # 运行30秒
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断监控")
        finally:
            monitor.stop()
            print("✅ 监控演示结束")
    else:
        print("跳过监控演示")


def main():
    """
    主函数：个股资金流向快速入门流程
    Main function: Quick start process for individual stock capital flow
    """
    print("🎯 东方财富个股资金流向数据 - 快速入门指南")
    print("🕒 开始时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 步骤1：测试连接
    print("📶 步骤1：测试API连接")
    if not test_api_connection():
        print("\n❌ API连接失败，请检查网络连接后重试")
        print("💡 可能的解决方案：")
        print("  • 检查网络连接")
        print("  • 确认防火墙设置")
        print("  • 稍后重试（可能是临时网络问题）")
        return
    
    # 步骤2：快速数据获取
    print(f"\n📈 步骤2：快速数据获取与分析")
    df = quickstart_data_fetching()
    
    if df is None:
        print("❌ 数据获取失败，无法继续后续步骤")
        return
    
    # 步骤3：高级爬虫演示
    print(f"\n🔧 步骤3：高级爬虫功能演示")
    advanced_scraper = quickstart_advanced_scraper()
    
    # 步骤4：监控功能演示
    print(f"\n📡 步骤4：实时监控功能演示")
    quickstart_monitoring_demo(advanced_scraper)
    
    # 结束总结
    print(f"\n" + "=" * 80)
    print("✅ 快速入门指南完成！")
    print("=" * 80)
    
    print("🎓 你已经学会了：")
    print("  ✓ 快速获取个股资金流向数据")
    print("  ✓ 进行基础的数据分析和筛选")
    print("  ✓ 使用高级爬虫类进行精确控制")
    print("  ✓ 使用实时监控功能")
    
    print(f"\n📚 下一步学习建议：")
    print("  • 查看 examples/basic_usage.py - 基础功能详细示例")
    print("  • 查看 examples/advanced_usage.py - 高级功能和分析")
    print("  • 查看 examples/monitor_usage.py - 监控功能详解")
    print("  • 阅读 README.md - 完整功能文档")
    
    print(f"\n🕒 结束时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)


if __name__ == "__main__":
    main()