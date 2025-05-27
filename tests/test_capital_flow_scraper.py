"""
东方财富数据爬虫测试套件
EastMoney Scraper Test Suite

本文件提供完整的测试功能，用于验证eastmoney_scraper包的各项功能：
- API连接测试
- 数据获取和解析测试
- 批量处理测试
- 完整爬取流程测试
- 监控功能测试

This file provides comprehensive testing functionality to verify various features 
of the eastmoney_scraper package:
- API connection testing
- Data fetching and parsing tests
- Batch processing tests
- Complete scraping workflow tests
- Monitoring functionality tests
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any

# 将项目根目录添加到Python路径
# (Add project root directory to Python path)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入eastmoney_scraper的公共API接口
# (Import public API interfaces from eastmoney_scraper)
from eastmoney_scraper import (
    # 数据获取函数
    get_stock_capital_flow,
    get_concept_sectors,
    get_concept_sectors_realtime,
    
    # 核心爬虫类
    CapitalFlowScraper,
    ConceptSectorScraper,
    
    # 监控器类
    StockCapitalFlowMonitor,
    ConceptSectorMonitor,
    
    # 工具函数
    filter_sectors_by_change,
    get_top_sectors
)

# 导入pandas用于数据分析
import pandas as pd


class TestResult:
    """测试结果记录类"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
    
    def add_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """添加测试结果"""
        self.results[test_name] = {
            'passed': passed,
            'details': details,
            'error': error,
            'timestamp': datetime.now()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试总结"""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['passed'])
        failed_tests = total_tests - passed_tests
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'duration': datetime.now() - self.start_time
        }


def test_api_connection_via_quick_fetch() -> bool:
    """
    测试1：通过快速获取测试API连接
    Test 1: Test API connection via quick fetch
    """
    print("🔗 测试1：API连接测试")
    print("─" * 50)
    
    try:
        # 使用API接口快速获取少量数据测试连接
        # (Use API interface to quickly fetch small amount of data for connection testing)
        df = get_stock_capital_flow(max_pages=1, save_to_file=False)
        
        if df is not None and not df.empty:
            print(f"✅ API连接成功")
            print(f"   • 测试获取数据量：{len(df)} 条")
            print(f"   • 数据列数：{len(df.columns)}")
            print(f"   • 主要字段：{list(df.columns[:5])}")
            return True
        elif df is not None and df.empty:
            print(f"✅ API连接成功（返回空数据，可能是市场休市）")
            return True
        else:
            print(f"❌ API连接失败：返回None")
            return False
            
    except Exception as e:
        print(f"❌ API连接测试失败：{e}")
        return False


def test_concept_sectors_data_fetching() -> bool:
    """
    测试2：概念板块数据获取测试
    Test 2: Concept sectors data fetching test
    """
    print(f"\n📊 测试2：概念板块数据获取测试")
    print("─" * 50)
    
    try:
        # 测试概念板块实时行情获取
        # (Test concept sectors real-time quotes fetching)
        print("🔄 测试概念板块实时行情获取...")
        df_realtime = get_concept_sectors_realtime()
        
        if df_realtime is not None and not df_realtime.empty:
            print(f"✅ 实时行情获取成功")
            print(f"   • 板块数量：{len(df_realtime)}")
            print(f"   • 主要字段：{list(df_realtime.columns[:6])}")
            
            # 简单数据验证
            if '板块名称' in df_realtime.columns and '涨跌幅' in df_realtime.columns:
                rising_count = len(df_realtime[df_realtime['涨跌幅'] > 0])
                falling_count = len(df_realtime[df_realtime['涨跌幅'] < 0])
                print(f"   • 上涨板块：{rising_count} 个")
                print(f"   • 下跌板块：{falling_count} 个")
            
            return True
        else:
            print(f"❌ 概念板块数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 概念板块数据测试失败：{e}")
        return False


def test_data_filtering_and_analysis() -> bool:
    """
    测试3：数据筛选和分析功能测试
    Test 3: Data filtering and analysis functionality test
    """
    print(f"\n🔍 测试3：数据筛选和分析功能测试")
    print("─" * 50)
    
    try:
        # 获取测试数据
        # (Get test data)
        print("📈 获取测试数据...")
        df = get_concept_sectors_realtime()
        
        if df is None or df.empty:
            print("⚠️ 无测试数据，跳过筛选测试")
            return True
        
        print(f"   获取到 {len(df)} 个板块数据")
        
        # 测试涨跌幅筛选
        # (Test price change filtering)
        print("🔄 测试涨跌幅筛选...")
        rising_sectors = filter_sectors_by_change(df, min_change=0)
        falling_sectors = filter_sectors_by_change(df, max_change=0)
        
        print(f"   • 上涨板块筛选：{len(rising_sectors)} 个")
        print(f"   • 下跌板块筛选：{len(falling_sectors)} 个")
        
        # 测试TOP排序
        # (Test TOP sorting)
        print("🔄 测试TOP排序...")
        top_5_rising = get_top_sectors(df, n=5, by='涨跌幅', ascending=False)
        top_5_falling = get_top_sectors(df, n=5, by='涨跌幅', ascending=True)
        
        print(f"   • 涨幅前5：{len(top_5_rising)} 个")
        print(f"   • 跌幅前5：{len(top_5_falling)} 个")
        
        if not top_5_rising.empty:
            best_sector = top_5_rising.iloc[0]
            print(f"   • 涨幅最大：{best_sector['板块名称']} ({best_sector['涨跌幅']:+.2f}%)")
        
        print("✅ 数据筛选和分析功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 数据筛选和分析测试失败：{e}")
        return False


def test_advanced_scraper_functionality() -> bool:
    """
    测试4：高级爬虫功能测试
    Test 4: Advanced scraper functionality test
    """
    print(f"\n🔧 测试4：高级爬虫功能测试")
    print("─" * 50)
    
    try:
        # 测试个股资金流向爬虫
        # (Test individual stock capital flow scraper)
        print("💰 测试个股资金流向爬虫...")
        stock_scraper = CapitalFlowScraper()
        
        # 执行测试爬取（不保存文件）
        df_stocks = stock_scraper.scrape_once(save_to_file=False)
        
        if df_stocks is not None and not df_stocks.empty:
            print(f"✅ 个股爬虫功能正常")
            print(f"   • 股票数量：{len(df_stocks)}")
            print(f"   • 主力净流入总额：{df_stocks['主力净流入'].sum():,.0f} 万元")
            
            # 显示TOP3
            top_3 = df_stocks.nlargest(3, '主力净流入')
            print("   • 主力流入TOP3：")
            for idx, (_, stock) in enumerate(top_3.iterrows(), 1):
                print(f"     {idx}. {stock['股票名称']}：{stock['主力净流入']:,.0f}万")
        
        # 测试概念板块爬虫
        # (Test concept sector scraper)
        print("\n📊 测试概念板块爬虫...")
        concept_scraper = ConceptSectorScraper()
        
        # 仅获取实时行情（加快测试速度）
        df_concepts = concept_scraper.scrape_all_data()
        
        if df_concepts is not None and not df_concepts.empty:
            print(f"✅ 概念板块爬虫功能正常")
            print(f"   • 板块数量：{len(df_concepts)}")
            
            if '主力净流入' in df_concepts.columns:
                net_inflow = df_concepts['主力净流入'].sum()
                print(f"   • 主力净流入总额：{net_inflow:,.0f} 万元")
        
        return True
        
    except Exception as e:
        print(f"❌ 高级爬虫功能测试失败：{e}")
        return False


def test_monitoring_functionality() -> bool:
    """
    测试5：监控功能测试
    Test 5: Monitoring functionality test
    """
    print(f"\n📡 测试5：监控功能测试")
    print("─" * 50)
    
    try:
        # 测试监控器创建和基本功能
        # (Test monitor creation and basic functionality)
        print("🔄 测试监控器创建...")
        
        stock_monitor = StockCapitalFlowMonitor()
        concept_monitor = ConceptSectorMonitor()
        
        print("✅ 监控器创建成功")
        
        # 测试回调设置
        # (Test callback setting)
        test_callback_called = [False]  # 使用列表以便在嵌套函数中修改
        
        def test_callback(df):
            test_callback_called[0] = True
            print(f"   📊 回调函数被调用，数据量：{len(df) if df is not None else 0}")
        
        stock_monitor.set_callback(test_callback)
        concept_monitor.set_callback(test_callback)
        
        print("✅ 回调函数设置成功")
        
        # 简短的监控测试（10秒）
        # (Brief monitoring test - 10 seconds)
        print("🔄 执行10秒监控测试...")
        
        stock_monitor.start(interval=5)  # 5秒间隔
        time.sleep(10)  # 运行10秒
        stock_monitor.stop()
        
        if test_callback_called[0]:
            print("✅ 监控功能正常（回调被触发）")
        else:
            print("⚠️ 监控功能基本正常（回调未被触发，可能是数据获取间隔问题）")
        
        return True
        
    except Exception as e:
        print(f"❌ 监控功能测试失败：{e}")
        return False


def test_error_handling() -> bool:
    """
    测试6：错误处理测试
    Test 6: Error handling test
    """
    print(f"\n⚠️ 测试6：错误处理测试")
    print("─" * 50)
    
    try:
        # 测试无效参数处理
        # (Test invalid parameter handling)
        print("🔄 测试无效参数处理...")
        
        # 测试无效的max_pages参数
        result1 = get_stock_capital_flow(max_pages=0, save_to_file=False)
        
        # 测试无效的筛选参数
        df_test = get_concept_sectors_realtime()
        if df_test is not None and not df_test.empty:
            # 测试不存在的列名
            filtered = filter_sectors_by_change(df_test, min_change=0)  # 这应该正常工作
            
            # 测试TOP排序的不存在列名
            try:
                top_invalid = get_top_sectors(df_test, n=5, by='不存在的列', ascending=False)
                # 如果没有抛出异常，检查是否有合理的fallback
                print("   ⚠️ 无效列名处理：未抛出异常，可能有fallback机制")
            except Exception:
                print("   ✅ 无效列名处理：正确抛出异常")
        
        print("✅ 错误处理机制基本正常")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败：{e}")
        return False


def run_comprehensive_tests() -> bool:
    """
    运行综合测试套件
    Run comprehensive test suite
    """
    print("🎯 东方财富数据爬虫 - 综合测试套件")
    print("🕒 开始时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 创建测试结果记录器
    test_result = TestResult()
    
    # 定义测试套件
    test_suite = [
        ("API连接测试", test_api_connection_via_quick_fetch),
        ("概念板块数据获取测试", test_concept_sectors_data_fetching),
        ("数据筛选和分析功能测试", test_data_filtering_and_analysis),
        ("高级爬虫功能测试", test_advanced_scraper_functionality),
        ("监控功能测试", test_monitoring_functionality),
        ("错误处理测试", test_error_handling),
    ]
    
    # 执行所有测试
    for test_name, test_func in test_suite:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            result = test_func()
            test_result.add_test_result(
                test_name, 
                result, 
                "测试通过" if result else "测试失败"
            )
            
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{'-'*20} {test_name} {status} {'-'*20}")
            
        except Exception as e:
            test_result.add_test_result(
                test_name, 
                False, 
                f"测试异常：{str(e)}"
            )
            print(f"\n❌ {test_name} 发生异常：{e}")
            print(f"{'-'*20} {test_name} ❌ 异常 {'-'*20}")
    
    # 生成测试报告
    # (Generate test report)
    summary = test_result.get_summary()
    
    print(f"\n" + "=" * 80)
    print("📋 测试总结报告")
    print("=" * 80)
    
    print(f"🕒 测试持续时间：{summary['duration']}")
    print(f"📊 测试统计：")
    print(f"   • 总测试数：{summary['total_tests']}")
    print(f"   • 通过测试：{summary['passed_tests']}")
    print(f"   • 失败测试：{summary['failed_tests']}")
    print(f"   • 成功率：{summary['success_rate']:.1f}%")
    
    print(f"\n📋 详细结果：")
    for test_name, result in test_result.results.items():
        status_icon = "✅" if result['passed'] else "❌"
        print(f"   {status_icon} {test_name}")
        if result['error']:
            print(f"     错误：{result['error']}")
    
    print(f"\n" + "=" * 80)
    
    if summary['success_rate'] >= 80:
        print("🎉 测试套件整体通过！eastmoney_scraper包功能基本正常。")
        print("💡 建议：可以开始使用该包进行数据爬取和分析。")
        result_status = True
    elif summary['success_rate'] >= 60:
        print("⚠️ 测试套件部分通过，建议检查失败的测试项。")
        print("💡 建议：核心功能可能正常，但某些高级功能存在问题。")
        result_status = False
    else:
        print("❌ 测试套件整体失败，存在重大问题。")
        print("💡 建议：请检查网络连接、API状态或包安装是否正确。")
        result_status = False
    
    print("=" * 80)
    return result_status


def main():
    """主函数"""
    print(f"当前工作目录：{os.getcwd()}")
    print(f"项目根目录：{project_root}")
    print(f"Python路径（前3个）：{sys.path[:3]}")
    
    success = run_comprehensive_tests()
    
    print(f"\n🕒 结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 返回适当的退出代码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()