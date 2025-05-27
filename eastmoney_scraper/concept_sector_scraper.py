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
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# 忽略特定类型的警告，例如在某些pandas版本中可能出现的FutureWarning
# (Ignore specific types of warnings, e.g., FutureWarning that might appear in some pandas versions)
warnings.filterwarnings('ignore', category=FutureWarning) # 更具体地忽略FutureWarning (More specifically ignore FutureWarning)
# warnings.filterwarnings('ignore') # 原来的方式会忽略所有警告 (The original way ignores all warnings)

# 获取日志记录器实例。该模块不应配置全局日志记录器，应由应用程序配置。
# (Get a logger instance. This module should not configure the global logger; it should be configured by the application.)
logger = logging.getLogger(__name__)


class ConceptSectorConfig:
    """
    概念板块爬虫配置类。
    (Configuration class for the Concept Sector Scraper.)

    存储API端点、请求头、字段映射等常量信息。
    (Stores constant information such as API endpoints, request headers, field mappings, etc.)
    """
    
    # HTTP 请求头 (HTTP Request Headers)
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/', # 东方财富行情中心作为Referer (EastMoney quote center as Referer)
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # API 接口地址 (API Endpoint URLs)
    # 概念板块行情和资金流向使用相同的基地址，通过参数区分
    # (Concept sector quotes and capital flow use the same base URL, differentiated by parameters)
    CONCEPT_QUOTE_URL = "https://push2.eastmoney.com/api/qt/clist/get"  # 用于获取概念板块行情 (For fetching concept sector quotes)
    CAPITAL_FLOW_URL = "https://push2.eastmoney.com/api/qt/clist/get"   # 用于获取资金流向数据 (For fetching capital flow data)
    # 成分股也使用 CONCEPT_QUOTE_URL，通过 'fs' 参数指定板块代码 (Constituents also use CONCEPT_QUOTE_URL, specifying sector code via 'fs' parameter)
    
    # 概念板块行情数据字段原始键名到中文名称的映射
    # (Mapping from raw field keys to Chinese names for concept sector quote data)
    QUOTE_FIELD_MAPPING = {
        'f12': '板块代码',      # Sector Code
        'f14': '板块名称',      # Sector Name
        'f2':  '最新价',        # Latest Price
        'f3':  '涨跌幅',        # Percentage Change
        'f4':  '涨跌额',        # Change Amount
        'f5':  '成交量',        # Volume (lots)
        'f6':  '成交额',        # Turnover (value)
        'f7':  '振幅',          # Amplitude
        'f15': '最高价',        # High Price
        'f16': '最低价',        # Low Price
        'f17': '开盘价',        # Open Price
        'f18': '昨收',          # Previous Close
        'f8':  '换手率',        # Turnover Rate
        'f10': '量比',          # Volume Ratio
        'f22': '涨速',          # Speed of Price Change
        'f11': '5分钟涨跌',     # 5-minute Percentage Change
        # 以下字段也可能在行情接口中直接返回，表示今日的资金流向
        # (The following fields might also be returned directly in the quote API, representing today's capital flow)
        'f62': '主力净流入',    # Main Force Net Inflow
        'f184':'主力净流入占比',# Main Force Net Inflow Percentage
        'f66': '超大单净流入',  # Super Large Order Net Inflow
        'f69': '大单净流入',    # Large Order Net Inflow
        'f72': '中单净流入',    # Medium Order Net Inflow
        'f75': '小单净流入',    # Small Order Net Inflow
        'f164':'超大单净流入占比',# Super Large Order Net Inflow Percentage
        'f165':'大单净流入占比',# Large Order Net Inflow Percentage
        'f166':'中单净流入占比',# Medium Order Net Inflow Percentage
        'f167':'小单净流入占比' # Small Order Net Inflow Percentage
    }

    # 概念板块成分股数据字段原始键名到中文名称的映射
    # (Mapping from raw field keys to Chinese names for concept sector constituent stock data)
    CONSTITUENT_FIELD_MAPPING = {
        'f12': '股票代码',      # Stock Code
        'f14': '股票名称',      # Stock Name
    }
    
    # 资金流向数据字段原始键名到中文名称的映射 (用于专门的资金流向接口)
    # (Mapping from raw field keys to Chinese names for capital flow data - for dedicated capital flow API calls)
    # 注意：部分字段与QUOTE_FIELD_MAPPING重复，但这里是针对资金流向接口的特定解析
    # (Note: Some fields overlap with QUOTE_FIELD_MAPPING, but this is for specific parsing of capital flow API responses)
    FLOW_FIELD_MAPPING = {
        'f12': '板块代码',          # Sector Code
        'f14': '板块名称',          # Sector Name
        'f3':  '涨跌幅',            # Percentage Change (often included for context)
        # 今日 (Today)
        'f62': '主力净流入',        # Main Force Net Inflow
        'f184':'主力净流入占比',    # Main Force Net Inflow Percentage
        'f66': '超大单净流入',      # Super Large Order Net Inflow
        'f69': '大单净流入',        # Large Order Net Inflow
        'f72': '中单净流入',        # Medium Order Net Inflow
        'f75': '小单净流入',        # Small Order Net Inflow
        # 5日 (5-day) - API使用不同字段代码 (API uses different field codes)
        'f267': '5日主力净流入',
        'f268': '5日主力净流入占比',
        'f269': '5日超大单净流入',
        'f270': '5日大单净流入',
        'f271': '5日中单净流入',
        'f272': '5日小单净流入',
        # 10日 (10-day) - API使用不同字段代码 (API uses different field codes)
        # 'f164' 在行情接口中可能是今日超大单占比，但在10日资金流向接口中可能代表10日主力净流入，需根据接口实际返回调整
        # ('f164' might be today's super large order percentage in quote API, but could be 10-day main force net inflow in 10-day capital flow API; adjust based on actual API response)
        # 以下为假设的10日字段，实际API可能不同，解析时需注意 (The following are assumed 10-day fields, actual API might differ, pay attention during parsing)
        # 'fXXX': '10日主力净流入',
        # 'fYYY': '10日主力净流入占比',
        # ...
        'f128': '领涨股票代码',      # Leading Stock Code
        'f140': '领涨股票名称',      # Leading Stock Name
        'f136': '领涨股票涨跌幅',    # Leading Stock Percentage Change
    }
    # 注意：东方财富的API字段 (f代码) 可能会变化，如果爬虫失效，需要检查这些映射。
    # (Note: EastMoney's API fields (f-codes) may change. If the scraper fails, these mappings need to be checked.)

