import datetime
import pymysql
from aiogram import utils
from parse_city import *
from config import url


# Конфигурация базы данных
db = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='Ilbibek444',
    db='mydatabase',
    charset='utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

async def get_city_id(city):
    # Создаем SQL-запрос для получения id города из таблицы cities
    query = f"SELECT id_city FROM city WHERE city_name = '{city}'"

    try:
        # Исполняем запрос
        with db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        # Если город найден, возвращаем его id
        if result:
            return result['id_city']
        else:
            return None
    except Exception as e:
        print(f'Error: {e}')

async def update_user_city_id(user_id, city_id):
    # Создаем SQL-запрос для обновления столбца city_id в таблице users
    query = f"UPDATE users SET city_id = {city_id} WHERE id = {user_id}"

    try:
        # Исполняем запрос
        with db.cursor() as cursor:
            cursor.execute(query)
        # Подтверждаем изменения в базе данных
        db.commit()
    except Exception as e:
        print(f'Error: {e}')

async def is_city_in_table(city):
    # Создаем SQL-запрос для проверки наличия города в таблице
    query = f"SELECT * FROM city WHERE city_name = '{city}'"

    try:
        # Исполняем запрос
        with db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        # Если город найден, возвращаем True, иначе False
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f'Error: {e}')

# Функция проверки есть ли город в БД
def check_city_in_db(city_dict):
    try:
        with db.cursor() as cursor:
            # Проверка каждого города из словаря
            for city, link in city_dict.items():

                # Проверяем, есть ли город в базе данных
                cursor.execute("SELECT id_city FROM city WHERE city_name = %s", city)
                result = cursor.fetchone()

                if result is not None:
                    city_id = result['id_city']  # получаем id города из результата запроса
                    # Город уже присутствует в базе данных, обновляем ссылку
                    cursor.execute("UPDATE city SET city_url = %s WHERE id_city = %s", (link, city_id))
                else:
                    # Город отсутствует в базе данных, добавляем его с ссылкой
                    cursor.execute("INSERT INTO city (city_name, city_url) VALUES (%s, %s)", (city, link))
                    city_id = cursor.lastrowid  # получаем id только что добавленного города

                #print(f"Город {city} добавлен/обновлен в базе данных с id {city_id}")

            # Запись изменений в базу данных
            db.commit()

    finally:
        db.close()


#check_city_in_db(city_dict)

# Функция для проверки, зарегистрирован ли пользователь
def check_user_registered(user_id):
    with db.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

def get_user_data(user_id):
    with db.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()

def update_user_data(user_id, firstname, lastname, birthday):

    day, month, year = birthday.split('.')

    # Получаем текущую дату
    current_date = datetime.date.today()

    # Создаем объект даты рождения пользователя
    user_birthday = datetime.date(int(year), int(month), int(day))

    # Вычисляем возраст пользователя
    age = current_date.year - user_birthday.year - (
            (current_date.month, current_date.day) < (user_birthday.month, user_birthday.day))
    # Преобразование даты в формат "ГГГГ.ММ.ДД"
    # birthday = datetime.datetime.strptime(birthday, "%d.%m.%Y").strftime("%Y-%m-%d")
    birthday = f"{year}-{month}-{day}"
    with db.cursor() as cursor:
        sql = "UPDATE users SET firstname = %s, lastname = %s, birthday = %s, age = %s WHERE id = %s"
        cursor.execute(sql, (firstname, lastname, birthday, age, user_id))
        db.commit()


# Функция для регистрации пользователя
def register_user(user_id, firstname, lastname, birthday):
    # Разбиваем строку с датой рождения на составляющие
    day, month, year = birthday.split('.')

    # Получаем текущую дату
    current_date = datetime.date.today()

    # Создаем объект даты рождения пользователя
    user_birthday = datetime.date(int(year), int(month), int(day))

    # Вычисляем возраст пользователя
    age = current_date.year - user_birthday.year - (
                (current_date.month, current_date.day) < (user_birthday.month, user_birthday.day))
    # Преобразование даты в формат "ГГГГ.ММ.ДД"
    birthday=f"{year}-{month}-{day}"
    # Сохраняем данные в базе данных
    with db.cursor() as cursor:
        sql = "INSERT INTO users (id, firstname, lastname, birthday, age) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id,firstname, lastname, birthday, age))
        db.commit()

# Функция для удаления пользователя по ID
def delete_user_by_id(user_id):
    with db.cursor() as cursor:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        db.commit()

def find_all_cards():
    pass

