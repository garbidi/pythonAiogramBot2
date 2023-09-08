import pymysql
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Инициализация бота и диспетчера
bot = Bot(token="6594265177:AAHTFx_n1PHVANsRr57rSPKuCjxoxQUh6r4")
dp = Dispatcher(bot, storage=MemoryStorage())

# Конфигурация базы данных
db = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='Ilbibek444',
    db='mydatabase',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
