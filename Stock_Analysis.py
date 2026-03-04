#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import os
MY_PATH="C:/Users/111075866/Python Code/NSE/../../"
MY_LIB_PATH="C:/Users/111075866/Python Code/NSE"
sys.path.append(MY_LIB_PATH)
sys.path.append(MY_PATH)

from nse_scrap import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import io
import datetime as datetime


# In[2]:


os.getcwd()


# In[3]:


# !pip install import_ipynb


# In[4]:


def getImgData(f): 
    file = io.BytesIO()
    # r = figure.plot(kind='bar')
    # f = r.get_figure()
    f.savefig(file,format='png')
    file.seek(0)
    img_data = file.read()
    return img_data


# In[5]:


def processScrip(s=None, compute52W=False):
    # 1. Select the columns that need to be numbers
    numeric_cols = ['52WH', '52WL', 'close', 'PrevCloase']

    if not compute52W:
        # NSE path: API provides 52WH/52WL — ensure columns exist and are numeric
        s['52WH'] = s.get('52WH', 0.0)
        s['52WL'] = s.get('52WL', 0.0)
    else:
        # yfinance path: no 52W data from API, initialise for later computation
        s['52WH'] = 0.0
        s['52WL'] = 0.0

    # 2. Remove commas from those columns and convert to float
    for col in numeric_cols:
        if col in s.columns:
            s[col] = pd.to_numeric(s[col].astype(str).str.replace(',', ''), errors='coerce')

    s["SMA10"] = s[["close"]].rolling(window=10).agg({"close": "mean"})
    s["SMA20"] = s[["close"]].rolling(window=20).agg({"close": "mean"})
    s["SMA50"] = s[["close"]].rolling(window=50).agg({"close": "mean"})
    s["SMA100"] = s[["close"]].rolling(window=100).agg({"close": "mean"})
    s["SMA200"] = s[["close"]].rolling(window=200).agg({"close": "mean"})
    s["SMA10_2_50"] = s["SMA10"] - s["SMA50"]
    s["SMA20_2_200"] = s["SMA20"] - s["SMA200"]
    s['SMA20_2_200P'] = s["SMA20_2_200"] / s["SMA200"] * 100
    s["SMA20_2_200_1"] = s["SMA20_2_200"].shift(1)
    s["SIG"] = 0
    s.loc[((s["SMA20_2_200_1"] < 0) & (s["SMA20_2_200"] > 0)), "SIG"] = 1
    s.loc[((s["SMA20_2_200_1"] > 0) & (s["SMA20_2_200"] < 0)), "SIG"] = -1

    if compute52W:
        # Compute rolling 52W (210 trading days) high/low per row
        s["52WH"] = s["close"].rolling(window=210, min_periods=1).max()
        s["52WL"] = s["close"].rolling(window=210, min_periods=1).min()
    else:
        # NSE provides 52WH/52WL from the API — use them as-is (already numeric)
        # Fill any missing values with rolling fallback
        s["52WH"] = s["52WH"].where(s["52WH"] > 0, s["close"].rolling(window=210, min_periods=1).max())
        s["52WL"] = s["52WL"].where(s["52WL"] > 0, s["close"].rolling(window=210, min_periods=1).min())

    s["52WH_P"] = (s["52WH"] - s["close"]) / s["52WH"] * 100
    s["52WL_P"] = (s["close"] - s["52WL"]) / s["52WL"] * 100
    s["52WHLP"] = (s["close"] - s["52WL"]) / (s["52WH"] - s["52WL"]) * 100

    # New High / Low - in Week, month, Qty, Yr, 2Yr
    s["1WH"]=s[["close"]].rolling(window=7).agg({"close":"max"})
    s["1MH"]=s[["close"]].rolling(window=30).agg({"close":"max"})
    s["3MH"]=s[["close"]].rolling(window=3*30).agg({"close":"max"})
    s["6MH"]=s[["close"]].rolling(window=6*30).agg({"close":"max"})
    s["1YH"]=s[["close"]].rolling(window=12*30).agg({"close":"max"})

    s["1WL"]=s[["close"]].rolling(window=7).agg({"close":"min"})
    s["1ML"]=s[["close"]].rolling(window=30).agg({"close":"min"})
    s["3ML"]=s[["close"]].rolling(window=3*30).agg({"close":"min"})
    s["6ML"]=s[["close"]].rolling(window=6*30).agg({"close":"min"})
    s["1YL"]=s[["close"]].rolling(window=12*30).agg({"close":"min"})

    s["1WHLP"] =(s["close"] - s["1WL"])/(s["1WH"] - s["1WL"] ) * 100
    s["1MHLP"] =(s["close"] - s["1ML"])/(s["1MH"] - s["1ML"] ) * 100
    s["3MHLP"] =(s["close"] - s["3ML"])/(s["3MH"] - s["3ML"] ) * 100
    s["6MHLP"] =(s["close"] - s["6ML"])/(s["6MH"] - s["6ML"] ) * 100
    s["1YHLP"] =(s["close"] - s["1YL"])/(s["1YH"] - s["1YL"] ) * 100
    

    
    return s


