"""
EastMoney Concept Sector Real-time Quotes and Capital Flow Scraper
东方财富概念板块实时行情及资金流向爬虫
"""

import requests
import json
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('concept_sector_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ConceptSectorConfig:
    """配置类"""
    
    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # API接口地址
    CONCEPT_QUOTE_URL = "https://push2.eastmoney.com/api/qt/clist/get"  # 概念板块行情
    CAPITAL_FLOW_URL = "https://push2.eastmoney.com/api/qt/clist/get"   # 资金流向
    
    # 概念板块行情字段映射
    QUOTE_FIELD_MAPPING = {
        'f12': '板块代码',
        'f14': '板块名称',
        'f2': '最新价',
        'f3': '涨跌幅',
        'f4': '涨跌额',
        'f5': '成交量',
        'f6': '成交额',
        'f7': '振幅',
        'f15': '最高价',
        'f16': '最低价',
        'f17': '开盘价',
        'f18': '昨收',
        'f8': '换手率',
        'f10': '量比',
        'f22': '涨速',
        'f11': '5分钟涨跌',
        'f62': '主力净流入',
        'f184': '主力净流入占比',
        'f66': '超大单净流入',
        'f69': '大单净流入',
        'f72': '中单净流入',
        'f75': '小单净流入',
        'f164': '超大单净流入占比',
        'f165': '大单净流入占比',
        'f166': '中单净流入占比',
        'f167': '小单净流入占比',
    }
    
    # 资金流向字段映射
    FLOW_FIELD_MAPPING = {
        'f12': '板块代码',
        'f14': '板块名称',
        'f62': '主力净流入',
        'f184': '主力净流入占比',
        'f66': '超大单净流入',
        'f69': '大单净流入',
        'f72': '中单净流入',
        'f75': '小单净流入',
        'f164': '超大单净流入占比',
        'f165': '大单净流入占比',
        'f166': '中单净流入占比',
        'f167': '小单净流入占比',
        'f3': '涨跌幅',
        'f128': '领涨股票代码',
        'f140': '领涨股票名称',
        'f136': '领涨股票涨跌幅',
    }


class ConceptSectorFetcher:
    """数据获取模块"""
    
    def __init__(self, config: ConceptSectorConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.config.HEADERS)
    
    def fetch_concept_quotes_page(self, page: int = 1, page_size: int = 100) -> Optional[Dict]:
        """
        获取概念板块实时行情数据（单页）
        """
        try:
            params = {
                'cb': 'jQuery1123045825600808390446_1640157637241',
                'fid': 'f3',  # 按涨跌幅排序
                'po': '1',
                'pz': str(page_size),
                'pn': str(page),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5',
                'fs': 'm:90+t:3',  # 概念板块
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f10,f11,f15,f16,f17,f18,f22,f62,f184,f66,f69,f72,f75,f164,f165,f166,f167'
            }
            
            response = self.session.get(
                self.config.CONCEPT_QUOTE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # 处理JSONP格式
            content = response.text
            json_start = content.index('(') + 1
            json_end = content.rindex(')')
            json_data = json.loads(content[json_start:json_end])
            
            return json_data
            
        except Exception as e:
            logger.error(f"获取概念板块行情失败 (页 {page}): {e}")
            return None
    
    def fetch_concept_quotes(self) -> List[Dict]:
        """
        获取所有概念板块实时行情数据（多页并行）
        """
        all_data = []
        
        # 先获取第一页，确定总数
        first_page = self.fetch_concept_quotes_page(1, 100)
        if not first_page or 'data' not in first_page:
            return all_data
        
        total_count = first_page['data'].get('total', 0)
        page_size = 100
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(f"概念板块总数: {total_count}, 需要获取 {total_pages} 页")
        
        # 添加第一页数据
        if 'diff' in first_page['data']:
            all_data.extend(first_page['data']['diff'])
        
        # 并行获取剩余页面
        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(self.fetch_concept_quotes_page, page, page_size)
                    for page in range(2, total_pages + 1)
                ]
                
                for future in futures:
                    result = future.result()
                    if result and 'data' in result and 'diff' in result['data']:
                        all_data.extend(result['data']['diff'])
        
        logger.info(f"成功获取 {len(all_data)} 个概念板块行情数据")
        return all_data
    
    def fetch_capital_flow_page(self, period: str = 'today', page: int = 1, page_size: int = 100) -> Optional[Dict]:
        """
        获取概念板块资金流向数据（单页）
        
        Args:
            period: 时间周期 'today'(今日), '5day'(5日), '10day'(10日)
            page: 页码
            page_size: 每页大小
        """
        try:
            # 根据周期设置不同的字段
            period_field_map = {
                'today': 'f62',    # 今日主力净流入
                '5day': 'f267',    # 5日主力净流入
                '10day': 'f164'    # 10日主力净流入
            }
            
            params = {
                'cb': 'jQuery1123045825600808390446_1640157637241',
                'fid': period_field_map.get(period, 'f62'),  # 按主力净流入排序
                'po': '1',
                'pz': str(page_size),
                'pn': str(page),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5',
                'fs': 'm:90+t:3',  # 概念板块
                'fields': 'f12,f14,f3,f62,f184,f66,f69,f72,f75,f164,f165,f166,f167,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f128,f140,f136'
            }
            
            response = self.session.get(
                self.config.CAPITAL_FLOW_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # 处理JSONP格式
            content = response.text
            json_start = content.index('(') + 1
            json_end = content.rindex(')')
            json_data = json.loads(content[json_start:json_end])
            
            return json_data
            
        except Exception as e:
            logger.error(f"获取概念板块资金流向失败 ({period}, 页 {page}): {e}")
            return None
    
    def fetch_capital_flow(self, period: str = 'today') -> List[Dict]:
        """
        获取所有概念板块资金流向数据（多页并行）
        
        Args:
            period: 时间周期 'today'(今日), '5day'(5日), '10day'(10日)
        """
        all_data = []
        
        # 先获取第一页，确定总数
        first_page = self.fetch_capital_flow_page(period, 1, 100)
        if not first_page or 'data' not in first_page:
            return all_data
        
        total_count = first_page['data'].get('total', 0)
        page_size = 100
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(f"{period} 资金流向板块总数: {total_count}, 需要获取 {total_pages} 页")
        
        # 添加第一页数据
        if 'diff' in first_page['data']:
            all_data.extend(first_page['data']['diff'])
        
        # 并行获取剩余页面
        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(self.fetch_capital_flow_page, period, page, page_size)
                    for page in range(2, total_pages + 1)
                ]
                
                for future in futures:
                    result = future.result()
                    if result and 'data' in result and 'diff' in result['data']:
                        all_data.extend(result['data']['diff'])
        
        logger.info(f"成功获取 {len(all_data)} 个概念板块 {period} 资金流向数据")
        return all_data


class ConceptSectorParser:
    """数据解析模块"""
    
    def __init__(self, config: ConceptSectorConfig):
        self.config = config
    
    def parse_concept_quotes(self, raw_data_list: List[Dict]) -> pd.DataFrame:
        """解析概念板块行情数据"""
        if not raw_data_list:
            return pd.DataFrame()
        
        stocks_data = []
        for item in raw_data_list:
            parsed_item = {}
            for field_key, field_name in self.config.QUOTE_FIELD_MAPPING.items():
                value = item.get(field_key, None)
                
                # 处理百分比字段
                if '占比' in field_name and value is not None:
                    value = round(value, 2)
                
                # 处理金额字段（转换为万元）
                if '流入' in field_name and '占比' not in field_name and value is not None:
                    value = round(value / 10000, 2)
                
                # 处理成交额（转换为万元）
                if field_name == '成交额' and value is not None:
                    value = round(value / 10000, 2)
                    
                parsed_item[field_name] = value
            
            stocks_data.append(parsed_item)
        
        df = pd.DataFrame(stocks_data)
        return df
    
    def parse_capital_flow(self, raw_data_list: List[Dict], period: str) -> pd.DataFrame:
        """解析资金流向数据"""
        if not raw_data_list:
            return pd.DataFrame()
        
        flow_data = []
        period_prefix = {
            'today': '',
            '5day': '5日',
            '10day': '10日'
        }[period]
        
        for item in raw_data_list:
            parsed_item = {
                '板块代码': item.get('f12'),
                '板块名称': item.get('f14'),
            }
            
            # 根据周期解析不同的字段
            if period == 'today':
                # 今日资金流向
                parsed_item[f'{period_prefix}主力净流入'] = round(item.get('f62', 0) / 10000, 2) if item.get('f62') else 0
                parsed_item[f'{period_prefix}主力净流入占比'] = round(item.get('f184', 0), 2) if item.get('f184') else 0
                parsed_item[f'{period_prefix}超大单净流入'] = round(item.get('f66', 0) / 10000, 2) if item.get('f66') else 0
                parsed_item[f'{period_prefix}大单净流入'] = round(item.get('f69', 0) / 10000, 2) if item.get('f69') else 0
                parsed_item[f'{period_prefix}中单净流入'] = round(item.get('f72', 0) / 10000, 2) if item.get('f72') else 0
                parsed_item[f'{period_prefix}小单净流入'] = round(item.get('f75', 0) / 10000, 2) if item.get('f75') else 0
            elif period == '5day':
                # 5日资金流向
                parsed_item[f'{period_prefix}主力净流入'] = round(item.get('f267', 0) / 10000, 2) if item.get('f267') else 0
                parsed_item[f'{period_prefix}主力净流入占比'] = round(item.get('f268', 0), 2) if item.get('f268') else 0
                parsed_item[f'{period_prefix}超大单净流入'] = round(item.get('f269', 0) / 10000, 2) if item.get('f269') else 0
                parsed_item[f'{period_prefix}大单净流入'] = round(item.get('f270', 0) / 10000, 2) if item.get('f270') else 0
                parsed_item[f'{period_prefix}中单净流入'] = round(item.get('f271', 0) / 10000, 2) if item.get('f271') else 0
                parsed_item[f'{period_prefix}小单净流入'] = round(item.get('f272', 0) / 10000, 2) if item.get('f272') else 0
            elif period == '10day':
                # 10日资金流向
                parsed_item[f'{period_prefix}主力净流入'] = round(item.get('f164', 0) / 10000, 2) if item.get('f164') else 0
                parsed_item[f'{period_prefix}主力净流入占比'] = round(item.get('f174', 0), 2) if item.get('f174') else 0
                parsed_item[f'{period_prefix}超大单净流入'] = round(item.get('f165', 0) / 10000, 2) if item.get('f165') else 0
                parsed_item[f'{period_prefix}大单净流入'] = round(item.get('f166', 0) / 10000, 2) if item.get('f166') else 0
                parsed_item[f'{period_prefix}中单净流入'] = round(item.get('f167', 0) / 10000, 2) if item.get('f167') else 0
                parsed_item[f'{period_prefix}小单净流入'] = round(item.get('f168', 0) / 10000, 2) if item.get('f168') else 0
            
            flow_data.append(parsed_item)
        
        df = pd.DataFrame(flow_data)
        return df


class ConceptSectorScraper:
    """概念板块爬虫主类"""
    
    def __init__(self, output_dir: str = "concept_sector_data"):
        self.config = ConceptSectorConfig()
        self.fetcher = ConceptSectorFetcher(self.config)
        self.parser = ConceptSectorParser(self.config)
        self.output_dir = output_dir
        self.is_running = False
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_all_data(self) -> pd.DataFrame:
        """
        爬取所有数据并合并
        """
        try:
            logger.info("开始爬取概念板块数据...")
            
            # 1. 获取实时行情数据
            logger.info("获取实时行情数据...")
            quotes_data_list = self.fetcher.fetch_concept_quotes()
            df_quotes = self.parser.parse_concept_quotes(quotes_data_list)
            
            if df_quotes.empty:
                logger.error("未能获取实时行情数据")
                return pd.DataFrame()
            
            # 2. 并发获取各周期资金流向数据
            logger.info("获取资金流向数据...")
            with ThreadPoolExecutor(max_workers=3) as executor:
                # 提交任务
                future_today = executor.submit(self.fetcher.fetch_capital_flow, 'today')
                future_5day = executor.submit(self.fetcher.fetch_capital_flow, '5day')
                future_10day = executor.submit(self.fetcher.fetch_capital_flow, '10day')
                
                # 获取结果
                today_data_list = future_today.result()
                day5_data_list = future_5day.result()
                day10_data_list = future_10day.result()
            
            # 解析资金流向数据
            df_today = self.parser.parse_capital_flow(today_data_list, 'today')
            df_5day = self.parser.parse_capital_flow(day5_data_list, '5day')
            df_10day = self.parser.parse_capital_flow(day10_data_list, '10day')
            
            # 3. 合并所有数据
            logger.info("合并数据...")
            df_merged = df_quotes.copy()
            
            # 合并今日资金流向
            if not df_today.empty:
                df_merged = pd.merge(
                    df_merged, 
                    df_today[['板块代码', '主力净流入', '主力净流入占比', '超大单净流入', 
                             '大单净流入', '中单净流入', '小单净流入']], 
                    on='板块代码', 
                    how='left',
                    suffixes=('', '_今日')
                )
            
            # 合并5日资金流向
            if not df_5day.empty:
                df_merged = pd.merge(
                    df_merged, 
                    df_5day[['板块代码', '5日主力净流入', '5日主力净流入占比', 
                            '5日超大单净流入', '5日大单净流入', '5日中单净流入', '5日小单净流入']], 
                    on='板块代码', 
                    how='left'
                )
            
            # 合并10日资金流向
            if not df_10day.empty:
                df_merged = pd.merge(
                    df_merged, 
                    df_10day[['板块代码', '10日主力净流入', '10日主力净流入占比', 
                             '10日超大单净流入', '10日大单净流入', '10日中单净流入', '10日小单净流入']], 
                    on='板块代码', 
                    how='left'
                )
            
            # 添加更新时间
            df_merged['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 按涨跌幅排序
            df_merged = df_merged.sort_values('涨跌幅', ascending=False)
            
            logger.info(f"成功获取 {len(df_merged)} 个概念板块数据")
            
            return df_merged
            
        except Exception as e:
            logger.error(f"爬取数据出错: {e}")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame) -> str:
        """保存数据到本地"""
        try:
            # 保存为CSV文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"concept_sectors_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"数据已保存到: {filepath}")
            
            # 同时保存一份最新数据（覆盖）
            latest_filepath = os.path.join(self.output_dir, 'concept_sectors_latest.csv')
            df.to_csv(latest_filepath, index=False, encoding='utf-8-sig')
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return ""
    
    def run_once(self) -> Tuple[pd.DataFrame, str]:
        """执行一次爬取并保存"""
        df = self.scrape_all_data()
        filepath = ""
        if not df.empty:
            filepath = self.save_data(df)
        return df, filepath
    
    def start_scheduled_scraping(self, interval: int = 10):
        """
        开始定时爬取
        
        Args:
            interval: 爬取间隔（秒）
        """
        self.is_running = True
        logger.info(f"开始定时爬取，间隔: {interval}秒")
        
        while self.is_running:
            try:
                df, filepath = self.run_once()
                if not df.empty:
                    # 显示前10个板块
                    print("\n" + "="*100)
                    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*100)
                    display_columns = ['板块名称', '涨跌幅', '最新价', '成交额', 
                                     '主力净流入', '5日主力净流入', '10日主力净流入']
                    available_columns = [col for col in display_columns if col in df.columns]
                    print(df[available_columns].head(10).to_string(index=False))
                    print("="*100)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("接收到中断信号，停止爬取")
                self.stop()
                break
            except Exception as e:
                logger.error(f"定时爬取出错: {e}")
                time.sleep(interval)
    
    def stop(self):
        """停止爬取"""
        self.is_running = False
        logger.info("爬虫已停止")


def main():
    """主函数"""
    scraper = ConceptSectorScraper()
    
    # 定时爬取（每10秒）
    scraper.start_scheduled_scraping(interval=10)


if __name__ == "__main__":
    main()