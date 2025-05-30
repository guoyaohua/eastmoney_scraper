"""
个股K线历史数据爬虫使用示例
展示如何使用StockKlineScraper获取各种周期的K线数据
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eastmoney_scraper.stock_kline_scraper import (
    StockKlineScraper,
    KlinePeriod,
    AdjustType
)


def example_1_single_stock_daily_kline():
    """
    示例1: 获取单只股票的日K线数据
    """
    print("=" * 60)
    print("示例1: 获取单只股票的日K线数据")
    print("=" * 60)
    
    # 创建K线数据爬虫实例
    scraper = StockKlineScraper()
    
    # 获取平安银行(000001)的日K线数据
    stock_code = '000001'
    print(f"正在获取股票 {stock_code} 的日K线数据...")
    
    # 执行爬取并保存
    df, filepath = scraper.run_single_stock(
        stock_code=stock_code,
        period=KlinePeriod.DAILY,
        adjust_type=AdjustType.FORWARD,  # 前复权
        limit=100,  # 获取最近100条数据
        save_format='csv'
    )
    
    if not df.empty:
        print(f"✓ 成功获取 {len(df)} 条日K线数据")
        print(f"✓ 数据已保存到: {filepath}")
        print(f"✓ 数据时间范围: {df['日期'].min()} 至 {df['日期'].max()}")
        
        print("\n最新5条数据预览:")
        preview_columns = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌幅']
        print(df[preview_columns].tail().to_string(index=False))
        
        # 显示基本统计信息
        print(f"\n基本统计信息:")
        print(f"  平均收盘价: {df['收盘价'].mean():.2f}")
        print(f"  最高价: {df['最高价'].max():.2f}")
        print(f"  最低价: {df['最低价'].min():.2f}")
        print(f"  平均成交量: {df['成交量'].mean():.0f}手")
    else:
        print("⚠ 未获取到数据")


def example_2_different_periods():
    """
    示例2: 获取不同周期的K线数据
    """
    print("\n" + "=" * 60)
    print("示例2: 获取不同周期的K线数据")
    print("=" * 60)
    
    scraper = StockKlineScraper()
    stock_code = '600000'  # 浦发银行
    
    # 测试不同的K线周期
    periods = [
        (KlinePeriod.DAILY, "日K"),
        (KlinePeriod.WEEKLY, "周K"),
        (KlinePeriod.MONTHLY, "月K"),
        (KlinePeriod.MIN_60, "60分钟K"),
        (KlinePeriod.MIN_30, "30分钟K")
    ]
    
    print(f"正在获取股票 {stock_code} 不同周期的K线数据...\n")
    
    results = {}
    for period, name in periods:
        print(f"获取{name}线数据...")
        df = scraper.scrape_single_stock(
            stock_code=stock_code,
            period=period,
            limit=50
        )
        
        results[name] = df
        if not df.empty:
            latest_data = df.iloc[-1]
            print(f"  ✓ {name}: {len(df)}条数据")
            print(f"    最新时间: {latest_data['日期']}")
            print(f"    收盘价: {latest_data['收盘价']}")
            print(f"    涨跌幅: {latest_data['涨跌幅']}%")
        else:
            print(f"  ⚠ {name}: 未获取到数据")
        print()
    
    return results


def example_3_different_adjust_types():
    """
    示例3: 不同复权类型的数据对比
    """
    print("=" * 60)
    print("示例3: 不同复权类型的数据对比")
    print("=" * 60)
    
    scraper = StockKlineScraper()
    stock_code = '000002'  # 万科A
    
    # 测试不同复权类型
    adjust_types = [
        (AdjustType.NONE, "不复权"),
        (AdjustType.FORWARD, "前复权"),
        (AdjustType.BACKWARD, "后复权")
    ]
    
    print(f"正在获取股票 {stock_code} 不同复权类型的数据...\n")
    
    results = {}
    for adjust_type, name in adjust_types:
        print(f"获取{name}数据...")
        df = scraper.scrape_single_stock(
            stock_code=stock_code,
            period=KlinePeriod.DAILY,
            adjust_type=adjust_type,
            limit=30
        )
        
        results[name] = df
        if not df.empty:
            latest_data = df.iloc[-1]
            first_data = df.iloc[0]
            print(f"  ✓ {name}: {len(df)}条数据")
            print(f"    最新收盘价: {latest_data['收盘价']}")
            print(f"    最早收盘价: {first_data['收盘价']}")
        else:
            print(f"  ⚠ {name}: 未获取到数据")
        print()
    
    # 比较不同复权方式的价格差异
    if all(not df.empty for df in results.values()):
        print("复权类型价格对比 (最新数据):")
        for name, df in results.items():
            latest_price = df.iloc[-1]['收盘价']
            print(f"  {name}: {latest_price}")
    
    return results


def example_4_batch_stocks():
    """
    示例4: 批量获取多只股票的K线数据
    """
    print("\n" + "=" * 60)
    print("示例4: 批量获取多只股票的K线数据")
    print("=" * 60)
    
    scraper = StockKlineScraper()
    
    # 选择一些热门股票
    stock_codes = [
        '000001',  # 平安银行
        '000002',  # 万科A
        '600000',  # 浦发银行
        '600036',  # 招商银行
        '000858',  # 五粮液
        '300001'   # 特锐德
    ]
    
    print(f"正在批量获取 {len(stock_codes)} 只股票的日K线数据...")
    print(f"股票列表: {', '.join(stock_codes)}")
    
    # 批量获取并保存数据
    data_dict, filepaths = scraper.run_multiple_stocks(
        stock_codes=stock_codes,
        period=KlinePeriod.DAILY,
        limit=50,
        max_workers=3,  # 使用3个并发线程
        save_format='csv',
        combine_files=False  # 分别保存每只股票的数据
    )
    
    print(f"\n批量获取结果:")
    success_count = 0
    total_records = 0
    
    for stock_code in stock_codes:
        df = data_dict.get(stock_code, pd.DataFrame())
        if not df.empty:
            success_count += 1
            total_records += len(df)
            latest_data = df.iloc[-1]
            print(f"✓ {stock_code}: {len(df)}条数据, 最新价: {latest_data['收盘价']}, 涨跌幅: {latest_data['涨跌幅']}%")
        else:
            print(f"⚠ {stock_code}: 未获取到数据")
    
    print(f"\n汇总信息:")
    print(f"  成功获取: {success_count}/{len(stock_codes)} 只股票")
    print(f"  总数据量: {total_records} 条记录")
    print(f"  保存文件: {len(filepaths)} 个")
    
    return data_dict


def example_5_combined_file_output():
    """
    示例5: 合并文件输出和数据分析
    """
    print("\n" + "=" * 60)
    print("示例5: 合并文件输出和数据分析")
    print("=" * 60)
    
    scraper = StockKlineScraper()
    
    # 选择一些银行股进行对比分析
    bank_stocks = ['000001', '600000', '600036', '601328']  # 平安、浦发、招商、交通银行
    
    print(f"正在获取银行股票的K线数据进行对比分析...")
    
    # 批量获取数据并合并到一个文件
    data_dict, filepaths = scraper.run_multiple_stocks(
        stock_codes=bank_stocks,
        period=KlinePeriod.DAILY,
        limit=30,
        max_workers=2,
        save_format='csv',
        combine_files=True  # 合并到一个文件
    )
    
    # 合并所有数据进行分析
    all_data = []
    for stock_code, df in data_dict.items():
        if not df.empty:
            all_data.append(df)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\n合并数据分析:")
        print(f"  总数据量: {len(combined_df)} 条记录")
        print(f"  涵盖股票: {combined_df['股票代码'].nunique()} 只")
        
        # 按股票分组计算平均涨跌幅
        avg_change = combined_df.groupby('股票代码')['涨跌幅'].mean().sort_values(ascending=False)
        print(f"\n平均涨跌幅排行:")
        for stock_code, avg_pct in avg_change.items():
            print(f"  {stock_code}: {avg_pct:.2f}%")
        
        # 成交量分析
        avg_volume = combined_df.groupby('股票代码')['成交量'].mean().sort_values(ascending=False)
        print(f"\n平均成交量排行:")
        for stock_code, avg_vol in avg_volume.items():
            print(f"  {stock_code}: {avg_vol:.0f}手")
        
        print(f"\n合并文件已保存: {filepaths[0] if filepaths else '无'}")


def example_6_time_range_analysis():
    """
    示例6: 时间范围数据分析
    """
    print("\n" + "=" * 60)
    print("示例6: 时间范围数据分析")
    print("=" * 60)
    
    scraper = StockKlineScraper()
    stock_code = '000858'  # 五粮液
    
    print(f"正在获取股票 {stock_code} 的长期历史数据...")
    
    # 获取更多历史数据
    df = scraper.scrape_single_stock(
        stock_code=stock_code,
        period=KlinePeriod.DAILY,
        limit=500  # 获取500天的数据
    )
    
    if not df.empty:
        print(f"✓ 成功获取 {len(df)} 条历史数据")
        print(f"✓ 时间范围: {df['日期'].min()} 至 {df['日期'].max()}")
        
        # 转换日期列为datetime类型以便分析
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 计算一些技术指标
        df['MA5'] = df['收盘价'].rolling(window=5).mean()  # 5日均线
        df['MA20'] = df['收盘价'].rolling(window=20).mean()  # 20日均线
        df['价格振幅'] = (df['最高价'] - df['最低价']) / df['最低价'] * 100
        
        # 分析统计信息
        print(f"\n技术分析:")
        latest_data = df.iloc[-1]
        print(f"  最新收盘价: {latest_data['收盘价']:.2f}")
        print(f"  5日均线: {latest_data['MA5']:.2f}")
        print(f"  20日均线: {latest_data['MA20']:.2f}")
        print(f"  最新振幅: {latest_data['价格振幅']:.2f}%")
        
        # 价格统计
        price_stats = df['收盘价'].describe()
        print(f"\n价格统计 (最近{len(df)}个交易日):")
        print(f"  平均价格: {price_stats['mean']:.2f}")
        print(f"  最高价格: {price_stats['max']:.2f}")
        print(f"  最低价格: {price_stats['min']:.2f}")
        print(f"  价格标准差: {price_stats['std']:.2f}")
        
        # 涨跌幅分析
        positive_days = (df['涨跌幅'] > 0).sum()
        negative_days = (df['涨跌幅'] < 0).sum()
        print(f"\n涨跌统计:")
        print(f"  上涨天数: {positive_days} ({positive_days/len(df)*100:.1f}%)")
        print(f"  下跌天数: {negative_days} ({negative_days/len(df)*100:.1f}%)")
        print(f"  最大单日涨幅: {df['涨跌幅'].max():.2f}%")
        print(f"  最大单日跌幅: {df['涨跌幅'].min():.2f}%")
        
        # 保存带技术指标的数据
        filepath = scraper.save_single_stock_data(df, stock_code, KlinePeriod.DAILY, 'csv')
        print(f"\n✓ 带技术指标的数据已保存到: {filepath}")
    else:
        print("⚠ 未获取到数据")


def main():
    """
    主函数：运行所有示例
    """
    print("东方财富个股K线历史数据爬虫 - 使用示例")
    print("=" * 80)
    
    try:
        # 运行各个示例
        example_1_single_stock_daily_kline()
        example_2_different_periods()
        example_3_different_adjust_types()
        example_4_batch_stocks()
        example_5_combined_file_output()
        example_6_time_range_analysis()
        
        print("\n" + "=" * 80)
        print("所有示例运行完成！")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n运行过程中发生错误: {e}")


if __name__ == "__main__":
    main()