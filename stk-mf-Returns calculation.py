#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[101]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


import jaydebeapi
from pathlib import Path
import os
import pandas as pd
import csv
from datetime import date
from datetime import datetime
from xirr.math import xirr


# In[102]:


# f = open("C:\\Users\\111075866\\Downloads\\stocks_28Nov.csv")
fileName = 'mf_21_aug-2024.csv'
f = open("C:\\Users\\111075866\\Downloads\\"+fileName)
mf = [0,6,7,14,12]
stk = [0,7,8,15,13]

##for stock use stk, for mutualfund use mf
cols = mf
# cols = stk
# Make sure to remove the totals row in the xl sheet from moneycontrol


# In[103]:


# f.name


# In[104]:


# f.close()
stks = pd.read_csv(f)


# In[105]:


stks 


# In[106]:


t = stks.shape[0]-1
stks = stks.iloc[0:stks.shape[0]-1]


# In[107]:


stks


# In[108]:


stks = stks.iloc[:, cols ]


# In[109]:


stks.columns = ['Stock', 'Inv. Date', 'Inv. Amt', 'Latest Value', 'Overall Gain']


# In[110]:


g = stks.groupby(by=["Stock"])


# In[111]:


# stks[["Inv. Date"]].map(lambda x: str(x)).map(lambda x: str(x[6:]))


# In[112]:


import datetime


# In[113]:


g1 = pd.DataFrame(g.sum()["Latest Value"])
g1["Inv. Amt"] = g1["Latest Value"]*-1
i = g1.index
g1["Stock"] = i.values
stk_name = i.values
g1["Inv. Date"] = datetime.date.today()
stks["Inv. Date"] = stks[["Inv. Date"]].map(lambda x: str(x)).map(lambda x: datetime.date(int(x[6:]), int(x[3:5]), int(x[:2])))
# stks[["Inv. Date"]].map(lambda x: str(x)).map(lambda x: int(x[:2]))


# In[114]:


s=g1


# In[115]:


ta = s[["Inv. Amt", "Stock","Inv. Date"]]
stks1 = pd.concat([stks, ta])


# In[116]:


inp = stks1[["Stock", "Inv. Amt", "Inv. Date"]]


# In[117]:


# inp
# stk_name = i.values
# stk_name


# In[118]:


# inp[["Inv. Amt"]].map( lambda amt: -1*amt if amt < 0 else 0)
sum(inp[["Inv. Amt"]].to_numpy())[0]
# print(inp[["Inv. Amt"]].sum())


# In[119]:


r = (datetime.date.today()  - min(inp["Inv. Date"]) ) 
print(r)


# In[120]:


r.days/365


# In[121]:


#Test one


# In[122]:


from xirr.math import xirr
# xirr(inp[[ "Inv. Date"]], inp[[ "Latest Value"]])
# x = datetime.date.today()
# x.month

s = []
print("{Stock}  - \t \t :  {XIRR}:  {current_value} : \t {abs_ret} : \t {avg_ret} : \t {strt_date} : \t {age}")
for stk in stk_name:
    t1 = inp[inp["Stock"] == stk]
    print ("------------------------------------------------------------------------------------------------")
    # print(t1)
    vperdate = dict(zip(t1["Inv. Date"], t1["Inv. Amt"]))
    strt_date = min(t1["Inv. Date"])
    age = (datetime.date.today() - min(t1["Inv. Date"])).days/365
    # print(min(t1["Inv. Date"]),t1["Inv. Date"] )
    # t1[["Inv. Amt"]].filter()
    inv_amount = sum(t1[["Inv. Amt"]].map( lambda amt: amt if amt > 0 else 0).to_numpy())[0]
    current_value = sum(t1[["Inv. Amt"]].map( lambda amt: -1*amt if amt < 0 else 0).to_numpy())[0]
    abs_ret = current_value/inv_amount-1
    avg_ret = abs_ret/age
    # print( "{}  - \t \t : {} \t \t:  {} \t \t :  {} : \t {} ".format(stk, xirr(vperdate),inv_amount, current_value,abs_ret ))
    xr = xirr(vperdate)
    print( "{}\t:{} :  {} : \t {} : \t {} : \t {} : \t {} ".format(stk,xr,current_value,abs_ret,avg_ret,strt_date,age ))
    s.append((stk,xr,inv_amount,current_value,abs_ret,avg_ret,strt_date,age))
    # print ()
# s


# In[123]:


# n = inp[["Inv. Amt"]].sum() 
# print(n)


# In[124]:


p1 = pd.DataFrame(g.sum()[["Inv. Amt","Latest Value"]])
# p1["Stock"] = p1.index.values
p2 = pd.DataFrame(s)


# In[125]:


p2.columns=["Stock", "XIRR","Total Investment", "Current Value","abs_ret","avg_ret","start_date","age"]
m = p1.join(p2.set_index("Stock"))


# In[126]:


str_tz = str(datetime.datetime.now()).replace(' ', '_').replace(':','_').replace('.','_')
print(str_tz)


# In[127]:


m.to_csv("C:\\Users\\111075866\\Downloads\\"+fileName+"-XIRR-"+str_tz+".csv")
inp.to_csv("C:\\Users\\111075866\\Downloads\\"+fileName+"-upd-"+str_tz+".csv")


# In[128]:


inp


# In[129]:


inp.describe()


# In[130]:


c = inp.loc[inp["Inv. Amt"]>0].pivot_table(values=["Inv. Amt"], index=["Stock"],aggfunc="sum").replace(np.nan, 0)
c.nlargest(5, columns=["Inv. Amt"])

# pivot_table(values=["Inv. Amt"], index=["Stock"],aggfunc="sum").replace(np.nan, 0)


# In[131]:


c.nlargest(5, columns=["Inv. Amt"]).plot(kind="pie", subplots=True)


# In[132]:


cut1 = pd.cut(c["Inv. Amt"],4)
type(cut1)


# In[ ]:




