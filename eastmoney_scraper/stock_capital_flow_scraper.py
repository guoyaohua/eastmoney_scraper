"""
东方财富个股资金流向爬虫
基于sector_scraper重构，优化数据保存机制，移除数据库依赖
"""

import requests
import json
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from enum import Enum

# 忽略pandas版本可能出现的FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

# 获取日志记录器实例，该模块不应配置全局日志记录器，应由应用程序配置
logger = logging.getLogger(__name__)


class MarketType(Enum):
    """
    市场类型枚举
    """
    ALL = "all"  # 全市场
    MAIN_BOARD = "main"  # 主板
    GEM = "gem"  # 创业板
    STAR = "star"  # 科创板
    BSE = "bse"  # 北交所


class StockCapitalFlowConfig:
    """
    个股资金流向爬虫配置类
    存储API端点、请求头、字段映射等常量信息
    """

    # HTTP请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://data.eastmoney.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # API接口地址
    CAPITAL_FLOW_URL = "https://push2.eastmoney.com/api/qt/clist/get"

    # 市场类型对应的筛选参数
    MARKET_FILTER_PARAMS = {
        MarketType.ALL: 'm:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2',
        MarketType.MAIN_BOARD: 'm:1+t:2,m:1+t:23',  # 主板
        MarketType.GEM: 'm:0+t:80',  # 创业板
        MarketType.STAR: 'm:1+t:23',  # 科创板
        MarketType.BSE: 'm:0+t:81'  # 北交所
    }

    # 资金流向数据字段原始键名到中文名称的映射
    FIELD_MAPPING = {
        'f12': '股票代码',
        'f14': '股票名称',
        'f2': '最新价',
        'f3': '涨跌幅',
        'f5': '成交量',
        'f6': '成交额',
        'f62': '主力净流入',
        'f184': '主力净流入占比',
        'f66': '超大单净流入',
        'f69': '超大单净流入占比',
        'f72': '大单净流入',
        'f75': '大单净流入占比',
        'f78': '中单净流入',
        'f81': '中单净流入占比',
        'f84': '小单净流入',
        'f87': '小单净流入占比',
        'f124': '更新时间戳',
    }


class StockCapitalFlowFetcher:
    """
    个股资金流向数据获取模块
    负责从东方财富API获取原始的个股资金流向数据
    """

    def __init__(self, config: StockCapitalFlowConfig, market_type: MarketType = MarketType.ALL, pool_size: int = 50):
        """
        初始化数据获取器

        Args:
            config (StockCapitalFlowConfig): 配置对象
            market_type (MarketType): 市场类型，默认为全市场
            pool_size (int): requests.Session连接池的大小，默认为50
        """
        self.config = config
        self.market_type = market_type
        self.session = requests.Session()
        # 配置HTTP适配器以提高并发性能
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_size,
                                                pool_maxsize=pool_size)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self.config.HEADERS)

    def fetch_capital_flow_page(self,
                               page_num: int = 1,
                               page_size: int = 100,
                               sort_field: str = 'f62') -> Optional[Dict]:
        """
        获取单页的个股资金流向数据

        Args:
            page_num (int): 页码，从1开始，默认为1
            page_size (int): 每页返回的数据条数，默认为100
            sort_field (str): 排序字段，默认为f62（主力净流入）

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None
        """
        try:
            # API请求参数
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',
                'fid': sort_field,  # 排序字段
                'po': '1',  # 排序方式，1为降序
                'pz': str(page_size),
                'pn': str(page_num),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5',
                'fs': self.config.MARKET_FILTER_PARAMS[self.market_type],
                'fields': ','.join(self.config.FIELD_MAPPING.keys()),
                '_': str(int(time.time() * 1000))  # 时间戳防缓存
            }

            response = self.session.get(
                self.config.CAPITAL_FLOW_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            # 处理JSONP响应格式
            content = response.text
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')

            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1:json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(
                    f"解析{self.market_type.value}市场资金流向JSONP响应失败 (页 {page_num}): 无法找到有效的JSON数据。响应内容: {content[:200]}..."
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取{self.market_type.value}市场资金流向网络请求失败 (页 {page_num}): {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(
                f"解析{self.market_type.value}市场资金流向JSON数据失败 (页 {page_num}): {e}. 响应内容: {response.text[:200]}..."
            )
            return None
        except Exception as e:
            logger.error(f"获取{self.market_type.value}市场资金流向时发生未知错误 (页 {page_num}): {e}")
            return None

    def fetch_all_capital_flow(self, max_pages: int = 10) -> List[Dict]:
        """
        获取所有个股资金流向数据，自动处理分页并行获取

        Args:
            max_pages (int): 最大获取页数，默认为10

        Returns:
            List[Dict]: 包含所有个股原始资金流向数据的列表
        """
        all_raw_data = []

        # 首先获取第一页数据，以确定总记录数和总页数
        page_size_for_total_count = 100
        first_page_response = self.fetch_capital_flow_page(
            page_num=1, page_size=page_size_for_total_count)

        if not first_page_response or 'data' not in first_page_response or not first_page_response['data']:
            logger.warning(f"获取{self.market_type.value}市场资金流向第一页数据失败或数据为空，无法继续获取")
            return all_raw_data

        total_records = first_page_response['data'].get('total', 0)
        if total_records == 0:
            logger.info(f"{self.market_type.value}市场资金流向总数为0，无需进一步获取")
            if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
                all_raw_data.extend(first_page_response['data']['diff'])
            return all_raw_data

        # 计算实际需要获取的页数
        total_pages = min(max_pages, (total_records + page_size_for_total_count - 1) // page_size_for_total_count)

        logger.info(f"{self.market_type.value}市场资金流向总数: {total_records}, 每页大小: {page_size_for_total_count}, 将获取: {total_pages}页")

        # 添加第一页的数据到结果列表
        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_data.extend(first_page_response['data']['diff'])

        # 如果总页数大于1，则并行获取剩余页面的数据
        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=min(10, total_pages - 1)) as executor:
                futures_map = {
                    executor.submit(self.fetch_capital_flow_page, page_num, page_size_for_total_count): page_num
                    for page_num in range(2, total_pages + 1)
                }

                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_data.extend(page_data['data']['diff'])
                        else:
                            logger.warning(f"获取{self.market_type.value}市场资金流向第 {page_num_completed} 页数据失败或数据不完整")
                    except Exception as e:
                        logger.error(f"处理{self.market_type.value}市场资金流向第 {page_num_completed} 页结果时发生错误: {e}")

        logger.info(f"成功获取 {len(all_raw_data)} 条原始{self.market_type.value}市场资金流向数据")
        return all_raw_data


class StockCapitalFlowParser:
    """
    个股资金流向数据解析模块
    负责将从API获取的原始JSON数据转换为结构化的Pandas DataFrame
    """

    def __init__(self, config: StockCapitalFlowConfig):
        """
        初始化数据解析器

        Args:
            config (StockCapitalFlowConfig): 配置对象
        """
        self.config = config

    def parse_capital_flow_data(self, raw_data_list: List[Dict]) -> pd.DataFrame:
        """
        解析个股资金流向原始数据列表

        Args:
            raw_data_list (List[Dict]): 从API获取的原始资金流向数据字典列表

        Returns:
            pd.DataFrame: 包含解析后资金流向数据的Pandas DataFrame，列名为中文
        """
        if not raw_data_list:
            logger.info("输入的原始资金流向数据列表为空，返回空DataFrame")
            return pd.DataFrame()

        parsed_data_list = []
        for raw_item in raw_data_list:
            parsed_item = {}
            for field_key, chinese_name in self.config.FIELD_MAPPING.items():
                raw_value = raw_item.get(field_key)

                # 对特定字段进行单位转换或格式化
                if raw_value is None or raw_value == '-':
                    parsed_value = None
                elif '占比' in chinese_name or '涨跌幅' in chinese_name:
                    # 百分比字段，保留两位小数
                    try:
                        parsed_value = round(float(raw_value), 2)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif ('流入' in chinese_name and '占比' not in chinese_name) or chinese_name == '成交额' or chinese_name == '涨跌额':
                    # 金额字段，API单位通常是元，转换为万元，保留两位小数
                    try:
                        parsed_value = round(float(raw_value) / 10000, 2)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif chinese_name == '成交量':
                    # 成交量单位是"手"
                    try:
                        parsed_value = int(raw_value)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif chinese_name == '最新价':
                    # 股价保留两位小数
                    try:
                        parsed_value = round(float(raw_value), 2)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif chinese_name == '更新时间戳':
                    # 时间戳转换为可读时间
                    try:
                        if raw_value:
                            parsed_value = datetime.fromtimestamp(int(raw_value)).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            parsed_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        parsed_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 其他字段直接使用
                    parsed_value = raw_value

                parsed_item[chinese_name] = parsed_value

            # 添加数据获取时间
            parsed_item['数据获取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            parsed_data_list.append(parsed_item)

        df = pd.DataFrame(parsed_data_list)
        
        # 按主力净流入排序
        if '主力净流入' in df.columns:
            df = df.sort_values('主力净流入', ascending=False)
        
        logger.info(f"成功解析 {len(df)} 条个股资金流向数据")
        return df


class StockCapitalFlowScraper:
    """
    个股资金流向爬虫主类
    集成数据获取、数据解析和数据存储功能，提供一次性爬取、定时爬取等功能
    """

    def __init__(self, market_type: MarketType = MarketType.ALL, output_dir: str = None):
        """
        初始化个股资金流向爬虫

        Args:
            market_type (MarketType): 市场类型，默认为全市场
            output_dir (str): 数据输出目录，如果为None则自动设置
        """
        self.market_type = market_type
        self.config = StockCapitalFlowConfig()
        self.fetcher = StockCapitalFlowFetcher(self.config, market_type)
        self.parser = StockCapitalFlowParser(self.config)
        self.is_running = False

        # 设置输出目录
        if output_dir is None:
            self.output_dir = f"output/stock_capital_flow_data_{market_type.value}"
        else:
            self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_all_data(self, max_pages: int = 10) -> pd.DataFrame:
        """
        执行完整的数据爬取流程

        Args:
            max_pages (int): 最大获取页数

        Returns:
            pd.DataFrame: 爬取并解析后的数据
        """
        try:
            logger.info(f"开始爬取{self.market_type.value}市场个股资金流向数据...")

            # 获取原始数据
            raw_data = self.fetcher.fetch_all_capital_flow(max_pages=max_pages)

            if not raw_data:
                logger.warning("未获取到任何原始数据")
                return pd.DataFrame()

            # 解析数据
            df = self.parser.parse_capital_flow_data(raw_data)

            if df.empty:
                logger.warning("解析后数据为空")
                return df

            logger.info(f"成功完成{self.market_type.value}市场个股资金流向数据爬取，共 {len(df)} 条记录")
            return df

        except Exception as e:
            logger.error(f"爬取{self.market_type.value}市场个股资金流向数据时发生错误: {e}")
            return pd.DataFrame()

    def save_data(self, df: pd.DataFrame, filename_prefix: str = "stock_capital_flow") -> str:
        """
        保存数据到CSV文件

        Args:
            df (pd.DataFrame): 要保存的数据
            filename_prefix (str): 文件名前缀

        Returns:
            str: 保存的文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{self.market_type.value}_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)

            # 保存为CSV文件，使用UTF-8编码和BOM以确保中文正确显示
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"数据已保存到: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"保存数据时发生错误: {e}")
            return ""

    def save_to_json(self, df: pd.DataFrame, filename_prefix: str = "stock_capital_flow") -> str:
        """
        保存数据到JSON文件

        Args:
            df (pd.DataFrame): 要保存的数据
            filename_prefix (str): 文件名前缀

        Returns:
            str: 保存的文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{self.market_type.value}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)

            # 转换为JSON格式
            data_dict = df.to_dict('records')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON数据已保存到: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"保存JSON数据时发生错误: {e}")
            return ""

    def run_once(self, max_pages: int = 10, save_format: str = 'csv') -> Tuple[pd.DataFrame, str]:
        """
        执行一次完整的爬取和保存流程

        Args:
            max_pages (int): 最大获取页数
            save_format (str): 保存格式，'csv'或'json'或'both'

        Returns:
            Tuple[pd.DataFrame, str]: 数据和保存路径
        """
        df = self.scrape_all_data(max_pages=max_pages)
        
        if df.empty:
            return df, ""

        filepath = ""
        if save_format in ['csv', 'both']:
            filepath = self.save_data(df)
        
        if save_format in ['json', 'both']:
            json_path = self.save_to_json(df)
            if save_format == 'json':
                filepath = json_path

        return df, filepath

    def start_scheduled_scraping(self, interval_seconds: int = 60, max_pages: int = 10, save_format: str = 'csv'):
        """
        开始定时爬取

        Args:
            interval_seconds (int): 爬取间隔秒数
            max_pages (int): 每次最大获取页数
            save_format (str): 保存格式
        """
        self.is_running = True
        logger.info(f"开始定时爬取{self.market_type.value}市场个股资金流向数据，间隔: {interval_seconds}秒")

        while self.is_running:
            try:
                df, filepath = self.run_once(max_pages=max_pages, save_format=save_format)
                if not df.empty:
                    logger.info(f"定时爬取完成，数据条数: {len(df)}, 保存路径: {filepath}")
                else:
                    logger.warning("定时爬取未获取到数据")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("接收到中断信号，停止定时爬取")
                self.stop()
                break
            except Exception as e:
                logger.error(f"定时爬取过程中发生错误: {e}")
                time.sleep(interval_seconds)

    def stop(self):
        """
        停止爬虫
        """
        self.is_running = False
        logger.info("个股资金流向爬虫已停止")

    def get_top_inflow_stocks(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """
        获取主力净流入最多的股票

        Args:
            df (pd.DataFrame): 股票数据
            top_n (int): 返回前N只股票

        Returns:
            pd.DataFrame: 主力净流入最多的股票
        """
        if df.empty or '主力净流入' not in df.columns:
            return pd.DataFrame()
        
        return df.nlargest(top_n, '主力净流入')[
            ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比', '数据获取时间']
        ]

    def get_top_outflow_stocks(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """
        获取主力净流出最多的股票

        Args:
            df (pd.DataFrame): 股票数据
            top_n (int): 返回前N只股票

        Returns:
            pd.DataFrame: 主力净流出最多的股票
        """
        if df.empty or '主力净流入' not in df.columns:
            return pd.DataFrame()
        
        return df.nsmallest(top_n, '主力净流入')[
            ['股票代码', '股票名称', '最新价', '涨跌幅', '主力净流入', '主力净流入占比', '数据获取时间']
        ]

    def analyze_market_summary(self, df: pd.DataFrame) -> Dict:
        """
        分析市场资金流向概况

        Args:
            df (pd.DataFrame): 股票数据

        Returns:
            Dict: 市场概况统计
        """
        if df.empty:
            return {}

        summary = {
            '总股票数': len(df),
            '主力净流入股票数': len(df[df['主力净流入'] > 0]) if '主力净流入' in df.columns else 0,
            '主力净流出股票数': len(df[df['主力净流入'] < 0]) if '主力净流入' in df.columns else 0,
            '市场主力净流入总额(万元)': round(df['主力净流入'].sum(), 2) if '主力净流入' in df.columns else 0,
            '平均主力净流入(万元)': round(df['主力净流入'].mean(), 2) if '主力净流入' in df.columns else 0,
            '上涨股票数': len(df[df['涨跌幅'] > 0]) if '涨跌幅' in df.columns else 0,
            '下跌股票数': len(df[df['涨跌幅'] < 0]) if '涨跌幅' in df.columns else 0,
            '平涨股票数': len(df[df['涨跌幅'] == 0]) if '涨跌幅' in df.columns else 0,
            '数据获取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return summary