class ConceptSectorFetcher:
    """
    概念板块数据获取模块。
    (Concept Sector Data Fetching Module.)

    负责从东方财富API获取原始的概念板块行情、资金流向和成分股数据。
    (Responsible for fetching raw concept sector quotes, capital flow, and constituent stock data from EastMoney APIs.)
    """
    
    def __init__(self, config: ConceptSectorConfig, pool_size: int = 50):
        """
        初始化数据获取器。
        (Initializes the data fetcher.)

        Args:
            config (ConceptSectorConfig): 配置对象。 (Configuration object.)
            pool_size (int): requests.Session连接池的大小。默认为50。
                             (Size of the requests.Session connection pool. Default is 50.)
        """
        self.config = config  # 配置实例 (Configuration instance)
        self.session = requests.Session() # 使用Session以复用TCP连接 (Use Session to reuse TCP connections)
        # 配置HTTP适配器以提高并发性能 (Configure HTTP adapter for better concurrent performance)
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self.config.HEADERS) # 设置默认请求头 (Set default request headers)
    
    def fetch_concept_quotes_page(self, page_num: int = 1, page_size: int = 100) -> Optional[Dict]:
        """
        获取单页的概念板块实时行情数据。
        (Fetches a single page of real-time concept sector quote data.)

        Args:
            page_num (int): 页码，从1开始。默认为1。
                           (Page number, starting from 1. Default is 1.)
            page_size (int): 每页返回的数据条数。默认为100。
                             (Number of data items to return per page. Default is 100.)

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None。
                            (Dictionary containing JSON data from the API response, or None if the request fails.)
        """
        try:
            # API请求参数 (API request parameters)
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}', # JSONP回调函数名，可以动态生成 (JSONP callback name, can be dynamically generated)
                'fid': 'f3',  # 按涨跌幅排序 (Sort by percentage change)
                'po': '1',    # 排序方式，1为降序 (Sort order, 1 for descending)
                'pz': str(page_size), # 每页数量 (Page size)
                'pn': str(page_num),  # 当前页码 (Current page number)
                'np': '1',    # 固定参数 (Fixed parameter)
                'fltt': '2',  # 固定参数 (Fixed parameter)
                'invt': '2',  # 固定参数 (Fixed parameter)
                'ut': 'b2884a393a59ad64002292a3e90d46a5', # 用户令牌或标识，可能固定 (User token or identifier, possibly fixed)
                'fs': 'm:90+t:3',  # 筛选条件：m:90表示概念板块 (Filter condition: m:90 means concept sectors)
                'fields': ','.join(self.config.QUOTE_FIELD_MAPPING.keys()) # 请求的字段列表 (List of requested fields)
            }
            
            response = self.session.get(
                self.config.CONCEPT_QUOTE_URL,
                params=params,
                timeout=10 # 请求超时时间（秒）(Request timeout in seconds)
            )
            response.raise_for_status() # 如果HTTP请求返回了失败状态码，则抛出HTTPError异常 (Raise HTTPError for bad responses (4xx or 5xx))
            
            # 处理JSONP响应格式 (Process JSONP response format)
            content = response.text
            # 寻找JSONP回调函数包裹的JSON数据部分 (Find the JSON data part wrapped by the JSONP callback)
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')
            
            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1 : json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(f"解析概念板块行情JSONP响应失败 (页 {page_num}): 无法找到有效的JSON数据。响应内容: {content[:200]}...")
                # (Failed to parse concept sector quote JSONP response (page {page_num}): Cannot find valid JSON data. Response content: ...)
                return None
            
        except requests.exceptions.RequestException as e: # 更具体的网络请求异常 (More specific network request exception)
            logger.error(f"获取概念板块行情网络请求失败 (页 {page_num}): {e}")
            # (Failed to fetch concept sector quotes due to network error (page {page_num}): {e})
            return None
        except json.JSONDecodeError as e: # JSON解析异常 (JSON parsing exception)
            logger.error(f"解析概念板块行情JSON数据失败 (页 {page_num}): {e}. 响应内容: {response.text[:200]}...")
            # (Failed to parse concept sector quote JSON data (page {page_num}): {e}. Response content: ...)
            return None
        except Exception as e: # 其他未知异常 (Other unknown exceptions)
            logger.error(f"获取概念板块行情时发生未知错误 (页 {page_num}): {e}")
            # (An unknown error occurred while fetching concept sector quotes (page {page_num}): {e})
            return None
    
    def fetch_concept_quotes(self) -> List[Dict]:
        """
        获取所有概念板块的实时行情数据（自动处理分页，并行获取）。
        (Fetches real-time quote data for all concept sectors, handling pagination automatically and fetching in parallel.)

        Returns:
            List[Dict]: 包含所有板块原始行情数据的列表。
                        (List containing raw quote data for all sectors.)
        """
        all_raw_quotes_data = [] # 用于存储所有原始行情数据 (To store all raw quote data)
        
        # 首先获取第一页数据，以确定总记录数和总页数
        # (First, fetch the first page to determine the total number of records and pages)
        page_size_for_total_count = 100 # API通常每页最多返回100条 (API usually returns max 100 items per page)
        first_page_response = self.fetch_concept_quotes_page(page_num=1, page_size=page_size_for_total_count)
        
        if not first_page_response or 'data' not in first_page_response or not first_page_response['data']:
            logger.warning("获取概念板块行情第一页数据失败或数据为空，无法继续获取。")
            # (Failed to fetch first page of concept sector quotes or data is empty, cannot proceed.)
            return all_raw_quotes_data
        
        total_records = first_page_response['data'].get('total', 0)
        if total_records == 0:
            logger.info("概念板块总数为0，无需进一步获取。")
            # (Total number of concept sectors is 0, no further fetching needed.)
            if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
                 all_raw_quotes_data.extend(first_page_response['data']['diff']) # 仍然添加第一页可能存在的少量数据 (Still add any few items that might be on the first page)
            return all_raw_quotes_data

        total_pages = (total_records + page_size_for_total_count - 1) // page_size_for_total_count
        
        logger.info(f"概念板块总数: {total_records}, 每页大小: {page_size_for_total_count}, 总页数: {total_pages}。")
        # (Total concept sectors: {total_records}, page size: {page_size_for_total_count}, total pages: {total_pages}.)
        
        # 添加第一页的数据到结果列表
        # (Add data from the first page to the result list)
        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_quotes_data.extend(first_page_response['data']['diff'])
        
        # 如果总页数大于1，则并行获取剩余页面的数据
        # (If total pages > 1, fetch remaining pages in parallel)
        if total_pages > 1:
            # 使用线程池并行处理分页请求 (Use ThreadPoolExecutor for parallel page requests)
            # max_workers可以根据网络情况调整 (max_workers can be adjusted based on network conditions)
            with ThreadPoolExecutor(max_workers=min(10, total_pages -1)) as executor: # 限制最大线程数 (Limit max workers)
                # 创建任务列表 (Create a list of tasks)
                futures_map = {
                    executor.submit(self.fetch_concept_quotes_page, page_num, page_size_for_total_count): page_num
                    for page_num in range(2, total_pages + 1) # 从第二页开始 (Start from page 2)
                }
                
                # 按完成顺序处理结果 (Process results as they complete)
                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_quotes_data.extend(page_data['data']['diff'])
                        else:
                            logger.warning(f"获取概念板块行情第 {page_num_completed} 页数据失败或数据不完整。")
                            # (Failed to fetch page {page_num_completed} of concept sector quotes or data is incomplete.)
                    except Exception as e:
                        logger.error(f"处理概念板块行情第 {page_num_completed} 页结果时发生错误: {e}")
                        # (Error processing result for page {page_num_completed} of concept sector quotes: {e})
        
        logger.info(f"成功获取 {len(all_raw_quotes_data)} 条原始概念板块行情数据。")
        # (Successfully fetched {len(all_raw_quotes_data)} raw concept sector quote data items.)
        return all_raw_quotes_data
    
    def fetch_capital_flow_page(self, period: str = 'today', page_num: int = 1, page_size: int = 100) -> Optional[Dict]:
        """
        获取单页的概念板块资金流向数据。
        (Fetches a single page of concept sector capital flow data.)
        
        Args:
            period (str): 时间周期，可选 'today' (今日), '5day' (5日), '10day' (10日)。默认为 'today'。
                          (Time period, options: 'today', '5day', '10day'. Default is 'today'.)
            page_num (int): 页码，从1开始。默认为1。
                           (Page number, starting from 1. Default is 1.)
            page_size (int): 每页返回的数据条数。默认为100。
                             (Number of data items to return per page. Default is 100.)

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None。
                            (Dictionary containing JSON data from the API response, or None if the request fails.)
        """
        try:
            # 根据不同的资金流向周期，API可能使用不同的'fid'参数进行排序或筛选
            # (API might use different 'fid' parameters for sorting or filtering based on capital flow period)
            # 注意：这里的字段映射可能需要根据实际API行为调整
            # (Note: Field mapping here might need adjustment based on actual API behavior)
            period_sort_field_map = {
                'today': 'f62',    # 今日主力净流入 (Today's main force net inflow)
                '5day': 'f267',    # 5日主力净流入 (5-day main force net inflow) - 假设的字段 (Assumed field)
                '10day': 'f164'    # 10日主力净流入 - 假设的字段，也可能是其他 (10-day main force net inflow - assumed field, could be others)
                                   # 东方财富API中，不同周期的资金流向字段代码可能不同，需要实际抓包确认
                                   # (In EastMoney API, field codes for different capital flow periods might vary, need to confirm via network sniffing)
            }
            
            # 构造请求参数 (Construct request parameters)
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',
                'fid': period_sort_field_map.get(period, 'f62'), # 根据周期选择排序字段 (Select sort field based on period)
                'po': '1', # 降序 (Descending order)
                'pz': str(page_size),
                'pn': str(page_num),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5', # 固定token (Fixed token)
                'fs': 'm:90+t:3',  # 概念板块 (Concept sectors)
                # 请求所有可能的资金流向相关字段，解析时再根据周期选择
                # (Request all possible capital flow related fields, select based on period during parsing)
                'fields': 'f12,f14,f3,f62,f184,f66,f69,f72,f75,f164,f165,f166,f167,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f128,f140,f136'
            }
            
            response = self.session.get(
                self.config.CAPITAL_FLOW_URL, # 使用资金流向URL (Use capital flow URL)
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            content = response.text
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')
            
            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1 : json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(f"解析概念板块资金流向JSONP响应失败 ({period}, 页 {page_num}): 无法找到JSON。响应: {content[:200]}...")
                # (Failed to parse concept sector capital flow JSONP response ({period}, page {page_num}): Cannot find JSON. Response: ...)
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取概念板块资金流向网络请求失败 ({period}, 页 {page_num}): {e}")
            # (Failed to fetch concept sector capital flow due to network error ({period}, page {page_num}): {e})
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析概念板块资金流向JSON数据失败 ({period}, 页 {page_num}): {e}. 响应: {response.text[:200]}...")
            # (Failed to parse concept sector capital flow JSON data ({period}, page {page_num}): {e}. Response: ...)
            return None
        except Exception as e:
            logger.error(f"获取概念板块资金流向时发生未知错误 ({period}, 页 {page_num}): {e}")
            # (An unknown error occurred while fetching concept sector capital flow ({period}, page {page_num}): {e})
            return None
    
    def fetch_capital_flow(self, period: str = 'today') -> List[Dict]:
        """
        获取指定周期的所有概念板块资金流向数据（自动处理分页，并行获取）。
        (Fetches capital flow data for all concept sectors for a specified period, handling pagination and fetching in parallel.)
        
        Args:
            period (str): 时间周期，可选 'today', '5day', '10day'。默认为 'today'。
                          (Time period, options: 'today', '5day', '10day'. Default is 'today'.)
        Returns:
            List[Dict]: 包含所有板块原始资金流向数据的列表。
                        (List containing raw capital flow data for all sectors.)
        """
        all_raw_flow_data = [] # 存储所有原始资金流数据 (Store all raw capital flow data)
        
        page_size_for_total_count = 100
        first_page_response = self.fetch_capital_flow_page(period=period, page_num=1, page_size=page_size_for_total_count)
        
        if not first_page_response or 'data' not in first_page_response or not first_page_response['data']:
            logger.warning(f"获取概念板块 {period} 资金流向第一页数据失败或数据为空。")
            # (Failed to fetch first page of concept sector {period} capital flow or data is empty.)
            return all_raw_flow_data
        
        total_records = first_page_response['data'].get('total', 0)
        if total_records == 0:
            logger.info(f"概念板块 {period} 资金流向总数为0。")
            # (Total number of concept sector {period} capital flow is 0.)
            if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
                all_raw_flow_data.extend(first_page_response['data']['diff'])
            return all_raw_flow_data

        total_pages = (total_records + page_size_for_total_count - 1) // page_size_for_total_count
        
        logger.info(f"概念板块 {period} 资金流向总数: {total_records}, 每页大小: {page_size_for_total_count}, 总页数: {total_pages}。")
        # (Total concept sector {period} capital flow: {total_records}, page size: {page_size_for_total_count}, total pages: {total_pages}.)
        
        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_flow_data.extend(first_page_response['data']['diff'])
        
        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=min(10, total_pages - 1)) as executor:
                futures_map = {
                    executor.submit(self.fetch_capital_flow_page, period, page_num, page_size_for_total_count): page_num
                    for page_num in range(2, total_pages + 1)
                }
                
                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_flow_data.extend(page_data['data']['diff'])
                        else:
                            logger.warning(f"获取概念板块 {period} 资金流向第 {page_num_completed} 页数据失败或不完整。")
                            # (Failed to fetch page {page_num_completed} of concept sector {period} capital flow or data is incomplete.)
                    except Exception as e:
                        logger.error(f"处理概念板块 {period} 资金流向第 {page_num_completed} 页结果时发生错误: {e}")
                        # (Error processing result for page {page_num_completed} of concept sector {period} capital flow: {e})
        
        logger.info(f"成功获取 {len(all_raw_flow_data)} 条原始概念板块 {period} 资金流向数据。")
        # (Successfully fetched {len(all_raw_flow_data)} raw concept sector {period} capital flow data items.)
        return all_raw_flow_data

    def fetch_sector_constituents_page(self, sector_code: str, page_num: int = 1, page_size: int = 200) -> Optional[Dict]:
        """
        获取指定概念板块的单页成分股数据。
        (Fetches a single page of constituent stock data for a specified concept sector.)

        Args:
            sector_code (str): 板块代码 (例如 "BK0715")。 (Sector code (e.g., "BK0715").)
            page_num (int): 页码，从1开始。默认为1。 (Page number, starting from 1. Default is 1.)
            page_size (int): 每页返回的数据条数。API对成分股列表似乎有每页100条的限制，即使设置更大。默认为200以尝试获取更多，但实际可能较少。
                             (Number of data items per page. API seems to have a limit of 100 per page for constituents, even if set higher. Default is 200 to try for more, but actual might be less.)

        Returns:
            Optional[Dict]: 包含API返回的JSON数据的字典，如果请求失败则为None。
                            (Dictionary containing JSON data from the API response, or None if the request fails.)
        """
        try:
            params = {
                'cb': f'jQuery_jsonp_callback_{int(time.time() * 1000)}',
                'fid': 'f3',  # 排序字段，对于成分股列表可能不重要 (Sort field, might not be important for constituent list)
                'po': '1',    # 排序方式 (Sort order)
                'pz': str(page_size), # 尝试请求的页面大小 (Attempted page size)
                'pn': str(page_num),
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'ut': 'b2884a393a59ad64002292a3e90d46a5',
                'fs': f'b:{sector_code}+f:!50',  # 关键参数：'b:{板块代码}' 用于指定板块 (Key parameter: 'b:{sector_code}' to specify sector)
                'fields': ','.join(self.config.CONSTITUENT_FIELD_MAPPING.keys()) # 通常只需要股票代码和名称 (Usually only stock code and name are needed)
            }
            
            response = self.session.get(
                self.config.CONCEPT_QUOTE_URL, # 成分股列表也通过此URL获取 (Constituent list is also fetched via this URL)
                params=params,
                timeout=15 # 成分股列表可能较大，增加超时 (Constituent list might be large, increase timeout)
            )
            response.raise_for_status()
            
            content = response.text
            json_start_index = content.find('(')
            json_end_index = content.rfind(')')
            
            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                json_str = content[json_start_index + 1 : json_end_index]
                json_data = json.loads(json_str)
                return json_data
            else:
                logger.error(f"解析板块 {sector_code} 成分股JSONP响应失败 (页 {page_num}): 无法找到JSON。响应: {content[:200]}...")
                # (Failed to parse sector {sector_code} constituent JSONP response (page {page_num}): Cannot find JSON. Response: ...)
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取板块 {sector_code} 成分股网络请求失败 (页 {page_num}): {e}")
            # (Failed to fetch sector {sector_code} constituents due to network error (page {page_num}): {e})
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析板块 {sector_code} 成分股JSON数据失败 (页 {page_num}): {e}. 响应: {response.text[:200]}...")
            # (Failed to parse sector {sector_code} constituent JSON data (page {page_num}): {e}. Response: ...)
            return None
        except Exception as e:
            logger.error(f"获取板块 {sector_code} 成分股时发生未知错误 (页 {page_num}): {e}")
            # (An unknown error occurred while fetching sector {sector_code} constituents (page {page_num}): {e})
            return None

    def fetch_sector_constituents(self, sector_code: str) -> List[Dict]:
        """
        获取指定概念板块的所有成分股数据（自动处理分页，并行获取）。
        (Fetches all constituent stock data for a specified concept sector, handling pagination and fetching in parallel.)

        Args:
            sector_code (str): 板块代码 (例如 "BK0715")。 (Sector code (e.g., "BK0715").)

        Returns:
            List[Dict]: 包含该板块所有原始成分股数据的列表。
                        (List containing raw data for all constituent stocks of the sector.)
        """
        all_raw_constituents = [] # 存储所有原始成分股数据 (Store all raw constituent data)
        # API对于成分股列表似乎有每页100条的实际限制 (API seems to have an effective limit of 100 items per page for constituents)
        API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS = 100

        first_page_response = self.fetch_sector_constituents_page(
            sector_code, page_num=1, page_size=API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS
        )
        
        if not first_page_response or 'data' not in first_page_response:
            logger.warning(f"获取板块 {sector_code} 成分股第一页数据失败或数据结构异常。")
            # (Failed to fetch first page of sector {sector_code} constituents or data structure is abnormal.)
            return all_raw_constituents
        
        if not first_page_response['data']: # 'data' 字段本身可能为 null 或空对象 (The 'data' field itself might be null or an empty object)
            logger.info(f"板块 {sector_code} 成分股API返回的 'data' 字段为空，可能无成分股或板块不存在。")
            # (The 'data' field returned by API for sector {sector_code} constituents is empty, possibly no constituents or sector does not exist.)
            return all_raw_constituents

        total_records = first_page_response['data'].get('total', 0)
        
        if 'diff' in first_page_response['data'] and first_page_response['data']['diff']:
            all_raw_constituents.extend(first_page_response['data']['diff'])
        
        if total_records == 0:
            logger.info(f"板块 {sector_code} 成分股总数报告为0。已从第一页获取 {len(all_raw_constituents)} 条记录（如有）。")
            # (Total constituents for sector {sector_code} reported as 0. Fetched {len(all_raw_constituents)} records from first page (if any).)
            return all_raw_constituents

        total_pages = (total_records + API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS - 1) // API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS
        
        logger.info(f"板块 {sector_code} 成分股总数: {total_records}, "
                    f"每页有效大小: {API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS}, 总页数: {total_pages} (已获取第1页).")
        # (Sector {sector_code} total constituents: {total_records}, effective page size: {API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS}, total pages: {total_pages} (page 1 fetched).)
        
        if total_pages > 1:
            with ThreadPoolExecutor(max_workers=min(5, total_pages - 1)) as executor: # 限制单板块成分股获取的线程数 (Limit threads for fetching constituents of a single sector)
                futures_map = {
                    executor.submit(self.fetch_sector_constituents_page, sector_code, page_num, API_EFFECTIVE_PAGE_SIZE_CONSTITUENTS): page_num
                    for page_num in range(2, total_pages + 1)
                }
                
                for future in as_completed(futures_map):
                    page_num_completed = futures_map[future]
                    try:
                        page_data = future.result()
                        if page_data and 'data' in page_data and 'diff' in page_data['data'] and page_data['data']['diff']:
                            all_raw_constituents.extend(page_data['data']['diff'])
                        elif page_data and 'data' in page_data and not page_data['data'].get('diff'):
                            logger.info(f"板块 {sector_code} 成分股第 {page_num_completed} 页未返回 'diff' 数据。")
                            # (Page {page_num_completed} of sector {sector_code} constituents did not return 'diff' data.)
                        elif not page_data:
                             logger.warning(f"获取板块 {sector_code} 成分股第 {page_num_completed} 页结果为空。")
                             # (Result for page {page_num_completed} of sector {sector_code} constituents is empty.)
                    except Exception as e:
                        logger.error(f"处理板块 {sector_code} 成分股第 {page_num_completed} 页结果时发生错误: {e}")
                        # (Error processing result for page {page_num_completed} of sector {sector_code} constituents: {e})
        
        logger.info(f"成功获取板块 {sector_code} 共 {len(all_raw_constituents)} 条原始成分股数据 (解析后将去重)。")
        # (Successfully fetched {len(all_raw_constituents)} raw constituent data items for sector {sector_code} (will be deduplicated after parsing).)
        return all_raw_constituents


