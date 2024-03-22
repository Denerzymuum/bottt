import telebot
from transformers import AutoTokenizer
from configg import API_TOKEN, max_tokens_in_task
from gptt import *
from databasee import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="a",  # append mode
)

bot = telebot.TeleBot(API_TOKEN)

COMMAND_TO_SUBJECT = {
                        "/math": "математика",
                        "/physic": "физика",
                        "artwork": "рисование",
                     }

COMMAND_TO_LEVEL = {
                        "/beginner": "начинающий",
                        "/advanced": "продвинутый",
                     }

create_db()
create_table()



def count_tokens(text):  # Подсчет токенов в сообщении пользоватея
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
    return len(tokenizer.encode(text))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот-помощникь для решения задач по разным предметам "
                                      "Выбери, используя команды, предмет, по которому тебе требуется помощь "
                                      "Математика - /math "
                                      "Физика - /physic "
                                      "удалить все свои данные - /delete ")


@bot.message_handler(commands=["delete"])
def deleting(message):
    user_id = int(message.from_user.id)
    logging.info(f" {user_id} Удалил свои данные")
    delete_data(user_id)  # вызывает функцию, удаляющую данные по юзер айди


@bot.message_handler(commands=["deleteall"])
def deleting(message):
    delete_data_all()  # вызывает функцию, удаляющую все данные


@bot.message_handler(commands=["math", "physic"])
def choose_subject(message):
    subject_from_user = message.text  # Берём текст команды, введённой пользователем. Например, help_with_maths
    subject = COMMAND_TO_SUBJECT.get(subject_from_user)  # Если использовать get, ошибки не будет
    user_id = int(message.from_user.id)
    rows = select_data(user_id)
    if rows is not None:
        column = 'subject'
        value = subject
        update_data(user_id, column, value)
    else:
        column = 'subject'
        value = subject
        insert_data(user_id, column, value)
    bot.send_message(message.chat.id, "теперь выбери уровень сложности ответов: "
                                      "профи - /advanced "
                                      "новичок - /beginner ")
    logging.info(f" {user_id} Выбрал предмет")


@bot.message_handler(commands=["beginner", "advanced"])
def choose_level(message):
    level_from_user = message.text  # Берём текст команды, введённой пользователем. Например, help_with_maths
    level = COMMAND_TO_LEVEL.get(level_from_user)  # Если использовать get, ошибки не будет
    user_id = int(message.from_user.id)
    rows = select_data(user_id)
    if rows is not None:
        column = 'level'
        value = level
        update_data(user_id, column, value)
    else:
        column = 'level'
        value = level
        insert_data(user_id, column, value)
    bot.send_message(message.chat.id, "теперь можешь писать свой вопрос к нейросети")


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['text'])
def task(message):
    user_id = int(message.from_user.id)
    rows = select_data(user_id)
    try:
        subject = rows[0][2]
    except:
        bot.send_message(message.chat.id, "Пожалуйста, выбери предмет, нажав на кнопку")
        return
    level = rows[0][3]
    if not subject:  # Если предмет не был указан, просим вернуться к предыдущему шагу
        bot.send_message(message.chat.id, "Пожалуйста, выбери предмет, нажав на кнопку")
        return
    if not level:  # Если уровень не был указан, просим вернуться к предыдущему шагу
        bot.send_message(message.chat.id, "Пожалуйста, выбери уровень сложности")
        return
    user_task = message.text  # Извлекаем текст задачи
    if rows is not None:
        column = 'task'
        value = user_task
        update_data(user_id, column, value)
    else:
        column = 'task'
        value = user_task
        insert_data(user_id, column, value)
    rows = select_data(user_id)
    user_content = rows[0][4]
    global answer
    if count_tokens(user_content) > max_tokens_in_task:
        bot.send_message(message.chat.id, f"твой вопрос cлишком длинный: {count_tokens(user_content)} "
                                          f"токенов (доступно 500)")
    else:
        bot.reply_to(message, "Генерация ответа...")
        if (user_content.lower() != "продолжить ответ") or ('answer' not in globals()):
            answer = ""
            column = 'answer'
            value = answer
            update_data(user_id, column, value)
        try:
            rows = select_data(user_id)
            answer = str(rows[0][5])
            resp = gpt_generate(user_content, answer, subject, level)
        except requests.RequestException:
            bot.reply_to(
                message,"Произошла ошибка! Попробуйте ещё раз.")
            return

        if resp.status_code == 200 and 'choices' in resp.json():
            result = resp.json()['choices'][0]['message']['content']
            if result == "":
                bot.send_message(message.chat.id, "Объяснение закончено")
            else:
                answer += result
                column = 'answer'
                value = answer
                update_data(user_id, column, value)
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row('Продолжить ответ', 'не реализовано')
                bot.send_message(message.chat.id, result,
                     reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Не удалось получить ответ от нейросети")
            bot.send_message(message.chat.id, 'Текст ошибки:', resp.json())


bot.polling()