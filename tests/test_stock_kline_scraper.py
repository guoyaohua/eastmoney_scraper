"""
个股K线历史数据爬虫测试脚本
测试各种K线周期、复权类型和批量获取功能
"""

import os
import sys
import unittest
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper.stock_kline_scraper import (
    StockKlineScraper,
    KlinePeriod,
    AdjustType,
    StockKlineConfig,
    StockKlineFetcher,
    StockKlineParser
)


class TestStockKlineScraper(unittest.TestCase):
    """个股K线数据爬虫测试类"""

    def setUp(self):
        """测试初始化"""
        self.scraper = StockKlineScraper(output_dir="output/test_kline_data")
        
        # 测试用股票代码
        self.test_stocks = [
            '000001',  # 平安银行（深市）
            '600000',  # 浦发银行（沪市）
            '300001'   # 特锐德（创业板）
        ]

    def test_config_initialization(self):
        """测试配置类初始化"""
        config = StockKlineConfig()
        
        # 检查必要的配置项
        self.assertIsNotNone(config.HEADERS)
        self.assertIsNotNone(config.KLINE_URL)
        self.assertIsNotNone(config.FIELD_MAPPING)
        self.assertIsNotNone(config.MARKET_MAPPING)
        
        print("✓ 配置类初始化测试通过")

    def test_stock_code_processing(self):
        """测试股票代码处理功能"""
        fetcher = StockKlineFetcher(StockKlineConfig())
        
        # 测试不同格式的股票代码
        test_cases = [
            ('000001', '0.000001'),  # 深市代码
            ('600000', '1.600000'),  # 沪市代码
            ('300001', '0.300001'),  # 创业板代码
            ('sh600000', '1.600000'),  # 带沪市前缀
            ('sz000001', '0.000001'),  # 带深市前缀
            ('1.600000', '1.600000'),  # 已处理格式
        ]
        
        for input_code, expected_output in test_cases:
            result = fetcher._get_stock_code_with_market(input_code)
            self.assertEqual(result, expected_output, 
                           f"股票代码 {input_code} 处理结果应为 {expected_output}，实际为 {result}")
        
        print("✓ 股票代码处理功能测试通过")

    def test_single_stock_daily_kline(self):
        """测试单只股票日K线数据获取"""
        stock_code = self.test_stocks[0]
        
        # 获取日K线数据
        df = self.scraper.scrape_single_stock(
            stock_code=stock_code,
            period=KlinePeriod.DAILY,
            adjust_type=AdjustType.FORWARD,
            limit=100
        )
        
        # 验证数据
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            # 检查必要的列
            required_columns = ['股票代码', '日期', '开盘价', '收盘价', '最高价', '最低价', '成交量']
            for col in required_columns:
                self.assertIn(col, df.columns, f"缺少必要列: {col}")
            
            # 检查股票代码
            self.assertTrue(all(df['股票代码'] == stock_code))
            
            # 检查数据类型
            self.assertTrue(df['开盘价'].dtype in ['float64', 'object'])
            self.assertTrue(df['成交量'].dtype in ['int64', 'object'])
            
            print(f"✓ 单只股票日K线测试通过，获取 {len(df)} 条数据")
            print(f"  股票代码: {stock_code}")
            print(f"  数据时间范围: {df['日期'].min()} 到 {df['日期'].max()}")
        else:
            print(f"⚠ 股票 {stock_code} 未获取到数据，可能是非交易时间或网络问题")

    def test_different_periods(self):
        """测试不同K线周期"""
        stock_code = self.test_stocks[0]
        
        # 测试不同周期
        periods_to_test = [
            KlinePeriod.DAILY,
            KlinePeriod.WEEKLY,
            KlinePeriod.MONTHLY,
            KlinePeriod.MIN_60
        ]
        
        results = {}
        for period in periods_to_test:
            df = self.scraper.scrape_single_stock(
                stock_code=stock_code,
                period=period,
                limit=50
            )
            results[period.value] = len(df) if not df.empty else 0
            print(f"  {period.value}周期: {len(df)}条数据")
        
        print("✓ 不同K线周期测试完成")
        return results

    def test_different_adjust_types(self):
        """测试不同复权类型"""
        stock_code = self.test_stocks[0]
        
        # 测试不同复权类型
        adjust_types = [
            AdjustType.NONE,      # 不复权
            AdjustType.FORWARD,   # 前复权
            AdjustType.BACKWARD   # 后复权
        ]
        
        results = {}
        for adjust_type in adjust_types:
            df = self.scraper.scrape_single_stock(
                stock_code=stock_code,
                period=KlinePeriod.DAILY,
                adjust_type=adjust_type,
                limit=50
            )
            results[adjust_type.value] = len(df) if not df.empty else 0
            print(f"  复权类型{adjust_type.value}: {len(df)}条数据")
        
        print("✓ 不同复权类型测试完成")
        return results

    def test_multiple_stocks_kline(self):
        """测试批量获取多只股票K线数据"""
        # 获取多只股票的数据
        data_dict = self.scraper.scrape_multiple_stocks(
            stock_codes=self.test_stocks,
            period=KlinePeriod.DAILY,
            limit=50,
            max_workers=3
        )
        
        # 验证结果
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(len(data_dict), len(self.test_stocks))
        
        success_count = 0
        total_records = 0
        
        for stock_code, df in data_dict.items():
            self.assertIn(stock_code, self.test_stocks)
            self.assertIsInstance(df, pd.DataFrame)
            
            if not df.empty:
                success_count += 1
                total_records += len(df)
                # 验证股票代码正确性
                self.assertTrue(all(df['股票代码'] == stock_code))
                print(f"  {stock_code}: {len(df)}条数据")
            else:
                print(f"  {stock_code}: 无数据")
        
        print(f"✓ 批量获取测试完成，成功: {success_count}/{len(self.test_stocks)}，总计: {total_records}条记录")
        return data_dict

    def test_data_saving(self):
        """测试数据保存功能"""
        stock_code = self.test_stocks[0]
        
        # 获取测试数据
        df = self.scraper.scrape_single_stock(
            stock_code=stock_code,
            period=KlinePeriod.DAILY,
            limit=50
        )
        
        if not df.empty:
            # 测试CSV保存
            csv_path = self.scraper.save_single_stock_data(
                df, stock_code, KlinePeriod.DAILY, 'csv'
            )
            self.assertTrue(os.path.exists(csv_path))
            print(f"✓ CSV保存测试通过: {csv_path}")
            
            # 测试JSON保存
            json_path = self.scraper.save_single_stock_data(
                df, stock_code, KlinePeriod.DAILY, 'json'
            )
            self.assertTrue(os.path.exists(json_path))
            print(f"✓ JSON保存测试通过: {json_path}")
        else:
            print("⚠ 数据保存测试跳过（无可用数据）")

    def test_complete_workflow(self):
        """测试完整工作流程"""
        stock_code = self.test_stocks[0]
        
        # 执行完整的单只股票爬取流程
        df, filepath = self.scraper.run_single_stock(
            stock_code=stock_code,
            period=KlinePeriod.DAILY,
            limit=100,
            save_format='csv'
        )
        
        # 验证结果
        self.assertIsInstance(df, pd.DataFrame)
        
        if not df.empty:
            self.assertTrue(os.path.exists(filepath))
            print(f"✓ 完整工作流程测试通过")
            print(f"  数据条数: {len(df)}")
            print(f"  保存路径: {filepath}")
        else:
            print("⚠ 完整工作流程测试：无可用数据")

    def test_batch_workflow(self):
        """测试批量工作流程"""
        # 执行批量爬取流程
        data_dict, filepaths = self.scraper.run_multiple_stocks(
            stock_codes=self.test_stocks,
            period=KlinePeriod.DAILY,
            limit=50,
            max_workers=3,
            save_format='csv',
            combine_files=False
        )
        
        # 验证结果
        self.assertIsInstance(data_dict, dict)
        self.assertIsInstance(filepaths, list)
        
        success_count = sum(1 for df in data_dict.values() if not df.empty)
        
        print(f"✓ 批量工作流程测试完成")
        print(f"  成功获取: {success_count}/{len(self.test_stocks)}")
        print(f"  保存文件: {len(filepaths)}个")
        
        # 验证文件存在
        for filepath in filepaths:
            self.assertTrue(os.path.exists(filepath))

    def test_supported_features(self):
        """测试支持的功能列表"""
        # 测试支持的周期
        periods = self.scraper.get_supported_periods()
        self.assertIsInstance(periods, list)
        self.assertGreater(len(periods), 0)
        print(f"✓ 支持的K线周期: {periods}")
        
        # 测试支持的复权类型
        adjust_types = self.scraper.get_supported_adjust_types()
        self.assertIsInstance(adjust_types, list)
        self.assertGreater(len(adjust_types), 0)
        print(f"✓ 支持的复权类型: {adjust_types}")


