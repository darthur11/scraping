# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 11:04:07 2020

@author: Artur.Dossatayev
"""





import grequests
from bs4 import BeautifulSoup
import random
from time import sleep
from requests.auth import HTTPProxyAuth
import timeit
import pandas as pd
import re
import math
import numpy as np

sys_random = random.SystemRandom()


proxylst = []
proxy_login = ""
proxy_pass = ""

def make_request(urls):
    headerList = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
                 ]
    proxyList = proxylst
    
    auth = HTTPProxyAuth(proxy_login, proxy_pass)

    r = (grequests.get(u, 
                       headers={'User-Agent' : sys_random.choice(headerList)}, 
                       proxies={'http:' : sys_random.choice(proxyList)}, 
                       auth=auth, stream = True) for u in urls)
    return grequests.map(r)

results = make_request(['https://www.numbeo.com/quality-of-life/region_rankings_current.jsp?region=150'])
columns = ['Rank', 'City', 'Quality of Life Index', 'Purchasing Power Index',
'Safety Index', 'Health Care Index', 'Cost of Living Index', 'Property Price to Income Ratio',
'Traffic Commute Time Index', 'Pollution Index', 'Climate Index']
pd_fin = pd.DataFrame()
for res in results:
    bs = BeautifulSoup(res.text, 'html.parser')
    table = bs.find("table", {"id":"t2"})
    tbody = table.find("tbody")
    rows = tbody.find_all("tr")
    for row in rows:
        row_vals = {}
        td = row.find_all("td")
        for i,col in enumerate(columns):
            if i==1:
                link = td[i].find("a")
                row_vals.update({col: link.text})
            elif i>1:
                row_vals.update({col: td[i].text})
            row_vals.update({"link":link['href']})
        pd_fin = pd_fin.append(pd.DataFrame(row_vals, index = [0]))


pd_fin['link_cost'] = pd_fin['link'].str.replace('quality-of-life','cost-of-living')+'?displayCurrency=USD'
pd_fin['link_pollution'] = pd_fin['link'].str.replace('quality-of-life','pollution')
pd_fin['link_climate'] = pd_fin['link'].str.replace('quality-of-life','climate')
pd_fin.index = range(len(pd_fin))


def process_request_cost(data):
    pd_fin = pd.DataFrame()
    intro_columns = ['four_person_costs','single_person_costs', 'cost_of_living', 'rating', 'cost_of_living_index']
    metric_columns = ['metric','value','range_from','range_to']
    for d in data:
        pd_url = pd.DataFrame()
        pd_intro  = pd.DataFrame()
        bs = BeautifulSoup(d.text, 'html.parser')
        header = bs.find("div", {"class":"seeding-call limit_size_ad_right padding_lower other_highlight_color"})
        lis = header.find_all("li")
        for i,li in enumerate(lis):
            span = li.find("span", {"class":"emp_number"}).text
            pd_intro = pd_intro.append(pd.DataFrame({'metric':intro_columns[i],
                                     'value':span,
                                     'range_from':0,
                                     'range_to':0}, index = [0]))
        table = bs.find("table", {"class":"data_wide_table"})
        rows = table.find_all("tr")
        pd_url = pd_url.append(pd_intro)
        for row in rows:
            row_vals = {}
            td = row.find_all("td")
            if len(td)>0:
                for i, col in enumerate(td):
                    if i<1:
                        row_vals.update({metric_columns[i]:col.text})
                    elif i==1:
                        val = re.search("[0-9]*[,]?[0-9]*[.]+[0-9]*",col.text).group(0)
                        val = val.replace(',','')
                        val = float(val)
                        row_vals.update({metric_columns[i]:val})
                    else:
                        try:
                            barleft = col.find("span", {"class":"barTextLeft"}).text
                            barleft = re.search("[0-9]*[,]?[0-9]*[.]+[0-9]*",barleft).group(0)
                            barleft = barleft.replace(',','')
                            barleft = float(barleft)
                        except:
                            barleft = 0
                        try:
                            barright = col.find("span", {"class":"barTextRight"}).text
                            barright = re.search("[0-9]*[,]?[0-9]*[.]+[0-9]*",barright).group(0)
                            barright = barright.replace(',','')
                            barright = float(barright)
                        except:
                            barright = 0
                        row_vals.update({metric_columns[2]:barleft})
                        row_vals.update({metric_columns[3]:barright})
            pd_row = pd.DataFrame(row_vals, index = [0])
            pd_url = pd_url.append(pd_row)
        pd_url = pd_url.loc[pd_url['metric'].notnull()]
        pd_url.index = range(len(pd_url))
        pd_url['link'] = d.url

        pd_fin = pd_fin.append(pd_url)
    return pd_fin


def process_request_pollution(data):
    columns_names = {'columnWithName':'metric',
                 'indexValueTd':'value',
                 'hidden_on_small_mobile':'description'}
    pd_fin = pd.DataFrame()
    for d in data:
        pd_url = pd.DataFrame()
        bs = BeautifulSoup(d.text, 'html.parser')
        pollution_data = bs.find_all("table",{"class":"table_builder_with_value_explanation data_wide_table"})
        rows = pollution_data[1].find_all("tr")
        for row in rows:
            row_vals = {}
            for key in columns_names.keys():
                try:
                    col = row.find("td",{"class":key}).text
                except:
                    col = ''
                if key == 'indexValueTd':
                    col = re.search("[0-9]*[.]+[0-9]*",col).group(0)
                    col = float(col)
                elif key == 'hidden_on_small_mobile':
                    col = re.search("[A-Za-z]+[ ]?[A-Za-z]*",col).group(0)
                row_vals.update({columns_names[key]:col})
            pd_row = pd.DataFrame(row_vals, index = [0])
            pd_url = pd_url.append(pd_row)
        pd_url = pd_url.loc[pd_url['metric'].notnull()]
        pd_url.index = range(len(pd_url))
        pd_url['link'] = d.url
        pd_fin = pd_fin.append(pd_url)
    return pd_fin


def process_request_climate(data):
    index_cols = ['month','value']
    temp_cols = ['month','avg_low','avg_high']
    pd_fin = pd.DataFrame()
    for d in data:
        pd_indexes = pd.DataFrame()
        pd_temps = pd.DataFrame()
        bs = BeautifulSoup(d.text, 'html.parser')
        tables = bs.find_all("table")
        
        indexes = tables[3].find_all("tr")
        temps = tables[4].find_all("tr")
        
        for j, index in enumerate(indexes):
            row_vals_index = {}
            if j>0:
                tds = index.find_all("td")
                for i, td in enumerate(tds):
                    if i<2:
                        row_vals_index.update({index_cols[i]:td.text})
            pd_index = pd.DataFrame(row_vals_index, index = [0])
            pd_indexes = pd_indexes.append(pd_index)
        for j, temp in enumerate(temps):
            row_vals_temp = {}
            if j>0:
                tds = temp.find_all("td")
                for i, td in enumerate(tds):
                    if i<1:                    
                        row_vals_temp.update({temp_cols[i]:td.text})
                    elif i in range(1,3):
                        val = re.search("[0-9]+",td.text).group(0)
                        val = float(val)
                        row_vals_temp.update({temp_cols[i]:val})
            pd_temp = pd.DataFrame(row_vals_temp, index = [0])
            pd_temps = pd_temps.append(pd_temp)
        pd_url = pd.merge(pd_temps,pd_indexes)
        pd_url = pd_url.loc[pd_url['month'].notnull()]
        pd_url['link'] = d.url
        pd_fin = pd_fin.append(pd_url.loc[:, ['month','avg_low','avg_high','value','link']])
    return pd_fin





pd_pollution = pd.DataFrame()
start_time = timeit.default_timer()
for i in range(math.ceil(len(pd_fin)/10)):
    down_pos = 10*i
    if 10*i+10>len(pd_fin):
        up_pos = len(pd_fin)
    else:
        up_pos = 10*i+10
    print(down_pos,up_pos)
    #Get pollution#
    urls = list(pd_fin['link_pollution'].iloc[down_pos:up_pos])    
    pd_pollution = pd_pollution.append(process_request_pollution(make_request(urls)))
    sleep(sys_random.random()*1.81)
    current_time = timeit.default_timer()
    diff_sec = round(current_time-start_time,0)
    print(f"Elapsed: {diff_sec} seconds")


pd_cost = pd.DataFrame()
for i in range(math.ceil(len(pd_fin)/10)):
    down_pos = 10*i
    if 10*i+10>len(pd_fin):
        up_pos = len(pd_fin)
    else:
        up_pos = 10*i+10
    print(down_pos,up_pos)    
    #Get cost of living:#
    urls = list(pd_fin['link_cost'].iloc[down_pos:up_pos])    
    pd_cost = pd_cost.append(process_request_cost(make_request(urls)))
    sleep(sys_random.random()*1.43)
    current_time = timeit.default_timer()
    diff_sec = round(current_time-start_time,0)
    print(f"Elapsed: {diff_sec} seconds")




pd_climate = pd.DataFrame()
for i in range(math.ceil(len(pd_fin)/10)):
    down_pos = 10*i
    if 10*i+10>len(pd_fin):
        up_pos = len(pd_fin)
    else:
        up_pos = 10*i+10
    print(down_pos,up_pos)    
    #Get climate#
    urls = list(pd_fin['link_climate'].iloc[down_pos:up_pos])
    pd_climate = pd_climate.append(process_request_climate(make_request(urls)))
    sleep(sys_random.random()*1.72)
    current_time = timeit.default_timer()
    diff_sec = round(current_time-start_time,0)
    print(f"Elapsed: {diff_sec} seconds")
    
    
    
    
folder = "G:/My Drive/Outputs/2020_02_06_numbeo/"

pd_pollution.to_csv(folder+'pollution.csv')
pd_cost.to_csv(folder+'cost.csv')
pd_climate.to_csv(folder+'climate.csv')
pd_fin.to_csv(folder+'main.csv')

pd_pollution_pivoted = pd_pollution[['metric','description', 'link']].pivot(index = 'link', columns = 'metric')['description'].reset_index()
pd_pollution_pivoted.to_csv(folder+'pollution_p.csv', index = False)


pd_pollution_pivoted[['Air quality','link']].groupby('Air quality').count().plot.bar()

pd_cost.columns
pd_cost_pivoted = pd_cost[pd_cost['metric']!='Imported Beer (0.33 liter bottle) '][['metric','value','link']].pivot(index = 'link', columns = 'metric')['value'].reset_index()
pd_cost_pivoted.to_csv(folder+'cost_p.csv', index = False)

pd_climate['value'] = pd.to_numeric(pd_climate['value'])
pd_climeate_p = pd_climate.groupby('link').agg({'avg_high':[max],'avg_low':[min],'value':[np.mean, np.std]})




pd_climeate_p.columns = pd_climeate_p.columns.droplevel(0)
pd_climeate_p = pd_climeate_p.reset_index()
pd_climeate_p.columns = ['link', 'max_temp', 'min_temp', 'avg_index', 'std_index']

pd_climeate_p.to_csv(folder+'climate_p.csv', index = False)
