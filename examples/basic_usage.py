"""
东方财富数据爬虫基础使用示例
EastMoney Scraper Basic Usage Examples

本文件展示了eastmoney_scraper包的基础功能使用方法，包括：
- 概念板块数据获取与分析
- 个股资金流向数据获取
- 数据筛选与统计分析
- 实时行情数据获取

This file demonstrates basic usage of the eastmoney_scraper package, including:
- Concept sector data fetching and analysis
- Individual stock capital flow data fetching
- Data filtering and statistical analysis
- Real-time quote data fetching
"""

import sys
import os
import pandas as pd
from datetime import datetime
import logging

# 添加父目录到Python路径以便导入eastmoney_scraper包
# (Add parent directory to Python path for importing eastmoney_scraper package)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入eastmoney_scraper的主要功能接口
# (Import main functional interfaces from eastmoney_scraper)
from eastmoney_scraper import (
    get_concept_sectors,          # 获取概念板块综合数据 (Get comprehensive concept sector data)
    get_concept_sectors_realtime, # 获取概念板块实时行情 (Get real-time concept sector quotes)
    get_stock_capital_flow,       # 获取个股资金流向数据 (Get individual stock capital flow data)
    filter_sectors_by_change,     # 根据涨跌幅筛选板块 (Filter sectors by price change)
    filter_sectors_by_capital,    # 根据资金流向筛选板块 (Filter sectors by capital flow)
    get_top_sectors               # 获取表现最佳的板块 (Get top-performing sectors)
)

# 配置日志格式，包含文件名、行号和函数名
# (Configure logging format with filename, line number and function name)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 设置pandas显示选项以获得更好的输出格式
# (Configure pandas display options for better output formatting)
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def example_1_comprehensive_sector_data():
    """
    示例1：获取概念板块综合数据（包含行情和资金流向）
    Example 1: Get comprehensive concept sector data (including quotes and capital flow)
    
    本示例展示如何获取包含实时行情和资金流向的完整概念板块数据，
    并进行基础的数据分析和统计。
    """
    print("=" * 80)
    print("📊 示例1：获取概念板块综合数据（行情 + 资金流向）")
    print("=" * 80)
    
    try:
        logger.info("开始获取概念板块综合数据")
        # 获取完整的概念板块数据，包含今日、5日、10日资金流向
        # (Get complete concept sector data including today, 5-day, 10-day capital flow)
        print("⏳ 正在获取概念板块数据...")
        comprehensive_data_df = get_concept_sectors(
            include_capital_flow=True,  # 包含资金流向数据 (Include capital flow data)
            periods=['today', '5day', '10day']  # 获取多个周期的资金流向 (Get multiple periods of capital flow)
        )
        print(comprehensive_data_df.columns.tolist())  # 输出列名以便调试 (Output column names for debugging)
        comprehensive_data_df.to_csv('comprehensive_concept_sectors.csv', index=False, encoding='utf-8')  # 保存数据到CSV文件 (Save data to CSV file)
        
        if comprehensive_data_df.empty:
            logger.warning("未获取到概念板块数据")
            print("❌ 未获取到数据，请检查网络连接或稍后重试")
            return
            
        logger.info(f"成功获取 {len(comprehensive_data_df)} 个概念板块的综合数据")
        print(f"✅ 成功获取 {len(comprehensive_data_df)} 个概念板块的综合数据")
        
        # 显示涨幅前10的板块
        # (Display top 10 sectors by price change)
        print("\n📈 今日涨幅前10的概念板块：")
        top_gainers = comprehensive_data_df.nlargest(10, '涨跌幅')
        display_columns = ['板块名称', '涨跌幅', '最新价', '成交额']
        
        # 安全检查资金流向列是否存在
        # (Safely check if capital flow columns exist)
        if '主力净流入' in comprehensive_data_df.columns:
            display_columns.append('主力净流入')
        if '5日主力净流入' in comprehensive_data_df.columns:
            display_columns.append('5日主力净流入')
            
        print(top_gainers[display_columns].to_string(index=False))
        
        # 市场统计分析
        # (Market statistical analysis)
        print(f"\n📊 市场统计分析：")
        rising_sectors = len(comprehensive_data_df[comprehensive_data_df['涨跌幅'] > 0])
        falling_sectors = len(comprehensive_data_df[comprehensive_data_df['涨跌幅'] < 0])
        flat_sectors = len(comprehensive_data_df[comprehensive_data_df['涨跌幅'] == 0])
        
        total_sectors = len(comprehensive_data_df)
        print(f"   • 上涨板块：{rising_sectors} 个 ({rising_sectors/total_sectors*100:.1f}%)")
        print(f"   • 下跌板块：{falling_sectors} 个 ({falling_sectors/total_sectors*100:.1f}%)")
        print(f"   • 平盘板块：{flat_sectors} 个 ({flat_sectors/total_sectors*100:.1f}%)")
        
        # 资金流向统计
        # (Capital flow statistics)
        if '主力净流入' in comprehensive_data_df.columns:
            total_inflow = comprehensive_data_df[comprehensive_data_df['主力净流入'] > 0]['主力净流入'].sum()
            total_outflow = abs(comprehensive_data_df[comprehensive_data_df['主力净流入'] < 0]['主力净流入'].sum())
            net_inflow = total_inflow - total_outflow
            
            print(f"\n💰 资金流向统计：")
            print(f"   • 总流入：{total_inflow:,.0f} 万元")
            print(f"   • 总流出：{total_outflow:,.0f} 万元")
            print(f"   • 净流入：{net_inflow:,.0f} 万元")
        else:
            logger.warning("数据中未包含主力净流入字段")
            print("\n💰 资金流向统计：数据中未包含资金流向信息")
            
    except Exception as e:
        logger.error(f"获取概念板块综合数据时发生错误: {e}", exc_info=True)
        print(f"❌ 获取数据时发生错误：{e}")


