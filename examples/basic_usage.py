"""
EastMoney Scraper 基础用法示例
"""

import sys
import os
# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import (
    get_concept_sectors,
    get_concept_sectors_realtime,
    get_stock_capital_flow,
    filter_sectors_by_change,
    get_top_sectors
)

def example_concept_sectors():
    """示例1: 获取概念板块数据"""
    print("=" * 80)
    print("示例1: 获取概念板块数据")
    print("=" * 80)
    
    # 获取完整数据（包含资金流向）
    df = get_concept_sectors()
    
    print(f"\n获取到 {len(df)} 个概念板块数据")
    print("\n涨幅前10的板块:")
    print(df[['板块名称', '涨跌幅', '成交额', '主力净流入', '5日主力净流入']].head(10))
    
    # 统计
    print(f"\n上涨板块: {len(df[df['涨跌幅'] > 0])} 个")
    print(f"下跌板块: {len(df[df['涨跌幅'] < 0])} 个")
    print(f"平盘板块: {len(df[df['涨跌幅'] == 0])} 个")


def example_realtime_quotes():
    """示例2: 仅获取实时行情"""
    print("\n" + "=" * 80)
    print("示例2: 仅获取实时行情（不含资金流向）")
    print("=" * 80)
    
    # 快速获取实时行情
    df = get_concept_sectors_realtime()
    
    print(f"\n获取到 {len(df)} 个板块的实时行情")
    print("\n成交额前5的板块:")
    top_volume = df.nlargest(5, '成交额')[['板块名称', '涨跌幅', '成交额', '换手率']]
    print(top_volume)


def example_stock_capital_flow():
    """示例3: 获取个股资金流向"""
    print("\n" + "=" * 80)
    print("示例3: 获取个股资金流向")
    print("=" * 80)
    
    # 获取前200只股票的资金流向
    df = get_stock_capital_flow(max_pages=2)
    
    if not df.empty:
        print(f"\n获取到 {len(df)} 只股票的资金流向数据")
        print("\n主力净流入前10的股票:")
        print(df.nlargest(10, '主力净流入')[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']])


def example_data_filtering():
    """示例4: 数据筛选"""
    print("\n" + "=" * 80)
    print("示例4: 数据筛选和分析")
    print("=" * 80)
    
    df = get_concept_sectors()
    
    # 筛选涨幅在3%以上的板块
    strong_sectors = filter_sectors_by_change(df, min_change=3.0)
    print(f"\n涨幅超过3%的板块: {len(strong_sectors)} 个")
    if not strong_sectors.empty:
        print(strong_sectors[['板块名称', '涨跌幅', '主力净流入']].head())
    
    # 获取主力净流入前10的板块
    print("\n主力净流入前10的板块:")
    top_inflow = get_top_sectors(df, n=10, by='主力净流入', ascending=False)
    print(top_inflow[['板块名称', '涨跌幅', '主力净流入', '5日主力净流入']])
    
    # 自定义筛选：强势板块（涨幅>2% 且 主力净流入>5000万）
    strong_with_inflow = df[(df['涨跌幅'] > 2) & (df['主力净流入'] > 5000)]
    print(f"\n强势且资金流入板块: {len(strong_with_inflow)} 个")
    if not strong_with_inflow.empty:
        print(strong_with_inflow[['板块名称', '涨跌幅', '主力净流入']].head())


def main():
    """运行所有示例"""
    example_concept_sectors()
    example_realtime_quotes()
    example_stock_capital_flow()
    example_data_filtering()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()