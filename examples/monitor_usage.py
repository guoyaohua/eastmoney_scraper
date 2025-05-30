"""
东方财富数据爬虫监控器使用示例

本文件展示了eastmoney_scraper包的实时监控功能，包括：
- 概念板块实时数据监控
- 个股资金流向实时监控
- 多监控器同时运行
- 自定义监控回调和警报系统
- 监控数据的实时分析和展示
"""

import sys
import os
import time
import signal
from datetime import datetime, timedelta
from typing import Optional

# 添加父目录到Python路径以便导入eastmoney_scraper包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入eastmoney_scraper的监控器类
from eastmoney_scraper import SectorMonitor, ConceptSectorMonitor, IndustrySectorMonitor, StockCapitalFlowMonitor
import pandas as pd


class MonitorStatistics:
    """
    监控统计器类，用于记录和分析监控过程中的统计信息
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.update_count = 0
        self.last_update_time: Optional[datetime] = None
        self.strong_sectors_history = []  # 记录强势板块
        self.abnormal_stocks_history = []  # 记录异常股票
        
    def record_update(self, data_type: str, data_count: int):
        """记录一次数据更新"""
        self.update_count += 1
        self.last_update_time = datetime.now()
        
    def add_strong_sector(self, sector_name: str, change_pct: float, main_inflow: float):
        """记录强势板块"""
        self.strong_sectors_history.append({
            'time': datetime.now(),
            'sector_name': sector_name,
            'change_pct': change_pct,
            'main_inflow': main_inflow
        })
        
    def add_abnormal_stock(self, stock_name: str, change_pct: float, main_inflow: float, reason: str):
        """记录异常股票"""
        self.abnormal_stocks_history.append({
            'time': datetime.now(),
            'stock_name': stock_name,
            'change_pct': change_pct,
            'main_inflow': main_inflow,
            'abnormal_reason': reason
        })
        
    def generate_report(self) -> str:
        """生成监控统计报告"""
        runtime = datetime.now() - self.start_time
        
        report = f"""