def example_2_realtime_quotes():
    """
    示例2：快速获取概念板块实时行情（不包含资金流向）
    Example 2: Quick fetching of real-time concept sector quotes (without capital flow)
    
    当只需要快速获取行情数据而不需要资金流向时，
    使用此方法可以大幅提升数据获取速度。
    """
    print("\n" + "=" * 80)
    print("⚡ 示例2：快速获取概念板块实时行情")
    print("=" * 80)
    
    try:
        logger.info("开始获取概念板块实时行情")
        # 快速获取实时行情数据
        # (Quick fetch of real-time quote data)
        print("⏳ 正在快速获取实时行情...")
        realtime_quotes_df = get_concept_sectors_realtime()
        
        if realtime_quotes_df.empty:
            logger.warning("未获取到实时行情数据")
            print("❌ 未获取到实时行情数据")
            return
            
        logger.info(f"成功获取 {len(realtime_quotes_df)} 个板块的实时行情")
        print(f"✅ 成功获取 {len(realtime_quotes_df)} 个板块的实时行情")
        
        # 显示成交额最大的前5个板块
        # (Display top 5 sectors by trading volume)
        print("\n💵 成交额最大的前5个板块：")
        top_volume_sectors = realtime_quotes_df.nlargest(5, '成交额')
        volume_display_columns = ['板块名称', '涨跌幅', '最新价', '成交额']
        if '换手率' in realtime_quotes_df.columns:
            volume_display_columns.append('换手率')
        print(top_volume_sectors[volume_display_columns].to_string(index=False))
        
        # 显示波动最大的板块
        # (Display most volatile sectors)
        print("\n📊 今日波动统计：")
        max_gain = realtime_quotes_df['涨跌幅'].max()
        max_loss = realtime_quotes_df['涨跌幅'].min()
        avg_change = realtime_quotes_df['涨跌幅'].mean()
        
        print(f"   • 最大涨幅：{max_gain:.2f}%")
        print(f"   • 最大跌幅：{max_loss:.2f}%")
        print(f"   • 平均涨跌幅：{avg_change:.2f}%")
        
    except Exception as e:
        logger.error(f"获取实时行情时发生错误: {e}", exc_info=True)
        print(f"❌ 获取实时行情时发生错误：{e}")