class ConceptSectorParser:
    """
    概念板块数据解析模块。
    (Concept Sector Data Parsing Module.)

    负责将从API获取的原始JSON数据转换为结构化的Pandas DataFrame或列表。
    (Responsible for converting raw JSON data fetched from APIs into structured Pandas DataFrames or lists.)
    """
    
    def __init__(self, config: ConceptSectorConfig):
        """
        初始化数据解析器。
        (Initializes the data parser.)

        Args:
            config (ConceptSectorConfig): 配置对象。 (Configuration object.)
        """
        self.config = config # 配置实例 (Configuration instance)
    
    def parse_concept_quotes(self, raw_quotes_list: List[Dict]) -> pd.DataFrame:
        """
        解析概念板块的实时行情原始数据列表。
        (Parses a list of raw real-time quote data for concept sectors.)

        Args:
            raw_quotes_list (List[Dict]): 从API获取的原始行情数据字典列表。
                                         (List of raw quote data dictionaries fetched from the API.)

        Returns:
            pd.DataFrame: 包含解析后行情数据的Pandas DataFrame。列名为中文。
                          (Pandas DataFrame containing parsed quote data. Column names are in Chinese.)
        """
        if not raw_quotes_list:
            logger.info("输入的原始行情数据列表为空，返回空DataFrame。")
            # (Input raw quote data list is empty, returning an empty DataFrame.)
            return pd.DataFrame()
        
        parsed_data_list = [] # 用于存储解析后的每条行情数据 (To store each parsed quote data item)
        for raw_item in raw_quotes_list:
            parsed_item = {} # 当前解析的条目 (Currently parsed item)
            for field_key, chinese_name in self.config.QUOTE_FIELD_MAPPING.items():
                raw_value = raw_item.get(field_key) # 从原始数据中获取值 (Get value from raw data)
                
                # 对特定字段进行单位转换或格式化
                # (Perform unit conversion or formatting for specific fields)
                if raw_value is None or raw_value == '-': # 处理空值或API返回的占位符 (Handle null values or API placeholders)
                    parsed_value = None # 或使用 pd.NA (or use pd.NA)
                elif '占比' in chinese_name or '换手率' in chinese_name or '涨跌幅' in chinese_name or '振幅' in chinese_name:
                    # 百分比字段，通常API直接给出数值，保留两位小数
                    # (Percentage fields, API usually gives numerical values, round to 2 decimal places)
                    try:
                        parsed_value = round(float(raw_value), 2)
                    except (ValueError, TypeError):
                        parsed_value = None # 如果转换失败 (If conversion fails)
                elif ('流入' in chinese_name and '占比' not in chinese_name) or chinese_name == '成交额':
                    # 金额字段（如主力净流入、成交额），API单位通常是元，转换为万元，保留两位小数
                    # (Monetary fields (e.g., main force net inflow, turnover), API unit is usually RMB, convert to 10,000 RMB, round to 2 decimal places)
                    try:
                        parsed_value = round(float(raw_value) / 10000, 2)
                    except (ValueError, TypeError):
                        parsed_value = None
                elif chinese_name == '成交量': # 成交量单位是“手” (Volume unit is "lots")
                     try:
                        parsed_value = int(raw_value) # 通常是整数 (Usually an integer)
                     except (ValueError, TypeError):
                        parsed_value = None
                else:
                    # 其他字段直接使用，或根据需要进行类型转换
                    # (Other fields are used directly, or type converted as needed)
                    parsed_value = raw_value
                
                parsed_item[chinese_name] = parsed_value
            
            parsed_data_list.append(parsed_item)
        
        df = pd.DataFrame(parsed_data_list)
        logger.info(f"成功解析 {len(df)} 条概念板块行情数据。")
        # (Successfully parsed {len(df)} concept sector quote data items.)
        return df
    
    def parse_capital_flow(self, raw_flow_list: List[Dict], period: str) -> pd.DataFrame:
        """
        解析概念板块的资金流向原始数据列表。
        (Parses a list of raw capital flow data for concept sectors.)

        Args:
            raw_flow_list (List[Dict]): 从API获取的原始资金流向数据字典列表。
                                        (List of raw capital flow data dictionaries fetched from the API.)
            period (str): 资金流向周期 ('today', '5day', '10day')。
                          (Capital flow period ('today', '5day', '10day').)

        Returns:
            pd.DataFrame: 包含解析后资金流向数据的Pandas DataFrame。列名包含周期前缀（如 '5日主力净流入'）。
                          (Pandas DataFrame containing parsed capital flow data. Column names include period prefix (e.g., '5日主力净流入').)
        """
        if not raw_flow_list:
            logger.info(f"输入的原始 {period} 资金流向数据列表为空，返回空DataFrame。")
            # (Input raw {period} capital flow data list is empty, returning an empty DataFrame.)
            return pd.DataFrame()
        
        parsed_data_list = [] # 用于存储解析后的每条资金流数据 (To store each parsed capital flow data item)
        # 定义列名前缀 (Define column name prefix)
        period_column_prefix = {
            'today': '',    # 今日数据列名不加前缀 (Today's data column names have no prefix)
            '5day': '5日',  # 5日数据列名前缀 (5-day data column name prefix)
            '10day': '10日' # 10日数据列名前缀 (10-day data column name prefix)
        }.get(period, '') # 默认为空字符串 (Default to empty string)
        
        for raw_item in raw_flow_list:
            parsed_item = {
                '板块代码': raw_item.get('f12'), # Sector Code
                '板块名称': raw_item.get('f14'), # Sector Name
            }
            
            # 根据不同周期，API返回的原始字段代码 (f代码) 可能不同
            # (Raw field codes (f-codes) from API may differ for different periods)
            # 需要仔细核对API文档或抓包结果来确定正确的f代码
            # (Need to carefully check API documentation or network sniffing results for correct f-codes)
            
            # 定义各周期对应的原始字段名 (Define raw field names for each period)
            # 注意：这些字段名是API返回的原始f代码，不是FLOW_FIELD_MAPPING中的中文名
            # (Note: These field names are raw f-codes from API, not Chinese names from FLOW_FIELD_MAPPING)
            # 确保这些f代码与ConceptSectorFetcher中请求的fields参数一致或为其子集
            # (Ensure these f-codes are consistent with or a subset of the 'fields' parameter requested in ConceptSectorFetcher)
            
            # 统一处理金额和占比的函数 (Unified function to process amount and percentage)
            def get_value(f_code_amount, f_code_percent=None, is_amount=True):
                amount_val = raw_item.get(f_code_amount)
                percent_val = raw_item.get(f_code_percent) if f_code_percent else None
                
                parsed_amount = None
                if amount_val is not None and amount_val != '-':
                    try:
                        # 金额转万元，占比或其他数值直接转float (Amount to 10k RMB, percentage or other numerics directly to float)
                        parsed_amount = round(float(amount_val) / 10000, 2) if is_amount else round(float(amount_val), 2)
                    except (ValueError, TypeError):
                        pass #保持None (Keep None)
                
                parsed_percent = None # 占比字段独立处理 (Percentage field handled separately if it exists)
                if f_code_percent and percent_val is not None and percent_val != '-':
                    try:
                        parsed_percent = round(float(percent_val), 2)
                    except (ValueError, TypeError):
                        pass #保持None (Keep None)
                return parsed_amount, parsed_percent

            if period == 'today':
                # 今日资金流向字段 (Today's capital flow fields)
                # (f62: 主力净流入, f184: 主力净流入占比, f66: 超大单, f69: 大单, f72: 中单, f75: 小单)
                parsed_item[f'{period_column_prefix}主力净流入'], parsed_item[f'{period_column_prefix}主力净流入占比'] = get_value('f62', 'f184')
                parsed_item[f'{period_column_prefix}超大单净流入'], _ = get_value('f66', is_amount=True) # 明确是金额 (Explicitly amount)
                parsed_item[f'{period_column_prefix}大单净流入'], _ = get_value('f69', is_amount=True)
                parsed_item[f'{period_column_prefix}中单净流入'], _ = get_value('f72', is_amount=True)
                parsed_item[f'{period_column_prefix}小单净流入'], _ = get_value('f75', is_amount=True)
            elif period == '5day':
                # 5日资金流向字段 (5-day capital flow fields)
                # (f267: 5日主力净流入, f268: 5日主力净流入占比, f269: 5日超大单, etc.)
                parsed_item[f'{period_column_prefix}主力净流入'], parsed_item[f'{period_column_prefix}主力净流入占比'] = get_value('f267', 'f268')
                parsed_item[f'{period_column_prefix}超大单净流入'], _ = get_value('f269', is_amount=True)
                parsed_item[f'{period_column_prefix}大单净流入'], _ = get_value('f270', is_amount=True)
                parsed_item[f'{period_column_prefix}中单净流入'], _ = get_value('f271', is_amount=True)
                parsed_item[f'{period_column_prefix}小单净流入'], _ = get_value('f272', is_amount=True)
            elif period == '10day':
                # 10日资金流向字段 (10-day capital flow fields)
                # 警告: 10日资金流向的f代码在Config中未明确定义，这里的f代码是基于之前代码的推测，极可能不准确。
                # (Warning: f-codes for 10-day capital flow are not explicitly defined in Config. f-codes here are guesses and highly likely inaccurate.)
                # 需要根据实际API返回调整。例如，东方财富网站上10日主力净流入的字段可能是 'f164' (与今日超大单净流入占比的f代码相同，但含义不同)
                # (Needs adjustment based on actual API response. For example, on EastMoney website, 10-day main force net inflow might be 'f164' (same f-code as today's super large order net inflow percentage, but different meaning))
                # 假设10日主力净流入占比是 'f174' (这是一个纯粹的假设，需要验证)
                # (Assuming 10-day main force net inflow percentage is 'f174' (this is a pure assumption, needs verification))
                logger.warning("10日资金流向的原始字段代码 (例如 f164, f174等) 是基于推测，可能不准确。请核实API。")
                # (Raw field codes for 10-day capital flow (e.g., f164, f174, etc.) are speculative and may be inaccurate. Please verify API.)
                parsed_item[f'{period_column_prefix}主力净流入'], parsed_item[f'{period_column_prefix}主力净流入占比'] = get_value('f164', 'f174') # f164 for 10d 主力净流入, f174 for 10d 主力净流入占比 (假设)
                parsed_item[f'{period_column_prefix}超大单净流入'], _ = get_value('f165', is_amount=True) # 假设 (Assumption)
                parsed_item[f'{period_column_prefix}大单净流入'], _ = get_value('f166', is_amount=True) # 假设 (Assumption)
                parsed_item[f'{period_column_prefix}中单净流入'], _ = get_value('f167', is_amount=True) # 假设 (Assumption)
                parsed_item[f'{period_column_prefix}小单净流入'], _ = get_value('f168', is_amount=True) # 假设 (Assumption)
            
            parsed_data_list.append(parsed_item)
        
        df = pd.DataFrame(parsed_data_list)
        logger.info(f"成功解析 {len(df)} 条概念板块 {period} 资金流向数据。")
        # (Successfully parsed {len(df)} concept sector {period} capital flow data items.)
        return df

    def parse_sector_constituents(self, raw_constituents_list: List[Dict]) -> List[str]:
        """
        解析概念板块的成分股原始数据列表，提取股票代码。
        (Parses a list of raw constituent stock data for concept sectors, extracting stock codes.)

        Args:
            raw_constituents_list (List[Dict]): 从API获取的原始成分股数据字典列表。
                                               (List of raw constituent stock data dictionaries fetched from the API.)

        Returns:
            List[str]: 去重后的股票代码列表。
                       (Deduplicated list of stock codes.)
        """
        if not raw_constituents_list:
            logger.info("输入的原始成分股数据列表为空，返回空列表。")
            # (Input raw constituent data list is empty, returning an empty list.)
            return []
        
        stock_codes_list = [] # 用于存储提取的股票代码 (To store extracted stock codes)
        
        # 从配置中获取“股票代码”对应的原始字段键名
        # (Get the raw field key corresponding to "股票代码" (Stock Code) from config)
        stock_code_field_key = None
        for key, chinese_name in self.config.CONSTITUENT_FIELD_MAPPING.items():
            if chinese_name == '股票代码':
                stock_code_field_key = key
                break
        
        if not stock_code_field_key:
            logger.error("在 CONSTITUENT_FIELD_MAPPING 配置中未找到 '股票代码' 的映射键。无法解析成分股。")
            # (Mapping key for '股票代码' not found in CONSTITUENT_FIELD_MAPPING config. Cannot parse constituents.)
            return []

        for raw_item in raw_constituents_list:
            stock_code = raw_item.get(stock_code_field_key)
            if stock_code: # 确保股票代码存在且不为空 (Ensure stock code exists and is not empty)
                stock_codes_list.append(str(stock_code)) # 统一转换为字符串 (Convert to string for consistency)
        
        # 去重并返回 (Deduplicate and return)
        unique_stock_codes = sorted(list(set(stock_codes_list))) # 排序使结果可预测 (Sort for predictable results)
        logger.info(f"成功解析出 {len(unique_stock_codes)} 个唯一的成分股代码 (原始数量: {len(stock_codes_list)})。")
        # (Successfully parsed {len(unique_stock_codes)} unique constituent stock codes (raw count: {len(stock_codes_list)}).)
        return unique_stock_codes


