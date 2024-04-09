import telebot
from Yan import *
from peremen import *
from database import *


bot = telebot.TeleBot(API)


def create_keyboard(options):
    buttons = []
    for opt in options:
        buttons.append(telebot.types.KeyboardButton(text=opt))

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard




@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id


    bot.send_message(user_id, text='Привет, я - говорящий бот. Ты можешь выбрать комманду /tts'
                                   ', написать текст и я отправлю тебе голосовое сообщение с этим текстом',
                     reply_markup=create_keyboard(['/tts']))


def is_tts_symbol_limit(message, text):
    global all_symbols
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text)


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    create_table()
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)


def tts(message):
    user_id = message.from_user.id
    text = message.text

    # Проверка, что сообщение действительно текстовое
    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

        # Считаем символы в тексте и проверяем сумму потраченных символов
    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return

    # Записываем сообщение и кол-во символов в БД
    insert_row(user_id, text, text_symbol)

    # Получаем статус и содержимое ответа от SpeechKit
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)


if __name__ == '__main__':
    bot.infinity_polling()