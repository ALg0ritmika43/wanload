from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from datetime import datetime
import threading
import requests
import time

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       title TEXT, 
                       deadline DATETIME, 
                       created DATETIME,
                       completed BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# Главная страница
@app.route('/')
def index():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY deadline')
    tasks = cursor.fetchall()
    conn.close()

    theme = request.cookies.get('theme', 'white')  # Получение текущей темы
    return render_template('index.html', tasks=tasks, theme=theme)

# Добавление задачи
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    deadline_date = request.form['deadline_date']
    deadline_time = request.form['deadline_time']
    deadline = f"{deadline_date} {deadline_time}"
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, deadline, created) VALUES (?, ?, ?)', (title, deadline, created))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Отметить задачу как выполненную
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Удаление задачи
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Изменение темы оформления
@app.route('/set-theme/<theme>')
def set_theme(theme):
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('theme', theme)  # Сохранение темы в cookie
    return resp

# Периодическая задача для отправки запроса
def periodic_task():
    while True:
        try:
            # Отправка запроса к самому себе
            requests.get('http://127.0.0.1:5000/')
        except Exception as e:
            print(f"Ошибка отправки запроса: {e}")
        time.sleep(30)  # Интервал в 30 секунд

# Запуск периодической задачи в отдельном потоке
threading.Thread(target=periodic_task, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
