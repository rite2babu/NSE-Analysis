#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nse_scrap import * 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[3]:


# def Get_Stock_Data2(_tickers, _number_of_recent_days, _type="stock"):

#     df1 = Get_Stock_Data(_tickers[0],_number_of_recent_days)
#     # df1 = df1.set_index("date")
    
#     for tkr in _tickers[1:]:
#         t = Get_Stock_Data(tkr,_number_of_recent_days)
#         df1 = pd.concat([df1, t])
#     return df1


dfs = Get_Stock_Data3(['WSTCSTPAPR'], 250)


# In[4]:


dfs


# In[5]:


# s = Get_Stock_Data('WSTCSTPAPR',300)
# p = dfs.pivot_table(index=["date"], columns=["symbol"], values =["close"]) 


# In[6]:


# p.close


# In[7]:


# p.close.INFY


# In[8]:


s = dfs[ dfs["symbol"]=="WSTCSTPAPR"]
type(s)
# s.index=s.date
# s.head()


# In[9]:


s


# In[10]:


s["SMA5"] = s[["close"]].rolling(window=5).agg({"close":"mean"})
s["SMA15"]=s[["close"]].rolling(window=15).agg({"close":"mean"})
s["SMA50"]=s[["close"]].rolling(window=50).agg({"close":"mean"})


# s["52WH"]=s[["close"]].rolling(window=210).agg({"close":"max"})
# s["52WL"]=s[["close"]].rolling(window=210).agg({"close":"min"})
s["52WH_P"] = (s["52WH"] - s["close"])/s["52WH"] * 100
s["52WL_P"] = (s["close"] - s["52WL"])/s["52WL"] * 100
s["52WHLP"] = (s["close"] - s["52WL"])/(s["52WH"] - s["52WL"] ) * 100

# agg({"close":"avg"})
# r.sum()


# In[11]:


s[["close", "52WL", "52WH"]]


# In[12]:


s["SMA5_2_50"] = s["SMA5"]- s["SMA50"]
s["SMA15_2_50"] = s["SMA15"]- s["SMA50"]


# In[13]:


s[["close","SMA5","SMA15","SMA50","SMA5_2_50","SMA15_2_50"]].plot(subplots=True, figsize=(20,5))


# In[14]:


# s["SIG"] = s["SMA5_2_50"].diff()[ (d> 0) & (d< 2) ]
s["SMA5_2_50_1"] = s["SMA5_2_50"].shift(1)
s["SIG"]=0
s.loc[ ((s["SMA5_2_50_1"] < 0 ) & (s["SMA5_2_50"] > 0 )), "SIG"] = 1 
s.loc[ ((s["SMA5_2_50_1"] > 0 ) & (s["SMA5_2_50"] < 0 )), "SIG"] = -1 

# s.loc[ s["SMA5_2_50_1"] <= s["SMA5_2_50"], "SIG"] = 0 


# In[15]:


s[["SMA5","SMA50","SMA15" ]].plot(subplots=False, figsize=(20,5))
s[["SMA5_2_50","SMA5_2_50_1","SIG"]].plot(subplots=False, figsize=(20,5))
s[["SIG"]].plot(subplots=False, figsize=(20,5))


# In[16]:


s.tail()


# In[17]:


# s.apply(lambda x: print("Y") if ( s.SMA5_2_50_1 > s.SMA5_2_50 ) else print(""))
# s["SIG"] = 1 if (s.SMA5_2_50_1 > s.SMA5_2_50) 0 else 



# In[18]:


s[ (s["SIG"]<0) | (s["SIG"]>0) ]


# In[19]:


s['EMA12'] = s[['close']].ewm(span=12).mean()
s['EMA26'] = s[['close']].ewm(span=26).mean()
s['MACD'] = s['EMA12']- s['EMA26']
s['SIG_MACD'] = s['MACD'].ewm(span=9).mean()
s['HIST_MACD'] = s['MACD'] - s['SIG_MACD']

s['EMA10'] = s[['close']].ewm(span=10).mean()
s['EMA100'] = s[['close']].ewm(span=100).mean()
s['EMA10_100_P'] = (s['EMA10'] - s['EMA100'])/s['EMA100']*100


tmp = s[['MACD','SIG_MACD','HIST_MACD','EMA10_100_P']]
# s[['HIST_MACD']].hist()


# In[20]:


bx = tmp[['HIST_MACD']].index.values.tolist()
by = tmp['HIST_MACD'].to_list()


# In[21]:


s[['MACD','SIG_MACD','HIST_MACD','EMA10_100_P']]


# In[ ]:





# In[24]:


import io
file = io.BytesIO()
r = tmp.plot(kind='bar')
f = r.get_figure()
f.savefig(file,format='png')
file.seek(0)
img_data = file.read()


# In[ ]:


plt.figure(figsize=(20,5))
plt.plot(tmp[['MACD','SIG_MACD']],label=["MACD","SIG_MACD"])
plt.plot(tmp[['EMA10_100_P']],'r>',label=[ 'EMA10_100_P'])
# plt.plot(tmp[['HIST_MACD']],)
plt.bar(tmp[['HIST_MACD']].index, tmp['HIST_MACD'], label='HIST')
# plt.bar(tmp[['HIST_MACD']], height=5.0, width=1.5)
# x = tmp[['HIST_MACD']].plot(kind='bar')
plt.legend()
plt.show()
plt.sav


# In[ ]:


# s[["close"]]
s[["close","52WH", "52WL", "52WH_P","52WL_P","52WHLP"]].tail()


# In[ ]:


(465.3 - 718.2)/(780 - 465.3)


# In[ ]:


txt = s[["close","52WH", "52WL", "52WH_P","52WL_P","52WHLP"]].tail().to_html()


# In[ ]:


txt


# In[ ]:


# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from base64 import b64encode

me  = 'peri47.study@gmail.com'
recipient = 'rite2babu@gmail.com'
subject = 'email test'

email_server_host = 'smtp.gmail.com'
port = 587
email_username = 'peri47.study@gmail.com'
email_password = 'zjxs btty xvqt gpuj'






msg = MIMEMultipart('alternative')
msg['From'] = me
msg['To'] = recipient
msg['Subject'] = subject
img_format = 'png'


msg.add_header('Content-Type','text/html')
section1 = """\
<html>
    <head> 52WH / L Table here </head>
    <body>
        <section>
            Golden X - nearing stocks: 
            {0}
            Golden X - Signals: 
            {1}
        </section>
        <section>
            52W - H/L - Arranged:
            {2}
        </section>
    </body>
</html>
""".format(s[["close","52WH", "52WL", "52WH_P","52WL_P","52WHLP"]].tail().to_html() )


email_body = body
# msg.a

msg.attach(MIMEText(section1, 'html'))
# msg.attach(MIMEText(section2, ' plain'))
# msg.attach(MIMEText(section3, 'html'))
msgimg = MIMEImage(img_data)
msg.attach(msgimg)

server = smtplib.SMTP(email_server_host, port)
server.ehlo()
server.starttls()
server.login(email_username, email_password)
server.sendmail(me, recipient, msg.as_string())
server.close()


