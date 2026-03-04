#!/usr/bin/env python
# coding: utf-8

# In[586]:


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


# In[587]:


import import_ipynb
import Stock_Analysis as SA


# In[588]:


os.getcwd()


# In[589]:


import io
def getImgData(f): 
    file = io.BytesIO()
    # r = figure.plot(kind='bar')
    # f = r.get_figure()
    f.savefig(file,format='png')
    file.seek(0)
    img_data = file.read()
    return img_data


# In[590]:


import warnings
warnings.filterwarnings("ignore")


# In[591]:


# stklist = ['ASPINWALL','ARE&M','COALINDIA','DRREDDY','EXIDEIND','CAMS','GAIL','HDFCBANK','ICICIBANK']
# stklist = ['ABSLAMC','ADANIPORTS','ARE&M','AMBUJACEM','ASIANPAINT','ASPINWALL','AUROPHARMA','BAJAJ-AUTO','BAJFINANCE','BALKRISIND','CAMS','CARTRADE','CASTROLIND','CEATLTD','CIPLA','COALINDIA','CROMPTON','DATAPATTNS','DRREDDY','EIDPARRY','EMBASSY-RR','EXIDEIND','GAIL','GENUSPOWER','GESHIP','GOLDBEES','GOLDETF','GULFOILLUB','HCLTECH','HDFCBANK','HDFCNIFIT','HEROMOTOCO','HGS','HIL','HINDALCO','HITECHGEAR','ICICIBANK','ICICIGOLD','ICICITECH','IDFC','IFCI','INFY','IOC','IRBINVIT','IRFC','ITC','JINDALPOLY','JINDALSAW','JSL','JUBLFOOD','KTKBANK','LGBBROSLTD','MANAPPURAM','MARUTI','MUTHOOTFIN','NATCOPHARM','NHIT-N1','NHIT-N3','NHIT-N2','PCBL','PETRONET','PGINVIT','PNBGILTS','PPL','RUBFILA','RVNL','SAIL','SBIGETS','SGBN28VIII-GB','SIL','STOVEKRAFT','TATACHEM','TATACOFFEE','TATAMOTORS','TATAMTRDVR','TATASTEEL','TCS','TECHM','TEGA','TITAGARH','TITAN','TMB','TTKPRESTIG','TVSMOTOR','VEDL','WHIRLPOOL','WIPRO','WSTCSTPAPR','ZYDUSLIFE']
stklist = ['ABSLAMC','ADANIPORTS','ARE&M','AMBUJACEM','ASIANPAINT','ASPINWALL','AUROPHARMA','BAJAJ-AUTO','BAJFINANCE','BALKRISIND','CAMS','CARTRADE','CASTROLIND','CEATLTD','CIPLA','COALINDIA','CROMPTON','DATAPATTNS','DRREDDY','EIDPARRY','EMBASSY-RR','EXIDEIND','GAIL','GENUSPOWER','GESHIP','GOLDBEES','GOLDETF','GULFOILLUB','HCLTECH','HDFCBANK','HDFCNIFIT','HEROMOTOCO','HGS','HIL','HINDALCO','HITECHGEAR','ICICIBANK','ICICIGOLD','ICICITECH','IDFC','IFCI','INFY','IOC','IRBINVIT-IV','IRFC','ITC','JINDALPOLY','JINDALSAW','JSL','JUBLFOOD','KTKBANK','LGBBROSLTD','MAGOLD','MANAPPURAM','MARUTI','MUTHOOTFIN','NATCOPHARM','NHIT-N1','NHIT-N3','NHIT-N2','PCBL','PETRONET','PGINVIT-IV','PNBGILTS','PPL','RUBFILA','RVNL','SAIL','SBIGETS','SGBN28VIII-GB','SIL-BE','STOVEKRAFT','TATACHEM','TATACOFFEE','TATAMOTORS','TATAMTRDVR','TATASTEEL','TCS','TECHM','TEGA','TITAGARH','TITAN','TMB','TTKPRESTIG','TVSMOTOR','VEDL','WHIRLPOOL','WIPRO','WSTCSTPAPR','ZYDUSLIFE']
stklist = ['HDFCBANK','AMBUJACEM','EMBASSY-RR']
# stklist = ['EMBASSY-RR']


# In[592]:


dfs = Get_Stock_Data3(stklist, 500, MAX_THREADS=2)


# In[593]:


import datetime as datetime


# In[594]:


n = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
dfs.to_csv(MY_PATH+"./dump/STKS-HIS"+n+".csv")


# In[595]:


sumary = None
for stk in set(dfs.symbol):
    s = dfs[ dfs["symbol"]==stk]
    s = SA.processScrip(s)
    sumary = pd.concat([sumary, s])


# In[596]:


