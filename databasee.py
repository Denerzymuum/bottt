import sqlite3


def create_db():
    connection = sqlite3.connect('sqlit.db')
    cur = connection.cursor()


def create_table():
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()
    sql_query = f'CREATE TABLE IF NOT EXISTS userss' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'subject TEXT, ' \
                f'level TEXT, ' \
                f'task TEXT, ' \
                f'answer TEXT)'
    cur.execute(sql_query)


def insert_data(user_id, column, value):
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()
    sql_query = f'''
        INSERT INTO userss(user_id, {column})
        VALUES(?, ?)
        '''
    cur.execute(sql_query, (user_id, value))
    connection.commit()
    connection.close()


def update_data(user_id, column, value):
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()  # создаём объект для работы с БД
    # формируем запрос UPDATE, в который подставляем название поля через f-строку
    # и значения через параметр ?
    sql_query = f"UPDATE userss SET {column} = ? WHERE user_id = ?;"
    cur.execute(sql_query, (value, user_id,))  # применяем запрос и подставляем значения
    connection.commit()  # сохраняем изменения в базе данных
    connection.close()  # закрываем соединение с БД


def select_data(user_id):
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()  # создаём объект для работы с БД
    sql_query = "SELECT * FROM userss WHERE user_id = ?;"
    cur.execute(sql_query, (user_id,))
    rows = cur.fetchall()  # Получаем результаты запроса
    connection.close()  # Закрываем соединение
    if not rows:
        rows = None
    return rows


def delete_data(user_id):
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()  # создаём объект для работы с БД
    sql_query = 'DELETE FROM userss WHERE user_id = ?;'
    cur.execute(sql_query, (user_id,))  # выполняем запрос с параметром
    connection.commit()  # сохраняем изменения в базе данных
    connection.close()  # закрываем соединение с БД


def delete_data_all():
    connection = sqlite3.connect('sqlit.db')  # устанавливаем соединение с БД
    cur = connection.cursor()  # создаём объект для работы с БД
    sql_query = 'DELETE FROM userss ;'
    cur.execute(sql_query, ())  # выполняем запрос с параметром
    connection.commit()  # сохраняем изменения в базе данных
    connection.close()  # закрываем соединение с БД