# In[6]:


def getGainerLosers(pvt = None):
    l = pvt.shape[0]-1 
    mil_stone = [l, l-1, l-5, l-20, l-20*3, l-20*6, l-20*12,]
    mil_stone_lbl = ["1dd", "1wd","1md","3md","6md","12md"]
    tmp = pvt.iloc[mil_stone].close.T
    tmp
    # tmp['1wp'] = tmp['2024-01-18']-tmp['2024-01-11']
    tmp[mil_stone_lbl[0]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[1]])/tmp[tmp.columns[1]]*100
    tmp[mil_stone_lbl[1]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[2]])/tmp[tmp.columns[2]]*100
    tmp[mil_stone_lbl[2]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[3]])/tmp[tmp.columns[3]]*100
    tmp[mil_stone_lbl[3]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[4]])/tmp[tmp.columns[4]]*100
    tmp[mil_stone_lbl[4]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[5]])/tmp[tmp.columns[5]]*100
    tmp[mil_stone_lbl[5]] = (tmp[tmp.columns[0]]-tmp[tmp.columns[6]])/tmp[tmp.columns[6]]*100
    
    top_gainer_losers = tmp
    top_gainer_losers
    return top_gainer_losers


# In[7]:


def getProcessedGainerLoser(pvt = None):
    t = pvt["1WHLP"].tail(1)
    # t.loc[:,t[t<1].replace(0.0,1).any()]
    t1 = t.loc[:, t[t<5].replace(0.0, 0.1).any()].T
    t1WHLP = t1
    
    t = pvt["1MHLP"].tail(1)
    # t.loc[:,t[t<1].replace(0.0,1).any()]
    t1 = t.loc[:, t[t<5].replace(0.0, 0.1).any()].T
    t1MHLP = t1
    
    t = pvt["3MHLP"].tail(1)
    # t.loc[:,t[t<1].replace(0.0,1).any()]
    t1 = t.loc[:, t[t<5].replace(0.0, 0.1).any()].T
    t3MHLP = t1
    
    t = pvt["6MHLP"].tail(1)
    # t.loc[:,t[t<1].replace(0.0,1).any()]
    t1 = t.loc[:, t[t<5].replace(0.0, 0.1).any()].T
    t6MHLP = t1

    t = pvt["1YHLP"].tail(1)
    # t.loc[:,t[t<1].replace(0.0,1).any()]
    t1 = t.loc[:, t[t<15].replace(0.0, 0.1).any()].T
    t1YHLP = t1
    t1YHLP
    return t1WHLP, t1MHLP, t3MHLP, t6MHLP, t1YHLP


# In[8]:


def getProcessedByMilestone(pvt = None):

    col = pvt["52WH_P"].tail(5).tail(1).T.columns.values[0]
    t1mhl = pvt["1MHLP"].tail(1).T.sort_values(by=[col])
    # pd.DataFrame(t[col])
    # t1mhl.plot(kind='bar', figsize=(20,5), title = '1 Month  Hi/ Low', subplots=True)
    
    t3mhl = pvt["3MHLP"].tail(1).T.sort_values(by=[col])
    # pd.DataFrame(t[col])
    # t3mhl.plot(kind='bar', figsize=(20,5), title = '3 Month Hi/ Low', subplots=True)
    
    t6mhl = pvt["6MHLP"].tail(1).T.sort_values(by=[col])
    # pd.DataFrame(t[col])
    # t6mhl.plot(kind='bar', figsize=(20,5), title = '6 Month Hi/ Low', subplots=True)
    
    t1yhl = pvt["1YHLP"].tail(1).T.sort_values(by=[col])
    # pd.DataFrame(t[col])
    # t1yhl.plot(kind='bar', figsize=(20,5), title = '1 Year  Hi/ Low', subplots=True)
    # t1mhl.size
    return t1mhl, t3mhl, t6mhl, t1yhl


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




