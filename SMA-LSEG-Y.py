#!/usr/bin/env python
# coding: utf-8

# In[31]:


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
import datetime as datetime


# In[32]:


import import_ipynb
import Stock_Analysis as SA


# In[33]:


import yfinance as yf


# In[34]:


os.getcwd()


# In[35]:


import warnings
warnings.filterwarnings("ignore")


# In[36]:


tkrs = ['THRL.L','BARC.L','RIO.L','LLOY.L','ASML','VHYL.L','VUKG.L','QCOM','BAC','QCOM','WHR','ABR','NLY',
        'UKCM.L','O','EPIC.L','RESI.L','SPR.L','WHR.L','IWDP.L','DPYE.L','UNIT','THRL.L','AEWU.L','NRR.L',
        'IUKP.L','LXI.L','LAND.L','CREI.L','BBOX.L','QCOM','ZIM','ARKO','IIIV','EVRI','ASML','PBR','GLEN.L',
        'VOD','BATS.L','SMT.L','FORT.L','RIO','BARC.L','SGRO.L','GSK','NG',
        'API','AEWU.L','AFCG','ADC','ARE','AAT','AMH','COLD','NLY','APLE','ABR','AHH','AGR','AVB','BCPT.L','TM',
       'TM','KO','MCD','SBUX','PG','CVX','NKE','TSCO.L','RKT.L','ULVR.L','HSBA.L','AV.L','NWG.L', 'RR.L',
        'RGL.L'
        , "SUPR.L", "RGL.L","CREI.L", "AEWU.L","MO", "BMY.L","LGEN.L","WBA","BNPQY"
       ]

# tkrs = ['API','AEWU.L','AFCG','ADC','ARE','AAT','AMH','COLD','NLY','APLE','ABR','AHH','AGR','AVB','BCPT.L']
# tkrs = ['THRL.L','BARC.L','RIO.L']

# tkrs = ['TM','KO','MCD','SBUX','PG','CVX','NKE','TSCO.L','RKT.L','ULVR.L','HSBA.L','AV.L','NWG.L', 'RR.L']

