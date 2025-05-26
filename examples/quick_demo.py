"""
EastMoney Scraper 快速演示
展示包的主要功能
"""

import sys
import os
# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import (
    get_concept_sectors,
    get_concept_sectors_realtime,
    filter_sectors_by_change,
    get_top_sectors
)
import pandas as pd

# 设置pandas显示选项
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

def demo():
    print("=" * 80)
    print("EastMoney Scraper 快速演示")
    print("=" * 80)
    
    # 1. 获取实时行情（快速）
    print("\n1. 获取概念板块实时行情...")
    df_realtime = get_concept_sectors_realtime()
    print(f"   获取到 {len(df_realtime)} 个板块")
    
    # 2. 显示涨幅前5
    print("\n2. 今日涨幅前5的板块:")
    top5 = get_top_sectors(df_realtime, n=5, by='涨跌幅', ascending=False)
    print(top5[['板块名称', '涨跌幅', '最新价', '成交额']].to_string(index=False))
    
    # 3. 筛选强势板块
    print("\n3. 筛选涨幅超过3%的板块:")
    strong = filter_sectors_by_change(df_realtime, min_change=3.0)
    print(f"   找到 {len(strong)} 个强势板块")
    if not strong.empty:
        print(strong[['板块名称', '涨跌幅', '成交额']].head().to_string(index=False))
    
    # 4. 获取完整数据（包含资金流向）
    print("\n4. 获取包含资金流向的完整数据...")
    df_full = get_concept_sectors(periods=['today'])  # 只获取今日资金流向以加快速度
    
    if not df_full.empty:
        # 显示资金流入前5
        print("\n5. 主力净流入前5的板块:")
        top_inflow = df_full.nlargest(5, '主力净流入')[['板块名称', '涨跌幅', '主力净流入', '主力净流入占比']]
        print(top_inflow.to_string(index=False))
        
        # 资金统计
        total_inflow = df_full[df_full['主力净流入'] > 0]['主力净流入'].sum()
        total_outflow = abs(df_full[df_full['主力净流入'] < 0]['主力净流入'].sum())
        
        print(f"\n6. 资金流向统计:")
        print(f"   总流入: {total_inflow:,.0f} 万元")
        print(f"   总流出: {total_outflow:,.0f} 万元")
        print(f"   净流入: {(total_inflow - total_outflow):,.0f} 万元")
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("\n更多用法请参考 examples 目录下的其他示例文件。")
    print("=" * 80)

if __name__ == "__main__":
    demo()