"""
东方财富个股K线历史数据爬虫
支持不同周期（日K、周K、月K、分钟K等）的K线数据获取
基于现有爬虫架构，提供高性能并行数据获取功能
"""

import requests
import json
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from enum import Enum
import re

# 忽略pandas版本可能出现的FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

# 获取日志记录器实例
logger = logging.getLogger(__name__)


class KlinePeriod(Enum):
    """
    K线周期枚举
    """
    MIN_1 = "1"      # 1分钟
    MIN_5 = "5"      # 5分钟
    MIN_15 = "15"    # 15分钟
    MIN_30 = "30"    # 30分钟
    MIN_60 = "60"    # 60分钟
    DAILY = "101"    # 日K
    WEEKLY = "102"   # 周K
    MONTHLY = "103"  # 月K


class AdjustType(Enum):
    """
    复权类型枚举
    """
    NONE = "0"       # 不复权
    FORWARD = "1"    # 前复权
    BACKWARD = "2"   # 后复权


class StockKlineConfig:
    """
    个股K线数据爬虫配置类
    存储API端点、请求头、字段映射等常量信息
    """

    # HTTP请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # K线数据API接口地址
    KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

    # K线数据字段映射
    FIELD_MAPPING = {
        0: '日期',
        1: '开盘价',
        2: '收盘价',
        3: '最高价',
        4: '最低价',
        5: '成交量',
        6: '成交额',
        7: '振幅',
        8: '涨跌幅',
        9: '涨跌额',
        10: '换手率'
    }

    # 市场代码映射
    MARKET_MAPPING = {
        'sh': '1',  # 上海证券交易所
        'sz': '0',  # 深圳证券交易所
        'bj': '0'   # 北京证券交易所
    }


