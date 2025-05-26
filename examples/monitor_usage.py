"""
EastMoney Scraper 监控器用法示例
"""

import sys
import os
# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from eastmoney_scraper import ConceptSectorMonitor, StockCapitalFlowMonitor

def example_concept_monitor():
    """示例: 概念板块实时监控"""
    print("=" * 80)
    print("概念板块实时监控示例")
    print("=" * 80)
    
    # 创建监控器
    monitor = ConceptSectorMonitor(output_dir="monitor_data/concept")
    
    # 定义回调函数
    def on_concept_update(df):
        """数据更新时的回调函数"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{timestamp}] 概念板块数据更新")
        print("-" * 60)
        
        # 显示涨幅前5
        print("涨幅前5板块:")
        top5 = df.head(5)[['板块名称', '涨跌幅', '成交额', '主力净流入']]
        for idx, row in top5.iterrows():
            print(f"  {row['板块名称']:15} {row['涨跌幅']:>6.2f}% "
                  f"成交额:{row['成交额']:>10.2f}万 "
                  f"主力:{row['主力净流入']:>10.2f}万")
        
        # 显示跌幅前5
        print("\n跌幅前5板块:")
        bottom5 = df.tail(5)[['板块名称', '涨跌幅', '成交额', '主力净流入']]
        for idx, row in bottom5.iterrows():
            print(f"  {row['板块名称']:15} {row['涨跌幅']:>6.2f}% "
                  f"成交额:{row['成交额']:>10.2f}万 "
                  f"主力:{row['主力净流入']:>10.2f}万")
        
        # 统计信息
        total_inflow = df[df['主力净流入'] > 0]['主力净流入'].sum()
        total_outflow = df[df['主力净流入'] < 0]['主力净流入'].sum()
        
        print(f"\n资金流向统计:")
        print(f"  流入板块: {len(df[df['主力净流入'] > 0])} 个, "
              f"总流入: {total_inflow:,.2f} 万元")
        print(f"  流出板块: {len(df[df['主力净流入'] < 0])} 个, "
              f"总流出: {total_outflow:,.2f} 万元")
        print(f"  净流入: {(total_inflow + total_outflow):,.2f} 万元")
        
        # 发现强势板块
        strong_sectors = df[(df['涨跌幅'] > 3) & (df['主力净流入'] > 10000)]
        if not strong_sectors.empty:
            print(f"\n发现 {len(strong_sectors)} 个强势板块（涨幅>3% 且 主力流入>1亿）:")
            for idx, row in strong_sectors.head(3).iterrows():
                print(f"  - {row['板块名称']}: 涨幅{row['涨跌幅']:.2f}%, "
                      f"主力流入{row['主力净流入']/10000:.2f}亿")
    
    # 设置回调
    monitor.set_callback(on_concept_update)
    
    # 开始监控（每30秒更新一次）
    print("\n开始监控概念板块，每30秒更新一次...")
    print("按 Ctrl+C 停止监控\n")
    
    monitor.start(interval=30)
    
    try:
        # 运行5分钟
        time.sleep(300)
    except KeyboardInterrupt:
        print("\n\n用户中断监控")
    finally:
        monitor.stop()
        print("监控已停止")


def example_stock_monitor():
    """示例: 个股资金流监控"""
    print("\n" + "=" * 80)
    print("个股资金流监控示例")
    print("=" * 80)
    
    # 创建监控器
    monitor = StockCapitalFlowMonitor(output_dir="monitor_data/stock")
    
    # 定义回调函数
    def on_stock_update(df):
        """个股数据更新回调"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{timestamp}] 个股资金流更新")
        print("-" * 60)
        
        # 主力净流入前10
        print("主力净流入前10股票:")
        top10 = df.nlargest(10, '主力净流入')[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']]
        for idx, row in top10.iterrows():
            print(f"  {row['股票名称']:10} {row['涨跌幅']:>6.2f}% "
                  f"流入:{row['主力净流入']:>10.2f}万 "
                  f"占比:{row['主力净流入占比']:>6.2f}%")
        
        # 主力净流出前10
        print("\n主力净流出前10股票:")
        bottom10 = df.nsmallest(10, '主力净流入')[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']]
        for idx, row in bottom10.iterrows():
            print(f"  {row['股票名称']:10} {row['涨跌幅']:>6.2f}% "
                  f"流出:{row['主力净流入']:>10.2f}万 "
                  f"占比:{row['主力净流入占比']:>6.2f}%")
    
    # 设置回调
    monitor.set_callback(on_stock_update)
    
    # 开始监控（每60秒更新一次）
    print("\n开始监控个股资金流，每60秒更新一次...")
    print("运行2分钟后自动停止\n")
    
    monitor.start(interval=60)
    
    # 运行2分钟
    time.sleep(120)
    monitor.stop()
    print("个股监控已停止")


def example_dual_monitor():
    """示例: 同时监控概念板块和个股"""
    print("\n" + "=" * 80)
    print("同时监控概念板块和个股示例")
    print("=" * 80)
    
    # 创建两个监控器
    concept_monitor = ConceptSectorMonitor()
    stock_monitor = StockCapitalFlowMonitor()
    
    # 简单的回调函数
    def on_concept_update(df):
        print(f"\n[概念板块] {datetime.now().strftime('%H:%M:%S')} - "
              f"更新 {len(df)} 个板块，领涨: {df.iloc[0]['板块名称']} "
              f"({df.iloc[0]['涨跌幅']:.2f}%)")
    
    def on_stock_update(df):
        print(f"[个股资金] {datetime.now().strftime('%H:%M:%S')} - "
              f"更新 {len(df)} 只股票，最大流入: {df.iloc[0]['股票名称']} "
              f"({df.iloc[0]['主力净流入']:.2f}万)")
    
    # 设置回调
    concept_monitor.set_callback(on_concept_update)
    stock_monitor.set_callback(on_stock_update)
    
    # 启动监控
    print("\n同时启动两个监控器...")
    concept_monitor.start(interval=30)  # 概念板块30秒更新
    stock_monitor.start(interval=45)    # 个股45秒更新
    
    print("监控运行中，按 Ctrl+C 停止\n")
    
    try:
        # 运行直到用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n停止所有监控器...")
        concept_monitor.stop()
        stock_monitor.stop()
        print("所有监控已停止")


def main():
    """选择要运行的示例"""
    print("EastMoney Scraper 监控器示例")
    print("1. 概念板块监控")
    print("2. 个股资金流监控")
    print("3. 双监控器同时运行")
    
    choice = input("\n请选择示例 (1-3): ")
    
    if choice == '1':
        example_concept_monitor()
    elif choice == '2':
        example_stock_monitor()
    elif choice == '3':
        example_dual_monitor()
    else:
        print("无效选择")


if __name__ == "__main__":
    main()