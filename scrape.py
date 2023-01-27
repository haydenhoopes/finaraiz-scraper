#!/usr/bin/env python
# coding: utf-8

# In[1]:


from scraper import FincaRaizScraper
from bs4 import BeautifulSoup
from datetime import datetime


# In[2]:


fr = FincaRaizScraper()
fr.set_cities('Bogota', 'Santa Marta', 'Villavicencio', 'Medellin', 'Cali', 'Armenia', 'Fusagasuga')
fr.go(pages_per_city=5)
fr.close()


# In[ ]:


fr.get_dataframe().to_csv('finca_raiz_data.csv')

