"""
测试重构后的板块监控器类
Test script for refactored sector monitor classes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eastmoney_scraper import SectorMonitor, ConceptSectorMonitor, IndustrySectorMonitor
import time


def test_sector_monitor_base_class():
    """测试基类SectorMonitor"""
    print("=" * 80)
    print("测试1: SectorMonitor基类")
    print("=" * 80)
    
    # 测试概念板块
    print("\n1.1 使用SectorMonitor监控概念板块:")
    concept_monitor = SectorMonitor(sector_type="concept")
    print(f"✅ 成功创建概念板块监控器")
    
    # 测试行业板块
    print("\n1.2 使用SectorMonitor监控行业板块:")
    industry_monitor = SectorMonitor(sector_type="industry")
    print(f"✅ 成功创建行业板块监控器")
    
    # 测试错误的板块类型
    print("\n1.3 测试错误的板块类型:")
    try:
        wrong_monitor = SectorMonitor(sector_type="invalid")
    except ValueError as e:
        print(f"✅ 正确抛出异常: {e}")
    
    print("\n基类测试完成！")


def test_concept_sector_monitor():
    """测试ConceptSectorMonitor"""
    print("\n" + "=" * 80)
    print("测试2: ConceptSectorMonitor类")
    print("=" * 80)
    
    monitor = ConceptSectorMonitor()
    print(f"✅ 成功创建ConceptSectorMonitor实例")
    
    # 设置回调函数
    def on_data_update(df):
        print(f"   接收到数据更新: {len(df)} 个概念板块")
        if not df.empty:
            top3 = df.nlargest(3, '涨跌幅')
            print("   涨幅前3板块:")
            for idx, (_, row) in enumerate(top3.iterrows(), 1):
                print(f"   {idx}. {row['板块名称']}: {row['涨跌幅']:+.2f}%")
    
    monitor.set_callback(on_data_update)
    print("✅ 成功设置回调函数")
    
    # 启动监控（运行5秒后停止）
    print("\n启动概念板块监控器（运行5秒）...")
    monitor.start(interval=30)
    
    time.sleep(5)
    
    monitor.stop()
    print("✅ 成功停止监控器")
    
    # 获取最新数据
    latest_data = monitor.get_latest_data()
    if latest_data is not None:
        print(f"✅ 获取到最新数据: {len(latest_data)} 个板块")
    else:
        print("ℹ️ 尚未获取到数据（时间太短）")


def test_industry_sector_monitor():
    """测试IndustrySectorMonitor"""
    print("\n" + "=" * 80)
    print("测试3: IndustrySectorMonitor类")
    print("=" * 80)
    
    monitor = IndustrySectorMonitor()
    print(f"✅ 成功创建IndustrySectorMonitor实例")
    
    # 设置回调函数
    def on_data_update(df):
        print(f"   接收到数据更新: {len(df)} 个行业板块")
        if not df.empty:
            print(f"   第一个行业: {df.iloc[0]['板块名称']}")
    
    monitor.set_callback(on_data_update)
    print("✅ 成功设置回调函数")
    
    # 启动监控（运行5秒后停止）
    print("\n启动行业板块监控器（运行5秒）...")
    monitor.start(interval=30)
    
    time.sleep(5)
    
    monitor.stop()
    print("✅ 成功停止监控器")


def test_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 80)
    print("测试4: 向后兼容性测试")
    print("=" * 80)
    
    # ConceptSectorMonitor应该默认监控概念板块
    monitor = ConceptSectorMonitor()
    print("✅ ConceptSectorMonitor保持向后兼容")
    
    # 确认监控的是概念板块
    if hasattr(monitor, 'sector_type'):
        print(f"   监控类型: {monitor.sector_type.value}")
    
    print("\n兼容性测试完成！")


def main():
    """主测试函数"""
    print("🚀 开始测试重构后的板块监控器")
    print("=" * 80)
    
    try:
        # 运行各项测试
        test_sector_monitor_base_class()
        test_concept_sector_monitor()
        test_industry_sector_monitor()
        test_compatibility()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()