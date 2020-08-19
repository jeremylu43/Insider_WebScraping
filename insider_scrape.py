import pandas as pd
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys   # For keyboard keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from datetime import datetime

d = {}
with open("ticker.txt") as f:
    for line in f:
        (key, val) = line.split()
        d[key] = val
        
driver = webdriver.Chrome(executable_path='./chromedriver.exe')
wait = WebDriverWait(driver, 5)
action = ActionChains(driver)
    
def make_csv(ticker):
    transactions = pd.DataFrame()
    cut_off_date= datetime(2018,1,1)
    start=0

    cik = d[ticker]
    driver.get(f'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK={cik}&type=&dateb=&owner=include&start={start}')
    isPresent = True

    while isPresent == True:  
        try:
            tbl = driver.find_element_by_xpath('//*[@id="transaction-report"]').get_attribute('outerHTML')
            df  = pd.read_html(tbl)
            df = df[0].dropna(axis=0, thresh=4) 
            transactions = transactions.append(df)
            last_date = df.iloc[-1]['Transaction Date']
            last_date = datetime.strptime(last_date, "%Y-%m-%d")
            if last_date < cut_off_date:
                isPresent=False
            start += 80
            driver.get(f'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK={cik}&type=&dateb=&owner=include&start={start}')
        except ElementClickInterceptedException:
            isPresent = False
        
    transactions.drop('Deemed Execution Date', 1, inplace=True)
    transactions = transactions[transactions['Acquistion or Disposition'] == 'A']
    transactions['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format= "%Y-%m-%d")
    transactions = transactions[transactions['Transaction Date'] > cut_off_date]
    transactions.reset_index(drop=True, inplace=True)
    transactions.drop('Acquistion or Disposition', 1, inplace=True)
    transactions.drop('Form', 1, inplace=True)
    transactions['Direct or Indirect Ownership'] = transactions['Direct or Indirect Ownership'].str.replace('--','')
    transactions.to_csv(f'{ticker}_transactions.csv')

ticker = input("Enter company ticker or EXIT to exit: ").lower()
while ticker != ("exit"):
    make_csv(ticker)
    ticker = input("Enter company ticker or EXIT to exit: ").lower()