values_arr = ["close","SMA20_2_200P","SIG","52WH_P","52WL_P","52WHLP","1WHLP","1MHLP","3MHLP","6MHLP","1YHLP"]
pvt = sumary.pivot_table(values=values_arr, columns=["symbol"], index=["date"])


# In[597]:


top_gainer_losers = SA.getGainerLosers(pvt)
top_gainer_losers.sort_values(by=['1md']).head(10)


# In[598]:


pvt.to_csv(MY_PATH+"./dump/STKS-HIS-processed-"+n+".csv")


# In[599]:


SIGNAL_WINDOW=8
i = pvt.SMA20_2_200P.tail(SIGNAL_WINDOW)
i.loc[:, i[(i > -1.0) & (i < 1.0)].any()].T.to_csv(MY_PATH+"./dump/SIGNAL-Detail-"+n+".csv")
ip = i.loc[:, i[(i > -1.0) & (i < 1.0)].any()].T
ip
# temp2 = pts.loc[:,pts[(pts > 0.75*1e6) & (pts < 0.3*1e7)].any() ]


# In[600]:


s = pvt.SIG.tail(SIGNAL_WINDOW)
s.loc[:, s[(s == 1) | (s==-1) ].any()].T.to_csv(MY_PATH+"./dump/SIGNAL-"+n+".csv")
sp  = s.loc[:, s[(s == 1) | (s==-1) ].any()].T
sp


# In[601]:


if (ip.shape[0] > 0 ):
    ipfig = ip.T.plot(figsize=(20,5), grid=True).get_figure()
if (sp.shape[0] > 0 ):
    spfig = sp.T.plot(figsize=(20,5), grid=True).get_figure()


# In[602]:


i52whp = pvt["52WH_P"].tail(5)
i52wlp = pvt["52WL_P"].tail(5)
i52whlp = pvt["52WHLP"].tail(5)


# In[603]:


# stocks staying close to 52WL. 
g52wl = i52wlp.loc[:, i52wlp[(i52wlp < 20) ].any()].T
g52wh = i52whp.loc[:, i52whp[(i52whp > 40.0) ].any()].T
g52wl


# In[604]:


# i52whp.T
g52wh


# In[605]:


if (g52wl.shape[0] > 0 ):
    g52wl.T.plot(figsize=(20,5), grid=True,title='52WL_P')
if (g52wh.shape[0] > 0 ):
    g52wh.T.plot(figsize=(20,5), grid=True,title='52WH_P')    


# In[606]:


# stocks fell a lot from 52WH close to 52WL. 
i52whp.loc[:, i52whp[(i52whp > 30.0) ].any()].T


# In[607]:


ULIM_52WH = 90
LLIM_52WH = 25

i52whlpl_all = i52whlp.tail(1).T
i52whlpl_low = i52whlp.tail(1).loc[:, i52whlp[(i52whlp<LLIM_52WH)].any()].T
i52whlpl_high = i52whlp.tail(1).loc[:, i52whlp[(i52whlp>ULIM_52WH)].any()].T
col = i52whlpl_all.columns.values[0]


# In[608]:


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
fig52whlclr = getImgData(fig52whlclr)
plt.show()


# In[609]:


fig52whl = i52whlpl_all.sort_values(by=[col]).plot(kind='bar', figsize=(20,5), grid=True, title='52W Hi/Low').get_figure()


# In[610]:


i52whlpl_allcsv = pd.DataFrame(i52whlpl_all[col])


# In[611]:


i52whlpl_allcsv.sort_values(by=[col]).to_csv(MY_PATH+"./dump/STKS-52WHLP-"+n+".csv")


# In[612]:


i52whlpl_allcsv.sort_values(by=[col])


# In[613]:


t1WHLP, t1MHLP, t3MHLP, t6MHLP, t1YHLP = SA.getProcessedGainerLoser(pvt)


# In[614]:


t1mhl, t3mhl, t6mhl, t1yhl = SA.getProcessedByMilestone(pvt)
# t1mhl.size


# In[615]:


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


# In[616]:


# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from base64 import b64encode

me  = 'peri47.study@gmail.com'
recipient = 'rite2babu@gmail.com'
subject = 'Signals for {}'.format('NSE')

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
msg.attach(MIMEImage(getImgData(fig52whl)))
msg.attach(MIMEImage(fig52whlclr))

try:
    ipfig
except: 
    #ignore
    print('')
else:
    msg.attach(MIMEImage(getImgData(ipfig)))

try:
    spfig
except: 
    #ignore
    print('')
else:
    msg.attach(MIMEImage(getImgData(spfig)))

# f = open("./test.html", "w")
# f.write(section1)
# f.close()


# In[617]:


server = smtplib.SMTP(email_server_host, port)
server.ehlo()
server.starttls()
server.login(email_username, email_password)
server.sendmail(me, recipient, msg.as_string())
server.close()

