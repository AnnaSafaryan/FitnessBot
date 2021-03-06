# -*- coding: utf-8 -*-
import random
import sqlite3
from datetime import datetime


#TODO: Запилить ООП?

# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
#Создание таблицы
conn = sqlite3.connect('fitness.sqlite')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id int primary key, surname varchar, name varchar, gruppa varchar, status varchar)")
conn.commit() #отправка данных в базу
c.close()
conn.close()

#добавить студента в базу
def add_student(id, surname, name, gruppa):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, surname, name, gruppa, status) VALUES (?, ?, ?, ?, ?)",(id, surname, name, gruppa, 'student'))
    conn.commit()

#добавить препода в базу
def add_teacher(id, surname, name):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, surname, name, gruppa, status) VALUES (?, ?, ?, ?, ?)",(id, surname, name, None, 'teacher'))
    conn.commit()

    # закрываем соединение с базой
    c.close()
    conn.close()


# список всех пользователей
def list_all():
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    c.execute('SELECT * FROM users')
    users_tup = c.fetchall()

    # закрываем соединение с базой
    c.close()
    conn.close()

    #print(users_tup)
    users = [{'user_id':user[0], 'surname':user[1], 'name':user[2], 'gruppa':user[3], 'status':user[4]} for user in users_tup]
    #print(users)
    return users

# список пользователей по id
def list_them(ids):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    users_tup = []
    for id in ids:
        user = c.execute('SELECT surname, name, gruppa FROM users WHERE user_id={}'.format(id)).fetchone()
        users_tup.append(user)
    # закрываем соединение с базой
    c.close()
    conn.close()

    #print(users_tup)
    users = []
    for user in users_tup:
        if user:
            users.append({'surname':user[0], 'name':user[1], 'gruppa':user[2]})
        else: # отсеиваем юзеров с несуществующими id
            users.append(None)
    #print(users)
    return users

