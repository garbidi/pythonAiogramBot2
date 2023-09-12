from config import URL
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
import time
import random
from bs4 import BeautifulSoup

driver= webdriver.Edge()
driver.get(URL)

# #element = driver.find_elements(By.TAG_NAME,'div')
# element= driver.find_element(By.CLASS_NAME, "oby5F TQjqQ")
# elements=element.find_elements(By.TAG_NAME,'a')
# for e in elements:
#     print(e.text)

# Ищем все элементы <div> с классом "oby5F TQjqQ"
elements = driver.find_elements(By.TAG_NAME, "div")

# Проходимся по каждому элементу <div>
for element in elements:
    # Ищем ссылки <a> внутри текущего элемента
    links = element.find_elements(By.CLASS_NAME, value="wsXlA pZeTF SUiYd")
    # Выводим текст каждой ссылки
    for link in links:
        print(link.text)

# Закрываем веб-драйвер
driver.quit()
