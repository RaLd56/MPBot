from selenium import webdriver #для парсинга
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import mysql.connector #для бдшки
import telebot
import time


class Good:
    def __init__(self, name, price, stock, info, shipping):
        self.name = name
        self.price = price
        self.stock = stock
        self.info = info
        self.shipping = shipping
    def __str__(self):
        return f'{self.name}, {self.price}, {self.stock}, {self.info}'

goods_list=[]

#ссылки, указанные пользователем(сейчас для примера, на деле заполняются ботом)
user_links_ozon=['https://www.ozon.ru/product/realistichnyy-rezinovyy-chlen-falloimitator-dlya-zhenshchin-i-muzhchin-dildo-na-prisoske-1618714153', 'https://www.ozon.ru/product/riboksin-tabletki-pokrytye-plenochnoy-obolochkoy-200-mg-50-sht-648571104/', 'https://www.ozon.ru/product/kaliya-orotat-tabletki-0-5-g-20-sht-1180243965'] 
user_links_wb=['https://www.wildberries.ru/catalog/238394541/detail.aspx', 'https://www.wildberries.ru/catalog/172203445/detail.aspx', 'https://www.wildberries.ru/catalog/244870640/detail.aspx', 'https://www.wildberries.ru/catalog/147884467/detail.aspx'] 
user_links_ali=['https://aliexpress.ru/item/1005004141553912.html','https://aliexpress.ru/item/4000378795761.html', 'https://aliexpress.ru/item/32978788459.html'] 



driver = webdriver.Chrome()
pattern_price = r'(\d+[.,\d]*)\s*₽'  
counter = 0
for url in user_links_ozon:
    name =''
    price = 0
    stock = False
    info = ''
    shipping = 0

    

    driver.get(url)
    time.sleep(5)


    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    age_confirmation = soup.find('div', {'data-widget': 'userAdultModal'})
    out_of_stock = soup.find('div', {'data-widget': 'webOutOfStock'})
    if age_confirmation:
        adult_good = True
        #ЛОГИКА ДЛЯ БОТА(пишем, что 18+ товары не парсим + указываем, о каком товаре речь)
        name = '18+ товар'
        price = '-'
        stock = False
        info = '-'
    elif out_of_stock:
        info = out_of_stock.find('h2').get_text().strip()
        stock = False
        out_of_stock_content = out_of_stock.get_text(separator=' ', strip=True)
        pattern_name = r'₽\s*(.*?)\.'   

        match_price = re.search(pattern_price, out_of_stock_content)
        if match_price:
            price = match_price.group(1)  # Цена
        
        match_name = re.search(pattern_name, out_of_stock_content)
        if match_name:
            name = match_name.group(1).strip()
        #ЛОГИКА ДЛЯ БОТА(пишем, что товар недоступен + указываем причину(переменная info))

    else:
        name = soup.find('div', {'data-widget': 'webProductHeading'}).find('h1').get_text(strip=True)
        sale_widget = soup.find('div', {'data-widget': 'webSale'}).get_text(separator=' ', strip=True)
        match_price = re.search(pattern_price, sale_widget)
        if match_price:
            price = match_price.group(1)
        stock = True
        info = '-'
        good = Good(name, price, stock, info, shipping)
        goods_list.append(good)

for url in user_links_wb:
    name =''
    price = 0
    stock = False
    info = ''
    shipping=0
    
    driver.get(url)
    time.sleep(5)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    age_confirmation = soup.find('div', {'class': 'popup popup-confirm-age shown'})
    if age_confirmation:
        adult_good = True
        #ЛОГИКА ДЛЯ БОТА(спрашиваем, точно ли есть 18)
        confirm_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Да, мне есть 18 лет')]")
        print(confirm_button)
        confirm_button.click()
        

    out_of_stock = soup.find('span', {'class': 'sold-out-product__text'})
    if out_of_stock:
        info = out_of_stock.get_text().strip()
        stock = False
        price = '-' #возможно, стоит брать последнюю известную цену из БД
        #ЛОГИКА ДЛЯ БОТА(пишем, что товар недоступен + указываем причину(переменная info))
    else:
        stock = True
        info = '-'
    name = soup.find('h1', {'class': 'product-page__title'}).get_text(strip=True)
    sale_widget = soup.find('ins', {'class': 'price-block__final-price wallet'}).get_text(strip=True)
    match_price = re.search(pattern_price, sale_widget)
    if match_price:
        price = match_price.group(1)

    good = Good(name, price, stock, info, shipping)
    goods_list.append(good)
    
for url in user_links_ali:
    name =''
    price = 0
    stock = False
    info = ''
    shipping=[]

    driver.get(url)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    age_confirmation = soup.find('span', {'class': 'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography-Primary__base__1xop0e snow-ali-kit_Typography__strong__1shggo snow-ali-kit_Typography__sizeTextXXL__1shggo'})
    if soup.find('div', {'class': "SnowPageNotFound_SnowPageNotFound__infoBlock__hc1bc"}):
        name =''
        price = 0
        stock = False
        info = 'Такого товара нет'
        shipping=[]
    elif age_confirmation:
        stock = False
        name = 'Товар 18+'
        price = '-'
        info = '-'
        time.sleep(1)
    else: 
        price = soup.find('div', {'class': "HazeProductPrice_SnowPrice__mainS__1jbkl"}).get_text().strip().replace(' ₽', '')
        name = soup.find('div', {'class': "HazeProductGridItem_HazeProductGridItem__item__1xcur"}).find('h1').get_text().strip()
        shipping_prices = soup.findAll('span', {'class': "RedProductDelivery_DeliveryMethodItem__price__1rxa6"})
        for shipping_price in shipping_prices:
            shipping.append((shipping_price.get_text().strip().replace(' ₽', '')))
        stock = True
        info = '-'

    good = Good(name, price, stock, info, shipping)
    goods_list.append(good)   


for good in goods_list:
    print(good)

