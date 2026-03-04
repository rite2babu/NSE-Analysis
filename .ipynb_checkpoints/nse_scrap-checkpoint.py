#########################################################################################
# NSE Stock/Indices Scrapper
# Source: https://github.com/alloc7260/NSE
#########################################################################################
import math
import requests
import datetime
import json
import urllib
import pandas as pd
import concurrent
from concurrent.futures import ALL_COMPLETED
# import logging
import brotli
#from datetime import datetime, timedelta

HISTORICAL_DATA_URL = 'https://www.nseindia.com/api/historical/cm/equity?series=[%22EQ%22]&'
BASE_URL = 'https://www.nseindia.com/'
SERIES_LIST = ['EQ', 'IV','N1','N2','N3','RR', 'GB','BE' ,'BZ', 'BL', 'ID','RT','SM','ST', 'SO','GS','TB','MF','ME']
DEFAULT_SER = 'EQ'


def get_adjusted_headers():
    return {
        'Host': 'www.nseindia.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

def fetch_cookies():
    response = requests.get(BASE_URL, timeout=30, headers=get_adjusted_headers())
    if response.status_code != requests.codes.ok:
        # logging.error("Fetched url: %s with status code: %s and response from server: %s" % (
        #     BASE_URL, response.status_code, response.content))
        raise ValueError("Please try again in a minute.")
    return response.cookies.get_dict()

def fetch_url(url, cookies):
    """
        This is the function call made by each thread. A get request is made for given start and end date, response is
        parsed and dataframe is returned
    """
    response = requests.get(url, timeout=30, headers=get_adjusted_headers(), cookies=cookies)
    if response.status_code == requests.codes.ok:
        # decompress_content = brotli.decompress(response.content)
        json_response = json.loads(response.content)
        return pd.DataFrame.from_dict(json_response['data'])
    else:
        raise ValueError("Please try again in a minute.")

def scrape_data(start_date, end_date, name=None, input_type='stock'):
    """
    Called by stocks and indices to scrape data.
    Create threads for different requests, parses data, combines them and returns dataframe
    Args:
        start_date (datetime.datetime): start date
        end_date (datetime.datetime): end date
        input_type (str): Either 'stock' or 'index'
        name (str, optional): stock symbol or index name. Defaults to None.
    Returns:
        Pandas DataFrame: df containing data for stocksymbol for provided date range
    """
    cookies = fetch_cookies()

    start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")

    threads, url_list = [], []

    # set the window size to one year
    window_size = datetime.timedelta(days=50)

    current_window_start = start_date

    parts = name.split(sep="-")
    sname = parts[0]
    if(len(parts)>1): 
        ser = parts[1]
        if ser not in SERIES_LIST :
            ser = DEFAULT_SER
            sname = name
    else : ser = DEFAULT_SER



    while current_window_start < end_date:
        current_window_end = current_window_start + window_size
        
        # check if the current window extends beyond the end_date
        if current_window_end > end_date:
            current_window_end = end_date
        
        st = current_window_start.strftime('%d-%m-%Y')
        et = current_window_end.strftime('%d-%m-%Y')
        # print(st,et)
        if input_type == 'stock':
            params = {'symbol': sname,
                        'from': st,
                        'to': et,
                        'series':ser}
            # logging.error(params)
            # print(param)
            
            
            url = HISTORICAL_DATA_URL + urllib.parse.urlencode(params)
            url_list.append(url)

        # move the window start to the next day after the current window end
        current_window_start = current_window_end + datetime.timedelta(days=1)

    # print("url_list",url_list)

    result = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch_url, url, cookies): url for url in url_list}
        concurrent.futures.wait(future_to_url, return_when=ALL_COMPLETED)
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                df = future.result()
                result = pd.concat([result, df])
            except Exception as exc:
                # logging.error('%r generated an exception: %s. Please try again later.' % (url, exc))
                raise exc
    return format_dataframe_result(result, start_date, end_date)