def example_3_stock_capital_flow():
    """
    示例3：获取个股资金流向数据
    Example 3: Get individual stock capital flow data
    
    展示如何获取个股资金流向排行数据，并进行分析。
    """
    print("\n" + "=" * 80)
    print("🏦 示例3：获取个股资金流向数据")
    print("=" * 80)
    
    try:
        logger.info("开始获取个股资金流向数据")
        # 获取个股资金流向数据（前2页约200只股票）
        # (Get individual stock capital flow data - first 2 pages, about 200 stocks)
        print("⏳ 正在获取个股资金流向数据...")
        stock_capital_flow_df = get_stock_capital_flow(
            max_pages=2,  # 限制爬取页数以控制时间 (Limit pages to control time)
            save_to_file=False  # 不保存到文件 (Don't save to file)
        )
        
        if stock_capital_flow_df.empty:
            logger.warning("未获取到个股资金流向数据")
            print("❌ 未获取到个股资金流向数据")
            return
            
        logger.info(f"成功获取 {len(stock_capital_flow_df)} 只股票的资金流向数据")
        print(f"✅ 成功获取 {len(stock_capital_flow_df)} 只股票的资金流向数据")
        
        # 显示主力净流入前10的股票
        # (Display top 10 stocks by main capital net inflow)
        print("\n💹 主力净流入前10的股票：")
        top_inflow_stocks = stock_capital_flow_df.nlargest(10, '主力净流入')
        stock_display_columns = ['股票名称', '股票代码', '最新价', '涨跌幅', '主力净流入']
        if '主力净流入占比' in stock_capital_flow_df.columns:
            stock_display_columns.append('主力净流入占比')
        print(top_inflow_stocks[stock_display_columns].to_string(index=False))
        
        # 显示主力净流出前5的股票
        # (Display top 5 stocks by main capital net outflow)
        print("\n💸 主力净流出前5的股票：")
        top_outflow_stocks = stock_capital_flow_df.nsmallest(5, '主力净流入')
        print(top_outflow_stocks[stock_display_columns].to_string(index=False))
        
        # 统计分析
        # (Statistical analysis)
        print(f"\n📈 个股资金流向统计：")
        inflow_stocks_count = len(stock_capital_flow_df[stock_capital_flow_df['主力净流入'] > 0])
        outflow_stocks_count = len(stock_capital_flow_df[stock_capital_flow_df['主力净流入'] < 0])
        
        print(f"   • 主力净流入股票：{inflow_stocks_count} 只")
        print(f"   • 主力净流出股票：{outflow_stocks_count} 只")
        if outflow_stocks_count > 0:
            inflow_outflow_ratio = inflow_stocks_count / outflow_stocks_count
            print(f"   • 流入/流出比：{inflow_outflow_ratio:.2f}")
        else:
            print("   • 流入/流出比：无穷大")
        
    except Exception as e:
        logger.error(f"获取个股资金流向时发生错误: {e}", exc_info=True)
        print(f"❌ 获取个股资金流向时发生错误：{e}")