def run_comprehensive_test():
    """运行综合测试"""
    print("=" * 60)
    print("东方财富个股K线历史数据爬虫 - 综合测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    test_cases = [
        'test_config_initialization',
        'test_stock_code_processing',
        'test_single_stock_daily_kline',
        'test_different_periods',
        'test_different_adjust_types',
        'test_multiple_stocks_kline',
        'test_data_saving',
        'test_complete_workflow',
        'test_batch_workflow',
        'test_supported_features'
    ]
    
    for test_case in test_cases:
        suite.addTest(TestStockKlineScraper(test_case))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("=" * 60)


def run_quick_demo():
    """运行快速演示"""
    print("=" * 50)
    print("个股K线数据爬虫 - 快速演示")
    print("=" * 50)
    
    # 创建爬虫实例
    scraper = StockKlineScraper()
    
    # 演示单只股票获取
    print("\n1. 单只股票日K线数据获取演示:")
    df, filepath = scraper.run_single_stock(
        stock_code='000001',
        period=KlinePeriod.DAILY,
        limit=10
    )
    
    if not df.empty:
        print(f"   成功获取 {len(df)} 条记录")
        print(f"   数据保存至: {filepath}")
        print(f"   最新数据预览:")
        print(df.head(3).to_string(index=False))
    
    # 演示不同周期获取
    print("\n2. 不同周期K线数据获取演示:")
    periods = [KlinePeriod.DAILY, KlinePeriod.WEEKLY, KlinePeriod.MIN_60]
    for period in periods:
        df = scraper.scrape_single_stock('000001', period=period, limit=5)
        print(f"   {period.value}周期: {len(df)}条数据")
    
    # 演示批量获取
    print("\n3. 批量股票数据获取演示:")
    stocks = ['000001', '600000', '300001']
    data_dict, filepaths = scraper.run_multiple_stocks(
        stock_codes=stocks,
        limit=5,
        max_workers=2
    )
    
    for stock_code, df in data_dict.items():
        print(f"   {stock_code}: {len(df)}条数据")
    
    print(f"\n演示完成，共保存 {len(filepaths)} 个文件")
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='个股K线数据爬虫测试')
    parser.add_argument('--mode', choices=['test', 'demo'], default='test',
                       help='运行模式: test=完整测试, demo=快速演示')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        run_comprehensive_test()
    else:
        run_quick_demo()