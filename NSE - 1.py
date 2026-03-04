#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bsedata.bse import BSE
b = BSE()
print(b)
# Output:
# Driver Class for Bombay Stock Exchange (BSE)

# to execute "updateScripCodes" on instantiation
b = BSE(update_codes = True)


# In[2]:


q = b.getQuote('534976')
print(q)
# Output:
# {'2WeekAvgQuantity': '0.14 Lakh',
#  '52weekHigh': '3298.00',
#  '52weekLow': '1874.00',
#  'buy': {'1': {'price': '0.00', 'quantity': '-'},
#          '2': {'price': '0.00', 'quantity': '-'},
#          '3': {'price': '0.00', 'quantity': '-'},
#          '4': {'price': '0.00', 'quantity': '-'},
#          '5': {'price': '0.00', 'quantity': '-'}},
#  'change': '76.75',
#  'companyName': 'V-MART RETAIL LTD.',
#  'currentValue': '2255.80',
#  'dayHigh': '2270.00',
#  'dayLow': '2185.10',
#  'faceValue': '10.00',
#  'group': 'A  / S&P BSE 500',
#  'industry': 'Department Stores',
#  'lowerPriceBand': '1804.65',
#  'marketCapFreeFloat': '1,883.72 Cr.',
#  'marketCapFull': '4,095.05 Cr.',
#  'pChange': '3.52',
#  'previousClose': '2179.05',
#  'previousOpen': '2199.65',
#  'priceBand': '20%',
#  'scripCode': '534976',
#  'securityID': 'VMART',
#  'sell': {'1': {'price': '0.00', 'quantity': '-'},
#           '2': {'price': '0.00', 'quantity': '-'},
#           '3': {'price': '0.00', 'quantity': '-'},
#           '4': {'price': '0.00', 'quantity': '-'},
#           '5': {'price': '0.00', 'quantity': '-'}},
#  'totalTradedQuantity': '0.01 Lakh',
#  'totalTradedValue': '0.13 Cr.',
#  'updatedOn': '14 Jun 19 | 04:00 PM',
#  'upperPriceBand': '2706.95',
#  'weightedAvgPrice': '2239.58'}


# In[12]:


symbol = "NIFTY 50"
days = 3
end_date = datetime.datetime.now().strftime("%d-%b-%Y")
end_date = str(end_date)

start_date = (datetime.datetime.now()- datetime.timedelta(days=days)).strftime("%d-%b-%Y")
start_date = str(start_date)

df2=index_history("NIFTY 50",start_date,end_date)
df2["daily_change"]=df2["CLOSE"].astype(float).pct_change()
df2=df2[['HistoricalDate','daily_change']]
df2 = df2.iloc[1: , :]
print(df2)


# In[42]:


symbol = 'TCS'
# series = "EQ"
# start_date = "08-06-2021"
# end_date ="14-06-2021"
# print(equity_history(symbol,series,start_date,end_date))
url1 = 'https://www.nseindia.com/api/historical/cm/equity?symbol=' + symbol + '&series=["' + series + '"]&from=' + start_date + '&to=' + end_date
url = 'https://www.nseindia.com/api/historical/cm/equity?symbol=' + symbol
# print(url)
payload = nsefetch(url)
df = pd.DataFrame.from_records(payload["data"])
# print(df)
df[['CH_CLOSING_PRICE', 'CH_TIMESTAMP' ]]





# In[46]:


from datetime import date
from jugaad_data.nse import bhavcopy_save, bhavcopy_fo_save

# Download bhavcopy
bhavcopy_save(date(2020,1,1), "./data")

# Download bhavcopy for futures and options
bhavcopy_fo_save(date(2020,1,1), "./data")


# In[65]:


from datetime import date
from jugaad_data.nse import stock_csv, stock_df

# Download as pandas dataframe
df = stock_df(symbol="ITI", from_date=date(2023,9,1),
            to_date=date(2023,10,1), series="EQ")
print(df.head())


# In[ ]:


df.head()

