import logging
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import bot, dp, url
from db import check_user_registered, get_user_data,update_user_data, \
    register_user, check_city_in_db, delete_user_by_id, is_city_in_table,\
    update_user_city_id,get_city_id
from parse_city import *

# Установка уровня логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# Определение стейтов для FSM (Finite State Machine)
class RegistrationForm(StatesGroup):
    waiting_for_firstname = State()
    waiting_for_lastname = State()
    waiting_for_birthday = State()

#Определение состояний через StatesGroup
class UpdateForm(StatesGroup):
    waiting_for_update_firstname=State()
    waiting_for_update_lastname=State()
    waiting_for_update_birthday=State()

# Обработчик ответа на вопрос о фамилии
@dp.message_handler(state=[UpdateForm.waiting_for_update_firstname, UpdateForm.waiting_for_update_firstname])
async def process_update_firstname(message: types.Message, state: FSMContext):
    # Проверяем, в каком состоянии находится пользователь
    if await state.get_state() == UpdateForm.waiting_for_update_firstname.state:
        # Сохраняем ответ в состояние
        await state.update_data(firstname=message.text)
        # Задаем следующий вопрос
        await UpdateForm.waiting_for_update_lastname.set()
        await message.reply("Отлично! Теперь введи свое имя:")
    else:
        # Сохраняем ответ в состояние
        await state.update_data(firstname=message.text)
        # Получаем остальные данные пользователя из состояния
        data = await state.get_data()
        lastname = data.get('lastname')
        birthday = data.get('birthday')

        # Обновляем данные пользователя в базе данных
        update_user_data(message.from_user.id, firstname=message.text, lastname=lastname, birthday=birthday)

        # Завершаем процесс редактирования профиля
        await state.finish()
        await my_profile_info(types.CallbackQuery.from_user(callback_query=False, user_id=message.from_user.id))

# Обработчик ответа на вопрос об имени
@dp.message_handler(state=UpdateForm.waiting_for_update_lastname)
async def process_update_lastname(message: types.Message, state: FSMContext):
    # Сохраняем ответ в состояние
    await state.update_data(lastname=message.text)
    # Задаем следующий вопрос
    await UpdateForm.waiting_for_update_birthday.set()
    await message.reply("Отлично! Введите дату своего рождения в формате ДД.ММ.ГГГГ:")

# Обработчик ответа на вопрос о дате рождения
@dp.message_handler(state=UpdateForm.waiting_for_update_birthday)
async def process_update_birthday(message: types.Message, state: FSMContext):
    # Сохраняем ответ в состояние
    await state.update_data(birthday=message.text)

    # Извлекаем данные из состояния
    data = await state.get_data()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birthday = data.get('birthday')
    user_id=message.from_user.id
    # Записываем данные в базу данных
    update_user_data(user_id, firstname, lastname, birthday)

    # Завершаем процесс регистрации
    await state.finish()

    # Создаём кнопку "Мой профиль"
    profile_button = InlineKeyboardButton("Мой профиль", callback_data='my_profile_info')
    keyboard = InlineKeyboardMarkup().add(profile_button)

    await message.reply("Поздравляю, вы успешно изменили данные!", reply_markup=keyboard)

@dp.callback_query_handler(text='update_data')
async def update(callback_query: types.CallbackQuery):
    # Запускаем процесс регистрации
    await UpdateForm.waiting_for_update_firstname.set()
    await bot.send_message(callback_query.from_user.id, "Редактируйте данные. Введите свою фамилию:")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Проверяем, зарегистрирован ли пользователь
    if check_user_registered(message.from_user.id):
        # Создаем кнопку "Мой профиль"
        profile_button = InlineKeyboardButton("Мой профиль", callback_data='my_profile_info')
        keyboard = InlineKeyboardMarkup().add(profile_button)

        button = InlineKeyboardButton('Найти мероприятие', callback_data='find_event')
        keyboard.add(button)

        # Если пользователь уже зарегистрирован, выводим ему приветственное сообщение с кнопкой "Мой профиль"
        await message.reply(f"""Привет, {message.from_user.first_name}!
Мы рады снова видеть тебя в нашей таверне!

Не знаешь чем занять себя? 
Сходи к доске объявлений. Ты обязатедбно найдешь для себя что-нибудь подходящее!""", reply_markup=keyboard)
        #await message.answer("Главное меню", reply_markup=get_main_menu_keyboard())
    else:
        # Если пользователь не зарегистрирован, запускаем процесс регистрации
        # await RegistrationForm.waiting_for_firstname.set()
        # await message.reply("Привет! Для регистрации введи свою фамилию:")
        register_button = InlineKeyboardButton("Регистрация", callback_data='register')
        keyboard = InlineKeyboardMarkup().add(register_button)
        await bot.send_message(message.from_user.id,
                               """Приветствую тебя, охотник! 

Чтобы ты мог погружаться в мир культуры, нам необходимо знать, кто ты, ибо мы не делаем ставку на инопланетных пришельцев 🛸. 

Так что, скажи нам, кто ты, и мы подарим тебе массу безудержных фантазий! 

Регистрируйся и пускай волна великого захлестнет тебя!""",
                               reply_markup=keyboard)

