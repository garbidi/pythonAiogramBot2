from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
import time
import random
from bs4 import BeautifulSoup
from config import url

class ParseWebBro:
    def __init__(self, url, bot=None):
        self.driver = webdriver.Edge()
        self.url = url
        self.bot = bot

    def del_connect(self):
        self.driver.close()

    def open_page_today(self):
        self.driver.get(self.url)
        #time.sleep(25) #Время успеть ввести капчу!
        button_city = self.driver.find_element(by=By.CLASS_NAME, value= "grid__container").find_element(By.TAG_NAME, 'button')
        #Кликает на кнопку показать далее)
        try:
            button_city.click()
            time.sleep(random.randint(2, 5))
        except ElementNotInteractableException:
            print('Страница полностью загружена!')

        return self.driver.page_source

class AnalyzeCode:
    def __init__(self, code=None):
        self.code = code

    def collect_event_today(self):
        soup = BeautifulSoup(self.code, 'lxml')
        links=soup.find_all(attrs={'class': 'CityListItem-rt6wcj-4 gVbDqc'})
        cards = soup.find_all(attrs={'class': 'CityListItem-rt6wcj-4 gVbDqc'})
        city_dict = {}  # словарь для хранения городов и ссылок

        if not bool(len(cards)):
            return None
        for card,link in zip(cards,links):
            card_title = card.find(attrs={'data-component': 'Text.Description'}).text
            href = url + link.get('href')
            city_dict[card_title] = href
            #print(f"{card_title}: {href}")
        return city_dict
        # for card in cards:
        #     card_title = card.find(attrs={'data-component': 'Text.Description'}).text
        #     #card_detail = card.find(attrs={'href': ''}).text
        #     #one, two = card_detail
        #     print(f'''{card_title}''')
        # for link in links:
        #     href=url+link.get('href')
        #     print(href)

if __name__ == '__main__':
    #url = 'https://afisha.yandex.ru'
    p = ParseWebBro(url)
    page_code = p.open_page_today()
    p.del_connect()
    AnalyzeCode(page_code).collect_event_today()
