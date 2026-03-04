#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Use stk.ipynp to compute XIRR 


# In[2]:


import pandas as pd
from pathlib import Path


# In[3]:


file_path = Path('C:\\Users\\111075866\\Downloads\\mf-13.csv')
mf = pd.read_csv(file_path)
mf.describe(include='all')
# mf.head()
#[['Scheme','Inv.Amt','Overall Gain','Inv.Date']]


# In[4]:


# mf.pivot_table(index='', )


# In[5]:


mf = pd.DataFrame(mf, columns=['Scheme','Inv.Amt','Overall Gain','Inv.Date'])
mf.groupby(['Scheme']).sum()


# In[6]:


mf.