to_date = (datetime.datetime.now() + + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
# 
from_date = (datetime.datetime.now() + datetime.timedelta(days=-1000)).strftime("%Y-%m-%d")

stk_yf = yf.download(tkrs, from_date, to_date).bfill()
# stk_yf = yf.download(tkrs,'2021-01-01','2023-12-13').fillna(method='backfill')
# stk_yf


# In[37]:


from_date


# In[ ]:





# In[38]:


n = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
stk_yf.to_csv(MY_PATH+"./dump/UK-STKS-HIS"+n+".csv")


# In[39]:


# stk_yf["Close"].symbol
stk_yf["Close"].columns


# In[40]:


y_stks = stk_yf["Close"]

sumary = None
for stk in tkrs:
    # print(stk)
    s = y_stks[stk].to_frame()
    s.columns=["close"]    
    s['symbol']=stk
    s = SA.processScrip(s, compute52W = True)
    sumary = pd.concat([sumary, s])
    
# t = dfs[ dfs["symbol"]=="ITC"]
# t= processScrip(t)
# u = dfs[ dfs["symbol"]=="INFY"]
# u= processScrip(u)
# print(t)


# In[41]:


values_arr = ["close","SMA20_2_200P","SIG","52WH_P","52WL_P","52WHLP","1WHLP","1MHLP","3MHLP","6MHLP","1YHLP"]
pvt = sumary.pivot_table(values=values_arr, columns=["symbol"], index=["Date"])

# pvt = sumary.pivot_table(values=["SMA20_2_200P","SIG","52WH_P","52WL_P","52WHLP"], columns=["symbol"], index=["Date"])


# In[42]:


12*30
s.shape


# In[43]:


pvt.to_csv(MY_PATH+"./dump/UK-STKS-HIS-processed-"+n+".csv")


# In[44]:


SIGNAL_WINDOW=8
i = pvt.SMA20_2_200P.tail(SIGNAL_WINDOW)
i.loc[:, i[(i > -1.0) & (i < 1.0)].any()].T.to_csv(MY_PATH+"./dump/UK-SIGNAL-Detail-"+n+".csv")
ip = i.loc[:, i[(i > -2.0) & (i < 1.0)].any()].T
ip
# temp2 = pts.loc[:,pts[(pts > 0.75*1e6) & (pts < 0.3*1e7)].any() ]


# In[45]:


s = pvt.SIG.tail(SIGNAL_WINDOW)
s.loc[:, s[(s == 1) | (s==-1) ].any()].T.to_csv(MY_PATH+"./dump/UK-SIGNAL-"+n+".csv")
sp  = s.loc[:, s[(s == 1) | (s==-1)  ].any()].T
sp


# In[46]:


if (ip.shape[0] > 0 ):
    ipfig = ip.T.plot(figsize=(20,5), grid=True, title='distance from Golden X - ').get_figure()
    
if (sp.shape[0] > 0 ):
    spfig = sp.T.plot(figsize=(20,5), grid=True, title='Golden X - ').get_figure()


# In[47]:


i52whp = pvt["52WH_P"].tail(5)
i52wlp = pvt["52WL_P"].tail(5)
i52whlp = pvt["52WHLP"].tail(5)


# In[48]:


# stocks staying close to 52WL. 
g52wl = i52wlp.loc[:, i52wlp[(i52wlp < 20) ].any()].T
g52wh = i52whp.loc[:, i52whp[(i52whp > 40.0) ].any()].T
g52wl


# In[49]:


ULIM_52WH = 90
LLIM_52WH = 25

i52whlpl_all = i52whlp.tail(1).T
i52whlpl_low = i52whlp.tail(1).loc[:, i52whlp[(i52whlp<LLIM_52WH)].any()].T
i52whlpl_high = i52whlp.tail(1).loc[:, i52whlp[(i52whlp>ULIM_52WH)].any()].T
col = i52whlpl_all.columns.values[0]


# In[50]:


# i52whlpl.plot(kind='bar', figsize=(20,5), grid=True)
plt.figure(figsize=(20,5))
plt.xticks(rotation=90)

i52whlpl_tmp = i52whlp.tail(1).loc[:, i52whlp[(i52whlp<=30)].any()].T
plt.bar(i52whlpl_tmp.index, i52whlpl_tmp[col], color='red', label="  % < 30")

i52whlpl_tmp = i52whlp.tail(1).loc[:, i52whlp[(i52whlp>30) & (i52whlp<=65) ].any()].T
plt.bar(i52whlpl_tmp.index, i52whlpl_tmp[col], color='blue', label="  30  <% < 65")

i52whlpl_tmp = i52whlp.tail(1).loc[:, i52whlp[(i52whlp>65) ].any()].T
plt.bar(i52whlpl_tmp.index, i52whlpl_tmp[col], color='green',label=" % > 65")

plt.bar(i52whlpl_high.index, i52whlpl_high[col], color='blue')
plt.title("52W H/L above {}% and below {}%".format(ULIM_52WH, LLIM_52WH))
plt.legend()
fig52whlclr = plt
fig52whlclr = SA.getImgData(fig52whlclr)
plt.show()


# In[51]:


avg_pct = i52whlpl_all[col].mean()
min_pct = i52whlpl_all[col].min()
max_pct = i52whlpl_all[col].max()
chart_title = '52W Hi/Low % Position  |  Avg: {:.1f}%  Min: {:.1f}%  Max: {:.1f}%  (as of {})'.format(avg_pct, min_pct, max_pct, col)
fig52whl = i52whlpl_all.sort_values(by=[col], ascending=False).plot(kind='barh', figsize=(8,25), grid=True, title=chart_title).get_figure()


# In[52]:


# SA.getGainerLosers(pvt)


# In[53]:


top_gainer_losers = SA.getGainerLosers(pvt)


# In[54]:


# pvt["1YHLP"]


# In[55]:


t1mhl, t3mhl, t6mhl, t1yhl = SA.getProcessedByMilestone(pvt)


# In[56]:


style_text = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {
  box-sizing: border-box;
}

/* Create two equal columns that floats next to each other */
.col {
  float: left;
  width: 50%;
}

/* Clear floats after the columns */
.row:after {
  width: 50%;
}
</style>

"""


# In[57]:


# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from base64 import b64encode

me  = 'peri47.study@gmail.com'
recipient = 'peri47.study@gmail.com'
subject = 'Signals for {}'.format('LSEG')

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
    <head> 
    {style_text}
    </head>
    <body>
            <H1>Stocks in Golden X - Signals: </H1>
            {signal_goldenx}
            <H1>Stocks nearing Golden X : </H1>
            {nearing_goldenx}
        <div class="row">
            <div class="col">
            <H1> %  From 52W H/L - Top 10: (Near Low)</H1>
            {hl52w_top10}
            </div>
            <div class="col">
            <H1>% From 52W H/L - Bottom10: (Near High)</H1>
            {hl52w_last10}
            </div>
        </div>
        <section>
        <div class="row">        
            <div class="col">
            <H1> 1 week Hi </H1>
            {h1w}
            </div>
            <div class="col">
            <H1> 1 weekLow </H1>
            {l1w}
            </div>
        </div>
        </section>
        <section>
        <div class="row">        
            <div class="col">
            <H1> 3 month Hi </H1>
            {h3m}
        </div>
        <div class="row">        
            <H1> 3 month low </H1>
            {l3m}
        </div>
        </div>
        </section>
        <section>
            <H1> Top Gainers / Losers  </H1>
                    <H1> 1 Week losers </H1>
                    {l1wl}
                    <H1> 1 Week gainers </H1>
                    {l1wh}
            <H1> 1 Month losers </H1>
            {l1ml}
            <H1> 1 Month gainers </H1>
            {l1mh}
            <H1> 3 Month losers </H1>
            {l3ml}
            <H1> 3 Month gainers </H1>
            {l6mh}
            <H1> 6 Month losers </H1>
            {l6ml}
            <H1> 6 Month gainers </H1>
            {l3mh}
        </section>
        
    </body>
</html>
""".format(nearing_goldenx=ip.to_html(),
           signal_goldenx=sp.to_html(),
           hl52w_top10 = i52whlpl_all.sort_values(by=[col]).head(10).to_html(), 
           hl52w_last10 = i52whlpl_all.sort_values(by=[col]).tail(10).to_html(),
           h1w = t1mhl.tail(10).to_html() , l1w = t1mhl.head(10).to_html() , h3m = t3mhl.tail(10).to_html(),
           l3m= t3mhl.head(10).to_html(),
           l1wl = top_gainer_losers.sort_values(by=['1wd']).head(10).to_html(),
           l1wh = top_gainer_losers.sort_values(by=['1wd']).tail(10).to_html(),
           l1ml = top_gainer_losers.sort_values(by=['1md']).head(10).to_html(),
           l1mh = top_gainer_losers.sort_values(by=['1md']).tail(10).to_html(),
           l3ml = top_gainer_losers.sort_values(by=['3md']).head(10).to_html(),
           l3mh = top_gainer_losers.sort_values(by=['3md']).tail(10).to_html(),
           l6ml = top_gainer_losers.sort_values(by=['6md']).head(10).to_html(),
           l6mh = top_gainer_losers.sort_values(by=['6md']).tail(10).to_html(),
           style_text = style_text,
           date=col )
email_body = section1
# msg.a

msg.attach(MIMEText(section1, 'html'))

# msgimg = 
msg.attach(MIMEImage(SA.getImgData(fig52whl)))
msg.attach(MIMEImage(fig52whlclr))

try:
    ipfig
except: 
    #ignore
    print('')
else:
    msg.attach(MIMEImage(SA.getImgData(ipfig)))

try:
    spfig
except: 
    #ignore
    print('')
else:
    msg.attach(MIMEImage(SA.getImgData(spfig)))

# f = open("./test.html", "w")
# f.write(section1)
# f.close()


# In[58]:


server = smtplib.SMTP(email_server_host, port)
server.ehlo()
server.starttls()
server.login(email_username, email_password)
server.sendmail(me, recipient, msg.as_string())
server.close()

