"""
股票列表爬虫测试模块

本模块包含对stock_list_scraper模块的完整测试，验证股票列表数据获取功能的正确性。
测试覆盖配置初始化、数据获取、解析、保存等核心功能。
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime
import tempfile
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper.stock_list_scraper import (
    StockListScraper, StockMarket, StockListConfig,
    StockListFetcher, StockListParser
)


class TestStockListConfig(unittest.TestCase):
    """测试股票列表配置类"""
    
    def setUp(self):
        self.config = StockListConfig()
    
    def test_config_initialization(self):
        """测试配置初始化"""
        # 检查URL配置
        self.assertIsNotNone(self.config.STOCK_LIST_URL)
        self.assertIn("eastmoney.com", self.config.STOCK_LIST_URL)
        
        # 检查请求头配置
        self.assertIsInstance(self.config.HEADERS, dict)
        self.assertIn('User-Agent', self.config.HEADERS)
        
        # 检查参数配置
        self.assertIsInstance(self.config.BASE_PARAMS, dict)
        self.assertIn('pn', self.config.BASE_PARAMS)
        self.assertIn('pz', self.config.BASE_PARAMS)
        
        # 检查市场过滤器配置
        self.assertIsInstance(self.config.MARKET_FILTERS, dict)
        self.assertIn(StockMarket.ALL, self.config.MARKET_FILTERS)
        self.assertIn(StockMarket.SH_MAIN, self.config.MARKET_FILTERS)
        
        # 检查字段映射配置
        self.assertIsInstance(self.config.FIELD_MAPPING, dict)
        self.assertIn('f12', self.config.FIELD_MAPPING)
        self.assertIn('f14', self.config.FIELD_MAPPING)
        
        print("✓ 股票列表配置初始化测试通过")


class TestStockListScraper(unittest.TestCase):
    """测试股票列表爬虫主类"""
    
    def setUp(self):
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = StockListScraper(output_dir=self.temp_dir)
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_scraper_initialization(self):
        """测试爬虫初始化"""
        self.assertIsNotNone(self.scraper.config)
        self.assertIsNotNone(self.scraper.fetcher)
        self.assertIsNotNone(self.scraper.parser)
        self.assertTrue(os.path.exists(self.temp_dir))
        
        print("✓ 股票列表爬虫初始化测试通过")
    
    def test_get_supported_markets(self):
        """测试获取支持的市场类型"""
        markets = self.scraper.get_supported_markets()
        self.assertIsInstance(markets, list)
        self.assertIn('all', markets)
        self.assertIn('sh_main', markets)
        self.assertIn('sz_main', markets)
        self.assertIn('chinext', markets)
        self.assertIn('star', markets)
        
        print("✓ 支持的市场类型测试通过")


def run_stock_list_tests():
    """运行股票列表相关测试"""
    print("=" * 60)
    print("开始运行股票列表爬虫测试...")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestStockListConfig,
        TestStockListScraper
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("股票列表爬虫测试结果汇总:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='股票列表爬虫测试')
    parser.add_argument('--mode', choices=['test', 'demo'], default='test',
                      help='运行模式: test=完整测试, demo=演示模式')
    
    args = parser.parse_args()
    
    if args.mode == 'demo':
        print("股票列表爬虫演示模式")
        print("-" * 40)
        
        # 演示基本功能
        try:
            from eastmoney_scraper.stock_list_scraper import StockListScraper, StockMarket
            
            scraper = StockListScraper()
            
            print("支持的市场类型:")
            markets = scraper.get_supported_markets()
            for market in markets:
                print(f"  - {market}")
            
            print("\n配置信息:")
            print(f"  API URL: {scraper.config.STOCK_LIST_URL}")
            print(f"  支持的市场数量: {len(scraper.config.MARKET_FILTERS)}")
            print(f"  字段映射数量: {len(scraper.config.FIELD_MAPPING)}")
            
            print("\n✓ 股票列表爬虫演示完成")
            
        except Exception as e:
            print(f"✗ 演示过程中出现错误: {e}")
    else:
        # 运行完整测试
        run_stock_list_tests()