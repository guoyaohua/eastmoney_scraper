"""
东方财富数据爬虫高级使用示例
EastMoney Scraper Advanced Usage Examples

本文件展示了eastmoney_scraper包的高级功能，包括：
- 个股资金流向详细分析
- 实时数据监控与回调
- 自定义数据分析策略
- 批量数据处理和存储
- 数据可视化分析

This file demonstrates advanced features of the eastmoney_scraper package, including:
- Detailed individual stock capital flow analysis
- Real-time data monitoring with callbacks
- Custom data analysis strategies
- Batch data processing and storage
- Data visualization analysis
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import glob
from typing import Optional

# 添加父目录到Python路径
# (Add parent directory to Python path)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入eastmoney_scraper的高级功能接口
# (Import advanced functional interfaces from eastmoney_scraper)
from eastmoney_scraper import (
    # 核心爬虫类 (Core scraper classes)
    CapitalFlowScraper,
    ConceptSectorScraper,
    
    # 监控器类 (Monitor classes)
    StockCapitalFlowMonitor,
    ConceptSectorMonitor,
    
    # API接口函数 (API interface functions)
    get_stock_capital_flow,
    get_concept_sectors,
    get_stock_to_concept_map,
    
    # 工具函数 (Utility functions)
    filter_sectors_by_change,
    filter_sectors_by_capital,
    get_top_sectors
)

# 单独导入内部分析类（用于高级分析功能）
# (Import internal analysis class separately for advanced analysis features)
try:
    from eastmoney_scraper.capital_flow_monitor import CapitalFlowAnalyzer
except ImportError:
    print("⚠️ 警告：CapitalFlowAnalyzer导入失败，部分高级分析功能将不可用")
    CapitalFlowAnalyzer = None

# 设置pandas显示选项
# (Configure pandas display options)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def 高级示例1_个股资金流向批量分析():
    """
    高级示例1：个股资金流向批量获取与深度分析
    Advanced Example 1: Batch fetching and deep analysis of individual stock capital flow
    
    展示如何批量获取个股资金流向数据并进行多维度分析
    """
    print("=" * 100)
    print("📊 高级示例1：个股资金流向批量分析")
    print("=" * 100)
    
    try:
        # 使用核心爬虫类进行更精细的控制
        # (Use core scraper class for more precise control)
        print("⏳ 正在创建个股资金流向爬虫实例...")
        资金流爬虫 = CapitalFlowScraper()
        
        # 执行批量数据获取并保存
        # (Execute batch data fetching and save)
        print("📈 开始批量获取个股资金流向数据（这可能需要一些时间）...")
        df_资金流数据 = 资金流爬虫.scrape_once(save_to_file=True)
        
        if df_资金流数据 is None or df_资金流数据.empty:
            print("❌ 未获取到个股资金流向数据")
            return
            
        print(f"✅ 成功获取 {len(df_资金流数据)} 只股票的资金流向数据")
        
        # 1. 主力资金流向TOP分析
        # (Main capital flow TOP analysis)
        print("\n💹 主力资金净流入TOP20分析：")
        主力流入TOP20 = df_资金流数据.nlargest(20, '主力净流入')
        显示列 = ['股票名称', '股票代码', '涨跌幅', '主力净流入', '超大单净流入', '大单净流入']
        print(主力流入TOP20[显示列].to_string(index=False))
        
        # 2. 主力资金流出分析
        # (Main capital outflow analysis)
        print("\n💸 主力资金净流出TOP10分析：")
        主力流出TOP10 = df_资金流数据.nsmallest(10, '主力净流入')
        print(主力流出TOP10[显示列].to_string(index=False))
        
        # 3. 资金流向与涨跌幅相关性分析
        # (Correlation analysis between capital flow and price change)
        print("\n📊 资金流向与涨跌幅相关性分析：")
        相关性数据 = df_资金流数据[['涨跌幅', '主力净流入', '超大单净流入', '大单净流入', '中单净流入', '小单净流入']]
        相关性矩阵 = 相关性数据.corr()
        
        print("涨跌幅与各类资金流向的相关系数：")
        涨跌幅相关性 = 相关性矩阵['涨跌幅'].sort_values(ascending=False)
        for 指标, 相关系数 in 涨跌幅相关性.items():
            if 指标 != '涨跌幅':
                print(f"   • {指标}：{相关系数:.4f}")
        
        # 4. 资金流向占比分析
        # (Capital flow ratio analysis)
        print(f"\n📈 主力净流入占比分析：")
        高占比股票 = df_资金流数据[df_资金流数据['主力净流入占比'] > 10]
        print(f"   • 主力净流入占比>10%的股票：{len(高占比股票)} 只")
        
        if not 高占比股票.empty:
            print("   高占比股票前10名：")
            高占比TOP10 = 高占比股票.nlargest(10, '主力净流入占比')
            print(高占比TOP10[['股票名称', '涨跌幅', '主力净流入', '主力净流入占比']].to_string(index=False))
        
        # 5. 按涨跌幅区间统计资金流向
        # (Statistics of capital flow by price change intervals)
        print(f"\n📊 按涨跌幅区间统计平均主力净流入：")
        df_资金流数据['涨跌幅区间'] = pd.cut(
            df_资金流数据['涨跌幅'], 
            bins=[-20, -5, -2, 0, 2, 5, 20],
            labels=['大跌区(<-5%)', '小跌区(-5%~-2%)', '微跌区(-2%~0%)', 
                   '微涨区(0%~2%)', '小涨区(2%~5%)', '大涨区(>5%)']
        )
        
        区间统计 = df_资金流数据.groupby('涨跌幅区间').agg({
            '主力净流入': ['mean', 'count', 'sum'],
            '涨跌幅': 'mean'
        }).round(2)
        
        区间统计.columns = ['平均主力净流入', '股票数量', '总主力净流入', '平均涨跌幅']
        print(区间统计.to_string())
        
    except Exception as e:
        print(f"❌ 批量分析过程中发生错误：{e}")


def 高级示例2_实时监控系统():
    """
    高级示例2：构建实时数据监控系统
    Advanced Example 2: Build real-time data monitoring system
    
    展示如何设置实时监控系统，包括回调函数和自定义警报
    """
    print("\n" + "=" * 100)
    print("📡 高级示例2：实时数据监控系统")
    print("=" * 100)
    
    # 定义概念板块监控回调函数
    # (Define concept sector monitoring callback function)
    def 概念板块数据更新回调(df_更新数据: pd.DataFrame):
        """概念板块数据更新时的回调处理"""
        print(f"\n🔄 概念板块数据更新 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📊 更新板块数量：{len(df_更新数据)}")
        
        # 识别强势板块
        强势板块 = df_更新数据[df_更新数据['涨跌幅'] > 5]
        if not 强势板块.empty:
            print(f"   🚀 发现强势板块({len(强势板块)}个)：")
            for _, 板块 in 强势板块.head(3).iterrows():
                print(f"      • {板块['板块名称']}：+{板块['涨跌幅']:.2f}%")
        
        # 资金流向警报
        if '主力净流入' in df_更新数据.columns:
            大额流入 = df_更新数据[df_更新数据['主力净流入'] > 50000]  # 5亿以上
            if not 大额流入.empty:
                print(f"   💰 大额资金流入警报({len(大额流入)}个)：")
                for _, 板块 in 大额流入.head(2).iterrows():
                    print(f"      • {板块['板块名称']}：{板块['主力净流入']:,.0f}万元")
    
    # 定义个股资金流监控回调函数
    # (Define individual stock capital flow monitoring callback function)
    def 个股资金流更新回调(df_更新数据: pd.DataFrame):
        """个股资金流向数据更新时的回调处理"""
        print(f"\n🔄 个股资金流数据更新 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📊 更新股票数量：{len(df_更新数据)}")
        
        # 主力大幅流入警报
        大幅流入 = df_更新数据[df_更新数据['主力净流入'] > 20000]  # 2亿以上
        if not 大幅流入.empty:
            print(f"   💎 主力大幅流入股票({len(大幅流入)}只)：")
            for _, 股票 in 大幅流入.head(3).iterrows():
                print(f"      • {股票['股票名称']}({股票['股票代码']})：{股票['主力净流入']:,.0f}万元, {股票['涨跌幅']:+.2f}%")
    
    try:
        print("🚀 正在启动实时监控系统...")
        
        # 创建概念板块监控器
        # (Create concept sector monitor)
        概念监控器 = ConceptSectorMonitor()
        概念监控器.set_callback(概念板块数据更新回调)
        
        # 创建个股资金流监控器
        # (Create individual stock capital flow monitor)
        个股监控器 = StockCapitalFlowMonitor()
        个股监控器.set_callback(个股资金流更新回调)
        
        print("✅ 监控系统已准备就绪")
        print("\n📋 监控系统运行参数：")
        print("   • 概念板块监控间隔：30秒")
        print("   • 个股资金流监控间隔：60秒")
        print("   • 监控运行时长：3分钟（演示）")
        print("\n🔄 开始监控...")
        
        # 启动监控器
        概念监控器.start(interval=30)  # 30秒更新间隔
        个股监控器.start(interval=60)   # 60秒更新间隔
        
        # 运行监控一段时间（演示用）
        监控时长 = 180  # 3分钟
        print(f"⏰ 监控将运行 {监控时长} 秒...")
        time.sleep(监控时长)
        
        # 停止监控
        print("\n🛑 正在停止监控系统...")
        概念监控器.stop()
        个股监控器.stop()
        print("✅ 监控系统已停止")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断监控")
        if '概念监控器' in locals():
            概念监控器.stop()
        if '个股监控器' in locals():
            个股监控器.stop()
    except Exception as e:
        print(f"❌ 监控系统运行错误：{e}")


def 高级示例3_历史数据分析():
    """
    高级示例3：历史数据深度分析
    Advanced Example 3: Deep analysis of historical data
    
    使用已保存的历史数据进行趋势分析和模式识别
    """
    print("\n" + "=" * 100)
    print("📈 高级示例3：历史数据深度分析")
    print("=" * 100)
    
    try:
        # 查找历史数据文件
        # (Find historical data files)
        项目根目录 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        资金流数据目录 = os.path.join(项目根目录, "capital_flow_data")
        csv文件模式 = os.path.join(资金流数据目录, "capital_flow_*.csv")
        csv文件列表 = glob.glob(csv文件模式)
        
        if not csv文件列表:
            print(f"❌ 在 {资金流数据目录} 中未找到历史数据文件")
            print("💡 提示：请先运行单次爬取或监控功能生成数据文件")
            return
        
        # 使用最新的数据文件
        最新csv文件 = max(csv文件列表, key=os.path.getctime)
        print(f"📂 正在分析文件：{os.path.basename(最新csv文件)}")
        
        df_历史数据 = pd.read_csv(最新csv文件)
        print(f"📊 数据记录数：{len(df_历史数据)} 条")
        
        # 1. 资金流向占比分布分析
        # (Capital flow ratio distribution analysis)
        print(f"\n📊 主力净流入占比分布分析：")
        占比区间 = [-100, -20, -10, -5, 0, 5, 10, 20, 100]
        占比标签 = ['大幅流出', '中等流出', '小幅流出', '微幅流出', '微幅流入', '小幅流入', '中等流入', '大幅流入']
        
        df_历史数据['流入占比区间'] = pd.cut(df_历史数据['主力净流入占比'], bins=占比区间, labels=占比标签)
        占比分布 = df_历史数据['流入占比区间'].value_counts().sort_index()
        
        for 区间, 数量 in 占比分布.items():
            比例 = 数量 / len(df_历史数据) * 100
            print(f"   • {区间}：{数量} 只股票 ({比例:.1f}%)")
        
        # 2. 行业资金流向分析（如果有行业数据）
        # (Industry capital flow analysis if industry data available)
        if '所属行业' in df_历史数据.columns:
            print(f"\n🏭 行业资金流向分析（TOP10）：")
            行业统计 = df_历史数据.groupby('所属行业').agg({
                '主力净流入': ['sum', 'mean', 'count']
            }).round(2)
            
            行业统计.columns = ['总流入', '平均流入', '股票数量']
            行业统计 = 行业统计.sort_values('总流入', ascending=False).head(10)
            print(行业统计.to_string())
        
        # 3. 超大单vs大单流向对比
        # (Ultra-large vs large order flow comparison)
        print(f"\n💰 超大单vs大单资金流向对比：")
        超大单流入股票 = len(df_历史数据[df_历史数据['超大单净流入'] > 0])
        大单流入股票 = len(df_历史数据[df_历史数据['大单净流入'] > 0])
        
        print(f"   • 超大单净流入股票：{超大单流入股票} 只 ({超大单流入股票/len(df_历史数据)*100:.1f}%)")
        print(f"   • 大单净流入股票：{大单流入股票} 只 ({大单流入股票/len(df_历史数据)*100:.1f}%)")
        
        # 4. 找出异常股票（主力和散户资金流向相反）
        # (Find anomalous stocks with opposite main and retail capital flows)
        print(f"\n🔍 异常资金流向股票分析：")
        异常股票 = df_历史数据[
            ((df_历史数据['主力净流入'] > 0) & (df_历史数据['小单净流入'] < -10000)) |  # 主力流入但散户大幅流出
            ((df_历史数据['主力净流入'] < 0) & (df_历史数据['小单净流入'] > 10000))    # 主力流出但散户大幅流入
        ]
        
        print(f"   发现 {len(异常股票)} 只异常资金流向股票")
        if not 异常股票.empty:
            print("   异常股票详情（前5只）：")
            异常显示列 = ['股票名称', '涨跌幅', '主力净流入', '小单净流入', '主力净流入占比']
            print(异常股票[异常显示列].head().to_string(index=False))
        
        # 5. 生成投资建议
        # (Generate investment suggestions)
        print(f"\n💡 基于数据的投资建议：")
        
        优质股票 = df_历史数据[
            (df_历史数据['主力净流入'] > 5000) &      # 主力净流入>5000万
            (df_历史数据['超大单净流入'] > 0) &        # 超大单流入
            (df_历史数据['涨跌幅'] > 0) &             # 上涨
            (df_历史数据['主力净流入占比'] > 5)        # 占比>5%
        ]
        
        print(f"   📈 优质标的筛选结果：{len(优质股票)} 只")
        if not 优质股票.empty:
            优质股票排序 = 优质股票.nlargest(5, '主力净流入')
            建议显示列 = ['股票名称', '股票代码', '涨跌幅', '主力净流入', '主力净流入占比']
            print("   推荐关注（TOP5）：")
            print(优质股票排序[建议显示列].to_string(index=False))
            
    except Exception as e:
        print(f"❌ 历史数据分析过程中发生错误：{e}")


def 高级示例4_数据库分析():
    """
    高级示例4：使用数据库分析器进行高级分析
    Advanced Example 4: Advanced analysis using database analyzer
    
    使用内置的数据库分析功能进行更深入的分析
    """
    print("\n" + "=" * 100)
    print("🗄️ 高级示例4：数据库深度分析")
    print("=" * 100)
    
    if CapitalFlowAnalyzer is None:
        print("❌ CapitalFlowAnalyzer不可用，跳过此示例")
        return
    
    try:
        # 创建分析器实例
        # (Create analyzer instance)
        分析器 = CapitalFlowAnalyzer()
        
        # 1. 获取最新数据概览
        # (Get latest data overview)
        print("📊 获取数据库最新数据...")
        最新数据 = 分析器.get_latest_data(limit=100)
        
        if 最新数据.empty:
            print("❌ 数据库中暂无数据，请先运行爬虫获取数据")
            return
        
        print(f"✅ 数据库中有 {len(最新数据)} 条最新记录")
        
        # 2. 主力净流入TOP分析
        # (Main capital inflow TOP analysis)
        print(f"\n💹 主力净流入TOP20分析：")
        top_流入股票 = 分析器.get_top_inflow_stocks(top_n=20)
        
        if not top_流入股票.empty:
            print(top_流入股票[['股票名称', '股票代码', '主力净流入', '涨跌幅', '更新时间']].to_string(index=False))
        else:
            print("   暂无主力净流入数据")
        
        # 3. 连续流入股票分析
        # (Continuous inflow stocks analysis)
        print(f"\n🔄 连续主力净流入股票分析：")
        for 天数 in [2, 3, 5]:
            连续流入股票 = 分析器.get_continuous_inflow_stocks(days=天数)
            print(f"   • 连续{天数}日主力净流入：{len(连续流入股票)} 只股票")
            
            if not 连续流入股票.empty and 天数 == 3:  # 详细显示3日连续的
                print("     连续3日流入详情（前10只）：")
                显示列 = ['股票名称', '股票代码', '连续天数', '平均净流入', '总净流入']
                print(连续流入股票[显示列].head(10).to_string(index=False))
        
        # 4. 板块资金流向分析
        # (Sector capital flow analysis)
        print(f"\n🏭 板块资金流向分析：")
        板块流向 = 分析器.analyze_sector_flow()
        
        if not 板块流向.empty:
            print(板块流向.to_string())
        else:
            print("   暂无板块资金流向数据")
            
    except Exception as e:
        print(f"❌ 数据库分析过程中发生错误：{e}")


def 高级示例5_股票概念映射分析():
    """
    高级示例5：股票与概念板块映射分析
    Advanced Example 5: Stock-to-concept sector mapping analysis
    
    分析个股与概念板块的关联关系
    """
    print("\n" + "=" * 100)
    print("🔗 高级示例5：股票与概念板块映射分析")
    print("=" * 100)
    
    try:
        print("⏳ 正在获取股票与概念板块映射关系...")
        
        # 获取股票到概念的映射（这可能需要较长时间）
        # (Get stock-to-concept mapping - this may take a long time)
        股票概念映射 = get_stock_to_concept_map(
            save_to_file=True,
            max_workers=5  # 减少并发数以避免被限制
        )
        
        if not 股票概念映射:
            print("❌ 未获取到股票概念映射数据")
            return
        
        print(f"✅ 成功获取 {len(股票概念映射)} 只股票的概念板块映射")
        
        # 1. 统计分析
        # (Statistical analysis)
        print(f"\n📊 映射关系统计分析：")
        
        概念数量分布 = {}
        for 股票代码, 概念列表 in 股票概念映射.items():
            概念数量 = len(概念列表)
            概念数量分布[概念数量] = 概念数量分布.get(概念数量, 0) + 1
        
        print("   股票所属概念数量分布：")
        for 概念数, 股票数 in sorted(概念数量分布.items()):
            print(f"     • 属于{概念数}个概念的股票：{股票数} 只")
        
        # 2. 找出概念最多的股票
        # (Find stocks with the most concepts)
        print(f"\n🏆 所属概念最多的股票TOP10：")
        概念最多股票 = sorted(股票概念映射.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        for 股票代码, 概念列表 in 概念最多股票:
            print(f"   • {股票代码}：{len(概念列表)} 个概念")
            if len(概念列表) > 10:  # 只显示概念特别多的股票的部分概念
                print(f"     主要概念：{', '.join(概念列表[:5])}...")
            else:
                print(f"     概念：{', '.join(概念列表)}")
        
        # 3. 概念热度分析
        # (Concept popularity analysis)
        print(f"\n🔥 概念板块热度分析（包含股票数最多的概念TOP20）：")
        概念热度统计 = {}
        
        for 概念列表 in 股票概念映射.values():
            for 概念 in 概念列表:
                概念热度统计[概念] = 概念热度统计.get(概念, 0) + 1
        
        热门概念 = sorted(概念热度统计.items(), key=lambda x: x[1], reverse=True)[:20]
        
        for 排名, (概念名称, 股票数量) in enumerate(热门概念, 1):
            print(f"   {排名:2d}. {概念名称}：{股票数量} 只股票")
            
    except Exception as e:
        print(f"❌ 股票概念映射分析过程中发生错误：{e}")


def 主函数():
    """
    主函数：运行高级示例选择器
    Main function: Run advanced examples selector
    """
    print("🎯 东方财富数据爬虫高级功能示例")
    print("🕒 开始时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 100)
    
    示例选项 = {
        '1': ('个股资金流向批量分析', 高级示例1_个股资金流向批量分析),
        '2': ('实时监控系统演示', 高级示例2_实时监控系统),
        '3': ('历史数据深度分析', 高级示例3_历史数据分析),
        '4': ('数据库深度分析', 高级示例4_数据库分析),
        '5': ('股票概念映射分析', 高级示例5_股票概念映射分析),
        'all': ('运行所有示例', None)
    }
    
    print("📋 可用的高级示例：")
    for 编号, (名称, _) in 示例选项.items():
        if 编号 != 'all':
            print(f"   {编号}. {名称}")
    print("   all. 运行所有示例（按顺序）")
    print("   0. 退出")
    
    while True:
        选择 = input(f"\n请选择要运行的示例 (1-5/all/0): ").strip().lower()
        
        if 选择 == '0':
            print("👋 退出高级示例程序")
            break
        elif 选择 in 示例选项:
            if 选择 == 'all':
                print("\n🚀 开始运行所有高级示例...")
                for 编号 in ['1', '2', '3', '4', '5']:
                    print(f"\n>>> 正在运行示例{编号}...")
                    try:
                        示例选项[编号][1]()
                    except Exception as e:
                        print(f"❌ 示例{编号}运行出错：{e}")
                        continue
                break
            else:
                print(f"\n🚀 开始运行：{示例选项[选择][0]}")
                try:
                    示例选项[选择][1]()
                except Exception as e:
                    print(f"❌ 示例运行出错：{e}")
                
                继续选择 = input(f"\n是否继续选择其他示例？(y/n): ").strip().lower()
                if 继续选择 != 'y':
                    break
        else:
            print("❌ 无效选择，请重新输入")
    
    print(f"\n✅ 高级示例程序结束")
    print("🕒 结束时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 100)


if __name__ == "__main__":
    主函数()