def format_dataframe_result(result, start_date, end_date):
    if result.empty:
        return f"No Data Found : for date range {start_date} to {end_date}"
    '''
    columns_required = ["CH_TIMESTAMP", "CH_SYMBOL", "CH_SERIES", "CH_TRADE_HIGH_PRICE",
                        "CH_TRADE_LOW_PRICE", "CH_OPENING_PRICE", "CH_CLOSING_PRICE", "CH_LAST_TRADED_PRICE",
                        "CH_PREVIOUS_CLS_PRICE", "CH_TOT_TRADED_QTY", "CH_TOT_TRADED_VAL", "CH_52WEEK_HIGH_PRICE",
                        "CH_52WEEK_LOW_PRICE"]
    '''
    columns_required = ["CH_TIMESTAMP", "CH_SYMBOL", "CH_TRADE_HIGH_PRICE",
                        "CH_TRADE_LOW_PRICE", "CH_OPENING_PRICE", "CH_CLOSING_PRICE", 
                        "CH_TOT_TRADED_QTY","CH_52WEEK_HIGH_PRICE",
                        "CH_52WEEK_LOW_PRICE"]    
    result = result[columns_required]
    '''
    result = result.set_axis(
        ['date', 'symbol', 'high', 'low', 'open', 'close',
         'Prev Close Price', 'volume', 'Total Traded Value', '52 Week High Price',
         '52 Week Low Price'], axis=1)
    '''
    result = result.set_axis(['date', 'symbol', 'high', 'low', 'open', 'close', 'volume','52WH','52WL'], axis=1)
    result['date'] = pd.to_datetime(result['date'])
    result = result.sort_values('date', ascending=True)
    result.reset_index(drop=True, inplace=True)
    return result

def Get_Stock_Data(_ticker, _number_of_recent_days, _type="stock"):
    _number_of_weekends = (_number_of_recent_days / 5) * 2
    _number_of_trading_days =  _number_of_recent_days + _number_of_weekends + 30 # 30 is to cover for other holidays
    _start_date = datetime.datetime.today() - datetime.timedelta(_number_of_trading_days)
    _start_date_str = _start_date.strftime('%d-%m-%Y')
    _todays_date_str = datetime.datetime.today().strftime('%d-%m-%Y')
    _data_frame = scrape_data(_start_date_str, _todays_date_str, _ticker, _type)
    _data_frame = _data_frame.tail(_number_of_recent_days)
    return(_data_frame)

def Get_Stock_Data2(_tickers, _number_of_recent_days, _type="stock"):

    df1 = Get_Stock_Data(_tickers[0],_number_of_recent_days)
    # df1 = df1.set_index("date")
    
    for tkr in _tickers[1:]:
        try:
            t = Get_Stock_Data(tkr,_number_of_recent_days)
            df1 = pd.concat([df1, t])
        except:
            print("error - "+ tkr)
    return df1


    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     future_to_url = {executor.submit(fetch_url, url, cookies): url for url in url_list}
    #     concurrent.futures.wait(future_to_url, return_when=ALL_COMPLETED)
    #     for future in concurrent.futures.as_completed(future_to_url):
    #         url = future_to_url[future]
    #         try:
    #             df = future.result()
    #             result = pd.concat([result, df])
    #         except Exception as exc:
    #             # logging.error('%r generated an exception: %s. Please try again later.' % (url, exc))
    #             raise exc
    # return format_dataframe_result(result, start_date, end_date)


def Get_Stock_Data3(_tickers, _number_of_recent_days, _type="stock", MAX_THREADS=5):

    # df1 = pd.DataFrame()

    result = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_Get_Stock_Data = {executor.submit(Get_Stock_Data, tkr, _number_of_recent_days): tkr for tkr in _tickers}
        concurrent.futures.wait(future_to_Get_Stock_Data, return_when=ALL_COMPLETED)
        for future in concurrent.futures.as_completed(future_to_Get_Stock_Data):
            tkr = future_to_Get_Stock_Data[future]
            try:
                df = future.result()
                result = pd.concat([result, df])
            except Exception as exc:
                # logging.error('%r generated an exception: %s. Please try again later.' % (url, exc))
                print("error - "+ tkr +" - " +  str(exc))
                # raise exc
    return result

    
    # for tkr in _tickers:
    #     try:
    #         t = Get_Stock_Data(tkr,_number_of_recent_days)
    #         df1 = pd.concat([df1, t])
    #     except:
    #         print("error - "+ tkr)
    # return df1