# изменить данные в нужном столбце
def change_name(surname, name, gruppa, id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    c.execute('UPDATE users SET surname=? WHERE user_id=?',(surname, id))
    c.execute('UPDATE users SET name=? WHERE user_id=?',(name, id))
    c.execute('UPDATE users SET gruppa=? WHERE user_id=?',(gruppa, id))
    conn.commit()

    # закрываем соединение с базой
    c.close()
    conn.close()


def get_status(id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    status = c.execute('SELECT status FROM users WHERE user_id={}'.format(id)).fetchone()[0]

    c.close()
    conn.close()
    #print(status)
    return status


def del_user(id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    c.execute('DELETE FROM users WHERE user_id={}'.format(id))
    conn.commit()

    # закрываем соединение с базой
    c.close()
    conn.close()



# РАБОТА С РАСПИСАНИЕМ
conn = sqlite3.connect('fitness.sqlite')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS timetable (lesson_id int, lesson varchar, time varchar, g_size tinyint, left tinyint)")
conn.commit() #отправка данных в базу
c.close()
conn.close()

# список всех занятий
def list_timetable():
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    lessons_tup = c.execute('SELECT lesson, time, left, lesson_id FROM timetable').fetchall()

    # закрываем соединение с базой
    c.close()
    conn.close()

    #print(lessons_tup)
    lessons = [{'lesson':lesson[0], 'time':datetime.strptime(lesson[1], '%Y-%m-%d %H:%M:%S'), 'left':lesson[2], 'lesson_id':lesson[3]} for lesson in lessons_tup]

    return lessons


# список всех занятий с оставшимися местами
def list_open():
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    lessons_tup = c.execute('SELECT lesson, time, left, lesson_id FROM timetable WHERE left>0').fetchall()

    # закрываем соединение с базой
    c.close()
    conn.close()
    lessons = [{'lesson':lesson[0], 'time':datetime.strptime(lesson[1], '%Y-%m-%d %H:%M:%S'), 'left':lesson[2], 'lesson_id':lesson[3]} for lesson in lessons_tup]

    return lessons



# создать занятие
def add_lesson(lesson, time, g_size):
    # 30-1 17-30
    #TODO: могут помешать лишние пробелы?
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    date, t = time.split()
    d, mo = date.split('-')
    h, mi = t.split('-')
    # определяем год
    now = datetime.now()
    if int(mo) == 1 and now.month == 12: # с декабря задаём на январь
        y = now.year+1 # переходим на следующий год
    else:
        y = now.year

    new_time = datetime(day=int(d), month=int(mo), year=y, hour=int(h), minute=int(mi))

    lesson_ids = [id[0] for id in c.execute('SELECT lesson_id FROM timetable').fetchall()]
    #print(lesson_ids)
    lesson_id = 10
    while lesson_id in lesson_ids: # если такой уже есть
        lesson_id = random.randint(10,99) # подбираем новый id -- используем буквы, т.к. нельзя создать таблицу с числом в имени
    #print('new', lesson_id)
    c.execute("INSERT INTO timetable (lesson_id, lesson, time, g_size, left) VALUES (?, ?, ?, ?, ?)",(lesson_id, lesson.lower(), new_time, g_size, g_size))

    # создаём табличку для занятия
    c.execute("CREATE TABLE IF NOT EXISTS z{} (user_id int primary key, surname varchar, name varchar, gruppa varchar)".format(lesson_id))
    conn.commit()

    # закрываем соединение с базой
    c.close()
    conn.close()



# записать пользователя на занятие
def add_to_lesson (lesson_id, user_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    # сколько людей может записаться на занятие
    g_size = c.execute('SELECT g_size FROM timetable WHERE lesson_id={}'.format(lesson_id)).fetchone()[0]
    #print(g_size)
    # сколько уже записались
    n_people = c.execute('SELECT COUNT(*) FROM z{}'.format(lesson_id)).fetchone()[0] # выдаёт кортеж
    #print(n_people)
    left = g_size - n_people
    #print(left)
    if left:
        #print(True)
        user_data = c.execute('SELECT surname, name, gruppa FROM users WHERE user_id={}'.format(user_id)).fetchone()
        print(user_data)
        # записали человека
        c.execute("INSERT INTO z{} VALUES (?, ?, ?, ?)".format(lesson_id),(user_id, user_data[0], user_data[1], user_data[2]))
        # уменьшили количество свободных мест на зантие
        c.execute('UPDATE timetable SET left=? WHERE lesson_id=?',(left-1, lesson_id))

        conn.commit()
        # закрываем соединение с базой
        c.close()
        conn.close()

    else:
        # закрываем соединение с базой
        c.close()
        conn.close()
        raise Exception('Мест больше нет!')


# id всех записавшихся
def list_lesson(lesson_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    user_ids = [id[0] for id in c.execute('SELECT user_id FROM z{}'.format(lesson_id)).fetchall()]

    # закрываем соединение с базой
    c.close()
    conn.close()

    return user_ids

# отменить запись на занятие
def del_from_lesson(lesson_id, user_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    # записавшиеся
    user_ids = list_lesson(lesson_id)
    #print(user_ids)
    if user_id in user_ids:
        c.execute('DELETE FROM z{} WHERE user_id={}'.format(lesson_id, user_id))
        # увеличили количество свободных мест на зантие
        left = c.execute('SELECT left FROM timetable WHERE lesson_id={}'.format(lesson_id)).fetchone()[0]
        c.execute('UPDATE timetable SET left=? WHERE lesson_id=?',(left+1, lesson_id))
        conn.commit()

        # закрываем соединение с базой
        c.close()
        conn.close()

    else:
        # закрываем соединение с базой
        c.close()
        conn.close()
        raise Exception('Нету таких!')

# просмотреть, на какие занятия записан пользователь
def user_lessons(user_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    lesson_ids = [id[0] for id in c.execute('SELECT lesson_id FROM timetable').fetchall()]
    #print(lesson_ids)
    user_lessons = [] # список занятий пользователя
    for lesson_id in lesson_ids:
        user_ids = list_lesson(lesson_id) # список всех, кто записался на занятие
        if user_id in user_ids: # пользователь записан на занятие
            user_lessons.append(lesson_id)

    # закрываем соединение с базой
    c.close()
    conn.close()

    return user_lessons

# просмотреть занятие по id
def get_lesson(lesson_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()
    lesson_tup = c.execute('SELECT lesson, time, g_size, left, lesson_id FROM timetable WHERE lesson_id={}'.format(lesson_id)).fetchone()
    c.close()
    conn.close()

    #print(lesson_tup)
    lesson = {'lesson':lesson_tup[0], 'time':datetime.strptime(lesson_tup[1], '%Y-%m-%d %H:%M:%S'), 'g_size':lesson_tup[2], 'left':lesson_tup[3], 'lesson_id':lesson_tup[4]}
    return lesson


# отменить занятие
def del_lesson(lesson_id):
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    user_ids = list_lesson(lesson_id) # список записавшихся
    c.execute('DELETE FROM timetable WHERE lesson_id={}'.format(lesson_id)) # удаляем из расписания
    c.execute('DROP TABLE z{}'.format(lesson_id)) # удаляем занятие
    conn.commit()

    # закрываем соединение с базой
    c.close()
    conn.close()

    return user_ids


# Очистка расписания от устаревших занятий
def clean_deprecated():
    conn = sqlite3.connect('fitness.sqlite')
    c = conn.cursor()

    now = datetime.now()
    print(now)

    lessons = c.execute('SELECT lesson_id, time FROM timetable').fetchall() # список старых занятий
    print(lessons)

    depred = [lesson_id for lesson_id, lesson_time in lessons if datetime.strptime(lesson_time, '%Y-%m-%d %H:%M:%S')<now] # id устаревших занятий
    print(depred)
    for lesson_id in depred:
        c.execute('DROP TABLE z' + str(lesson_id)) # удаляем занятие
        c.execute('DELETE FROM timetable WHERE lesson_id={}'.format(lesson_id))
    conn.commit() #отправка данных в базу

    c.close()
    conn.close()
