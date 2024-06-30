import telebot
from telebot import types  # для указание типов
import requests
from bs4 import BeautifulSoup

bot = telebot.TeleBot("7005009562:AAH5VGmjrRZGYlC1rOYr7zA1CTsp9JkeJB8", threaded=True, num_threads=300)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Узнать расписание преподавателей")
    btn2 = types.KeyboardButton("Заказать характеристику")
    btn3 = types.KeyboardButton("Подать данные на повышенную стипендию")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот-помощник кафедры ТОКБиК СГУ! \nВыбери интересующий вопрос или оставь его вручную, чтобы лишний раз не тревожить делопроизводителя".format(
                         message.from_user), reply_markup=markup)

def get_schedule(day):
    url = "https://old.sgu.ru/schedule/teacher/2494"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    schedule = []
    table = soup.find('table', {'id': 'schedule'})  # Найти таблицу с id="schedule"
    if not table:
        return "Не удалось найти таблицу с расписанием"

    # Находим все строки таблицы, кроме заголовков
    rows = table.find_all('tr')[1:]

    # Дни недели в таблице начинаются с понедельника
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    start_index = days_of_week.index(day)

    for row in rows:
        # Находим время занятий (в первой ячейке строки)
        time_cells = row.find_all('th')
        time = time_cells[0].get_text(strip=True)

        # Находим занятие для указанного дня недели
        lesson_cell = row.find_all('td')[start_index]  # +1, т.к. первая ячейка с временем

        # Проверяем, что ячейка не пустая
        if lesson_cell.get_text(strip=True):
            schedule.append(f"{time}\n{lesson_cell.get_text(strip=True)}\n")

    return "\n".join(schedule) if schedule else "Расписание не найдено"


def get_session(day):
    url = "https://old.sgu.ru/schedule/teacher/2494"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Для отладки выведем весь HTML-код страницы
    print(soup.prettify())

    schedule = []
    table = soup.find('table', {'id': 'session'})  # Найти таблицу с id="session"
    if not table:
        return "Не удалось найти таблицу с расписанием"

    rows = table.find_all('tr')  # Найти все строки таблицы

    for i in range(0, len(rows), 3):
        date = rows[i].find_all('td')[0].text.strip()
        time = rows[i].find_all('td')[1].text.strip()
        lesson_type = rows[i].find_all('td')[2].text.strip()
        subject = rows[i].find_all('td')[3].text.strip()
        group = rows[i + 1].find_all('td')[1].text.strip()
        room = rows[i + 2].find_all('td')[1].text.strip()
        schedule.append(f"{date} {time} {lesson_type}\n{subject}\n{group}\n{room}\n")

    return "\n".join(schedule) if schedule else "Расписание не найдено"


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Узнать расписание преподавателей":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Понедельник")
        btn2 = types.KeyboardButton("Вторник")
        btn3 = types.KeyboardButton("Среда")
        btn4 = types.KeyboardButton("Четверг")
        btn5 = types.KeyboardButton("Пятница")
        btn6 = types.KeyboardButton("Суббота")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id, text="Выберите день недели", reply_markup=markup)
    else:
        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        if message.text in days_of_week:
            schedule = get_schedule(message.text)
            session = get_session(message.text)
            bot.send_message(message.chat.id, text="Расписание занятий")
            bot.send_message(message.chat.id, text=schedule)
            bot.send_message(message.chat.id, text="Расписание сессии")
            bot.send_message(message.chat.id, text=session)
        else:
            bot.send_message(message.chat.id, text="Выберите день недели из предложенных кнопок.")

bot.polling(none_stop=True)