📊 监控统计报告
{'='*50}
运行时长: {runtime}
总更新次数: {self.update_count}
上次更新: {self.last_update_time.strftime('%H:%M:%S') if self.last_update_time else '无'}
发现强势板块: {len(self.strong_sectors_history)} 次
发现异常股票: {len(self.abnormal_stocks_history)} 次
"""
        return report


def example_1_intelligent_concept_monitor():
    """
    监控示例1：概念板块智能实时监控
    Monitor Example 1: Intelligent real-time concept sector monitoring
    
    展示带有智能分析和警报功能的概念板块监控
    """
    print("=" * 100)
    print("📊 监控示例1：概念板块智能实时监控")
    print("=" * 100)
    
    # 创建统计器和监控器
    # (Create statistics tracker and monitor)
    statistics = MonitorStatistics()
    monitor = ConceptSectorMonitor(output_dir="monitor_data/concept_sectors")
    
    # 设置监控参数
    # (Set monitoring parameters)
    strong_sector_threshold = {'change_pct': 3.0, 'main_inflow': 10000}  # 涨幅>3% 且 主力流入>1亿
    abnormal_sector_threshold = {'change_pct': 8.0, 'main_inflow': 50000}  # 涨幅>8% 且 主力流入>5亿
    
    def concept_data_update_callback(df_sectors: pd.DataFrame):
        """
        概念板块数据更新时的智能回调处理函数
        Intelligent callback handler for concept sector data updates
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        statistics.record_update("概念板块", len(df_sectors))
        
        print(f"\n🔄 [{current_time}] 概念板块数据更新")
        print("─" * 80)
        
        # 基础统计信息
        # (Basic statistics)
        rising_sectors = df_sectors[df_sectors['涨跌幅'] > 0]
        falling_sectors = df_sectors[df_sectors['涨跌幅'] < 0]
        
        print(f"📈 市场概况：总板块 {len(df_sectors)} 个 | "
              f"上涨 {len(rising_sectors)} 个 | 下跌 {len(falling_sectors)} 个")
        
        # 显示涨幅前5板块
        # (Display top 5 rising sectors)
        print(f"\n🚀 涨幅前5板块：")
        top_5_rising = df_sectors.nlargest(5, '涨跌幅')
        for idx, (_, sector) in enumerate(top_5_rising.iterrows(), 1):
            inflow_status = "💰" if sector['主力净流入'] > 0 else "💸"
            print(f"   {idx}. {sector['板块名称']:12} {sector['涨跌幅']:+6.2f}% "
                  f"{inflow_status} {sector['主力净流入']:>8.0f}万 "
                  f"成交额: {sector['成交额']:>10.0f}万")
        
        # 显示跌幅前3板块  
        # (Display top 3 declining sectors)
        print(f"\n📉 跌幅前3板块：")
        top_3_falling = df_sectors.nsmallest(3, '涨跌幅')
        for idx, (_, sector) in enumerate(top_3_falling.iterrows(), 1):
            inflow_status = "💰" if sector['主力净流入'] > 0 else "💸"
            print(f"   {idx}. {sector['板块名称']:12} {sector['涨跌幅']:+6.2f}% "
                  f"{inflow_status} {sector['主力净流入']:>8.0f}万")
        
        # 资金流向统计
        # (Capital flow statistics)
        total_inflow = df_sectors[df_sectors['主力净流入'] > 0]['主力净流入'].sum()
        total_outflow = abs(df_sectors[df_sectors['主力净流入'] < 0]['主力净流入'].sum())
        net_inflow = total_inflow - total_outflow
        
        flow_status = "📈 净流入" if net_inflow > 0 else "📉 净流出"
        print(f"\n💰 资金流向统计：")
        print(f"   • 总流入：{total_inflow:>12,.0f} 万元")
        print(f"   • 总流出：{total_outflow:>12,.0f} 万元") 
        print(f"   • {flow_status}：{abs(net_inflow):>10,.0f} 万元")
        
        # 强势板块识别和警报
        # (Strong sector identification and alerts)
        strong_sectors = df_sectors[
            (df_sectors['涨跌幅'] > strong_sector_threshold['change_pct']) & 
            (df_sectors['主力净流入'] > strong_sector_threshold['main_inflow'])
        ]
        
        if not strong_sectors.empty:
            print(f"\n⭐ 发现 {len(strong_sectors)} 个强势板块（涨幅>{strong_sector_threshold['change_pct']}% 且 主力流入>{strong_sector_threshold['main_inflow']/10000}亿）：")
            for _, sector in strong_sectors.head(3).iterrows():
                print(f"   🔥 {sector['板块名称']}：涨幅 {sector['涨跌幅']:.2f}%，"
                      f"主力流入 {sector['主力净流入']/10000:.2f}亿元")
                statistics.add_strong_sector(sector['板块名称'], sector['涨跌幅'], sector['主力净流入'])
        
        # 异常板块识别（超高涨幅或超大资金流入）
        # (Abnormal sector identification - extremely high gains or massive capital inflow)
        abnormal_sectors = df_sectors[
            (df_sectors['涨跌幅'] > abnormal_sector_threshold['change_pct']) | 
            (df_sectors['主力净流入'] > abnormal_sector_threshold['main_inflow'])
        ]
        
        if not abnormal_sectors.empty:
            print(f"\n🚨 异常板块警报！发现 {len(abnormal_sectors)} 个异常板块：")
            for _, sector in abnormal_sectors.iterrows():
                abnormal_reasons = []
                if sector['涨跌幅'] > abnormal_sector_threshold['change_pct']:
                    abnormal_reasons.append(f"超高涨幅{sector['涨跌幅']:.2f}%")
                if sector['主力净流入'] > abnormal_sector_threshold['main_inflow']:
                    abnormal_reasons.append(f"超大资金流入{sector['主力净流入']/10000:.1f}亿")
                
                print(f"   ⚠️ {sector['板块名称']}：{' + '.join(abnormal_reasons)}")
    
    # 设置回调并启动监控
    # (Set callback and start monitoring)
    monitor.set_callback(concept_data_update_callback)
    
    print("🚀 开始概念板块智能监控...")
    print("⏰ 更新间隔：30秒")
    print("🔍 监控功能：强势板块识别、异常警报、资金流向分析")
    print("⚡ 按 Ctrl+C 随时停止监控\n")
    
    try:
        monitor.start(interval=30)
        
        # 运行监控（可以设置运行时间或无限运行）
        runtime_seconds = 300  # 5分钟演示
        print(f"📅 演示模式：将运行 {runtime_seconds//60} 分钟...")
        time.sleep(runtime_seconds)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断监控")
    finally:
        monitor.stop()
        print(f"\n✅ 概念板块监控已停止")
        print(statistics.generate_report())


