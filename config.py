from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Инициализация бота и диспетчера
bot = Bot(token="6594265177:AAHTFx_n1PHVANsRr57rSPKuCjxoxQUh6r4")
dp = Dispatcher(bot, storage=MemoryStorage())

url='https://afisha.yandex.ru'
DRIVER_PATH='C:/Users/iscka/pythonProject/pythonTeleBotT/chromedriver'


async def send_list(message:types.Message):
    pass
