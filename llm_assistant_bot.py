import telebot
from telebot import types
import logging

from model_wrapper import ModelWrapper

"""
get_text_messages - обработка любого текстового сообщения, в том числе того, что отправился при нажатии кнопки.

Методы, реализующие одноименные команды телеграм-боту:
start
help
generate
checkmodel
model
"""

TOKEN = "..."
bot = telebot.TeleBot(TOKEN)

model_wrapper = ModelWrapper() # внутри класса описание

logger = logging.getLogger('my_logger')
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename='myapp.log', level=logging.INFO, format=FORMAT)
logger.info('Started')

MODEL = ''

@bot.message_handler(commands=['help'])
def help(message):
    logger.info('\help')
    help_message = """Доступны следующие команды:
/start старт бота
/model выбор модели
/checkmodel посмотреть, как модель сейчас загружена
/generate сгенерировать текст по контексту (можно использовать без введения команды)
"""
    bot.send_message(message.from_user.id, help_message)


@bot.message_handler(commands=['start'])
def start(message):
    logger.info('\start')
    bot.send_message(message.from_user.id, """Привет! Это бот, который поможет вам сгенерировать рецепты к любимым блюдам <3 Для знакомства с доступными командами введите /help
Для получения осмысленного результата требуется ввести название (или часть названия) блюда на английском языке""")


@bot.message_handler(commands=['model'])
def model(message):
    logger.info('\model')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("StatLM")
    btn2 = types.KeyboardButton("GPT")
    btn3 = types.KeyboardButton("Llama")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id, "Выберите модель для генерации", reply_markup=markup)

@bot.message_handler(commands=['type'])
def type(message):
    logger.info('\type')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Ingredients")
    btn2 = types.KeyboardButton("Recipe")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "Теперь выберите, что генерировать", reply_markup=markup)


@bot.message_handler(commands=['checkmodel'])
def checkmodel(message):
    logger.info('\checkmodel')
    bot.send_message(message.from_user.id, f"Текущая модель: {str(model_wrapper.current_model_name)}")


@bot.message_handler(commands=['generate'])
def generate(message):
    bot.send_message(message.from_user.id, "Введите название (или часть названия) блюда на английском языке")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global MODEL
    logger.info('Got massage: %s', message.text)
    print(f'<{message.text}>')
    if message.text in ['StatLM', 'GPT', 'Llama']:
        print(f'@{message.text}@')
        MODEL = message.text
        type(message)
    elif message.text in ['Ingredients', 'Recipe']:
        print(f'@{message.text}@')
        status, result = model_wrapper.load(MODEL, test_inference=True, model_type=['Ingredients', 'Recipe'].index(message.text))
        if status:
            logger.info('Model loaded successfully')
            bot.send_message(message.from_user.id, "Подгружено")
        else:
            logger.info('Got error from model: %s', result)
            bot.send_message(message.from_user.id, f"Проблемы с загрузкой модели, ниже описаны ошибки.\n{result}")
    else:
        status, result = model_wrapper.generate(message.text)
        if status:
            bot.send_message(message.from_user.id, result)
        else:
            bot.send_message(message.from_user.id, f"Проблемы с генерацией, ниже описаны ошибки.\n{result}")


bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть
# TODO: сделайте логирование запросов с указанием модели и параметров - это полезно