def example_2_intelligent_stock_monitor():
    """
    监控示例2：个股资金流向智能监控
    Monitor Example 2: Intelligent individual stock capital flow monitoring
    
    展示个股资金流向的智能监控，包括异常股票识别和投资机会发现
    """
    print("\n" + "=" * 100)
    print("💹 监控示例2：个股资金流向智能监控")
    print("=" * 100)
    
    # 创建统计器和监控器
    statistics = MonitorStatistics()
    monitor = StockCapitalFlowMonitor(output_dir="monitor_data/stock_capital_flow")
    
    # 设置监控阈值
    # (Set monitoring thresholds)
    investment_opportunity_threshold = {
        'main_inflow': 15000,    # 1.5亿以上
        'change_pct': 2.0,       # 涨幅2%以上
        'inflow_ratio': 8.0      # 占比8%以上
    }
    
    abnormal_stock_threshold = {
        'main_inflow': 50000,    # 5亿以上
        'change_pct': 9.0        # 涨幅9%以上
    }
    
    def stock_flow_update_callback(df_stocks: pd.DataFrame):
        """
        个股资金流向数据更新时的智能回调处理函数
        Intelligent callback handler for individual stock capital flow data updates
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        statistics.record_update("个股资金流", len(df_stocks))
        
        print(f"\n🔄 [{current_time}] 个股资金流向数据更新")
        print("─" * 80)
        
        # 基础统计
        # (Basic statistics)
        inflow_stocks = df_stocks[df_stocks['主力净流入'] > 0]
        outflow_stocks = df_stocks[df_stocks['主力净流入'] < 0]
        
        print(f"📊 个股概况：总股票 {len(df_stocks)} 只 | "
              f"主力流入 {len(inflow_stocks)} 只 | 主力流出 {len(outflow_stocks)} 只")
        
        # 显示主力净流入TOP8
        # (Display top 8 stocks by main capital inflow)
        print(f"\n💎 主力净流入TOP8：")
        top_8_inflow = df_stocks.nlargest(8, '主力净流入')
        for idx, (_, stock) in enumerate(top_8_inflow.iterrows(), 1):
            ratio_status = "🔥" if stock['主力净流入占比'] > 10 else "📈" if stock['主力净流入占比'] > 5 else "💰"
            print(f"   {idx}. {stock['股票名称']:8} ({stock['股票代码']}) "
                  f"{stock['涨跌幅']:+6.2f}% {ratio_status} {stock['主力净流入']:>8.0f}万 "
                  f"占比:{stock['主力净流入占比']:>5.1f}%")
        
        # 显示主力净流出TOP5
        # (Display top 5 stocks by main capital outflow)
        print(f"\n💸 主力净流出TOP5：")
        top_5_outflow = df_stocks.nsmallest(5, '主力净流入')
        for idx, (_, stock) in enumerate(top_5_outflow.iterrows(), 1):
            print(f"   {idx}. {stock['股票名称']:8} ({stock['股票代码']}) "
                  f"{stock['涨跌幅']:+6.2f}% 💸 {stock['主力净流入']:>8.0f}万")
        
        # 投资机会识别
        # (Investment opportunity identification)
        opportunity_stocks = df_stocks[
            (df_stocks['主力净流入'] > investment_opportunity_threshold['main_inflow']) &
            (df_stocks['涨跌幅'] > investment_opportunity_threshold['change_pct']) &
            (df_stocks['主力净流入占比'] > investment_opportunity_threshold['inflow_ratio'])
        ]
        
        if not opportunity_stocks.empty:
            print(f"\n🎯 发现 {len(opportunity_stocks)} 只潜在投资机会股票：")
            print(f"   📋 筛选条件：主力流入>{investment_opportunity_threshold['main_inflow']/10000:.1f}亿 + "
                  f"涨幅>{investment_opportunity_threshold['change_pct']}% + 占比>{investment_opportunity_threshold['inflow_ratio']}%")
            
            for _, stock in opportunity_stocks.head(5).iterrows():
                print(f"   ⭐ {stock['股票名称']} ({stock['股票代码']})：")
                print(f"      涨幅 {stock['涨跌幅']:+.2f}%，主力流入 {stock['主力净流入']/10000:.2f}亿，占比 {stock['主力净流入占比']:.1f}%")
        
        # 异常股票识别
        # (Abnormal stock identification)
        abnormal_stocks = df_stocks[
            (df_stocks['主力净流入'] > abnormal_stock_threshold['main_inflow']) |
            (df_stocks['涨跌幅'] > abnormal_stock_threshold['change_pct'])
        ]
        
        if not abnormal_stocks.empty:
            print(f"\n🚨 异常股票警报！发现 {len(abnormal_stocks)} 只异常股票：")
            for _, stock in abnormal_stocks.head(3).iterrows():
                abnormal_reasons = []
                if stock['主力净流入'] > abnormal_stock_threshold['main_inflow']:
                    abnormal_reasons.append(f"超大资金流入{stock['主力净流入']/10000:.1f}亿")
                if stock['涨跌幅'] > abnormal_stock_threshold['change_pct']:
                    abnormal_reasons.append(f"超高涨幅{stock['涨跌幅']:.1f}%")
                
                print(f"   ⚠️ {stock['股票名称']} ({stock['股票代码']})：{' + '.join(abnormal_reasons)}")
                statistics.add_abnormal_stock(stock['股票名称'], stock['涨跌幅'], stock['主力净流入'], ' + '.join(abnormal_reasons))
        
        # 资金流向结构分析
        # (Capital flow structure analysis)
        ultra_large_inflow_ratio = len(df_stocks[df_stocks['超大单净流入'] > 0]) / len(df_stocks) * 100
        large_inflow_ratio = len(df_stocks[df_stocks['大单净流入'] > 0]) / len(df_stocks) * 100
        
        print(f"\n📊 资金流向结构：")
        print(f"   • 超大单净流入股票占比：{ultra_large_inflow_ratio:.1f}%")
        print(f"   • 大单净流入股票占比：{large_inflow_ratio:.1f}%")
    
    # 设置回调并启动监控
    monitor.set_callback(stock_flow_update_callback)
    
    print("🚀 开始个股资金流向智能监控...")
    print("⏰ 更新间隔：60秒")
    print("🔍 监控功能：投资机会识别、异常股票警报、资金结构分析")
    print("⚡ 按 Ctrl+C 随时停止监控\n")
    
    try:
        monitor.start(interval=60)
        
        # 运行监控
        runtime_seconds = 240  # 4分钟演示
        print(f"📅 演示模式：将运行 {runtime_seconds//60} 分钟...")
        time.sleep(runtime_seconds)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断监控")
    finally:
        monitor.stop()
        print(f"\n✅ 个股资金流监控已停止")
        print(statistics.generate_report())


def example_3_dual_monitor_coordination():
    """
    监控示例3：概念板块和个股双监控器协同运行
    Monitor Example 3: Dual monitors (concept sectors and individual stocks) running in coordination
    
    展示同时运行两个监控器，并进行关联分析
    """
    print("\n" + "=" * 100)
    print("🔗 监控示例3：双监控器协同运行系统")
    print("=" * 100)
    
    # 创建监控器
    concept_monitor = ConceptSectorMonitor(output_dir="monitor_data/coordination/concept")
    stock_monitor = StockCapitalFlowMonitor(output_dir="monitor_data/coordination/stock")
    
    # 共享数据存储
    latest_concept_data: Optional[pd.DataFrame] = None
    latest_stock_data: Optional[pd.DataFrame] = None
    
    def concept_sector_callback(df_concept: pd.DataFrame):
        """概念板块数据更新回调"""
        nonlocal latest_concept_data
        latest_concept_data = df_concept
        
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n🏢 [{current_time}] 概念板块更新：{len(df_concept)} 个板块")
        
        # 显示领涨板块
        if not df_concept.empty:
            leading_sector = df_concept.iloc[0]
            print(f"   📈 领涨：{leading_sector['板块名称']} ({leading_sector['涨跌幅']:+.2f}%)")
            
            # 强势板块统计
            strong_sectors_count = len(df_concept[df_concept['涨跌幅'] > 3])
            print(f"   🚀 强势板块(>3%)：{strong_sectors_count} 个")
    
    def stock_capital_flow_callback(df_stock: pd.DataFrame):
        """个股资金流数据更新回调"""
        nonlocal latest_stock_data
        latest_stock_data = df_stock
        
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"💰 [{current_time}] 个股资金流更新：{len(df_stock)} 只股票")

        # 显示最大流入股票
        if not df_stock.empty:
            max_inflow_stock = df_stock.iloc[0]
            print(f"   💎 最大流入：{max_inflow_stock['股票名称']} "
                  f"({max_inflow_stock['主力净流入']:.0f}万元)")
            
            # 大额流入统计
            large_inflow_count = len(df_stock[df_stock['主力净流入'] > 10000])
            print(f"   💸 大额流入(>1亿)：{large_inflow_count} 只")
        
        # 如果两个数据都有，进行关联分析
        # (If both datasets are available, perform correlation analysis)
        if latest_concept_data is not None and not latest_concept_data.empty:
            perform_correlation_analysis()
    
    def perform_correlation_analysis():
        """进行概念板块与个股的关联分析"""
        if latest_concept_data is None or latest_stock_data is None:
            return
            
        print(f"\n🔍 关联分析报告：")
        
        # 分析强势板块与大额流入股票的关系
        strong_sectors = latest_concept_data[latest_concept_data['涨跌幅'] > 5]
        large_inflow_stocks = latest_stock_data[latest_stock_data['主力净流入'] > 20000]
        
        if not strong_sectors.empty and not large_inflow_stocks.empty:
            print(f"   • 强势板块({len(strong_sectors)}个) vs 大额流入股票({len(large_inflow_stocks)}只)")
            market_activity = "高" if len(strong_sectors) > 5 and len(large_inflow_stocks) > 10 else "中等"
            print(f"   • 市场活跃度：{market_activity}")
        
        # 资金流向一致性分析
        concept_net_inflow = latest_concept_data['主力净流入'].sum() if '主力净流入' in latest_concept_data.columns else 0
        stock_net_inflow = latest_stock_data['主力净流入'].sum()
        
        consistency = "一致" if (concept_net_inflow > 0) == (stock_net_inflow > 0) else "分化"
        print(f"   • 资金流向一致性：{consistency}")
    
    # 设置回调
    concept_monitor.set_callback(concept_sector_callback)
    stock_monitor.set_callback(stock_capital_flow_callback)
    
    print("🚀 启动双监控器协同系统...")
    print("📊 概念板块监控间隔：45秒")
    print("💹 个股资金流监控间隔：75秒")
    print("🔗 将进行实时关联分析")
    print("⚡ 按 Ctrl+C 停止所有监控\n")
    
    try:
        # 启动双监控器
        concept_monitor.start(interval=45)
        stock_monitor.start(interval=75)
        
        print("🔄 双监控器运行中...")
        
        # 保持运行直到用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断，正在停止所有监控器...")
    finally:
        concept_monitor.stop()
        stock_monitor.stop()
        print(f"✅ 所有监控器已停止")


def example_4_industry_sector_monitor():
    """
    示例4：行业板块实时监控
    Example 4: Real-time industry sector monitoring
    """
    print("\n" + "="*80)
    print("📊 示例4：行业板块实时监控")
    print("📋 功能：监控行业板块的行情和资金流向变化")
    print("🎯 特点：使用IndustrySectorMonitor专门监控行业板块")
    print("="*80 + "\n")
    
    # 创建行业板块监控器
    monitor = IndustrySectorMonitor(output_dir="monitor_data/industry_sectors")
    
    def industry_data_callback(df_sectors: pd.DataFrame):
        """行业板块数据更新回调"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔄 [{current_time}] 行业板块数据更新")
        print("─" * 80)
        
        # 基础统计
        rising_sectors = df_sectors[df_sectors['涨跌幅'] > 0]
        falling_sectors = df_sectors[df_sectors['涨跌幅'] < 0]
        
        print(f"📈 市场概况：总行业 {len(df_sectors)} 个 | "
              f"上涨 {len(rising_sectors)} 个 | 下跌 {len(falling_sectors)} 个")
        
        # 显示涨幅前5行业
        print(f"\n🚀 涨幅前5行业：")
        top_5_rising = df_sectors.nlargest(5, '涨跌幅')
        for idx, (_, sector) in enumerate(top_5_rising.iterrows(), 1):
            inflow_status = "💰" if sector.get('主力净流入', 0) > 0 else "💸"
            print(f"   {idx}. {sector['板块名称']:12} {sector['涨跌幅']:+6.2f}% "
                  f"{inflow_status} {sector.get('主力净流入', 0):>8.0f}万 "
                  f"成交额: {sector.get('成交额', 0):>10.0f}万")
        
        # 显示跌幅前3行业
        print(f"\n📉 跌幅前3行业：")
        top_3_falling = df_sectors.nsmallest(3, '涨跌幅')
        for idx, (_, sector) in enumerate(top_3_falling.iterrows(), 1):
            inflow_status = "💰" if sector.get('主力净流入', 0) > 0 else "💸"
            print(f"   {idx}. {sector['板块名称']:12} {sector['涨跌幅']:+6.2f}% "
                  f"{inflow_status} {sector.get('主力净流入', 0):>8.0f}万")
        
        # 主力资金流向分析
        if '主力净流入' in df_sectors.columns:
            inflow_sectors = df_sectors[df_sectors['主力净流入'] > 0]
            outflow_sectors = df_sectors[df_sectors['主力净流入'] < 0]
            
            print(f"\n💰 主力资金流向：")
            print(f"   • 净流入行业：{len(inflow_sectors)} 个")
            print(f"   • 净流出行业：{len(outflow_sectors)} 个")
            
            # 显示资金流入前3的行业
            if not inflow_sectors.empty:
                print(f"\n💎 主力净流入前3行业：")
                top_inflow = inflow_sectors.nlargest(3, '主力净流入')
                for idx, (_, sector) in enumerate(top_inflow.iterrows(), 1):
                    print(f"   {idx}. {sector['板块名称']:12} "
                          f"净流入: {sector['主力净流入']:>10.0f}万 "
                          f"涨幅: {sector['涨跌幅']:+6.2f}%")
    
    # 设置回调
    monitor.set_callback(industry_data_callback)
    
    print("🚀 启动行业板块监控器...")
    print("📊 数据更新间隔：30秒")
    print("⚡ 按 Ctrl+C 停止监控\n")
    
    try:
        # 启动监控
        monitor.start(interval=30)
        
        print("🔄 行业板块监控器运行中...")
        
        # 保持运行直到用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断，正在停止监控器...")
    finally:
        monitor.stop()
        print(f"✅ 行业板块监控器已停止")