@dp.callback_query_handler(text='find_event')
async def find_event(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите название города')

# Обработчик ввода города
@dp.message_handler()
async def handle_city(message: types.Message):
    city = message.text

    # Проверяем наличие города в таблице
    if await is_city_in_table(city):
        # Получите id города из таблицы cities
        city_id = await get_city_id(city)  # Здесь вам нужно написать свою функцию для получения id города
        await update_user_city_id(message.from_user.id, city_id)
        await message.answer(f'Город {city} найден в таблице и id города {city} добавлен в таблицу users!')
    else:
        await message.answer(f'Город {city} не найден в таблице.')

@dp.callback_query_handler(text='edit_profile')
async def edit_profile_info(callback_query: types.CallbackQuery):
    # Получаем информацию о пользователе из базы данных
    user_data = get_user_data(callback_query.from_user.id)

    # Проверяем наличие ключей в словаре user_data и формируем сообщение с текущими данными пользователя
    # с предупреждением, если ключи отсутствуют
    if 'firstname' in user_data and 'lastname' in user_data and 'birthday' in user_data:
        birthday=user_data['birthday']
        year, month, day= str(birthday).split('-')
        info_text = f"""Текущие данные о профиле:
Фамилия: {user_data['firstname']}
Имя: {user_data['lastname']}
Дата рождения: {day}.{month}.{year}"""
    else:
        info_text = "Текущие данные о профиле недоступны."

    # Отправляем сообщение с текущими данными о профиле и кнопкой "Отмена"
    await bot.send_message(callback_query.from_user.id, info_text,
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton("Изменить", callback_data='edit_profile_confirm'),
                               InlineKeyboardButton("Отмена", callback_data='cancel_delete')
                           ))
