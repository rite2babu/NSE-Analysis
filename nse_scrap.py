#########################################################################################
# NSE Stock/Indices Scrapper
# Uses curl_cffi to bypass Akamai bot-protection (TLS fingerprint impersonation)
#########################################################################################
import math
import datetime
import json
import urllib.parse
import pandas as pd
import concurrent.futures
from concurrent.futures import ALL_COMPLETED
from curl_cffi import requests as cf_requests
import time

HISTORICAL_DATA_URL = 'https://www.nseindia.com/api/historical/cm/equity?series=[%22EQ%22]&'
BASE_URL = 'https://www.nseindia.com/'
SERIES_LIST = ['EQ', 'IV','N1','N2','N3','RR', 'GB','BE' ,'BZ', 'BL', 'ID','RT','SM','ST', 'SO','GS','TB','MF','ME']
DEFAULT_SER = 'EQ'

# Module-level shared session — call init_session() once before bulk fetching
_session = None

def init_session():
    """Create a curl_cffi session impersonating Chrome to bypass Akamai.
    Call this before Get_Stock_Data3()."""
    global _session
    _session = cf_requests.Session(impersonate='chrome120')
    r = _session.get(BASE_URL, timeout=30)
    if r.status_code != 200:
        raise ValueError(f"NSE homepage returned {r.status_code}. Please try again.")
    time.sleep(1)
    return _session


def fetch_url(url, cookies=None):
    """Fetch a URL using the shared curl_cffi session."""
    global _session
    if _session is None:
        init_session()
    response = _session.get(url, timeout=30)
    if response.status_code == 200:
        json_response = json.loads(response.content)
        return pd.DataFrame.from_dict(json_response['data'])
    else:
        raise ValueError(f"HTTP {response.status_code} for {url}")

def scrape_data(start_date, end_date, name=None, input_type='stock'):
    """
    Called by stocks and indices to scrape data.
    Create threads for different requests, parses data, combines them and returns dataframe
    """
    global _session
    if _session is None:
        init_session()

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
            
            
            url = HISTORICAL_DATA_URL + urllib.parse.urlencode(params)  # type: ignore
            url_list.append(url)

        # move the window start to the next day after the current window end
        current_window_start = current_window_end + datetime.timedelta(days=1)

    # print("url_list",url_list)

    result = pd.DataFrame()
    for url in url_list:
        df = fetch_url(url)
        result = pd.concat([result, df])
        time.sleep(0.2)
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
    """Fetch data for multiple tickers sequentially to avoid Akamai rate limiting."""
    result = pd.DataFrame()
    for tkr in _tickers:
        try:
            df = Get_Stock_Data(tkr, _number_of_recent_days)
            result = pd.concat([result, df])
        except Exception as exc:
            print("error - " + tkr + " - " + str(exc))
        time.sleep(0.5)
    return result

    
    # for tkr in _tickers:
    #     try:
    #         t = Get_Stock_Data(tkr,_number_of_recent_days)
    #         df1 = pd.concat([df1, t])
    #     except:
    #         print("error - "+ tkr)
    # return df1

