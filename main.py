# -*- coding: utf-8 -*-

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import telebot
import requests
import json
from fake_useragent import UserAgent
import sys

token = '1436931925:AAE8NEZhF-2UBMbGeM1JX22nSXAoAG6yCLI' # telegram bot token
name = 'ZavozBot' # telegram bot name
chat_id = '-1001236908133' # telegram chat id

removed = [[], [], []]

config = {
    'name': name,
    'token': token,
    'chat_id': chat_id
}
percent = -5
percent = float(percent)

filtercount = 30
filtercount = str(filtercount)
client = telebot.TeleBot(config['token'])

def send(msg):
    client.send_message(chat_id=config['chat_id'], text=msg)

# Price scrap by median_price
def jsonparse(itemurl):
    url1 = itemurl
    url2 = url1[47:]
    standard_url = r'https://steamcommunity.com/market/priceoverview/?currency=1&appid=730&market_hash_name='
    ready_url = standard_url + url2
    response = requests.get(ready_url, headers={'User-Agent': UserAgent().chrome})
    j = response.text
    if j == 'null':
        print('Await...')
        time.sleep(100)
        response = requests.get(ready_url, headers={'User-Agent': UserAgent().chrome})
        j = response.text
        if j == 'null':
            print('Await...')
            time.sleep(300)
            response = requests.get(ready_url, headers={'User-Agent': UserAgent().chrome})
            j = response.text
            if j == 'null':
                print('Await...')
                time.sleep(300)
                response = requests.get(ready_url, headers={'User-Agent': UserAgent().chrome})
                j = response.text
                parsed_string = json.loads(j)
                steamreaprice = parsed_string['median_price']
            else:
                parsed_string = json.loads(j)
                steamreaprice = parsed_string['median_price']
        else:
            parsed_string = json.loads(j)
            steamreaprice = parsed_string['median_price']
    else:
        pass
    parsed_string = json.loads(j)
    steamreaprice = parsed_string['median_price']
    steamrealprice = steamreaprice.replace("$", "")
    steamrealprice = float(steamrealprice)
    steamrealprice = steamrealprice*0.87
    return steamrealprice

# Load webdriver
def htmlRequest():
    global driver
    print('Initialization')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# Steam auth (Read login and password from login.txt)
def steamauth():
    global url
    with open('config.txt') as file:
        loginSteam = file.readline()
        passwordSteam = file.readline()
        url = file.readline()
        if loginSteam == '':
            print('Login or password incorrect [login.txt]\nChange it and try again')
            sys.exit()
        else:
            pass
    file.close()
    try:
        driver.get('https://tradeback.io/ru/comparison')
        username = driver.find_element_by_id('steamAccountName')
        password = driver.find_element_by_id('steamPassword')
        loginbtn = driver.find_element_by_id('imageLogin')
        print('Logging in steam acc...')
        try:
            username.send_keys(loginSteam)
            password.send_keys(passwordSteam)
        except:
            loginbtn.click()
        time.sleep(5)
    except:
        driver.get('https://tradeback.io/ru/comparison')
        time.sleep(5)
        username = driver.find_element_by_id('steamAccountName')
        password = driver.find_element_by_id('steamPassword')
        loginbtn = driver.find_element_by_id('imageLogin')
        print('Logging in steam acc...')
        try:
            username.send_keys(loginSteam)
            password.send_keys(passwordSteam)
        except:
            loginbtn.click()
        time.sleep(5)

# Apply number of sales filter (100 default)
def filters(filtercount):
    print('Applying filters')
    filters = driver.find_element_by_id('more-filters')
    filters.click()
    time.sleep(2)
    filterinput = driver.find_element_by_css_selector('[data-key="s"]')
    filterinput.send_keys(filtercount)
    time.sleep(5)
    exit = driver.find_element_by_class_name('iziModal-button')
    exit.click()

# Load page with table
def reloadhtml():
    driver.get(url)
    print('Opening table')
    time.sleep(2)
    driver.get(url)
    time.sleep(8)
    time.sleep(1)
    sort = driver.find_element_by_css_selector('div.column-profit')
    sort.click()
    time.sleep(4)

