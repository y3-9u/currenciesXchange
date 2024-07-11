import telebot
from currency_converter import CurrencyConverter, RateNotFoundError
from config import TOKEN, bot
from telebot import types

currency = CurrencyConverter()
amount = 0


def ask_continue(message):
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton('Yes', callback_data='yes')
    btn_no = types.InlineKeyboardButton('No', callback_data='no')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.chat.id, 'Do you want to continue?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
def handle_callback(call):
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Enter the new amount you want to exchange:')
        bot.register_next_step_handler(call.message, summ)
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Thank you for using currenciesXchange. Goodbye!')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Hello {message.from_user.first_name}, welcome to <b>currenciesXchange</b>!\n\n'
                                      f'Enter the amount you want to exchange: ', parse_mode='html')
    bot.register_next_step_handler(message, summ)


def summ(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Only integers allowed.')
        bot.register_next_step_handler(message, summ)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_1 = types.InlineKeyboardButton('USD/EUR', callback_data='USD/EUR')
        btn_2 = types.InlineKeyboardButton('EUR/USD', callback_data='EUR/USD')
        btn_3 = types.InlineKeyboardButton('PLN/USD', callback_data='PLN/USD')
        btn_4 = types.InlineKeyboardButton('USD/PLN', callback_data='USD/PLN')
        btn_5 = types.InlineKeyboardButton('PLN/EUR', callback_data='PLN/EUR')
        btn_6 = types.InlineKeyboardButton('EUR/PLN', callback_data='EUR/PLN')
        btn_7 = types.InlineKeyboardButton('User selection', callback_data='else')
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
        bot.send_message(message.chat.id, 'Choose a pair of currencies:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'The amount must be greater than 0. Enter the new one:')
        bot.register_next_step_handler(message, summ)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'{amount} {values[0]} = {round(res, 2)} {values[1]}\n\n')
        ask_continue(call.message)
    else:
        bot.send_message(call.message.chat.id, 'Enter a pair of currencies using a slash:')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'{amount} {values[0]} = {round(res, 2)} {values[1]}.\n\n')
        ask_continue(message)
    except RateNotFoundError:
        bot.send_message(message.chat.id,
                         f'Rates not available. Please try later or use another pair of currencies.\n\n')
        ask_continue(message)
    except Exception:
        bot.send_message(message.chat.id, f'Something went wrong :(\n\n'
                                          f'Enter a pair of currencies using a slash, e.g. USD/EUR:')
        bot.register_next_step_handler(message, my_currency)


bot.polling(non_stop=True)