def example_5_base_sector_monitor():
    """
    示例5：使用基类SectorMonitor灵活监控
    Example 5: Flexible monitoring using base class SectorMonitor
    """
    print("\n" + "="*80)
    print("📊 示例5：使用基类SectorMonitor灵活监控")
    print("📋 功能：可选择监控概念板块或行业板块")
    print("🎯 特点：展示SectorMonitor基类的使用方式")
    print("="*80 + "\n")
    
    # 让用户选择板块类型
    print("请选择要监控的板块类型：")
    print("1. 概念板块")
    print("2. 行业板块")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == '1':
        sector_type = "concept"
        sector_name = "概念板块"
    elif choice == '2':
        sector_type = "industry"
        sector_name = "行业板块"
    else:
        print("无效选择，默认使用概念板块")
        sector_type = "concept"
        sector_name = "概念板块"
    
    # 使用基类SectorMonitor创建监控器
    monitor = SectorMonitor(
        sector_type=sector_type,
        output_dir=f"monitor_data/{sector_type}_sectors"
    )
    
    def sector_data_callback(df_sectors: pd.DataFrame):
        """板块数据更新回调"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔄 [{current_time}] {sector_name}数据更新")
        print("─" * 80)
        
        # 显示前5个板块
        print(f"\n📊 {sector_name}列表（前5个）：")
        for idx, (_, sector) in enumerate(df_sectors.head().iterrows(), 1):
            change_icon = "📈" if sector['涨跌幅'] > 0 else "📉"
            print(f"   {idx}. {sector['板块名称']:12} "
                  f"{change_icon} {sector['涨跌幅']:+6.2f}% "
                  f"最新价: {sector.get('最新价', 0):>8.2f}")
        
        print(f"\n共监控到 {len(df_sectors)} 个{sector_name}")
    
    # 设置回调
    monitor.set_callback(sector_data_callback)
    
    print(f"\n🚀 启动{sector_name}监控器...")
    print("📊 数据更新间隔：20秒")
    print("⚡ 按 Ctrl+C 停止监控\n")
    
    try:
        # 启动监控
        monitor.start(interval=20)
        
        print(f"🔄 {sector_name}监控器运行中...")
        
        # 保持运行直到用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断，正在停止监控器...")
    finally:
        monitor.stop()
        print(f"✅ {sector_name}监控器已停止")


def main():
    """
    主函数：监控示例选择器
    Main function: Monitor examples selector
    """
    print("🎯 东方财富数据爬虫监控器使用示例")
    print("🕒 启动时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 100)
    
    monitor_options = {
        '1': ('概念板块智能监控（ConceptSectorMonitor）', example_1_intelligent_concept_monitor),
        '2': ('个股资金流智能监控', example_2_intelligent_stock_monitor),
        '3': ('双监控器协同运行', example_3_dual_monitor_coordination),
        '4': ('行业板块实时监控（IndustrySectorMonitor）', example_4_industry_sector_monitor),
        '5': ('灵活板块监控（SectorMonitor基类）', example_5_base_sector_monitor),
    }
    
    print("📋 可用的监控示例：")
    for option_id, (name, _) in monitor_options.items():
        print(f"   {option_id}. {name}")
    print("   0. 退出")
    
    while True:
        choice = input(f"\n请选择要运行的监控示例 (1-5/0): ").strip()
        
        if choice == '0':
            print("👋 退出监控示例程序")
            break
        elif choice in monitor_options:
            print(f"\n🚀 开始运行：{monitor_options[choice][0]}")
            try:
                monitor_options[choice][1]()
            except Exception as e:
                print(f"❌ 监控示例运行出错：{e}")
            
            continue_choice = input(f"\n是否继续选择其他示例？(y/n): ").strip().lower()
            if continue_choice != 'y':
                break
        else:
            print("❌ 无效选择，请重新输入")
    
    print(f"\n✅ 监控示例程序结束")
    print("🕒 结束时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 100)


if __name__ == "__main__":
    main()