class StockKlineFetcher:
    """
    个股K线数据获取模块
    负责从东方财富API获取原始的K线历史数据
    """

    def __init__(self, config: StockKlineConfig, pool_size: int = 50):
        """
        初始化K线数据获取器

        Args:
            config (StockKlineConfig): 配置对象
            pool_size (int): requests.Session连接池的大小，默认为50
        """
        self.config = config
        self.session = requests.Session()
        # 配置HTTP适配器以提高并发性能
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_size,
                                                pool_maxsize=pool_size)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self.config.HEADERS)

    def _get_stock_code_with_market(self, stock_code: str) -> str:
        """
        根据股票代码获取带市场前缀的完整代码

        Args:
            stock_code (str): 股票代码，如 '000001', 'sh000001', 'sz000001'

        Returns:
            str: 带市场前缀的完整代码，如 '1.000001', '0.000001'
        """
        # 如果已经包含市场前缀，直接处理
        if '.' in stock_code:
            return stock_code
        
        # 移除可能的市场前缀字母
        clean_code = re.sub(r'^(sh|sz|bj)', '', stock_code.lower())
        
        # 根据代码规律判断市场
        if clean_code.startswith('6'):  # 沪市主板
            return f"1.{clean_code}"
        elif clean_code.startswith('0') or clean_code.startswith('3'):  # 深市主板/创业板
            return f"0.{clean_code}"
        elif clean_code.startswith('8') or clean_code.startswith('4'):  # 北交所
            return f"0.{clean_code}"
        else:
            # 默认深市
            return f"0.{clean_code}"

    def fetch_kline_data(self,
                        stock_code: str,
                        period: KlinePeriod = KlinePeriod.DAILY,
                        adjust_type: AdjustType = AdjustType.FORWARD,
                        start_date: str = None,
                        end_date: str = None,
                        limit: int = 500) -> Optional[Dict]:
        """
        获取单只股票的K线数据

        Args:
            stock_code (str): 股票代码，如 '000001', 'sh600000'
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期，格式 'YYYYMMDD'
            end_date (str): 结束日期，格式 'YYYYMMDD'
            limit (int): 获取数据条数限制

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None
        """
        try:
            # 处理股票代码
            full_code = self._get_stock_code_with_market(stock_code)
            
            # 构建请求参数
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',
                'secid': full_code,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': period.value,
                'fqt': adjust_type.value,
                'end': '20500101',  # 默认结束日期
                'lmt': str(limit),
                '_': str(int(time.time() * 1000))
            }

            # 如果指定了日期范围
            if end_date:
                params['end'] = end_date

            response = self.session.get(
                self.config.KLINE_URL,
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
                    f"解析股票 {stock_code} K线数据JSONP响应失败: 无法找到有效的JSON数据。响应内容: {content[:200]}..."
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取股票 {stock_code} K线数据网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(
                f"解析股票 {stock_code} K线数据JSON失败: {e}. 响应内容: {response.text[:200]}..."
            )
            return None
        except Exception as e:
            logger.error(f"获取股票 {stock_code} K线数据时发生未知错误: {e}")
            return None

    def fetch_multiple_stocks_kline(self,
                                   stock_codes: List[str],
                                   period: KlinePeriod = KlinePeriod.DAILY,
                                   adjust_type: AdjustType = AdjustType.FORWARD,
                                   start_date: str = None,
                                   end_date: str = None,
                                   limit: int = 500,
                                   max_workers: int = 10) -> Dict[str, Optional[Dict]]:
        """
        并行获取多只股票的K线数据

        Args:
            stock_codes (List[str]): 股票代码列表
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期
            end_date (str): 结束日期
            limit (int): 每只股票获取数据条数限制
            max_workers (int): 最大并发线程数

        Returns:
            Dict[str, Optional[Dict]]: 股票代码到K线数据的映射
        """
        results = {}
        
        if not stock_codes:
            logger.warning("股票代码列表为空")
            return results

        logger.info(f"开始并行获取 {len(stock_codes)} 只股票的K线数据，周期: {period.value}")

        with ThreadPoolExecutor(max_workers=min(max_workers, len(stock_codes))) as executor:
            # 提交所有任务
            future_to_code = {
                executor.submit(
                    self.fetch_kline_data,
                    stock_code, period, adjust_type, start_date, end_date, limit
                ): stock_code
                for stock_code in stock_codes
            }

            # 收集结果
            for future in as_completed(future_to_code):
                stock_code = future_to_code[future]
                try:
                    result = future.result()
                    results[stock_code] = result
                    if result:
                        logger.debug(f"成功获取股票 {stock_code} 的K线数据")
                    else:
                        logger.warning(f"获取股票 {stock_code} 的K线数据失败")
                except Exception as e:
                    logger.error(f"处理股票 {stock_code} K线数据时发生错误: {e}")
                    results[stock_code] = None

        success_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"并行获取完成，成功: {success_count}/{len(stock_codes)}")
        
        return results


