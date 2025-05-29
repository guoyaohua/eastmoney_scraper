"""
API接口测试脚本
测试新的通用板块爬虫API接口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper import get_sectors, get_industry_sectors, SectorType
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_api():
    """测试新的API接口"""
    print("=" * 60)
    print("API接口测试")
    print("=" * 60)
    
    # 测试1: 使用字符串参数获取概念板块数据
    print("测试1: 获取概念板块数据（使用字符串参数）")
    df_concept = get_sectors("concept")
    print(f"获取到 {len(df_concept)} 个概念板块")
    print(df_concept[['板块名称', '涨跌幅', '主力净流入']].head())
    print()
    
    # 测试2: 使用枚举类型获取行业板块数据
    print("测试2: 获取行业板块数据（使用枚举类型）")
    df_industry = get_sectors(SectorType.INDUSTRY, save_to_file=True)
    print(f"获取到 {len(df_industry)} 个行业板块")
    print(df_industry[['板块名称', '涨跌幅', '主力净流入']].head())
    print()
    
    # 测试3: 使用便捷接口获取行业板块数据
    print("测试3: 使用便捷接口获取行业板块数据")
    df_industry2 = get_industry_sectors()
    print(f"获取到 {len(df_industry2)} 个行业板块")
    print()
    
    # 验证数据一致性
    if len(df_industry) == len(df_industry2):
        print("✅ 数据一致性验证通过：两种方法获取的行业板块数量相同")
    else:
        print("❌ 数据一致性验证失败：两种方法获取的数据不一致")

if __name__ == "__main__":
    try:
        test_api()
        print("\n🎉 所有API接口测试完成！")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()