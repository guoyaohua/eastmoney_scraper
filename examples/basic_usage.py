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

# 设置pandas显示选项以获得更好的输出格式
# (Configure pandas display options for better output formatting)
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def 示例1_概念板块综合数据():
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
        # 获取完整的概念板块数据，包含今日、5日、10日资金流向
        # (Get complete concept sector data including today, 5-day, 10-day capital flow)
        print("⏳ 正在获取概念板块数据...")
        df_综合数据 = get_concept_sectors(
            include_capital_flow=True,  # 包含资金流向数据 (Include capital flow data)
            periods=['today', '5day', '10day']  # 获取多个周期的资金流向 (Get multiple periods of capital flow)
        )
        
        if df_综合数据.empty:
            print("❌ 未获取到数据，请检查网络连接或稍后重试")
            return
            
        print(f"✅ 成功获取 {len(df_综合数据)} 个概念板块的综合数据")
        
        # 显示涨幅前10的板块
        # (Display top 10 sectors by price change)
        print("\n📈 今日涨幅前10的概念板块：")
        涨幅前10 = df_综合数据.nlargest(10, '涨跌幅')
        显示列 = ['板块名称', '涨跌幅', '最新价', '成交额', '主力净流入', '5日主力净流入']
        print(涨幅前10[显示列].to_string(index=False))
        
        # 市场统计分析
        # (Market statistical analysis)
        print(f"\n📊 市场统计分析：")
        上涨板块数 = len(df_综合数据[df_综合数据['涨跌幅'] > 0])
        下跌板块数 = len(df_综合数据[df_综合数据['涨跌幅'] < 0])
        平盘板块数 = len(df_综合数据[df_综合数据['涨跌幅'] == 0])
        
        print(f"   • 上涨板块：{上涨板块数} 个 ({上涨板块数/len(df_综合数据)*100:.1f}%)")
        print(f"   • 下跌板块：{下跌板块数} 个 ({下跌板块数/len(df_综合数据)*100:.1f}%)")
        print(f"   • 平盘板块：{平盘板块数} 个 ({平盘板块数/len(df_综合数据)*100:.1f}%)")
        
        # 资金流向统计
        # (Capital flow statistics)
        if '主力净流入' in df_综合数据.columns:
            总流入 = df_综合数据[df_综合数据['主力净流入'] > 0]['主力净流入'].sum()
            总流出 = abs(df_综合数据[df_综合数据['主力净流入'] < 0]['主力净流入'].sum())
            净流入 = 总流入 - 总流出
            
            print(f"\n💰 资金流向统计：")
            print(f"   • 总流入：{总流入:,.0f} 万元")
            print(f"   • 总流出：{总流出:,.0f} 万元")
            print(f"   • 净流入：{净流入:,.0f} 万元")
            
    except Exception as e:
        print(f"❌ 获取数据时发生错误：{e}")


def 示例2_实时行情快速获取():
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
        # 快速获取实时行情数据
        # (Quick fetch of real-time quote data)
        print("⏳ 正在快速获取实时行情...")
        df_实时行情 = get_concept_sectors_realtime()
        
        if df_实时行情.empty:
            print("❌ 未获取到实时行情数据")
            return
            
        print(f"✅ 成功获取 {len(df_实时行情)} 个板块的实时行情")
        
        # 显示成交额最大的前5个板块
        # (Display top 5 sectors by trading volume)
        print("\n💵 成交额最大的前5个板块：")
        成交额前5 = df_实时行情.nlargest(5, '成交额')
        print(成交额前5[['板块名称', '涨跌幅', '最新价', '成交额', '换手率']].to_string(index=False))
        
        # 显示波动最大的板块
        # (Display most volatile sectors)
        print("\n📊 今日波动统计：")
        最大涨幅 = df_实时行情['涨跌幅'].max()
        最大跌幅 = df_实时行情['涨跌幅'].min()
        平均涨跌幅 = df_实时行情['涨跌幅'].mean()
        
        print(f"   • 最大涨幅：{最大涨幅:.2f}%")
        print(f"   • 最大跌幅：{最大跌幅:.2f}%")
        print(f"   • 平均涨跌幅：{平均涨跌幅:.2f}%")
        
    except Exception as e:
        print(f"❌ 获取实时行情时发生错误：{e}")


