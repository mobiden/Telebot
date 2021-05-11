import telebot
from telebot import types
from collections import defaultdict


START, TITLE, PRICE, CONFIRMATION = range(4)
USER_STATE = defaultdict(lambda: START)

PRODUCTS = defaultdict(lambda:{})


token = '1812923232:AAHa40m7AutDRvcOkZ_p8NyNUStNfCYZLUk'
bot = telebot.TeleBot(token)
currencies = ['евро', 'доллар']

# статусы
def get_state(message):
    return USER_STATE[message.chat.id]

def update_state(message, state):
    USER_STATE[message.chat.id] = state

# продукция

def update_product(user_id, key, value):
    PRODUCTS[user_id][key] = value

def get_product(user_id):
    return PRODUCTS[user_id]

def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text= c, callback_data= c) for c in currencies]
    keyboard.add(*buttons)
    return keyboard

@bot.callback_query_handler(func = lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    curr, value = check_curr_value(text)
    if curr:
        bot.answer_callback_query(callback_query.id, text="Курс {} равен {}.".format(curr, value),)
    else:
        bot.send_message(chat_id=message.chat.id, text="Узнай курс")


def clocest_bank(location):
    lat = location.latitude
    lon = location.longitude
    bank_addres = "Петровка 38"
    bank_lat, bank_lon = 55.800389, 37.543710
    return bank_addres, bank_lat, bank_lon

def check_curr(message):
    for c in currencies:
        if c in message.text.lower():
            return True
    return False

def check_curr_value(text):
    currency_value = {'евро': 90, 'доллар': 80}
    for currency, value in currency_value.items():
        if currency in text.lower():
            return currency, value
    return None, None

@bot.message_handler(content_types=['location'])
def handle_location(message):
    print (message.location)
    image = open('77.jpg', 'rb')
    bank_addres, bank_lat, bank_lon = clocest_bank(message.location)
    bot.send_photo(message.chat.id, image, caption="Ближайший банк {}".format(bank_addres))
    bot.send_location(message.chat.id, bank_lat, bank_lon)


@bot.message_handler(commands = ['rate'])
@bot.message_handler(func = check_curr)
def handle_message(message):
    print (message)
    curr, value = check_curr_value(message.text)
    keyboard = create_keyboard()
    if curr:
        bot.send_message(chat_id=message.chat.id, text="Курс {} равен {}.".format(curr, value),
                         reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text="Узнай курс", reply_markup=keyboard)




@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_message(message):
    print (message.text)
    bot.send_message(chat_id=message.chat.id, text="Напиши название")
    update_state(message, TITLE)

@bot.message_handler(func=lambda message: get_state(message) == TITLE)
def handle_title(message):
    # название
    print (message.text)
    update_product(message.chat.id, 'title', message.text)
    bot.send_message(chat_id=message.chat.id, text="Укажи цену")
    update_state(message, PRICE)

@bot.message_handler(func=lambda message: get_state(message) == PRICE)
def handle_price(message):
    # цена
    print (message.text)
    update_product(message.chat.id, 'price', message.text)
    product = get_product(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text="Опубликовать объявление? {}".format(product))
    update_state(message, CONFIRMATION)

@bot.message_handler(func=lambda message: get_state(message) == CONFIRMATION)
def handle_confirmation(message):
    # подтверждение
    if 'yes' in message.text.lower() or 'да' in message.text.lower():
        bot.send_message(chat_id=message.chat.id, text="Объявление опубликовано")
    print (message.text)
    update_state(message, START)


bot.polling()