class ConceptSectorScraper:
    """
    概念板块爬虫主类。
    (Main class for the Concept Sector Scraper.)

    集成数据获取 (Fetcher)、数据解析 (Parser) 和数据存储功能，
    提供一次性爬取、定时爬取以及板块成分股映射等功能。
    (Integrates data fetching, parsing, and storage functionalities.
     Provides features like one-time scraping, scheduled scraping, and sector-to-constituent mapping.)
    """
    
    def __init__(self, output_dir: str = "concept_sector_data"):
        """
        初始化概念板块爬虫。
        (Initializes the Concept Sector Scraper.)

        Args:
            output_dir (str): 数据输出目录。默认为 "concept_sector_data"。
                              (Output directory for data. Default is "concept_sector_data".)
        """
        self.config = ConceptSectorConfig() # 加载配置 (Load configuration)
        self.fetcher = ConceptSectorFetcher(self.config) # 初始化数据获取器 (Initialize data fetcher)
        self.parser = ConceptSectorParser(self.config)   # 初始化数据解析器 (Initialize data parser)
        self.output_dir = output_dir # 设置输出目录 (Set output directory)
        self.is_running = False      # 爬虫运行状态标志 (Scraper running state flag)
        os.makedirs(self.output_dir, exist_ok=True) # 创建输出目录 (如果不存在) (Create output directory if it doesn't exist)
    
    def scrape_all_data(self) -> pd.DataFrame:
        """
        爬取所有概念板块的实时行情和多周期资金流向数据，并合并成一个DataFrame。
        (Scrapes real-time quotes and multi-period capital flow data for all concept sectors,
         and merges them into a single DataFrame.)

        Returns:
            pd.DataFrame: 包含合并后数据的Pandas DataFrame。如果出错则返回空DataFrame。
                          (Pandas DataFrame containing the merged data. Returns an empty DataFrame on error.)
        """
        try:
            logger.info("开始爬取概念板块综合数据（行情与资金流）...")
            # (Starting to scrape comprehensive concept sector data (quotes and capital flow)...)
            
            # 1. 获取实时行情数据 (Fetch real-time quote data)
            logger.info("步骤1: 获取实时行情数据...")
            # (Step 1: Fetching real-time quote data...)
            raw_quotes_list = self.fetcher.fetch_concept_quotes()
            df_quotes = self.parser.parse_concept_quotes(raw_quotes_list)
            
            if df_quotes.empty:
                logger.error("未能获取实时行情数据，操作中止。")
                # (Failed to fetch real-time quote data, operation aborted.)
                return pd.DataFrame()
            
            # 2. 并发获取各周期资金流向数据 (Concurrently fetch capital flow data for various periods)
            logger.info("步骤2: 并发获取各周期资金流向数据 (今日, 5日, 10日)...")
            # (Step 2: Concurrently fetching capital flow data for various periods (today, 5-day, 10-day)...)
            with ThreadPoolExecutor(max_workers=3) as executor: # 3个周期，3个线程 (3 periods, 3 threads)
                future_flow_today = executor.submit(self.fetcher.fetch_capital_flow, 'today')
                future_flow_5day = executor.submit(self.fetcher.fetch_capital_flow, '5day')
                future_flow_10day = executor.submit(self.fetcher.fetch_capital_flow, '10day')
                
                raw_flow_today_list = future_flow_today.result()
                raw_flow_5day_list = future_flow_5day.result()
                raw_flow_10day_list = future_flow_10day.result()
            
            # 解析资金流向数据 (Parse capital flow data)
            df_flow_today = self.parser.parse_capital_flow(raw_flow_today_list, 'today')
            df_flow_5day = self.parser.parse_capital_flow(raw_flow_5day_list, '5day')
            df_flow_10day = self.parser.parse_capital_flow(raw_flow_10day_list, '10day')
            
            # 3. 合并所有数据 (Merge all data)
            logger.info("步骤3: 合并行情与资金流数据...")
            # (Step 3: Merging quote and capital flow data...)
            df_merged = df_quotes.copy() # 从行情数据开始 (Start with quote data)
            
            # 合并今日资金流向 (Merge today's capital flow)
            # 注意：行情数据本身可能已包含今日资金流，这里用专门的资金流接口数据进行合并或更新
            # (Note: Quote data itself might contain today's flow; here we merge/update with dedicated flow API data)
            # 为避免列名冲突，可以考虑在parse_capital_flow中对 '主力净流入' 等基础字段名前不加 '今日' 前缀
            # (To avoid column name conflicts, consider not adding '今日' prefix to base field names like '主力净流入' in parse_capital_flow for 'today')
            # 或者在合并时指定suffixes，但目前parse_capital_flow对'today'不加前缀，所以直接合并。
            # (Or specify suffixes during merge. Currently, parse_capital_flow adds no prefix for 'today', so direct merge is fine.)
            if not df_flow_today.empty:
                # 选择要合并的列，避免重复板块名称等 (Select columns to merge, avoid duplicate sector names etc.)
                cols_to_merge_today = [col for col in df_flow_today.columns if col not in ['板块名称']]
                df_merged = pd.merge(df_merged, df_flow_today[cols_to_merge_today], on='板块代码', how='left')
            
            # 合并5日资金流向 (Merge 5-day capital flow)
            if not df_flow_5day.empty:
                cols_to_merge_5day = [col for col in df_flow_5day.columns if col not in ['板块名称']]
                df_merged = pd.merge(df_merged, df_flow_5day[cols_to_merge_5day], on='板块代码', how='left')
            
            # 合并10日资金流向 (Merge 10-day capital flow)
            if not df_flow_10day.empty:
                cols_to_merge_10day = [col for col in df_flow_10day.columns if col not in ['板块名称']]
                df_merged = pd.merge(df_merged, df_flow_10day[cols_to_merge_10day], on='板块代码', how='left')
            
            # 添加更新时间戳 (Add update timestamp)
            df_merged['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 按涨跌幅降序排序 (Sort by percentage change in descending order)
            if '涨跌幅' in df_merged.columns:
                df_merged = df_merged.sort_values('涨跌幅', ascending=False).reset_index(drop=True)
            
            logger.info(f"成功获取并合并 {len(df_merged)} 个概念板块的综合数据。")
            # (Successfully fetched and merged comprehensive data for {len(df_merged)} concept sectors.)
            
            return df_merged
            
        except Exception as e:
            logger.exception("爬取并合并所有数据时发生严重错误。") # 使用 logger.exception 记录堆栈信息 (Use logger.exception to record stack trace)
            # (A critical error occurred while scraping and merging all data.)
            return pd.DataFrame() # 返回空DataFrame表示失败 (Return empty DataFrame to indicate failure)
    
    def save_data(self, df: pd.DataFrame, filename_prefix: str = "concept_sectors") -> str:
        """
        将DataFrame数据保存到CSV文件。
        (Saves DataFrame data to a CSV file.)

        同时保存带时间戳的文件和一份名为 '..._latest.csv' 的最新文件。
        (Saves both a timestamped file and a latest file named '..._latest.csv'.)

        Args:
            df (pd.DataFrame): 需要保存的DataFrame。 (DataFrame to save.)
            filename_prefix (str): 文件名前缀。默认为 "concept_sectors"。
                                   (Filename prefix. Default is "concept_sectors".)

        Returns:
            str: 带时间戳的文件的完整路径。如果保存失败则返回空字符串。
                 (Full path of the timestamped file. Returns an empty string if saving fails.)
        """
        if df.empty:
            logger.warning("输入数据为空，不执行保存操作。")
            # (Input data is empty, skipping save operation.)
            return ""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamped_filename = f"{filename_prefix}_{timestamp}.csv"
            timestamped_filepath = os.path.join(self.output_dir, timestamped_filename)
            
            df.to_csv(timestamped_filepath, index=False, encoding='utf-8-sig') # utf-8-sig 确保Excel正确显示中文 (utf-8-sig ensures Excel displays Chinese correctly)
            logger.info(f"数据已保存到: {timestamped_filepath}")
            # (Data saved to: {timestamped_filepath})
            
            latest_filename = f"{filename_prefix}_latest.csv"
            latest_filepath = os.path.join(self.output_dir, latest_filename)
            df.to_csv(latest_filepath, index=False, encoding='utf-8-sig')
            logger.info(f"最新数据已同步到: {latest_filepath}")
            # (Latest data synchronized to: {latest_filepath})
            
            return timestamped_filepath
            
        except Exception as e:
            logger.exception(f"保存数据到CSV文件失败。文件名: {timestamped_filename if 'timestamped_filename' in locals() else filename_prefix}")
            # (Failed to save data to CSV file. Filename: ...)
            return ""
    
    def run_once(self) -> Tuple[pd.DataFrame, str]:
        """
        执行一次完整的爬取（行情和资金流）并保存数据。
        (Executes a single complete scrape (quotes and capital flow) and saves the data.)

        Returns:
            Tuple[pd.DataFrame, str]: 包含爬取数据的DataFrame和保存文件的路径。
                                      (Tuple containing the DataFrame with scraped data and the path to the saved file.)
        """
        df = self.scrape_all_data()
        saved_filepath = ""
        if not df.empty:
            saved_filepath = self.save_data(df, filename_prefix="concept_sectors_综合") # 使用特定前缀 (Use specific prefix)
        return df, saved_filepath
    
    def start_scheduled_scraping(self, interval_seconds: int = 60):
        """
        开始定时爬取概念板块综合数据。
        (Starts scheduled scraping of comprehensive concept sector data.)
        
        Args:
            interval_seconds (int): 爬取间隔时间（秒）。默认为60秒。
                                   (Scraping interval in seconds. Default is 60 seconds.)
        """
        if interval_seconds < 10:
            logger.warning(f"设置的爬取间隔 {interval_seconds}秒 过短，可能导致IP被封禁。建议至少10秒以上。")
            # (The scraping interval {interval_seconds}s is too short and may lead to IP ban. Recommend at least 10 seconds.)
        self.is_running = True
        logger.info(f"启动定时爬取任务，每 {interval_seconds} 秒更新一次概念板块综合数据。")
        # (Starting scheduled scraping task, updating comprehensive concept sector data every {interval_seconds} seconds.)
        
        while self.is_running:
            try:
                logger.info(f"执行定时爬取 (间隔: {interval_seconds}s)...")
                # (Executing scheduled scrape (interval: {interval_seconds}s)...)
                df, filepath = self.run_once()
                
                if not df.empty and filepath:
                    logger.info(f"定时爬取完成，数据已保存到 {filepath}。")
                    # (Scheduled scrape completed, data saved to {filepath}.)
                    # 可以在这里添加回调函数或进一步处理逻辑 (Callback function or further processing logic can be added here)
                    # 例如，打印部分数据到控制台 (For example, print some data to console)
                    print(f"\n--- 定时更新 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                    display_columns = ['板块名称', '涨跌幅', '最新价', '主力净流入', '5日主力净流入']
                    available_columns = [col for col in display_columns if col in df.columns]
                    print(df[available_columns].head(5).to_string(index=False))
                    print("--- 更新结束 ---\n")
                else:
                    logger.warning("定时爬取未获取到数据或保存失败。")
                    # (Scheduled scrape did not fetch data or save failed.)
                
                # 等待指定间隔时间 (Wait for the specified interval)
                # 为了能及时响应 stop() 方法，可以将长sleep拆分为短sleep循环检查 is_running
                # (To respond to stop() method promptly, long sleep can be split into short sleep loops checking is_running)
                for _ in range(interval_seconds):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("接收到手动中断 (KeyboardInterrupt)，正在停止定时爬取...")
                # (Received manual interruption (KeyboardInterrupt), stopping scheduled scraping...)
                self.stop()
                break # 退出while循环 (Exit while loop)
            except Exception as e:
                logger.exception(f"定时爬取过程中发生未知错误，将在 {interval_seconds} 秒后重试。")
                # (An unknown error occurred during scheduled scraping, will retry after {interval_seconds} seconds.)
                time.sleep(interval_seconds) # 发生错误后也等待一段时间 (Wait for a while after an error too)
    
    def stop(self):
        """
        停止正在运行的定时爬取任务。
        (Stops the currently running scheduled scraping task.)
        """
        if self.is_running:
            self.is_running = False
            logger.info("定时爬取任务已标记为停止，将在当前循环结束后退出。")
            # (Scheduled scraping task marked as stopped, will exit after the current loop finishes.)
        else:
            logger.info("定时爬取任务未在运行。")
            # (Scheduled scraping task is not running.)

    def _fetch_and_parse_sector_constituents(self, sector_info: Dict) -> Tuple[str, List[str]]:
        """
        辅助方法：获取并解析单个概念板块的成分股。
        (Helper method: Fetches and parses constituents for a single concept sector.)

        Args:
            sector_info (Dict): 包含板块代码 ('code') 和板块名称 ('name') 的字典。
                                (Dictionary containing sector code ('code') and sector name ('name').)

        Returns:
            Tuple[str, List[str]]: 板块代码和其对应的成分股代码列表。获取失败则股票列表为空。
                                   (Tuple of (sector_code, list_of_stock_codes). Stock list is empty on failure.)
        """
        sector_code = sector_info.get('code')
        sector_name = sector_info.get('name', '未知板块') # Default name if not provided
        
        if not sector_code:
            logger.warning(f"提供的板块信息缺少板块代码: {sector_info}，跳过此板块。")
            # (Provided sector info is missing sector code: {sector_info}, skipping this sector.)
            return "", []

        # logger.debug(f"开始获取板块 '{sector_name}' ({sector_code}) 的成分股...") # 改为debug级别，避免过多日志 (Changed to debug level to avoid excessive logging)
        try:
            # 考虑移除或大幅减小这里的延时，因为外部调用者 (scrape_concept_to_stock_mapping) 使用了线程池。
            # (Consider removing or significantly reducing the delay here, as the caller (scrape_concept_to_stock_mapping) uses a ThreadPoolExecutor.)
            # time.sleep(0.05) # 较小的延时 (Slightly smaller delay)
            
            raw_constituent_data = self.fetcher.fetch_sector_constituents(sector_code)
            
            if not raw_constituent_data:
                # fetch_sector_constituents 内部已有日志记录 (fetch_sector_constituents already logs internally)
                # logger.warning(f"板块 '{sector_name}' ({sector_code}) 未获取到原始成分股数据。")
                return sector_code, []
            
            stock_codes_list = self.parser.parse_sector_constituents(raw_constituent_data)
            # parser.parse_sector_constituents 内部已有日志记录 (parser.parse_sector_constituents already logs internally)
            # logger.debug(f"板块 '{sector_name}' ({sector_code}) 解析出 {len(stock_codes_list)} 个成分股。")
            return sector_code, stock_codes_list
        except Exception as e:
            logger.exception(f"处理板块 '{sector_name}' ({sector_code}) 成分股时发生内部错误。")
            # (An internal error occurred while processing constituents for sector '{sector_name}' ({sector_code}).)
            return sector_code, [] # 确保在异常情况下也返回符合类型的空结果 (Ensure returning type-consistent empty result on exception)

    def scrape_concept_to_stock_mapping(self, max_workers: int = 10) -> Dict[str, List[str]]:
        """
        爬取所有概念板块及其成分股，生成 “股票代码 -> [概念板块代码列表]” 的映射。
        (Scrapes all concept sectors and their constituents to generate a mapping of "stock_code -> [list_of_concept_sector_codes]".)
        
        此方法会并行获取各个板块的成分股。
        (This method fetches constituents for each sector in parallel.)

        Args:
            max_workers (int): 用于并行获取成分股的最大线程数。默认为10。
                               (Maximum number of threads for parallel fetching of constituents. Default is 10.)

        Returns:
            Dict[str, List[str]]: 股票代码到其所属概念板块代码列表的映射字典。
                                  (Dictionary mapping stock codes to a list of their associated concept sector codes.)
        """
        logger.info(f"开始构建“股票代码-概念板块”映射 (最大并行数: {max_workers})...")
        # (Starting to build "stock_code-concept_sector" mapping (max parallelism: {max_workers})...)
        stock_to_concept_map: Dict[str, List[str]] = {} # 初始化结果字典 (Initialize result dictionary)

        # 1. 获取所有概念板块的基础信息 (代码和名称)
        # (Fetch basic info (code and name) for all concept sectors)
        logger.info("步骤1: 获取所有概念板块列表...")
        # (Step 1: Fetching list of all concept sectors...)
        raw_concept_sectors = self.fetcher.fetch_concept_quotes() # 行情接口也返回板块列表 (Quote API also returns sector list)
        if not raw_concept_sectors:
            logger.error("未能获取概念板块列表，无法构建映射。")
            # (Failed to fetch concept sector list, cannot build mapping.)
            return stock_to_concept_map
        
        # 提取板块代码和名称 (Extract sector codes and names)
        concept_sectors_to_process = [
            {'code': sector_data.get('f12'), 'name': sector_data.get('f14')}
            for sector_data in raw_concept_sectors
            if sector_data.get('f12') and sector_data.get('f14') #确保代码和名称都存在 (Ensure both code and name exist)
        ]
        total_sectors_count = len(concept_sectors_to_process)
        if total_sectors_count == 0:
            logger.warning("获取到的概念板块列表为空，无法构建映射。")
            # (Fetched concept sector list is empty, cannot build mapping.)
            return stock_to_concept_map
        logger.info(f"获取到 {total_sectors_count} 个概念板块待处理。")
        # (Fetched {total_sectors_count} concept sectors to process.)

        # 2. 并行获取每个概念板块的成分股，并构建映射
        # (Concurrently fetch constituents for each concept sector and build the mapping)
        logger.info("步骤2: 并行获取各板块成分股并构建映射...")
        # (Step 2: Concurrently fetching constituents for each sector and building mapping...)
        processed_sectors_count = 0
        # 使用线程池进行并行处理 (Use ThreadPoolExecutor for parallel processing)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 创建future到板块信息的映射，方便后续处理 (Map future to sector info for easier processing later)
            future_to_sector_info_map = {
                executor.submit(self._fetch_and_parse_sector_constituents, sector_info): sector_info
                for sector_info in concept_sectors_to_process
            }
            
            for future in as_completed(future_to_sector_info_map):
                original_sector_info = future_to_sector_info_map[future]
                original_sector_code = original_sector_info['code']
                original_sector_name = original_sector_info['name']
                processed_sectors_count += 1
                progress_percent = (processed_sectors_count / total_sectors_count) * 100
                
                try:
                    # 获取该板块的成分股列表 (Get constituent list for this sector)
                    fetched_sector_code, stock_codes_in_sector = future.result()
                    
                    if fetched_sector_code != original_sector_code: # 基本校验 (Basic check)
                        logger.warning(f"处理板块 '{original_sector_name}' 时返回的板块代码 ({fetched_sector_code}) 与预期 ({original_sector_code}) 不符。")
                        # (Returned sector code ({fetched_sector_code}) does not match expected ({original_sector_code}) when processing sector '{original_sector_name}'.)
                    
                    if stock_codes_in_sector:
                        logger.info(f"({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) 板块 '{original_sector_name}' ({original_sector_code}) "
                                    f"包含 {len(stock_codes_in_sector)} 个成分股。")
                        # (({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) Sector '{original_sector_name}' ({original_sector_code}) contains {len(stock_codes_in_sector)} constituents.)
                        for stock_code in stock_codes_in_sector:
                            if stock_code not in stock_to_concept_map:
                                stock_to_concept_map[stock_code] = []
                            # 添加板块代码到股票的板块列表 (确保不重复添加)
                            # (Add sector code to the stock's list of sectors (ensure no duplicates))
                            if original_sector_code not in stock_to_concept_map[stock_code]:
                                stock_to_concept_map[stock_code].append(original_sector_code)
                    else:
                         logger.info(f"({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) 板块 '{original_sector_name}' ({original_sector_code}) "
                                     f"无成分股或获取失败。")
                         # (({processed_sectors_count}/{total_sectors_count} - {progress_percent:.1f}%) Sector '{original_sector_name}' ({original_sector_code}) has no constituents or fetch failed.)

                except Exception as exc: # 捕获 _fetch_and_parse_sector_constituents 可能抛出的其他异常 (Catch other exceptions _fetch_and_parse_sector_constituents might throw)
                    logger.error(f"处理板块 '{original_sector_name}' ({original_sector_code}) 的成分股映射时发生严重错误: {exc}", exc_info=True)
                    # (A critical error occurred while processing constituent mapping for sector '{original_sector_name}' ({original_sector_code}): {exc})
        
        logger.info(f"“股票代码-概念板块”映射构建完成。总共映射了 {len(stock_to_concept_map)} 只不同的股票。")
        # ("Stock_code-concept_sector" mapping construction completed. Total {len(stock_to_concept_map)} unique stocks mapped.)
        return stock_to_concept_map

    def save_stock_to_concept_mapping(self, mapping_data: Dict[str, List[str]], filename: str = "stock_to_concept_map.json") -> str:
        """
        将 “股票代码 -> [概念板块代码列表]” 的映射数据保存到JSON文件。
        (Saves the "stock_code -> [list_of_concept_sector_codes]" mapping data to a JSON file.)

        Args:
            mapping_data (Dict[str, List[str]]): 需要保存的映射字典。
                                                 (Mapping dictionary to save.)
            filename (str): 保存的JSON文件名。默认为 "stock_to_concept_map.json"。
                            (Filename for the saved JSON. Default is "stock_to_concept_map.json".)

        Returns:
            str: 保存文件的完整路径。如果保存失败或数据为空则返回空字符串。
                 (Full path of the saved file. Returns an empty string if saving fails or data is empty.)
        """
        if not mapping_data:
            logger.warning("股票到概念板块的映射数据为空，不执行保存操作。")
            # (Stock-to-concept mapping data is empty, skipping save operation.)
            return ""
            
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=4) # ensure_ascii=False 保证中文正确显示 (ensure_ascii=False ensures Chinese displays correctly)
            logger.info(f"股票到概念板块的映射已成功保存到: {filepath}")
            # (Stock-to-concept mapping successfully saved to: {filepath})
            return filepath
        except Exception as e:
            logger.exception(f"保存股票到概念板块映射至 {filepath} 失败。")
            # (Failed to save stock-to-concept mapping to {filepath}.)
            return ""

# 主程序入口 (Main program entry point)
# 当此脚本作为主程序直接运行时，以下代码块将被执行。
# (When this script is run directly as the main program, the following code block will be executed.)
if __name__ == '__main__':
    
    # 配置基本的日志输出格式，方便直接运行脚本时查看日志
    # (Configure basic logging format for easy viewing when running the script directly)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('concept_sector_scraper_direct_run.log', encoding='utf-8'), # 保存到文件 (Save to file)
            logging.StreamHandler() # 输出到控制台 (Output to console)
        ]
    )
    main_logger = logging.getLogger(__name__) # 获取当前模块的logger (Get logger for the current module)

    def run_market_and_flow_scraper_once():
        """
        运行一次概念板块行情和资金流爬虫，并打印概览。
        (Run the concept sector quotes and capital flow scraper once and print an overview.)
        """
        main_logger.info("开始执行单次行情与资金流爬取任务...")
        # (Starting single run task for quotes and capital flow...)
        scraper = ConceptSectorScraper(output_dir="concept_sector_data_output") # 指定输出目录 (Specify output directory)
        df_market_flow, saved_path = scraper.run_once()
        
        if not df_market_flow.empty and saved_path:
            main_logger.info(f"行情和资金流数据已成功获取并保存到: {saved_path}")
            # (Quotes and capital flow data successfully fetched and saved to: {saved_path})
            print("\n" + "="*40 + " 行情与资金流数据概览 " + "="*40)
            # (Overview of Quotes and Capital Flow Data)
            display_cols = ['板块名称', '涨跌幅', '最新价', '成交额', '主力净流入', '5日主力净流入', '10日主力净流入', '更新时间']
            # 确保只选择DataFrame中实际存在的列 (Ensure only selecting columns that actually exist in the DataFrame)
            available_cols = [col for col in display_cols if col in df_market_flow.columns]
            print(df_market_flow[available_cols].head(15).to_string(index=False)) # 显示前15条 (Show top 15)
            print("="*100)
        else:
            main_logger.error("未能获取或保存行情和资金流数据。")
            # (Failed to fetch or save quotes and capital flow data.)

    def run_stock_to_concept_mapping_scraper():
        """
        运行一次股票到概念板块映射的爬虫，并打印部分结果。
        (Run the stock-to-concept-sector mapping scraper once and print some results.)
        """
        main_logger.info("开始执行股票到概念板块映射构建任务...")
        # (Starting task to build stock-to-concept-sector mapping...)
        output_dir_mapping = "concept_mapping_output" # 为映射文件指定不同目录 (Specify a different directory for mapping files)
        os.makedirs(output_dir_mapping, exist_ok=True)
        scraper = ConceptSectorScraper(output_dir=output_dir_mapping) # Scraper实例使用此目录 (Scraper instance uses this directory)
        
        # 使用较高的并行度，因为涉及大量小请求 (Use higher parallelism as it involves many small requests)
        stock_concept_map = scraper.scrape_concept_to_stock_mapping(max_workers=20)
        
        if stock_concept_map:
            saved_map_path = scraper.save_stock_to_concept_mapping(stock_concept_map, "stock_to_concept_map_latest.json")
            if saved_map_path:
                main_logger.info(f"股票到概念板块的映射已成功生成并保存到: {saved_map_path}")
                # (Stock-to-concept mapping successfully generated and saved to: {saved_map_path})
                print(f"\n总共映射了 {len(stock_concept_map)} 只股票。")
                # (Total {len(stock_concept_map)} stocks mapped.)
                print("部分映射示例 (前5条):")
                # (Some mapping examples (first 5):)
                count = 0
                for stock_code, concept_codes in stock_concept_map.items():
                    if count < 5:
                        print(f"  股票代码 {stock_code} 属于概念板块代码: {concept_codes}")
                        # (Stock code {stock_code} belongs to concept sector codes: {concept_codes})
                        count += 1
                    else:
                        break
            else:
                main_logger.error("保存股票到概念板块映射文件失败。")
                # (Failed to save stock-to-concept mapping file.)
        else:
            main_logger.error("未能成功生成股票到概念板块的映射。")
            # (Failed to successfully generate stock-to-concept mapping.)

    # --- 在这里选择要运行的功能 ---
    # (Choose the functionality to run here)

    # 示例1: 运行一次行情和资金流爬虫
    # (Example 1: Run the quotes and capital flow scraper once)
    # run_market_and_flow_scraper_once()
    
    # 示例2: 运行一次股票到概念板块的映射爬虫
    # (Example 2: Run the stock-to-concept-sector mapping scraper once)
    run_stock_to_concept_mapping_scraper()

    # 示例3: 启动定时爬取行情和资金流数据 (例如每5分钟一次)
    # (Example 3: Start scheduled scraping for quotes and capital flow data (e.g., every 5 minutes))
    # main_logger.info("准备启动定时爬取任务 (行情与资金流)...")
    # # (Preparing to start scheduled scraping task (quotes and capital flow)...)
    # scheduled_market_scraper = ConceptSectorScraper(output_dir="concept_sector_data_scheduled")
    # try:
    #     scheduled_market_scraper.start_scheduled_scraping(interval_seconds=300) # 300秒 = 5分钟
    # except KeyboardInterrupt:
    #     main_logger.info("通过Ctrl+C接收到中断信号，正在停止定时爬虫...")
    #     # (Received interrupt signal via Ctrl+C, stopping scheduled scraper...)
    #     if 'scheduled_market_scraper' in locals() and hasattr(scheduled_market_scraper, 'stop'):
    #         scheduled_market_scraper.stop()
    #     main_logger.info("定时爬虫已停止。")
    #     # (Scheduled scraper stopped.)
    # except Exception as e:
    #     main_logger.exception("启动或运行定时爬虫时发生未捕获的异常。")
    #     # (Uncaught exception occurred while starting or running the scheduled scraper.)
    
    main_logger.info("脚本执行完毕。")
    # (Script execution finished.)