class StockKlineParser:
    """
    个股K线数据解析模块
    负责将从API获取的原始JSON数据转换为结构化的Pandas DataFrame
    """

    def __init__(self, config: StockKlineConfig):
        """
        初始化数据解析器

        Args:
            config (StockKlineConfig): 配置对象
        """
        self.config = config

    def parse_single_stock_kline(self, raw_data: Dict, stock_code: str) -> pd.DataFrame:
        """
        解析单只股票的K线原始数据

        Args:
            raw_data (Dict): 从API获取的原始K线数据
            stock_code (str): 股票代码

        Returns:
            pd.DataFrame: 包含解析后K线数据的DataFrame
        """
        if not raw_data or 'data' not in raw_data:
            logger.warning(f"股票 {stock_code} 的原始数据为空或格式错误")
            return pd.DataFrame()

        data_section = raw_data['data']
        if not data_section or 'klines' not in data_section:
            logger.warning(f"股票 {stock_code} 无K线数据")
            return pd.DataFrame()

        klines = data_section['klines']
        if not klines:
            logger.warning(f"股票 {stock_code} K线数据列表为空")
            return pd.DataFrame()

        parsed_data = []
        for kline_str in klines:
            # K线数据格式: "日期,开,收,高,低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率"
            kline_parts = kline_str.split(',')
            if len(kline_parts) >= len(self.config.FIELD_MAPPING):
                parsed_row = {'股票代码': stock_code}
                
                for i, chinese_name in self.config.FIELD_MAPPING.items():
                    raw_value = kline_parts[i] if i < len(kline_parts) else None
                    
                    # 数据类型转换和格式化
                    if raw_value is None or raw_value == '-':
                        parsed_value = None
                    elif chinese_name == '日期':
                        # 日期格式转换
                        try:
                            parsed_value = datetime.strptime(raw_value, '%Y-%m-%d').strftime('%Y-%m-%d')
                        except ValueError:
                            parsed_value = raw_value
                    elif chinese_name in ['开盘价', '收盘价', '最高价', '最低价']:
                        # 价格字段，保留两位小数
                        try:
                            parsed_value = round(float(raw_value), 2)
                        except (ValueError, TypeError):
                            parsed_value = None
                    elif chinese_name == '成交量':
                        # 成交量单位是手
                        try:
                            parsed_value = int(raw_value)
                        except (ValueError, TypeError):
                            parsed_value = None
                    elif chinese_name == '成交额':
                        # 成交额单位是元，转换为万元
                        try:
                            parsed_value = round(float(raw_value) / 10000, 2)
                        except (ValueError, TypeError):
                            parsed_value = None
                    elif chinese_name in ['振幅', '涨跌幅', '换手率']:
                        # 百分比字段，保留两位小数
                        try:
                            parsed_value = round(float(raw_value), 2)
                        except (ValueError, TypeError):
                            parsed_value = None
                    elif chinese_name == '涨跌额':
                        # 涨跌额，保留两位小数
                        try:
                            parsed_value = round(float(raw_value), 2)
                        except (ValueError, TypeError):
                            parsed_value = None
                    else:
                        parsed_value = raw_value
                    
                    parsed_row[chinese_name] = parsed_value
                
                # 添加数据获取时间
                parsed_row['数据获取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                parsed_data.append(parsed_row)

        df = pd.DataFrame(parsed_data)
        
        # 按日期排序
        if '日期' in df.columns:
            df = df.sort_values('日期')
            df.reset_index(drop=True, inplace=True)
        
        logger.info(f"成功解析股票 {stock_code} 的 {len(df)} 条K线数据")
        return df

    def parse_multiple_stocks_kline(self, raw_data_dict: Dict[str, Optional[Dict]]) -> Dict[str, pd.DataFrame]:
        """
        解析多只股票的K线原始数据

        Args:
            raw_data_dict (Dict[str, Optional[Dict]]): 股票代码到原始数据的映射

        Returns:
            Dict[str, pd.DataFrame]: 股票代码到解析后DataFrame的映射
        """
        parsed_results = {}
        
        for stock_code, raw_data in raw_data_dict.items():
            if raw_data is not None:
                df = self.parse_single_stock_kline(raw_data, stock_code)
                parsed_results[stock_code] = df
            else:
                parsed_results[stock_code] = pd.DataFrame()
        
        success_count = sum(1 for df in parsed_results.values() if not df.empty)
        logger.info(f"成功解析 {success_count}/{len(raw_data_dict)} 只股票的K线数据")
        
        return parsed_results


class StockKlineScraper:
    """
    个股K线历史数据爬虫主类
    集成数据获取、数据解析和数据存储功能，提供单股和批量爬取功能
    """

    def __init__(self, output_dir: str = None):
        """
        初始化个股K线数据爬虫

        Args:
            output_dir (str): 数据输出目录，如果为None则自动设置
        """
        self.config = StockKlineConfig()
        self.fetcher = StockKlineFetcher(self.config)
        self.parser = StockKlineParser(self.config)
        self.is_running = False

        # 设置输出目录
        if output_dir is None:
            self.output_dir = "output/stock_kline_data"
        else:
            self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_single_stock(self,
                           stock_code: str,
                           period: KlinePeriod = KlinePeriod.DAILY,
                           adjust_type: AdjustType = AdjustType.FORWARD,
                           start_date: str = None,
                           end_date: str = None,
                           limit: int = 500) -> pd.DataFrame:
        """
        爬取单只股票的K线数据

        Args:
            stock_code (str): 股票代码
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期
            end_date (str): 结束日期
            limit (int): 数据条数限制

        Returns:
            pd.DataFrame: K线数据DataFrame
        """
        try:
            logger.info(f"开始爬取股票 {stock_code} 的{period.value}周期K线数据...")

            # 获取原始数据
            raw_data = self.fetcher.fetch_kline_data(
                stock_code, period, adjust_type, start_date, end_date, limit
            )

            if not raw_data:
                logger.warning(f"未获取到股票 {stock_code} 的原始K线数据")
                return pd.DataFrame()

            # 解析数据
            df = self.parser.parse_single_stock_kline(raw_data, stock_code)

            if df.empty:
                logger.warning(f"股票 {stock_code} 解析后数据为空")
                return df

            logger.info(f"成功完成股票 {stock_code} K线数据爬取，共 {len(df)} 条记录")
            return df

        except Exception as e:
            logger.error(f"爬取股票 {stock_code} K线数据时发生错误: {e}")
            return pd.DataFrame()

    def scrape_multiple_stocks(self,
                              stock_codes: List[str],
                              period: KlinePeriod = KlinePeriod.DAILY,
                              adjust_type: AdjustType = AdjustType.FORWARD,
                              start_date: str = None,
                              end_date: str = None,
                              limit: int = 500,
                              max_workers: int = 10) -> Dict[str, pd.DataFrame]:
        """
        批量爬取多只股票的K线数据

        Args:
            stock_codes (List[str]): 股票代码列表
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期
            end_date (str): 结束日期
            limit (int): 每只股票数据条数限制
            max_workers (int): 最大并发线程数

        Returns:
            Dict[str, pd.DataFrame]: 股票代码到K线数据DataFrame的映射
        """
        try:
            logger.info(f"开始批量爬取 {len(stock_codes)} 只股票的{period.value}周期K线数据...")

            # 并行获取原始数据
            raw_data_dict = self.fetcher.fetch_multiple_stocks_kline(
                stock_codes, period, adjust_type, start_date, end_date, limit, max_workers
            )

            if not raw_data_dict:
                logger.warning("未获取到任何原始K线数据")
                return {}

            # 解析数据
            parsed_results = self.parser.parse_multiple_stocks_kline(raw_data_dict)

            success_count = sum(1 for df in parsed_results.values() if not df.empty)
            total_records = sum(len(df) for df in parsed_results.values())
            
            logger.info(f"成功完成 {success_count}/{len(stock_codes)} 只股票K线数据爬取，共 {total_records} 条记录")
            return parsed_results

        except Exception as e:
            logger.error(f"批量爬取股票K线数据时发生错误: {e}")
            return {}

    def save_single_stock_data(self,
                              df: pd.DataFrame,
                              stock_code: str,
                              period: KlinePeriod,
                              file_format: str = 'csv') -> str:
        """
        保存单只股票的K线数据

        Args:
            df (pd.DataFrame): K线数据
            stock_code (str): 股票代码
            period (KlinePeriod): K线周期
            file_format (str): 文件格式，'csv'或'json'

        Returns:
            str: 保存的文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"kline_{stock_code}_{period.value}_{timestamp}.{file_format}"
            filepath = os.path.join(self.output_dir, filename)

            if file_format == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            elif file_format == 'json':
                data_dict = df.to_dict('records')
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"股票 {stock_code} K线数据已保存到: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"保存股票 {stock_code} K线数据时发生错误: {e}")
            return ""

    def save_multiple_stocks_data(self,
                                 data_dict: Dict[str, pd.DataFrame],
                                 period: KlinePeriod,
                                 file_format: str = 'csv',
                                 combine_files: bool = False) -> List[str]:
        """
        保存多只股票的K线数据

        Args:
            data_dict (Dict[str, pd.DataFrame]): 股票代码到K线数据的映射
            period (KlinePeriod): K线周期
            file_format (str): 文件格式
            combine_files (bool): 是否合并到一个文件

        Returns:
            List[str]: 保存的文件路径列表
        """
        saved_files = []

        if combine_files:
            # 合并所有股票数据到一个文件
            all_data = []
            for stock_code, df in data_dict.items():
                if not df.empty:
                    all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"kline_multiple_stocks_{period.value}_{timestamp}.{file_format}"
                filepath = os.path.join(self.output_dir, filename)

                try:
                    if file_format == 'csv':
                        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    elif file_format == 'json':
                        data_list = combined_df.to_dict('records')
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(data_list, f, ensure_ascii=False, indent=2)
                    
                    saved_files.append(filepath)
                    logger.info(f"合并文件已保存到: {filepath}")
                except Exception as e:
                    logger.error(f"保存合并文件时发生错误: {e}")
        else:
            # 分别保存每只股票的数据
            for stock_code, df in data_dict.items():
                if not df.empty:
                    filepath = self.save_single_stock_data(df, stock_code, period, file_format)
                    if filepath:
                        saved_files.append(filepath)

        return saved_files

    def run_single_stock(self,
                        stock_code: str,
                        period: KlinePeriod = KlinePeriod.DAILY,
                        adjust_type: AdjustType = AdjustType.FORWARD,
                        start_date: str = None,
                        end_date: str = None,
                        limit: int = 500,
                        save_format: str = 'csv') -> Tuple[pd.DataFrame, str]:
        """
        执行单只股票K线数据的完整爬取和保存流程

        Args:
            stock_code (str): 股票代码
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期
            end_date (str): 结束日期
            limit (int): 数据条数限制
            save_format (str): 保存格式

        Returns:
            Tuple[pd.DataFrame, str]: 数据和保存路径
        """
        df = self.scrape_single_stock(stock_code, period, adjust_type, start_date, end_date, limit)
        
        if df.empty:
            return df, ""

        filepath = self.save_single_stock_data(df, stock_code, period, save_format)
        return df, filepath

    def run_multiple_stocks(self,
                           stock_codes: List[str],
                           period: KlinePeriod = KlinePeriod.DAILY,
                           adjust_type: AdjustType = AdjustType.FORWARD,
                           start_date: str = None,
                           end_date: str = None,
                           limit: int = 500,
                           max_workers: int = 10,
                           save_format: str = 'csv',
                           combine_files: bool = False) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
        """
        执行多只股票K线数据的完整爬取和保存流程

        Args:
            stock_codes (List[str]): 股票代码列表
            period (KlinePeriod): K线周期
            adjust_type (AdjustType): 复权类型
            start_date (str): 开始日期
            end_date (str): 结束日期
            limit (int): 每只股票数据条数限制
            max_workers (int): 最大并发线程数
            save_format (str): 保存格式
            combine_files (bool): 是否合并文件

        Returns:
            Tuple[Dict[str, pd.DataFrame], List[str]]: 数据字典和保存路径列表
        """
        data_dict = self.scrape_multiple_stocks(
            stock_codes, period, adjust_type, start_date, end_date, limit, max_workers
        )
        
        if not data_dict:
            return {}, []

        filepaths = self.save_multiple_stocks_data(data_dict, period, save_format, combine_files)
        return data_dict, filepaths

    def get_supported_periods(self) -> List[str]:
        """
        获取支持的K线周期列表

        Returns:
            List[str]: 支持的周期列表
        """
        return [period.value for period in KlinePeriod]

    def get_supported_adjust_types(self) -> List[str]:
        """
        获取支持的复权类型列表

        Returns:
            List[str]: 支持的复权类型列表
        """
        return [adjust.value for adjust in AdjustType]