def 示例3_个股资金流向():
    """
    示例3：获取个股资金流向数据
    Example 3: Get individual stock capital flow data
    
    展示如何获取个股资金流向排行数据，并进行分析。
    """
    print("\n" + "=" * 80)
    print("🏦 示例3：获取个股资金流向数据")
    print("=" * 80)
    
    try:
        # 获取个股资金流向数据（前2页约200只股票）
        # (Get individual stock capital flow data - first 2 pages, about 200 stocks)
        print("⏳ 正在获取个股资金流向数据...")
        df_个股资金流 = get_stock_capital_flow(
            max_pages=2,  # 限制爬取页数以控制时间 (Limit pages to control time)
            save_to_file=False  # 不保存到文件 (Don't save to file)
        )
        
        if df_个股资金流.empty:
            print("❌ 未获取到个股资金流向数据")
            return
            
        print(f"✅ 成功获取 {len(df_个股资金流)} 只股票的资金流向数据")
        
        # 显示主力净流入前10的股票
        # (Display top 10 stocks by main capital net inflow)
        print("\n💹 主力净流入前10的股票：")
        主力流入前10 = df_个股资金流.nlargest(10, '主力净流入')
        显示列 = ['股票名称', '股票代码', '最新价', '涨跌幅', '主力净流入', '主力净流入占比']
        print(主力流入前10[显示列].to_string(index=False))
        
        # 显示主力净流出前5的股票
        # (Display top 5 stocks by main capital net outflow)
        print("\n💸 主力净流出前5的股票：")
        主力流出前5 = df_个股资金流.nsmallest(5, '主力净流入')
        print(主力流出前5[显示列].to_string(index=False))
        
        # 统计分析
        # (Statistical analysis)
        print(f"\n📈 个股资金流向统计：")
        流入股票数 = len(df_个股资金流[df_个股资金流['主力净流入'] > 0])
        流出股票数 = len(df_个股资金流[df_个股资金流['主力净流入'] < 0])
        
        print(f"   • 主力净流入股票：{流入股票数} 只")
        print(f"   • 主力净流出股票：{流出股票数} 只")
        print(f"   • 流入/流出比：{流入股票数/流出股票数:.2f}" if 流出股票数 > 0 else "   • 流入/流出比：无穷大")
        
    except Exception as e:
        print(f"❌ 获取个股资金流向时发生错误：{e}")


def 示例4_数据筛选与分析():
    """
    示例4：数据筛选和高级分析
    Example 4: Data filtering and advanced analysis
    
    展示如何使用内置的筛选函数对数据进行筛选和分析。
    """
    print("\n" + "=" * 80)
    print("🔍 示例4：数据筛选和高级分析")
    print("=" * 80)
    
    try:
        # 获取完整数据用于分析
        # (Get complete data for analysis)
        print("⏳ 正在获取数据用于分析...")
        df_分析数据 = get_concept_sectors()
        
        if df_分析数据.empty:
            print("❌ 未获取到分析数据")
            return
        
        # 1. 筛选强势板块（涨幅超过3%）
        # (Filter strong sectors with price change > 3%)
        print("\n🚀 筛选涨幅超过3%的强势板块：")
        强势板块 = filter_sectors_by_change(df_分析数据, min_change=3.0)
        print(f"   找到 {len(强势板块)} 个强势板块")
        
        if not 强势板块.empty:
            print("   强势板块详情：")
            print(强势板块[['板块名称', '涨跌幅', '成交额', '主力净流入']].head().to_string(index=False))
        
        # 2. 筛选资金大幅流入的板块
        # (Filter sectors with significant capital inflow)
        print("\n💰 筛选主力净流入超过1亿的板块：")
        资金流入板块 = filter_sectors_by_capital(df_分析数据, min_capital=10000, flow_type='主力净流入')
        print(f"   找到 {len(资金流入板块)} 个资金大幅流入板块")
        
        if not 资金流入板块.empty:
            print("   资金流入板块详情：")
            print(资金流入板块[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']].head().to_string(index=False))
        
        # 3. 获取综合表现最佳的板块
        # (Get top overall performing sectors)
        print("\n🏆 主力净流入排行前10的板块：")
        资金流入排行 = get_top_sectors(df_分析数据, n=10, by='主力净流入', ascending=False)
        print(资金流入排行[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']].to_string(index=False))
        
        # 4. 自定义复合筛选：又涨又有资金流入的板块
        # (Custom composite filtering: sectors with both price rise and capital inflow)
        print(f"\n⭐ 自定义筛选：涨幅>2% 且 主力净流入>5000万的板块：")
        复合条件板块 = df_分析数据[
            (df_分析数据['涨跌幅'] > 2) & 
            (df_分析数据['主力净流入'] > 5000)
        ]
        print(f"   找到 {len(复合条件板块)} 个符合条件的优质板块")
        
        if not 复合条件板块.empty:
            print("   优质板块详情：")
            print(复合条件板块[['板块名称', '涨跌幅', '主力净流入', '成交额']].head().to_string(index=False))
            
    except Exception as e:
        print(f"❌ 数据筛选分析时发生错误：{e}")


def 主函数():
    """
    主函数：运行所有示例
    Main function: Run all examples
    """
    print("🎯 东方财富数据爬虫基础使用示例")
    print("🕒 开始时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 依次运行所有示例
    # (Run all examples sequentially)
    示例1_概念板块综合数据()
    示例2_实时行情快速获取() 
    示例3_个股资金流向()
    示例4_数据筛选与分析()
    
    print("\n" + "=" * 80)
    print("✅ 所有基础示例运行完成！")
    print("🕒 结束时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\n📚 更多高级用法请参考：")
    print("   • examples/advanced_usage.py - 高级功能示例")
    print("   • examples/monitor_usage.py - 实时监控示例") 
    print("   • examples/quickstart_capital_flow.py - 个股资金流向快速入门")
    print("=" * 80)


if __name__ == "__main__":
    主函数()