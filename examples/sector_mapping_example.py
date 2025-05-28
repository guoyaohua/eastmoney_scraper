"""
板块成分股映射示例
演示如何获取股票到板块的映射关系
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import get_stock_to_sector_mapping, SectorType
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_concept_mapping():
    """演示获取概念板块映射（限制获取数量以节省时间）"""
    print("=" * 60)
    print("概念板块成分股映射示例（仅获取部分数据作为演示）")
    print("=" * 60)
    
    try:
        # 注意：这里使用max_workers=2来限制并发数，避免过度请求API
        # 在实际使用中，可以根据需要调整max_workers的值
        mapping = get_stock_to_sector_mapping(
            sector_type="concept",
            save_to_file=True,
            max_workers=2  # 限制并发数
        )
        
        if mapping:
            print(f"成功获取 {len(mapping)} 只股票的概念板块映射")
            
            # 显示前5个股票的映射关系
            print("\n前5个股票的概念板块映射:")
            for i, (stock_code, concepts) in enumerate(mapping.items()):
                if i >= 5:
                    break
                print(f"  {stock_code}: {concepts}")
            
            # 统计概念板块的股票数量
            concept_count = {}
            for stock, concepts in mapping.items():
                for concept in concepts:
                    concept_count[concept] = concept_count.get(concept, 0) + 1
            
            print("\n概念板块股票数量排行（前10）:")
            for concept, count in sorted(concept_count.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {concept}: {count}只股票")
                
        else:
            print("未能获取概念板块映射")
            
    except Exception as e:
        print(f"获取概念板块映射时发生错误: {e}")

def demo_industry_mapping():
    """演示获取行业板块映射（限制获取数量以节省时间）"""
    print("\n" + "=" * 60)
    print("行业板块成分股映射示例（仅获取部分数据作为演示）")
    print("=" * 60)
    
    try:
        # 同样限制并发数
        mapping = get_stock_to_sector_mapping(
            sector_type=SectorType.INDUSTRY,
            save_to_file=True,
            max_workers=2  # 限制并发数
        )
        
        if mapping:
            print(f"成功获取 {len(mapping)} 只股票的行业板块映射")
            
            # 显示前5个股票的映射关系
            print("\n前5个股票的行业板块映射:")
            for i, (stock_code, industries) in enumerate(mapping.items()):
                if i >= 5:
                    break
                print(f"  {stock_code}: {industries}")
            
            # 统计行业板块的股票数量
            industry_count = {}
            for stock, industries in mapping.items():
                for industry in industries:
                    industry_count[industry] = industry_count.get(industry, 0) + 1
            
            print("\n行业板块股票数量排行（前10）:")
            for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {industry}: {count}只股票")
                
        else:
            print("未能获取行业板块映射")
            
    except Exception as e:
        print(f"获取行业板块映射时发生错误: {e}")

if __name__ == "__main__":
    print("⚠️  注意：获取完整的板块映射数据需要较长时间（可能需要几分钟）")
    print("本示例使用限制并发数的方式来演示功能，实际使用时可以根据需要调整参数。")
    print("如果您想快速测试，可以注释掉映射获取部分，只运行板块数据获取。\n")
    
    try:
        # 演示概念板块映射
        demo_concept_mapping()
        
        # 演示行业板块映射
        demo_industry_mapping()
        
        print("\n🎉 所有映射示例演示完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断了程序执行")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()