def example_4_data_filtering_analysis():
    """
    示例4：数据筛选和高级分析
    Example 4: Data filtering and advanced analysis
    
    展示如何使用内置的筛选函数对数据进行筛选和分析。
    """
    print("\n" + "=" * 80)
    print("🔍 示例4：数据筛选和高级分析")
    print("=" * 80)
    
    try:
        logger.info("开始获取数据用于筛选分析")
        # 获取完整数据用于分析
        # (Get complete data for analysis)
        print("⏳ 正在获取数据用于分析...")
        analysis_data_df = get_concept_sectors()
        
        if analysis_data_df.empty:
            logger.warning("未获取到分析数据")
            print("❌ 未获取到分析数据")
            return
        
        logger.info(f"获取到 {len(analysis_data_df)} 个概念板块数据用于分析")
        
        # 1. 筛选强势板块（涨幅超过3%）
        # (Filter strong sectors with price change > 3%)
        print("\n🚀 筛选涨幅超过3%的强势板块：")
        strong_sectors = filter_sectors_by_change(analysis_data_df, min_change=3.0)
        print(f"   找到 {len(strong_sectors)} 个强势板块")
        
        if not strong_sectors.empty:
            print("   强势板块详情：")
            strong_display_columns = ['板块名称', '涨跌幅', '成交额']
            if '主力净流入' in strong_sectors.columns:
                strong_display_columns.append('主力净流入')
            print(strong_sectors[strong_display_columns].head().to_string(index=False))
        
        # 2. 筛选资金大幅流入的板块（仅当有资金流向数据时）
        # (Filter sectors with significant capital inflow - only when capital flow data exists)
        if '主力净流入' in analysis_data_df.columns:
            print("\n💰 筛选主力净流入超过1亿的板块：")
            capital_inflow_sectors = filter_sectors_by_capital(analysis_data_df, min_capital=10000, capital_flow_column='主力净流入')
            print(f"   找到 {len(capital_inflow_sectors)} 个资金大幅流入板块")
            
            if not capital_inflow_sectors.empty:
                print("   资金流入板块详情：")
                capital_display_columns = ['板块名称', '涨跌幅', '主力净流入']
                if '5日主力净流入' in capital_inflow_sectors.columns:
                    capital_display_columns.append('5日主力净流入')
                print(capital_inflow_sectors[capital_display_columns].head().to_string(index=False))
            
            # 3. 获取综合表现最佳的板块
            # (Get top overall performing sectors)
            print("\n🏆 主力净流入排行前10的板块：")
            top_capital_flow_sectors = get_top_sectors(analysis_data_df, n=10, sort_by='主力净流入', ascending=False)
            ranking_display_columns = ['板块名称', '涨跌幅', '主力净流入']
            if '5日主力净流入' in top_capital_flow_sectors.columns:
                ranking_display_columns.append('5日主力净流入')
            print(top_capital_flow_sectors[ranking_display_columns].to_string(index=False))
            
            # 4. 自定义复合筛选：又涨又有资金流入的板块
            # (Custom composite filtering: sectors with both price rise and capital inflow)
            print(f"\n⭐ 自定义筛选：涨幅>2% 且 主力净流入>5000万的板块：")
            composite_filter_sectors = analysis_data_df[
                (analysis_data_df['涨跌幅'] > 2) & 
                (analysis_data_df['主力净流入'] > 5000)
            ]
            print(f"   找到 {len(composite_filter_sectors)} 个符合条件的优质板块")
            
            if not composite_filter_sectors.empty:
                print("   优质板块详情：")
                composite_display_columns = ['板块名称', '涨跌幅', '主力净流入', '成交额']
                print(composite_filter_sectors[composite_display_columns].head().to_string(index=False))
        else:
            logger.warning("数据中未包含主力净流入字段，跳过资金流向相关分析")
            print("\n💰 注意：当前数据未包含资金流向信息，跳过资金流向相关分析")
            
    except Exception as e:
        logger.error(f"数据筛选分析时发生错误: {e}", exc_info=True)
        print(f"❌ 数据筛选分析时发生错误：{e}")


def main_function():
    """
    主函数：运行所有示例
    Main function: Run all examples
    """
    print("🎯 东方财富数据爬虫基础使用示例")
    print("🕒 开始时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    logger.info("开始执行所有基础示例")
    
    # 依次运行所有示例
    # (Run all examples sequentially)
    example_1_comprehensive_sector_data()
    example_2_realtime_quotes() 
    example_3_stock_capital_flow()
    example_4_data_filtering_analysis()
    
    print("\n" + "=" * 80)
    print("✅ 所有基础示例运行完成！")
    print("🕒 结束时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\n📚 更多高级用法请参考：")
    print("   • examples/advanced_usage.py - 高级功能示例")
    print("   • examples/monitor_usage.py - 实时监控示例") 
    print("   • examples/quickstart_capital_flow.py - 个股资金流向快速入门")
    print("=" * 80)
    
    logger.info("所有基础示例执行完成")


if __name__ == "__main__":
    main_function()