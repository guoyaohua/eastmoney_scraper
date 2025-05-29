"""
东方财富板块实时行情及资金流向爬虫
支持概念板块和行业板块的数据获取
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


class SectorType(Enum):
    """
    板块类型枚举
    """
    CONCEPT = "concept"  # 概念板块
    INDUSTRY = "industry"  # 行业板块


class SectorConfig:
    """
    板块爬虫配置类
    存储API端点、请求头、字段映射等常量信息
    """

    # HTTP请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/',  # 东方财富行情中心作为Referer
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # API接口地址
    # 板块行情和资金流向使用相同的基地址，通过参数区分
    SECTOR_QUOTE_URL = "https://push2.eastmoney.com/api/qt/clist/get"  # 获取板块行情
    CAPITAL_FLOW_URL = "https://push2.eastmoney.com/api/qt/clist/get"  # 获取资金流向数据
    # 成分股也使用SECTOR_QUOTE_URL，通过'fs'参数指定板块代码

    # 板块类型对应的筛选参数
    SECTOR_FILTER_PARAMS = {
        SectorType.CONCEPT: 'm:90+t:3',  # 概念板块
        SectorType.INDUSTRY: 'm:90+t:2'  # 行业板块
    }

    # 板块行情数据字段原始键名到中文名称的映射
    QUOTE_FIELD_MAPPING = {
        'f12': '板块代码',
        'f14': '板块名称',
        'f2': '最新价',
        'f3': '涨跌幅',
        'f4': '涨跌额',
        'f5': '成交量',
        'f6': '成交额',
        'f22': '涨速',
        'f11': '5分钟涨跌',
        'f104': '上涨家数',
        'f105': '下跌家数',
        # 以下字段在行情接口中直接返回，表示今日的资金流向
        'f62': '主力净流入',
        'f184': '主力净流入占比',
        'f66': '超大单净流入',
        'f69': '超大单净流入占比',
        # 5日资金流向字段
        'f164': '5日主力净流入',
        'f165': '5日主力净流入占比',
        'f166': '5日超大单净流入',
        'f167': '5日超大单净流入占比',
        # 10日资金流向字段
        'f174': '10日主力净流入',
        'f175': '10日主力净流入占比',
        'f176': '10日超大单净流入',
        'f177': '10日超大单净流入占比',
        # 领涨股票相关字段
        'f128': '领涨股票代码',
        'f140': '领涨股票名称',
        'f136': '领涨股票涨跌幅',
    }

    # 板块成分股数据字段原始键名到中文名称的映射
    CONSTITUENT_FIELD_MAPPING = {
        'f12': '股票代码',
        'f14': '股票名称',
    }


class SectorDataFetcher:
    """
    板块数据获取模块
    负责从东方财富API获取原始的板块行情、资金流向和成分股数据
    """
    def __init__(self, config: SectorConfig, sector_type: SectorType, pool_size: int = 50):
        """
        初始化数据获取器

        Args:
            config (SectorConfig): 配置对象
            sector_type (SectorType): 板块类型（概念板块或行业板块）
            pool_size (int): requests.Session连接池的大小，默认为50
        """
        self.config = config  # 配置实例
        self.sector_type = sector_type  # 板块类型
        self.session = requests.Session()  # 使用Session以复用TCP连接
        # 配置HTTP适配器以提高并发性能
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_size,
                                                pool_maxsize=pool_size)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self.config.HEADERS)  # 设置默认请求头

    def fetch_quotes_page(self,
                         page_num: int = 1,
                         page_size: int = 100) -> Optional[Dict]:
        """
        获取单页的板块实时行情数据

        Args:
            page_num (int): 页码，从1开始，默认为1
            page_size (int): 每页返回的数据条数，默认为100

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None
        """
        try:
            # API请求参数
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',  # JSONP回调函数名
                'fid': 'f3',  # 按涨跌幅排序
                'po': '1',  # 排序方式，1为降序
                'pz': str(page_size),  # 每页数量
                'pn': str(page_num),  # 当前页码
                'np': '1',  # 固定参数
                'fltt': '2',  # 固定参数
                'invt': '2',  # 固定参数
                'ut': 'b2884a393a59ad64002292a3e90d46a5',  # 用户令牌或标识
                'fs': self.config.SECTOR_FILTER_PARAMS[self.sector_type],  # 筛选条件：根据板块类型设置
                'fields': ','.join(self.config.QUOTE_FIELD_MAPPING.keys())  # 请求的字段列表
            }

            response = self.session.get(
                self.config.SECTOR_QUOTE_URL,
                params=params,
                timeout=10  # 请求超时时间（秒）
            )
            response.raise_for_status()  # 如果HTTP请求返回了失败状态码，则抛出HTTPError异常

            # 处理JSONP响应格式
            content = response.text
            # 寻找JSONP回调函数包裹的JSON数据部分
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')

            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1:json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(
                    f"解析{self.sector_type.value}板块行情JSONP响应失败 (页 {page_num}): 无法找到有效的JSON数据。响应内容: {content[:200]}..."
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取{self.sector_type.value}板块行情网络请求失败 (页 {page_num}): {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(
                f"解析{self.sector_type.value}板块行情JSON数据失败 (页 {page_num}): {e}. 响应内容: {response.text[:200]}..."
            )
            return None
        except Exception as e:
            logger.error(f"获取{self.sector_type.value}板块行情时发生未知错误 (页 {page_num}): {e}")
            return None

    def fetch_all_quotes(self) -> List[Dict]:
        """
        获取所有板块的实时行情数据，自动处理分页并行获取

        Returns:
            List[Dict]: 包含所有板块原始行情数据的列表
        """
        all_raw_quotes_data = []  # 用于存储所有原始行情数据

        # 首先获取第一页数据，以确定总记录数和总页数
        page_size_for_total_count = 100  # API通常每页最多返回100条
        first_page_response = self.fetch_quotes_page(
            page_num=1, page_size=page_size_for_total_count)

        if not first_page_response or 'data' not in first_page_response or not first_page_response['data']:
            logger.warning(f"获取{self.sector_type.value}板块行情第一页数据失败或数据为空，无法继续获取")
            return all_raw_quotes_data

        total_records = first_page_response['data'].get('total', 0)
        if total_records == 0:
            logger.info(f"{self.sector_type.value}板块总数为0，无需进一步获取")
            if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
                all_raw_quotes_data.extend(first_page_response['data']['diff'])  # 仍然添加第一页可能存在的少量数据
            return all_raw_quotes_data

        total_pages = (total_records + page_size_for_total_count - 1) // page_size_for_total_count

        logger.info(f"{self.sector_type.value}板块总数: {total_records}, 每页大小: {page_size_for_total_count}, 总页数: {total_pages}")

        # 添加第一页的数据到结果列表
        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_quotes_data.extend(first_page_response['data']['diff'])

        # 如果总页数大于1，则并行获取剩余页面的数据
        if total_pages > 1:
            # 使用线程池并行处理分页请求，max_workers可以根据网络情况调整
            with ThreadPoolExecutor(max_workers=min(10, total_pages - 1)) as executor:  # 限制最大线程数
                # 创建任务列表
                futures_map = {
                    executor.submit(self.fetch_quotes_page, page_num, page_size_for_total_count): page_num
                    for page_num in range(2, total_pages + 1)  # 从第二页开始
                }

                # 按完成顺序处理结果
                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_quotes_data.extend(page_data['data']['diff'])
                        else:
                            logger.warning(f"获取{self.sector_type.value}板块行情第 {page_num_completed} 页数据失败或数据不完整")
                    except Exception as e:
                        logger.error(f"处理{self.sector_type.value}板块行情第 {page_num_completed} 页结果时发生错误: {e}")

        logger.info(f"成功获取 {len(all_raw_quotes_data)} 条原始{self.sector_type.value}板块行情数据")
        return all_raw_quotes_data

    def fetch_constituents_page(self,
                               sector_code: str,
                               page_num: int = 1,
                               page_size: int = 200) -> Optional[Dict]:
        """
        获取指定板块的单页成分股数据

        Args:
            sector_code (str): 板块代码，例如"BK0715"
            page_num (int): 页码，从1开始，默认为1
            page_size (int): 每页返回的数据条数，API对成分股列表似乎有每页100条的限制，默认为200

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None
        """
        try:
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',
                'fid': 'f3',  # 排序字段，对于成分股列表可能不重要
                'po': '1',  # 排序方式
                'pz': str(page_size),  # 尝试请求的页面大小
                'pn': str(page_num),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5',
                'fs': f'b:{sector_code}+f:!50',  # 关键参数：'b:{板块代码}'用于指定板块
                'fields': ','.join(self.config.CONSTITUENT_FIELD_MAPPING.keys())  # 通常只需要股票代码和名称
            }

            response = self.session.get(
                self.config.SECTOR_QUOTE_URL,  # 成分股列表也通过此URL获取
                params=params,
                timeout=15  # 成分股列表可能较大，增加超时
            )
            response.raise_for_status()

            content = response.text
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')

            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1:json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(
                    f"解析板块 {sector_code} 成分股JSONP响应失败 (页 {page_num}): 无法找到JSON。响应: {content[:200]}..."
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取板块 {sector_code} 成分股网络请求失败 (页 {page_num}): {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(
                f"解析板块 {sector_code} 成分股JSON数据失败 (页 {page_num}): {e}. 响应: {response.text[:200]}..."
            )
            return None
        except Exception as e:
            logger.error(f"获取板块 {sector_code} 成分股时发生未知错误 (页 {page_num}): {e}")
            return None

    def fetch_all_constituents(self, sector_code: str) -> List[Dict]:
        """
        获取指定板块的所有成分股数据，自动处理分页并行获取

        Args:
            sector_code (str): 板块代码，例如"BK0715"

        Returns:
            List[Dict]: 包含该板块所有原始成分股数据的列表
        """
        all_raw_constituents = []  # 存储所有原始成分股数据
        # API对于成分股列表似乎有每页100条的实际限制
        API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS = 100

        first_page_response = self.fetch_constituents_page(
            sector_code,
            page_num=1,
            page_size=API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS)

        if not first_page_response or 'data' not in first_page_response:
            logger.warning(f"获取板块 {sector_code} 成分股第一页数据失败或数据结构异常")
            return all_raw_constituents

        if not first_page_response['data']:  # 'data'字段本身可能为null或空对象
            logger.info(f"板块 {sector_code} 成分股API返回的'data'字段为空，可能无成分股或板块不存在")
            return all_raw_constituents

        total_records = first_page_response['data'].get('total', 0)

        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_constituents.extend(first_page_response['data']['diff'])

        if total_records == 0:
            logger.info(f"板块 {sector_code} 成分股总数报告为0。已从第一页获取 {len(all_raw_constituents)} 条记录（如有）")
            return all_raw_constituents

        total_pages = (total_records + API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS - 1) // API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS

        logger.info(
            f"板块 {sector_code} 成分股总数: {total_records}, "
            f"每页有效大小: {API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS}, 总页数: {total_pages} (已获取第1页)"
        )

        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=min(5, total_pages - 1)) as executor:  # 限制单板块成分股获取的线程数
                futures_map = {
                    executor.submit(self.fetch_constituents_page, sector_code, page_num, API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS): page_num
                    for page_num in range(2, total_pages + 1)
                }

                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_constituents.extend(page_data['data']['diff'])
                        elif page_data and 'data' in page_data and not page_data['data'].get('diff'):
                            logger.info(f"板块 {sector_code} 成分股第 {page_num_completed} 页未返回'diff'数据")
                        elif not page_data:
                            logger.warning(f"获取板块 {sector_code} 成分股第 {page_num_completed} 页结果为空")
                    except Exception as e:
                        logger.error(f"处理板块 {sector_code} 成分股第 {page_num_completed} 页结果时发生错误: {e}")

        logger.info(f"成功获取板块 {sector_code} 共 {len(all_raw_constituents)} 条原始成分股数据（解析后将去重）")
        return all_raw_constituents


class SectorDataParser:
    """
    板块数据解析模块
    负责将从API获取的原始JSON数据转换为结构化的Pandas DataFrame或列表
    """
    def __init__(self, config: SectorConfig):
        """
        初始化数据解析器

        Args:
            config (SectorConfig): 配置对象
        """
        self.config = config  # 配置实例

    def parse_quotes_data(self, raw_quotes_list: List[Dict]) -> pd.DataFrame:
        """
        解析板块的实时行情原始数据列表

        Args:
            raw_quotes_list (List[Dict]): 从API获取的原始行情数据字典列表

        Returns:
            pd.DataFrame: 包含解析后行情数据的Pandas DataFrame，列名为中文
        """
        if not raw_quotes_list:
            logger.info("输入的原始行情数据列表为空，返回空DataFrame")
            return pd.DataFrame()

        parsed_data_list = []  # 用于存储解析后的每条行情数据
        for raw_item in raw_quotes_list:
            parsed_item = {}  # 当前解析的条目
            for field_key, chinese_name in self.config.QUOTE_FIELD_MAPPING.items():
                raw_value = raw_item.get(field_key)  # 从原始数据中获取值

                # 对特定字段进行单位转换或格式化
                if raw_value is None or raw_value == '-':  # 处理空值或API返回的占位符
                    parsed_value = None
                elif '占比' in chinese_name or '换手率' in chinese_name or '涨跌幅' in chinese_name or '振幅' in chinese_name:
                    # 百分比字段，通常API直接给出数值，保留两位小数
                    try:
                        parsed_value = round(float(raw_value), 2)
                    except (ValueError, TypeError):
                        parsed_value = None  # 如果转换失败
                elif ('流入' in chinese_name and '占比' not in chinese_name) or chinese_name == '成交额':
                    # 金额字段（如主力净流入、成交额），API单位通常是元，转换为万元，保留两位小数
                    try:
                        parsed_value = round(float(raw_value) / 10000, 2)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif chinese_name == '成交量':  # 成交量单位是"手"
                    try:
                        parsed_value = int(raw_value)  # 通常是整数
                    except (ValueError, TypeError):
                        parsed_value = None
                else:
                    # 其他字段直接使用，或根据需要进行类型转换
                    parsed_value = raw_value

                parsed_item[chinese_name] = parsed_value

            parsed_data_list.append(parsed_item)

        df = pd.DataFrame(parsed_data_list)
        logger.info(f"成功解析 {len(df)} 条板块行情数据")
        return df

    def parse_constituents_data(self, raw_constituents_list: List[Dict]) -> List[str]:
        """
        解析板块的成分股原始数据列表，提取股票代码

        Args:
            raw_constituents_list (List[Dict]): 从API获取的原始成分股数据字典列表

        Returns:
            List[str]: 去重后的股票代码列表
        """
        if not raw_constituents_list:
            logger.info("输入的原始成分股数据列表为空，返回空列表")
            return []

        stock_codes_list = []  # 用于存储提取的股票代码

        # 从配置中获取"股票代码"对应的原始字段键名
        stock_code_field_key = None
        for key, chinese_name in self.config.CONSTITUENT_FIELD_MAPPING.items():
            if chinese_name == '股票代码':
                stock_code_field_key = key
                break

        if not stock_code_field_key:
            logger.error("在CONSTITUENT_FIELD_MAPPING配置中未找到'股票代码'的映射键，无法解析成分股")
            return []

        for raw_item in raw_constituents_list:
            stock_code = raw_item.get(stock_code_field_key)
            if stock_code:  # 确保股票代码存在且不为空
                stock_codes_list.append(str(stock_code))  # 统一转换为字符串

        # 去重并返回
        unique_stock_codes = sorted(list(set(stock_codes_list)))  # 排序使结果可预测
        logger.info(f"成功解析出 {len(unique_stock_codes)} 个唯一的成分股代码（原始数量: {len(stock_codes_list)}）")
        return unique_stock_codes


class SectorScraper:
    """
    板块爬虫主类
    集成数据获取、数据解析和数据存储功能，提供一次性爬取、定时爬取以及板块成分股映射等功能
    支持概念板块和行业板块
    """
    def __init__(self, sector_type: SectorType, output_dir: str = None):
        """
        初始化板块爬虫

        Args:
            sector_type (SectorType): 板块类型（概念板块或行业板块）
            output_dir (str): 数据输出目录，如果为None则根据板块类型自动设置
        """
        self.sector_type = sector_type
        self.config = SectorConfig()  # 加载配置
        self.fetcher = SectorDataFetcher(self.config, sector_type)  # 初始化数据获取器
        self.parser = SectorDataParser(self.config)  # 初始化数据解析器
        self.is_running = False  # 爬虫运行状态标志
        
        # 设置输出目录
        if output_dir is None:
            output_dir = f"output/{sector_type.value}_sector_data"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # 创建输出目录（如果不存在）

    def scrape_all_data(self) -> pd.DataFrame:
        """
        爬取所有板块的实时行情数据，并合并成一个DataFrame

        Returns:
            pd.DataFrame: 包含合并后数据的Pandas DataFrame，如果出错则返回空DataFrame
        """
        try:
            logger.info(f"开始爬取{self.sector_type.value}板块综合数据（行情与资金流）...")

            logger.info("步骤1: 获取实时行情数据...")
            raw_quotes_list = self.fetcher.fetch_all_quotes()
            df_quotes = self.parser.parse_quotes_data(raw_quotes_list)

            if df_quotes.empty:
                logger.error("未能获取实时行情数据，操作中止")
                return pd.DataFrame()

            # 添加更新时间戳
            df_quotes['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 按涨跌幅降序排序
            if '涨跌幅' in df_quotes.columns:
                df_quotes = df_quotes.sort_values('涨跌幅', ascending=False).reset_index(drop=True)

            logger.info(f"成功获取并合并 {len(df_quotes)} 个{self.sector_type.value}板块的综合数据")

            return df_quotes

        except Exception as e:
            logger.exception("爬取并合并所有数据时发生严重错误")  # 使用logger.exception记录堆栈信息
            return pd.DataFrame()  # 返回空DataFrame表示失败

    def save_data(self, df: pd.DataFrame, filename_prefix: str = "concept_sectors") -> str:
        """
        将DataFrame数据保存到CSV文件
        同时保存带时间戳的文件和一份名为'..._latest.csv'的最新文件

        Args:
            df (pd.DataFrame): 需要保存的DataFrame
            filename_prefix (str): 文件名前缀，默认根据板块类型设置

        Returns:
            str: 带时间戳的文件的完整路径，如果保存失败则返回空字符串
        """
        if df.empty:
            logger.warning("输入数据为空，不执行保存操作")
            return ""
        if not self.output_dir:
            logger.error("未设置输出目录，无法保存数据")
            return ""

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamped_filename = f"{filename_prefix}_{timestamp}.csv"
            timestamped_filepath = os.path.join(self.output_dir, timestamped_filename)

            df.to_csv(timestamped_filepath, index=False, encoding='utf-8-sig')  # utf-8-sig确保Excel正确显示中文
            logger.info(f"数据已保存到: {timestamped_filepath}")

            latest_filename = f"{filename_prefix}_latest.csv"
            latest_filepath = os.path.join(self.output_dir, latest_filename)
            df.to_csv(latest_filepath, index=False, encoding='utf-8-sig')
            logger.info(f"最新数据已同步到: {latest_filepath}")

            return timestamped_filepath

        except Exception as e:
            logger.exception(
                f"保存数据到CSV文件失败。文件名: {timestamped_filename if 'timestamped_filename' in locals() else filename_prefix}"
            )
            return ""

    def run_once(self) -> Tuple[pd.DataFrame, str]:
        """
        执行一次完整的爬取（行情和资金流）并保存数据

        Returns:
            Tuple[pd.DataFrame, str]: 包含爬取数据的DataFrame和保存文件的路径
        """
        df = self.scrape_all_data()
        saved_filepath = ""
        if not df.empty:
            saved_filepath = self.save_data(df, filename_prefix=f"{self.sector_type.value}_sectors_综合")  # 使用特定前缀
        return df, saved_filepath

    def start_scheduled_scraping(self, interval_seconds: int = 60):
        """
        开始定时爬取板块综合数据
        
        Args:
            interval_seconds (int): 爬取间隔时间（秒），默认为60秒
        """
        if interval_seconds < 10:
            logger.warning(f"设置的爬取间隔 {interval_seconds}秒 过短，可能导致IP被封禁。建议至少10秒以上")
        self.is_running = True
        logger.info(f"启动定时爬取任务，每 {interval_seconds} 秒更新一次{self.sector_type.value}板块综合数据")

        while self.is_running:
            try:
                logger.info(f"执行定时爬取 (间隔: {interval_seconds}s)...")
                df, filepath = self.run_once()

                if not df.empty and filepath:
                    logger.info(f"定时爬取完成，数据已保存到 {filepath}")
                    # 可以在这里添加回调函数或进一步处理逻辑
                else:
                    logger.warning("定时爬取未获取到数据或保存失败")

                # 等待指定间隔时间
                # 为了能及时响应stop()方法，可以将长sleep拆分为短sleep循环检查is_running
                for _ in range(interval_seconds):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except KeyboardInterrupt:
                logger.info("接收到手动中断 (KeyboardInterrupt)，正在停止定时爬取...")
                self.stop()
                break  # 退出while循环
            except Exception as e:
                logger.exception(f"定时爬取过程中发生未知错误，将在 {interval_seconds} 秒后重试")
                time.sleep(interval_seconds)  # 发生错误后也等待一段时间

    def stop(self):
        """
        停止正在运行的定时爬取任务
        """
        if self.is_running:
            self.is_running = False
            logger.info("定时爬取任务已标记为停止，将在当前循环结束后退出")
        else:
            logger.info("定时爬取任务未在运行")

    def _fetch_and_parse_constituents(self, sector_info: Dict) -> Tuple[str, List[str]]:
        """
        辅助方法：获取并解析单个板块的成分股

        Args:
            sector_info (Dict): 包含板块代码('code')和板块名称('name')的字典

        Returns:
            Tuple[str, List[str]]: 板块代码和其对应的成分股代码列表，获取失败则股票列表为空
        """
        sector_code = sector_info.get('code')
        sector_name = sector_info.get('name', '未知板块')

        if not sector_code:
            logger.warning(f"提供的板块信息缺少板块代码: {sector_info}，跳过此板块")
            return "", []

        try:
            raw_constituent_data = self.fetcher.fetch_all_constituents(sector_code)

            if not raw_constituent_data:
                return sector_code, []

            stock_codes_list = self.parser.parse_constituents_data(raw_constituent_data)
            return sector_code, stock_codes_list
        except Exception as e:
            logger.exception(f"处理板块 '{sector_name}' ({sector_code}) 成分股时发生内部错误")
            return sector_code, []  # 确保在异常情况下也返回符合类型的空结果

    def scrape_stock_to_sector_mapping(self, max_workers: int = 10) -> Dict[str, List[str]]:
        """
        爬取所有板块及其成分股，生成"股票代码 -> [板块代码列表]"的映射
        此方法会并行获取各个板块的成分股

        Args:
            max_workers (int): 用于并行获取成分股的最大线程数，默认为10

        Returns:
            Dict[str, List[str]]: 股票代码到其所属板块代码列表的映射字典
        """
        logger.info(f"开始构建'股票代码-{self.sector_type.value}板块'映射（最大并行数: {max_workers}）...")
        stock_to_sector_map: Dict[str, List[str]] = {}  # 初始化结果字典

        # 1. 获取所有板块的基础信息（代码和名称）
        logger.info(f"步骤1: 获取所有{self.sector_type.value}板块列表...")
        raw_sectors = self.fetcher.fetch_all_quotes()  # 行情接口也返回板块列表
        if not raw_sectors:
            logger.error(f"未能获取{self.sector_type.value}板块列表，无法构建映射")
            return stock_to_sector_map

        # 提取板块代码和名称
        sectors_to_process = [
            {
                'code': sector_data.get('f12'),
                'name': sector_data.get('f14')
            } for sector_data in raw_sectors
            if sector_data.get('f12') and sector_data.get('f14')  # 确保代码和名称都存在
        ]
        total_sectors_count = len(sectors_to_process)
        if total_sectors_count == 0:
            logger.warning(f"获取到的{self.sector_type.value}板块列表为空，无法构建映射")
            return stock_to_sector_map
        logger.info(f"获取到 {total_sectors_count} 个{self.sector_type.value}板块待处理")

        # 2. 并行获取每个板块的成分股，并构建映射
        logger.info("步骤2: 并行获取各板块成分股并构建映射...")
        processed_sectors_count = 0
        # 使用线程池进行并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 创建future到板块信息的映射，方便后续处理
            future_to_sector_info_map = {
                executor.submit(self._fetch_and_parse_constituents, sector_info): sector_info
                for sector_info in sectors_to_process
            }

            for future in as_completed(future_to_sector_info_map):
                original_sector_info = future_to_sector_info_map[future]
                original_sector_code = original_sector_info['code']
                original_sector_name = original_sector_info['name']
                processed_sectors_count += 1
                progress_percent = (processed_sectors_count / total_sectors_count) * 100

                try:
                    # 获取该板块的成分股列表
                    fetched_sector_code, stock_codes_in_sector = future.result()

                    if fetched_sector_code != original_sector_code:  # 基本校验
                        logger.warning(
                            f"处理板块 '{original_sector_name}' 时返回的板块代码 ({fetched_sector_code}) 与预期 ({original_sector_code}) 不符"
                        )

                    if stock_codes_in_sector:
                        logger.info(
                            f"({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) 板块 '{original_sector_name}' ({original_sector_code}) "
                            f"包含 {len(stock_codes_in_sector)} 个成分股")
                        for stock_code in stock_codes_in_sector:
                            if stock_code not in stock_to_sector_map:
                                stock_to_sector_map[stock_code] = []
                            # 添加板块代码到股票的板块列表（确保不重复添加）
                            if original_sector_code not in stock_to_sector_map[stock_code]:
                                stock_to_sector_map[stock_code].append(original_sector_code)
                    else:
                        logger.info(
                            f"({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) 板块 '{original_sector_name}' ({original_sector_code}) "
                            f"无成分股或获取失败")

                except Exception as exc:  # 捕获_fetch_and_parse_constituents可能抛出的其他异常
                    logger.error(
                        f"处理板块 '{original_sector_name}' ({original_sector_code}) 的成分股映射时发生严重错误: {exc}",
                        exc_info=True)

        logger.info(f"'股票代码-{self.sector_type.value}板块'映射构建完成。总共映射了 {len(stock_to_sector_map)} 只不同的股票")
        return stock_to_sector_map

    def save_mapping_data(
            self,
            mapping_data: Dict[str, List[str]],
            filename: str = None) -> str:
        """
        将"股票代码 -> [板块代码列表]"的映射数据保存到JSON文件

        Args:
            mapping_data (Dict[str, List[str]]): 需要保存的映射字典
            filename (str): 保存的JSON文件名，如果为None则根据板块类型自动设置

        Returns:
            str: 保存文件的完整路径，如果保存失败或数据为空则返回空字符串
        """
        if not mapping_data:
            logger.warning(f"股票到{self.sector_type.value}板块的映射数据为空，不执行保存操作")
            return ""

        if filename is None:
            filename = f"stock_to_{self.sector_type.value}_map.json"
            
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=4)  # ensure_ascii=False保证中文正确显示
            logger.info(f"股票到{self.sector_type.value}板块的映射已成功保存到: {filepath}")
            return filepath
        except Exception as e:
            logger.exception(f"保存股票到{self.sector_type.value}板块映射至 {filepath} 失败")
            return ""