# Take data from tradeback table
def parse():
    print('Data collection...')
    bigdata_name = []
    bigdata_tradeitprice = []
    bigdata_steamprice = []
    requiredHtml = driver.page_source
    soup = BeautifulSoup(requiredHtml, 'html5lib')
    table = soup.find('table', attrs={'class': 'price-table'})
    table_body = table.find('tbody')
    trs = table_body.find_all('tr')
    bigdata = [[], [], []]
    hrefs = []
    for tds in trs:
        namefield = tds.find('td', {'class': ['copy-name']})
        name = namefield.text
        bigdata[0].append(name)
        try:
            tprice = tds.find('td', {'class': ['field-price'], 'data-column': ['first']})
            divs = tprice.find('div', {'class': ['first-line']})
            tradeitprice = divs.find('span', {'class': ['price usd']}).text
            bigdata[1].append(tradeitprice)
        except:
            tprice = tds.find('td', {'class': ['field-price'], 'data-column': ['first']})
            divs = tprice.find('div', {'class': ['first-line']})
            tradeitprice = divs.find('span', {'class': ['price usd unavailable']}).text
            tradeitprice = float(tradeitprice)
            bigdata[1].append(tradeitprice)
        rows = tds.findAll('td', {'data-link-key': ['steamcommunity']})
        for col in rows:
            itemurl = col.find('a').get('href')
            hrefs.append(itemurl)
        for col in rows:
            columns = col.findAll('div', {'class': ['last-sales-container']})
            for divs in columns:
                salelist = divs.findAll('div', {'class': ['last-sales-list']})
                for parm in salelist:
                    price = parm.findAll('div', {'class': ['last-sales-row prices title']})
                    for pricelist in price:
                        prices = pricelist.findAll('span')[2]
                        div = prices.findAll('div')[1]
                        text = div.text
                        text = text.replace("$", "")
                        steamprice = float(text)
                        steamprice = round(steamprice, 2)
                        bigdata[2].append(steamprice)
    bigdata_name = bigdata[0]
    bigdata_tradeitprice = bigdata[1]
    bigdata_steamprice = bigdata[2]
    bigdata = [[], [], []]
    removed_name = removed[0]
    removed_tradeitprice = removed[1]
    removed_steamprice = removed[2]
    value = len(bigdata_name)
    for i in range(value):
        if bigdata_name[i] not in removed_name and bigdata_tradeitprice[i] not in removed_tradeitprice and bigdata_steamprice[i] not in removed_steamprice:
            bigdata[0].append(bigdata_name[i])
            bigdata[1].append(bigdata_tradeitprice[i])
            bigdata[2].append(bigdata_steamprice[i])
        else:
            pass
    removed_name = []
    removed_tradeitprice = []
    removed_steamprice = []
    value = len(bigdata[0])
    count = 0
    for i in range(value):
        old = bigdata[1][i]
        new = float(old)
        bigdata[1][i] = new
    for i in range(value):
        link = hrefs[i]
        t = bigdata[1][i]
        s = bigdata[2][i]
        diff = float(((s-t)*100)/t)
        count += 1
        if diff > percent:
            med = jsonparse(link)
            difference = float(((med-t)*100)/t)
            if difference > percent:
                t = str(t)
                ctext = '$'
                actext = t + ctext
                dtext = str(bigdata[0][i])
                textlist = []
                textlist.append(dtext)
                textlist.append(actext)
                s = ' '
                message = s.join(textlist)
                send(message)
                removed[0].append(bigdata[0][i])
                removed[1].append(bigdata[1][i])
                removed[2].append(bigdata[2][i])
            else:
                pass
        else:
            pass
def main():
    htmlRequest()
    steamauth()
    reloadhtml()
    filters(filtercount)
    while True:
        try:
            parse()
        except:
            print('Unexpected error')

if __name__ == '__main__':
    main()

