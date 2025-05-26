"""
测试脚本 - 验证爬虫功能是否正常
"""

import sys
import json
from .eastmoney_capital_flow_scraper import DataFetcher, DataParser, CapitalFlowConfig

def test_api_connection():
    """测试API连接"""
    print("1. 测试API连接...")
    config = CapitalFlowConfig()
    fetcher = DataFetcher(config)
    
    try:
        # 尝试获取第一页数据
        result = fetcher.fetch_data(page=1, page_size=10)
        
        if result and 'data' in result:
            print("✓ API连接成功")
            print(f"  - 返回数据条数: {len(result['data']['diff'])}")
            print(f"  - 总记录数: {result['data']['total']}")
            return True
        else:
            print("✗ API返回数据格式异常")
            return False
            
    except Exception as e:
        print(f"✗ API连接失败: {e}")
        return False


def test_data_parsing():
    """测试数据解析"""
    print("\n2. 测试数据解析...")
    config = CapitalFlowConfig()
    fetcher = DataFetcher(config)
    parser = DataParser(config)
    
    try:
        # 获取数据
        result = fetcher.fetch_data(page=1, page_size=5)
        
        if result and 'data' in result and result['data']['diff']:
            # 解析第一条数据
            first_stock = result['data']['diff'][0]
            parsed = parser.parse_stock_data(first_stock)
            
            print("✓ 数据解析成功")
            print("  示例数据:")
            for key, value in parsed.items():
                if key != '更新时间':
                    print(f"    {key}: {value}")
            
            # 检查必要字段
            required_fields = ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入']
            missing_fields = [field for field in required_fields if field not in parsed]
            
            if missing_fields:
                print(f"  ⚠ 缺少字段: {missing_fields}")
                return False
            
            return True
        else:
            print("✗ 无数据可解析")
            return False
            
    except Exception as e:
        print(f"✗ 数据解析失败: {e}")
        return False


def test_batch_processing():
    """测试批量处理"""
    print("\n3. 测试批量数据处理...")
    config = CapitalFlowConfig()
    fetcher = DataFetcher(config)
    parser = DataParser(config)
    
    try:
        # 获取多页数据
        all_data = fetcher.fetch_all_pages(max_pages=2)
        
        if all_data:
            # 批量解析
            df = parser.parse_batch_data(all_data)
            
            print("✓ 批量处理成功")
            print(f"  - 处理数据条数: {len(df)}")
            print(f"  - 数据列: {df.columns.tolist()}")
            
            # 显示TOP5主力净流入
            print("\n  主力净流入TOP5:")
            top5 = df.nlargest(5, '主力净流入')[['股票代码', '股票名称', '主力净流入']]
            for _, row in top5.iterrows():
                print(f"    {row['股票代码']} {row['股票名称']}: {row['主力净流入']:.2f}万")
            
            return True
        else:
            print("✗ 批量获取数据失败")
            return False
            
    except Exception as e:
        print(f"✗ 批量处理失败: {e}")
        return False


def test_full_scraping():
    """测试完整爬取流程"""
    print("\n4. 测试完整爬取流程...")
    from .eastmoney_capital_flow_scraper import CapitalFlowScraper
    
    try:
        scraper = CapitalFlowScraper()
        
        # 执行爬取但不保存文件
        df = scraper.scrape_once(save_to_file=False)
        
        if df is not None and not df.empty:
            print("✓ 完整爬取成功")
            print(f"  - 数据条数: {len(df)}")
            print(f"  - 数据时间跨度: {df['更新时间'].iloc[0]}")
            
            # 基本统计
            print("\n  基本统计:")
            print(f"    主力净流入总额: {df['主力净流入'].sum():.2f}万")
            print(f"    流入股票数: {len(df[df['主力净流入'] > 0])}")
            print(f"    流出股票数: {len(df[df['主力净流入'] < 0])}")
            print(f"    平均涨跌幅: {df['涨跌幅'].mean():.2f}%")
            
            return True
        else:
            print("✗ 爬取返回空数据")
            return False
            
    except Exception as e:
        print(f"✗ 完整爬取失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("东方财富个股资金流向爬虫 - 功能测试")
    print("=" * 50)
    
    tests = [
        test_api_connection,
        test_data_parsing,
        test_batch_processing,
        test_full_scraping
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试异常: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！爬虫功能正常。")
    else:
        print("✗ 部分测试失败，请检查相关功能。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)