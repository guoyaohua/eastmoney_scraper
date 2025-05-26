"""
EastMoney Individual Stock Capital Flow Scraper
爬取东方财富网个股资金流向数据
URL: https://data.eastmoney.com/zjlx/detail.html
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('capital_flow_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CapitalFlowConfig:
    """配置类"""
    # API接口地址
    BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"
    
    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://data.eastmoney.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # 数据字段映射
    FIELD_MAPPING = {
        'f2': '最新价',
        'f3': '涨跌幅',
        'f12': '股票代码',
        'f14': '股票名称',
        'f62': '主力净流入',
        'f66': '超大单净流入',
        'f69': '大单净流入',
        'f72': '中单净流入',
        'f75': '小单净流入',
        'f184': '主力净流入占比',
        'f165': '超大单净流入占比',
        'f166': '大单净流入占比',
        'f167': '中单净流入占比',
        'f168': '小单净流入占比',
    }
    
    # 请求参数
    DEFAULT_PARAMS = {
        'cb': 'jQuery112309632391668044285_1640157564641',
        'fid': 'f3', # 排序字段 f3: 涨跌幅
        'po': '1',
        'pz': '100',
        'pn': '1',
        'np': '1',
        'fltt': '2',
        'invt': '2',
        'ut': 'b2884a393a59ad64002292a3e90d46a5',
        'fs': 'm:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2',
        'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13'
    }


class DataFetcher:
    """数据获取模块"""
    
    def __init__(self, config: CapitalFlowConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.config.HEADERS)
    
    def fetch_data(self, page: int = 1, page_size: int = 100) -> Optional[Dict]:
        """
        获取指定页的资金流向数据
        
        Args:
            page: 页码
            page_size: 每页数据量
            
        Returns:
            原始JSON数据或None
        """
        try:
            params = self.config.DEFAULT_PARAMS.copy()
            params['pn'] = str(page)
            params['pz'] = str(page_size)
            params['_'] = str(int(time.time() * 1000))
            
            response = self.session.get(
                self.config.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # 处理JSONP格式
            content = response.text
            json_start = content.index('(') + 1
            json_end = content.rindex(')')
            json_data = json.loads(content[json_start:json_end])
            print(json_data)
            return json_data
            
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            return None
    
    def fetch_all_pages(self, max_pages: int = 10) -> List[Dict]:
        """
        获取多页数据
        
        Args:
            max_pages: 最大页数
            
        Returns:
            所有页面的数据列表
        """
        all_data = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.fetch_data, page) for page in range(1, max_pages + 1)]
            
            for future in futures:
                result = future.result()
                if result and 'data' in result and result['data']:
                    all_data.extend(result['data']['diff'])
        
        return all_data


class DataParser:
    """数据解析模块"""
    
    def __init__(self, config: CapitalFlowConfig):
        self.config = config
    
    def parse_stock_data(self, raw_data: Dict) -> Dict:
        """
        解析单只股票数据
        
        Args:
            raw_data: 原始股票数据
            
        Returns:
            解析后的股票数据
        """
        parsed_data = {}
        
        for field_key, field_name in self.config.FIELD_MAPPING.items():
            value = raw_data.get(field_key, None)
            
            # 处理百分比字段
            if '占比' in field_name and value is not None:
                value = round(value, 2)
            
            # 处理金额字段（转换为万元）
            if '流入' in field_name and '占比' not in field_name and value is not None:
                value = round(value / 10000, 2)
                
            parsed_data[field_name] = value
        
        # 添加时间戳
        parsed_data['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return parsed_data
    
    def parse_batch_data(self, raw_data_list: List[Dict]) -> pd.DataFrame:
        """
        批量解析股票数据
        
        Args:
            raw_data_list: 原始数据列表
            
        Returns:
            DataFrame格式的数据
        """
        parsed_list = []
        
        for raw_data in raw_data_list:
            try:
                parsed_data = self.parse_stock_data(raw_data)
                parsed_list.append(parsed_data)
            except Exception as e:
                logger.error(f"解析数据失败: {e}")
                continue
        
        if parsed_list:
            df = pd.DataFrame(parsed_list)
            # 按主力净流入排序
            df = df.sort_values('主力净流入', ascending=False)
            return df
        
        return pd.DataFrame()


class DataStorage:
    """数据存储模块"""
    
    def __init__(self, output_dir: str = "capital_flow_data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        保存数据到CSV文件
        
        Args:
            df: 数据DataFrame
            filename: 文件名，如果不提供则使用时间戳
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"capital_flow_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"数据已保存到: {filepath}")
        
        return filepath
    
    def save_to_json(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """
        保存数据到JSON文件
        
        Args:
            data: 数据列表
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"capital_flow_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath}")
        return filepath
    
    def append_to_database(self, df: pd.DataFrame, db_file: str = "capital_flow.db") -> None:
        """
        追加数据到SQLite数据库
        
        Args:
            df: 数据DataFrame
            db_file: 数据库文件名
        """
        import sqlite3
        
        db_path = os.path.join(self.output_dir, db_file)
        
        with sqlite3.connect(db_path) as conn:
            df.to_sql('capital_flow', conn, if_exists='append', index=False)
            logger.info(f"数据已追加到数据库: {db_path}")


class CapitalFlowScraper:
    """资金流向爬虫主类"""
    
    def __init__(self):
        self.config = CapitalFlowConfig()
        self.fetcher = DataFetcher(self.config)
        self.parser = DataParser(self.config)
        self.storage = DataStorage()
        self.is_running = False
    
    def scrape_once(self, save_to_file: bool = True) -> Optional[pd.DataFrame]:
        """
        执行一次爬取
        
        Args:
            save_to_file: 是否保存到文件
            
        Returns:
            爬取的数据DataFrame
        """
        try:
            logger.info("开始爬取资金流向数据...")
            
            # 获取数据
            raw_data = self.fetcher.fetch_all_pages(max_pages=1)
            
            if not raw_data:
                logger.warning("未获取到数据")
                return None
            
            # 解析数据
            df = self.parser.parse_batch_data(raw_data)
            
            if df.empty:
                logger.warning("解析后数据为空")
                return None
            
            logger.info(f"成功获取 {len(df)} 条数据")
            
            # 保存数据
            if save_to_file:
                self.storage.save_to_csv(df)
                # 同时保存到数据库
                self.storage.append_to_database(df)
            
            return df
            
        except Exception as e:
            logger.error(f"爬取过程出错: {e}")
            return None
    
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
                self.scrape_once()
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
    scraper = CapitalFlowScraper()
    
    # 单次爬取示例
    # df = scraper.scrape_once()
    # if df is not None:
    #     print(df.head(10))
    
    # 定时爬取（每10秒）
    scraper.start_scheduled_scraping(interval=10)


if __name__ == "__main__":
    main()