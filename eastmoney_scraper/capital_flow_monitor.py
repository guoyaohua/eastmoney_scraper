"""
资金流向监控器 - 实时监控和分析资金流向
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import time
from .eastmoney_capital_flow_scraper import CapitalFlowScraper, DataStorage
import sqlite3
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class CapitalFlowAnalyzer:
    """资金流向分析器"""
    
    def __init__(self, db_path: str = "capital_flow_data/capital_flow.db"):
        self.db_path = db_path
        self.storage = DataStorage()
    
    def get_latest_data(self, limit: int = 100) -> pd.DataFrame:
        """获取最新的资金流向数据"""
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM capital_flow 
                ORDER BY 更新时间 DESC 
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
        
        return df
    
    def get_top_inflow_stocks(self, top_n: int = 20) -> pd.DataFrame:
        """获取主力净流入最多的股票"""
        df = self.get_latest_data(limit=1000)
        if df.empty:
            return df
        
        # 获取每只股票的最新数据
        latest_df = df.drop_duplicates(subset=['股票代码'], keep='first')
        
        # 按主力净流入排序
        top_stocks = latest_df.nlargest(top_n, '主力净流入')[
            ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比', '更新时间']
        ]
        
        return top_stocks
    
    def get_continuous_inflow_stocks(self, days: int = 3) -> pd.DataFrame:
        """获取连续多日主力净流入的股票"""
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取最近几天的数据
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = f"""
                SELECT * FROM capital_flow 
                WHERE 更新时间 >= '{cutoff_date}'
                ORDER BY 股票代码, 更新时间 DESC
            """
            df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return df
        
        # 分析连续流入
        continuous_stocks = []
        
        for stock_code, group in df.groupby('股票代码'):
            # 获取每天的主力净流入
            daily_inflow = group.groupby(pd.to_datetime(group['更新时间']).dt.date)['主力净流入'].last()
            
            # 检查是否连续流入
            if len(daily_inflow) >= days and all(daily_inflow.tail(days) > 0):
                latest_data = group.iloc[0]
                continuous_stocks.append({
                    '股票代码': stock_code,
                    '股票名称': latest_data['股票名称'],
                    '最新价': latest_data['最新价'],
                    '涨跌幅': latest_data['涨跌幅'],
                    '连续流入天数': len(daily_inflow[daily_inflow > 0]),
                    '累计流入': daily_inflow.sum(),
                    '平均每日流入': daily_inflow.mean()
                })
        
        return pd.DataFrame(continuous_stocks).sort_values('累计流入', ascending=False)
    
    def analyze_sector_flow(self) -> pd.DataFrame:
        """分析板块资金流向"""
        df = self.get_latest_data(limit=2000)
        if df.empty:
            return df
        
        # 这里简单按股票代码前缀分类，实际应该有板块映射表
        df['板块'] = df['股票代码'].apply(lambda x: 
            '主板' if x.startswith('60') else 
            '创业板' if x.startswith('30') else 
            '科创板' if x.startswith('68') else 
            '北交所' if x.startswith('8') else '其他'
        )
        
        # 计算板块资金流向
        sector_flow = df.groupby('板块').agg({
            '主力净流入': 'sum',
            '股票代码': 'count'
        }).rename(columns={'股票代码': '股票数量'})
        
        sector_flow['平均每股流入'] = sector_flow['主力净流入'] / sector_flow['股票数量']
        
        return sector_flow.sort_values('主力净流入', ascending=False)


class CapitalFlowMonitor:
    """资金流向监控器"""
    
    def __init__(self):
        self.scraper = CapitalFlowScraper()
        self.analyzer = CapitalFlowAnalyzer()
        self.is_monitoring = False
    
    def display_realtime_data(self):
        """显示实时数据"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print(f"资金流向实时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 获取主力净流入TOP20
        top_stocks = self.analyzer.get_top_inflow_stocks(20)
        if not top_stocks.empty:
            print("\n【主力净流入TOP20】")
            print("-" * 80)
            print(f"{'股票代码':<10} {'股票名称':<10} {'最新价':<10} {'涨跌幅':<10} {'主力净流入(万)':<15} {'流入占比':<10}")
            print("-" * 80)
            
            for _, row in top_stocks.iterrows():
                print(f"{row['股票代码']:<10} {row['股票名称']:<10} "
                      f"{row['最新价']:<10.2f} {row['涨跌幅']:<10.2f}% "
                      f"{row['主力净流入']:<15.2f} {row['主力净流入占比']:<10.2f}%")
        
        # 获取连续流入股票
        continuous_stocks = self.analyzer.get_continuous_inflow_stocks(days=3)
        if not continuous_stocks.empty:
            print("\n【连续3日主力净流入】")
            print("-" * 80)
            print(f"{'股票代码':<10} {'股票名称':<10} {'连续天数':<10} {'累计流入(万)':<15} {'日均流入(万)':<15}")
            print("-" * 80)
            
            for _, row in continuous_stocks.head(10).iterrows():
                print(f"{row['股票代码']:<10} {row['股票名称']:<10} "
                      f"{row['连续流入天数']:<10} {row['累计流入']:<15.2f} "
                      f"{row['平均每日流入']:<15.2f}")
        
        # 板块资金流向
        sector_flow = self.analyzer.analyze_sector_flow()
        if not sector_flow.empty:
            print("\n【板块资金流向】")
            print("-" * 50)
            print(f"{'板块':<10} {'主力净流入(万)':<15} {'股票数量':<10} {'平均流入':<15}")
            print("-" * 50)
            
            for sector, row in sector_flow.iterrows():
                print(f"{sector:<10} {row['主力净流入']:<15.2f} "
                      f"{row['股票数量']:<10} {row['平均每股流入']:<15.2f}")
    
    def plot_analysis(self):
        """生成分析图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('资金流向分析报告', fontsize=16)
        
        # 1. 主力净流入TOP10柱状图
        top_stocks = self.analyzer.get_top_inflow_stocks(10)
        if not top_stocks.empty:
            ax1 = axes[0, 0]
            ax1.bar(range(len(top_stocks)), top_stocks['主力净流入'], 
                   color=['red' if x > 0 else 'green' for x in top_stocks['主力净流入']])
            ax1.set_xticks(range(len(top_stocks)))
            ax1.set_xticklabels(top_stocks['股票名称'], rotation=45)
            ax1.set_title('主力净流入TOP10')
            ax1.set_ylabel('净流入金额(万元)')
            ax1.grid(True, alpha=0.3)
        
        # 2. 板块资金流向饼图
        sector_flow = self.analyzer.analyze_sector_flow()
        if not sector_flow.empty:
            ax2 = axes[0, 1]
            positive_sectors = sector_flow[sector_flow['主力净流入'] > 0]
            if not positive_sectors.empty:
                ax2.pie(positive_sectors['主力净流入'], 
                       labels=positive_sectors.index,
                       autopct='%1.1f%%')
                ax2.set_title('板块资金流入分布')
        
        # 3. 涨跌幅与资金流入散点图
        latest_data = self.analyzer.get_latest_data(200)
        if not latest_data.empty:
            ax3 = axes[1, 0]
            scatter = ax3.scatter(latest_data['涨跌幅'], 
                                 latest_data['主力净流入'],
                                 c=latest_data['主力净流入'],
                                 cmap='RdYlGn',
                                 alpha=0.6)
            ax3.set_xlabel('涨跌幅(%)')
            ax3.set_ylabel('主力净流入(万元)')
            ax3.set_title('涨跌幅与主力净流入关系')
            ax3.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax3)
        
        # 4. 资金流入占比分布
        if not latest_data.empty:
            ax4 = axes[1, 1]
            ax4.hist(latest_data['主力净流入占比'], bins=30, alpha=0.7, color='blue')
            ax4.set_xlabel('主力净流入占比(%)')
            ax4.set_ylabel('股票数量')
            ax4.set_title('主力净流入占比分布')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(f'capital_flow_data/analysis_{timestamp}.png', dpi=300)
        plt.close()
    
    def start_monitoring(self, interval: int = 10, display_interval: int = 30):
        """
        开始监控
        
        Args:
            interval: 数据爬取间隔(秒)
            display_interval: 显示更新间隔(秒)
        """
        self.is_monitoring = True
        last_display_time = time.time()
        
        print("开始监控资金流向...")
        print(f"数据更新间隔: {interval}秒")
        print(f"显示刷新间隔: {display_interval}秒")
        print("按 Ctrl+C 停止监控\n")
        
        while self.is_monitoring:
            try:
                # 爬取数据
                df = self.scraper.scrape_once()
                
                # 更新显示
                current_time = time.time()
                if current_time - last_display_time >= display_interval:
                    self.display_realtime_data()
                    last_display_time = current_time
                    
                    # 每小时生成一次分析图表
                    if int(current_time) % 3600 < interval:
                        self.plot_analysis()
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n停止监控...")
                self.stop_monitoring()
                break
            except Exception as e:
                print(f"监控出错: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.scraper.stop()


def main():
    """主函数"""
    monitor = CapitalFlowMonitor()
    
    # 开始监控（每10秒更新数据，每30秒刷新显示）
    monitor.start_monitoring(interval=10, display_interval=30)


if __name__ == "__main__":
    main()