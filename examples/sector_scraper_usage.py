"""
板块爬虫使用示例
演示如何使用通用板块爬虫获取概念板块和行业板块数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper.sector_scraper import SectorScraper, SectorType
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_concept_sector():
    """演示概念板块数据获取"""
    print("=" * 50)
    print("概念板块数据获取示例")
    print("=" * 50)
    
    # 创建概念板块爬虫实例
    concept_scraper = SectorScraper(SectorType.CONCEPT)
    
    # 获取概念板块数据
    df, filepath = concept_scraper.run_once()
    
    if not df.empty:
        print(f"成功获取 {len(df)} 个概念板块数据")
        print(f"数据已保存到: {filepath}")
        print("\n前5个概念板块:")
        print(df[['板块代码', '板块名称', '涨跌幅', '主力净流入']].head())
    else:
        print("未能获取概念板块数据")

def example_industry_sector():
    """演示行业板块数据获取"""
    print("=" * 50)
    print("行业板块数据获取示例")
    print("=" * 50)
    
    # 创建行业板块爬虫实例
    industry_scraper = SectorScraper(SectorType.INDUSTRY)
    
    # 获取行业板块数据
    df, filepath = industry_scraper.run_once()
    
    if not df.empty:
        print(f"成功获取 {len(df)} 个行业板块数据")
        print(f"数据已保存到: {filepath}")
        print("\n前5个行业板块:")
        print(df[['板块代码', '板块名称', '涨跌幅', '主力净流入']].head())
    else:
        print("未能获取行业板块数据")

def example_sector_mapping():
    """演示板块成分股映射获取"""
    print("=" * 50)
    print("板块成分股映射示例")
    print("=" * 50)
    
    # 获取概念板块映射（仅获取前3个板块作为示例）
    concept_scraper = SectorScraper(SectorType.CONCEPT)
    
    print("正在获取概念板块成分股映射...")
    mapping = concept_scraper.scrape_stock_to_sector_mapping(max_workers=3)
    
    if mapping:
        print(f"成功获取 {len(mapping)} 只股票的概念板块映射")
        # 保存映射数据
        filepath = concept_scraper.save_mapping_data(mapping)
        if filepath:
            print(f"映射数据已保存到: {filepath}")
        
        # 显示前5个股票的映射
        print("\n前5个股票的概念板块映射:")
        for i, (stock_code, sectors) in enumerate(mapping.items()):
            if i >= 5:
                break
            print(f"  {stock_code}: {sectors}")
    else:
        print("未能获取概念板块映射")

if __name__ == "__main__":
    try:
        # 运行概念板块示例
        example_concept_sector()
        
        print("\n")
        
        # 运行行业板块示例
        example_industry_sector()
        
        print("\n")
        
        # 运行映射示例（注意：这会比较耗时）
        # example_sector_mapping()
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()