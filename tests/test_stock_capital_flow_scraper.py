"""
测试个股资金流向爬虫
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import StockCapitalFlowScraper, MarketType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试个股资金流向爬虫")
    print("=" * 60)
    
    try:
        # 创建全市场爬虫实例
        scraper = StockCapitalFlowScraper(
            market_type=MarketType.ALL,
            output_dir="output"
        )
        
        print("✅ 爬虫实例创建成功")
        
        # 执行一次爬取，只获取1页数据进行测试
        print("📡 开始爬取数据...")
        df, filepath = scraper.run_once(max_pages=1, save_format='csv')
        
        if not df.empty:
            print(f"✅ 成功爬取 {len(df)} 条数据")
            print(f"📁 数据已保存到: {filepath}")
            
            # 显示数据列信息
            print(f"\n📊 数据列信息:")
            for col in df.columns:
                print(f"   - {col}")
            
            # 显示前5条数据
            print(f"\n📈 前5条数据预览:")
            print(df.head().to_string())
            
            # 测试分析功能
            print(f"\n🔍 市场概况分析:")
            summary = scraper.analyze_market_summary(df)
            for key, value in summary.items():
                print(f"   {key}: {value}")
                
            # 测试主力净流入TOP5
            top_inflow = scraper.get_top_inflow_stocks(df, 5)
            if not top_inflow.empty:
                print(f"\n🔥 主力净流入TOP5:")
                for _, row in top_inflow.iterrows():
                    print(f"   {row['股票名称']}({row['股票代码']}): {row['主力净流入']:.2f}万元")
            
            print(f"\n✅ 所有测试通过!")
            
        else:
            print("❌ 未获取到数据")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_different_markets():
    """测试不同市场类型"""
    print(f"\n🧪 测试不同市场类型")
    print("=" * 60)
    
    markets = [
        (MarketType.GEM, "创业板"),
        (MarketType.STAR, "科创板"),
        (MarketType.MAIN_BOARD, "主板")
    ]
    
    for market_type, market_name in markets:
        try:
            print(f"\n📡 测试 {market_name} 数据爬取...")
            scraper = StockCapitalFlowScraper(
                market_type=market_type,
                output_dir="output"
            )
            
            df, filepath = scraper.run_once(max_pages=1, save_format='json')
            
            if not df.empty:
                print(f"✅ {market_name}: 成功获取 {len(df)} 条数据")
                summary = scraper.analyze_market_summary(df)
                print(f"   上涨股票: {summary.get('上涨股票数', 0)} / {summary.get('总股票数', 0)}")
                print(f"   净流入总额: {summary.get('市场主力净流入总额(万元)', 0):.2f} 万元")
            else:
                print(f"⚠️ {market_name}: 未获取到数据")
                
        except Exception as e:
            print(f"❌ {market_name} 测试失败: {e}")


if __name__ == "__main__":
    print(f"🚀 开始测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_basic_functionality()
    test_different_markets()
    
    print(f"\n🏁 测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 查看生成的output目录中的数据文件")