# Работает!!!
@dp.callback_query_handler(text='edit_profile_confirm')
async def edit_profile_confirm(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите новые данные о профиле. Введите Вашу фамилию:")
    await UpdateForm.waiting_for_update_firstname.set()

# @dp.callback_query_handler(text='cancel_edit_profile')
# async def cancel_edit_profile(callback_query: types.CallbackQuery):
#     await my_profile(callback_query)

@dp.callback_query_handler(text='delete_profile')
async def delete_profile(callback_query: types.CallbackQuery):
    if check_user_registered(callback_query.from_user.id):
        # Создаем кнопки "Подтвердить удаление" и "Отмена"
        confirm_button = InlineKeyboardButton("Подтвердить удаление", callback_data='confirm_delete')
        cancel_button = InlineKeyboardButton("Отмена", callback_data='cancel_delete')
        keyboard = InlineKeyboardMarkup().add(confirm_button, cancel_button)

        await bot.send_message(callback_query.from_user.id, "Вы действительно хотите удалить свой профиль?", reply_markup=keyboard)
    else:
        # Создаем кнопку "Регистрация"
        register_button = InlineKeyboardButton("Регистрация", callback_data='register')
        keyboard = InlineKeyboardMarkup().add(register_button)

        await bot.send_message(callback_query.from_user.id,
                               "Ваш аккаунт уже был удален. Пройдите процедуру регистрации заново.",
                               reply_markup=keyboard)

@dp.callback_query_handler(text='confirm_delete')
async def confirm_delete(callback_query: types.CallbackQuery):
    # Удаляем пользователя
    delete_user_by_id(callback_query.from_user.id)

    await bot.send_message(callback_query.from_user.id, "Ваш профиль был успешно удален.")

@dp.callback_query_handler(text='cancel_delete')
async def cancel_delete(callback_query: types.CallbackQuery):
    # Возвращаемся в "Мой профиль"
    await my_profile_info(callback_query)


@dp.callback_query_handler(text='cancel')
async def cancel(callback_query: types.CallbackQuery):
    # Проверяем, зарегистрирован ли пользователь
    if check_user_registered(callback_query.from_user.id):
        await bot.send_message(callback_query.from_user.id, "Удаление профиля отменено.")
    else:
        # Создаем кнопку "Регистрация"
        register_button = InlineKeyboardButton("Регистрация", callback_data='register')
        keyboard = InlineKeyboardMarkup().add(register_button)

        await bot.send_message(callback_query.from_user.id,
                               "Ваш аккаунт уже был удален. Пройдите процедуру регистрации заново.",
                               reply_markup=keyboard)

@dp.callback_query_handler(text='register')
async def register(callback_query: types.CallbackQuery):
    # Запускаем процесс регистрации
    await RegistrationForm.waiting_for_firstname.set()
    await bot.send_message(callback_query.from_user.id, "Пройдите процесс регистрации. Введите свою фамилию:")


# Переход в главное меню
@dp.callback_query_handler(text='my_main_menu')
async def my_main_menu(callback_query: types.CallbackQuery):
    profile_button = InlineKeyboardButton("Мой профиль", callback_data='my_profile_info')
    keyboard = InlineKeyboardMarkup().add(profile_button)

    # Выводим ему приветственное сообщение с кнопкой "Мой профиль"
    await bot.send_message.reply(f"""Тихий шелест листьев. Это ГЛАВНОЕ МЕНЮ""", reply_markup=keyboard)

@dp.callback_query_handler(text='my_profile_info')
async def my_profile_info(callback_query: types.CallbackQuery):
    # Получаем информацию о пользователе из базы данных
    user_data = get_user_data(callback_query.from_user.id)

    # Проверяем наличие ключей в словаре user_data и формируем сообщение с информацией о пользователе
    # с предупреждением, если значения отсутствуют или равны None
    if 'lastname' in user_data and user_data['lastname'] is not None:
        lastname = user_data['lastname']
    else:
        lastname = "Нет данных"

    if 'firstname' in user_data and user_data['firstname'] is not None:
        firstname = user_data['firstname']
    else:
        firstname = "Нет данных"

    if 'birthday' in user_data and user_data['birthday'] is not None:
        birthday = user_data['birthday']
    else:
        birthday = "Нет данных"

    year, month, day = str(birthday).split('-')

    info_text = f"""Фамилия: {firstname}
Имя: {lastname}
Дата рождения: {day}.{month}.{year}"""

    # Создаем кнопку "Редактировать профиль"
    delete_button = InlineKeyboardButton("Удалить профиль", callback_data='delete_profile')
    edit_button = InlineKeyboardButton("Редактировать профиль", callback_data='edit_profile')
    keyboard = InlineKeyboardMarkup().add(edit_button, delete_button)

    await bot.send_message(callback_query.from_user.id, text=info_text, reply_markup=keyboard)

# Обработчик ответа на вопрос о фамилии
@dp.message_handler(state=[RegistrationForm.waiting_for_firstname, RegistrationForm.waiting_for_firstname])
async def process_firstname(message: types.Message, state: FSMContext):
    # Проверяем, в каком состоянии находится пользователь
    if await state.get_state() == RegistrationForm.waiting_for_firstname.state:
        # Сохраняем ответ в состояние
        await state.update_data(firstname=message.text)
        # Задаем следующий вопрос
        await RegistrationForm.waiting_for_lastname.set()
        await message.reply("Отлично! Теперь введи свое имя:")
    else:
        # Сохраняем ответ в состояние
        await state.update_data(firstname=message.text)
        # Получаем остальные данные пользователя из состояния
        data = await state.get_data()
        lastname = data.get('lastname')
        birthday = data.get('birthday')

        # Обновляем данные пользователя в базе данных
        update_user_data(message.from_user.id, firstname=message.text, lastname=lastname, birthday=birthday)

        # Завершаем процесс редактирования профиля
        await state.finish()
        await my_profile_info(types.CallbackQuery.from_user(callback_query=False, user_id=message.from_user.id))

# Обработчик ответа на вопрос об имени
@dp.message_handler(state=RegistrationForm.waiting_for_lastname)
async def process_lastname(message: types.Message, state: FSMContext):
    # Сохраняем ответ в состояние
    await state.update_data(lastname=message.text)
    # Задаем следующий вопрос
    await RegistrationForm.waiting_for_birthday.set()
    await message.reply("Отлично! Введите дату своего рождения в формате ДД.ММ.ГГГГ:")

# Обработчик ответа на вопрос о дате рождения
@dp.message_handler(state=RegistrationForm.waiting_for_birthday)
async def process_birthday(message: types.Message, state: FSMContext):
    # Сохраняем ответ в состояние
    await state.update_data(birthday=message.text)

    # Извлекаем данные из состояния
    data = await state.get_data()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birthday = data.get('birthday')

    # Записываем данные в базу данных
    register_user(message.from_user.id, firstname, lastname, birthday)

    # Завершаем процесс регистрации
    await state.finish()

    # Создаём кнопку "Мой профиль"
    button = InlineKeyboardButton('Найти мероприятие', callback_data='find_event')
    profile_button = InlineKeyboardButton("Мой профиль", callback_data='my_profile_info')
    keyboard = InlineKeyboardMarkup().add(profile_button)
    keyboard.add(button)

    await message.reply("Поздравляю, вы успешно зарегистрированы!", reply_markup=keyboard)

def check_city():
    p = ParseWebBro(url)
    page_code = p.open_page_today()
    p.del_connect()
    city_dict = AnalyzeCode(page_code).collect_event_today()
    check_city_in_db(city_dict)

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)


