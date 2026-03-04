#!/usr/bin/env python
# coding: utf-8

# In[9]:


from bsedata.bse import BSE
import pprint
pp = pprint.PrettyPrinter(indent=4)


# In[12]:


def pprint(obj):
    pp.pprint(obj)


# In[2]:


b = BSE()
print(b)
# Output:
# Driver Class for Bombay Stock Exchange (BSE)

# to execute "updateScripCodes" on instantiation
b = BSE(update_codes = True)


# In[14]:


q = b.getQuote('534976')
pprint(q)


# In[15]:


codelist = ["500116", "512573"]
for code in codelist:
    quote = b.getQuote(code)
    pprint(quote["companyName"])
    pprint(quote["currentValue"])
    pprint(quote["updatedOn"])


# In[20]:


l = b.topLosers()
# pprint(l)


# In[21]:


b.getIndices(category='corporate')


# In[23]:


d = b.getScripCodes()


# In[26]:


# b.get

