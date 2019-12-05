# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 15:58:43 2019

@author: Artur.Dossatayev
"""
### Selenium driver could be downloaded from: https://chromedriver.chromium.org/downloads


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import re
import timeit
from time import sleep
import random

sys_random = random.SystemRandom()
driver_path = "C:/chromedriver/chromedriver.exe"

def process_request(r_l):
    df = pd.DataFrame()
    bs_2 = BeautifulSoup(r_l, 'html.parser')
    divs= bs_2.find_all("div",{"data-asin":True})
    for k, div in enumerate(divs):
        title, sponsored, num_reviews, rating, price, prev_price, alternative_price, price_per_sheets = '','','','','','','',''
        title_value, num_reviews_value, rating_value, sponsored_value, price_value, prev_price_value, alternative_price_value, price_per_sheets_value = '','','','','','','',''
        
        sub_divs = div.find_all("div", {"class":"sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"})
        for i, sub_div in enumerate(sub_divs):
            if i == 3:
                
                sponsored_div = sub_div.find("div",{"class":"a-row a-spacing-micro"})
                if sponsored_div:
                    sponsored = sponsored_div.find("span", {"class":"a-size-base a-color-secondary"})
                title = sub_div.find("span", {"class":"a-size-base-plus a-color-base a-text-normal"})

                review_div = sub_div.find("div", {"class":"a-section a-spacing-none a-spacing-top-micro"})
                if review_div:
                    rating = review_div.find("span", {"class":"a-icon-alt"})
                    num_reviews = review_div.find("span", {"class":"a-size-base"})

            if i == 4:
                
                small_part = sub_div.find("div", {"class":"a-section a-spacing-none a-spacing-top-small"})
                mini_part = sub_div.find("div", {"class":"a-section a-spacing-none a-spacing-top-mini"})
                
                if small_part:
                    price_div = small_part.find("span", {"class":"a-price"})    
                    old_price_div = small_part.find("span",{"data-a-strike":True})
                    price_per_sheets = small_part.find("span", {"class":"a-size-base a-color-secondary"})
                    if old_price_div:
                        prev_price = old_price_div.find("span", {"class":"a-offscreen"})                        
                    
                    if price_div:
                        price = price_div.find("span", {"class":"a-offscreen"})
                
                if mini_part:
                    alternative_price = mini_part.find("span", {"class":"a-color-base"})
        


                if rating:
                    rating_value = rating.text
        
                if price:
                    price_value = price.text
                
                if prev_price:
                    prev_price_value = prev_price.text
                
                if alternative_price:
                    alternative_price_value = alternative_price.text
        
                if price_per_sheets:
                    price_per_sheets_value = price_per_sheets.text
        
                if num_reviews:
                    num_reviews_value = num_reviews.text
                    
                if sponsored:
                    sponsored_value = sponsored.text
                
                if title:
                    title_value = title.text
        pd_fin = pd.DataFrame([[title_value, num_reviews_value, rating_value, price_value, prev_price_value, 
                                alternative_price_value, price_per_sheets_value, sponsored_value]],
                                          columns = ['title', 'num_reviews', 'rating', 'price', 'prev_price',  
                                                     'alternative_price', 'price_per_sheet', 'sponsored'])  
        df = df.append(pd_fin)
    return df

def get_page_number(page_url):
    return int(re.search('[0-9]+',re.search('page=[0-9]+',page_url).group()).group())

def increment_page_number(page_url):
    pn = get_page_number(page_url)
    return re.sub('page=[0-9]+','page='+str(pn+1), page_url)




driver = webdriver.Chrome(driver_path)

start_time = timeit.default_timer()
df_fin = pd.DataFrame()
for i in range(1,100):
    try:
        if (i==1):
            driver.get('https://www.amazon.com/s?k=toilet+paper&ref=nb_sb_noss')
            sleep(10)
        elif (i>1 and i<=3):
            ul = driver.find_elements_by_xpath('//ul[@class="a-pagination"]/li/a')
            li = [x for x in ul]
            for k,l in enumerate(li):
                print(k,l.text)
                if (l.text =='Next→'):
                    li[k].click()
        elif (i>3):
            current_url = driver.current_url
            next_url = increment_page_number(current_url)
            driver.get(next_url);
        else:
            print('something went wrong')

        sleep(random.random()*12.38)
        df_processed = process_request(driver.page_source)
        df_fin = df_fin.append(df_processed)        
        elapsed = round(timeit.default_timer() - start_time,2)
        print('Step: '+str(i)+' из '+str(50))
        print('Elapsed: '+str(elapsed))
        print(df_processed['title'][0:5])
    except:
        print('ERROR: '+str(i))


df_fin.to_csv('output_amz_2.csv', index =False)

