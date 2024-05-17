import datetime
from flask import Flask, render_template, request
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\ORACLE\instantclient_21_13")

app = Flask(__name__)

# Подключение к базе данных
dsn = cx_Oracle.makedsn('localhost', 1521, service_name='xe')
conn = cx_Oracle.connect(user='system', password='Admin', dsn=dsn)

# Функция для получения данных из базы данных
def get_data():
    cur = conn.cursor()
    cur.execute("SELECT Sample_Date, Variable, min_value, max_value FROM statistics_sample")
    data = [{'Sample_Date': row[0], 'Variable': row[1], 'min_value': row[2], 'max_value': row[3]} for row in cur.fetchall()]
    cur.close()
    return data

# Функция для поиска данных по дате
def search_data(date):
    cur = conn.cursor()
    cur.execute("SELECT Variable, min_value, max_value, Sample_Date FROM statistics_sample WHERE Sample_Date = :1", (date,))
    data = [{'Variable': row[0], 'min_value': row[1], 'max_value': row[2], 'Sample_Date': row[3]} for row in cur.fetchall()]
    cur.close()
    return data

# Функция для поиска данных по диапазону дат
def search_data_range(date1, date2):
    cur = conn.cursor()
    cur.execute("SELECT Variable, SUM(min_value), SUM(max_value) FROM statistics_sample WHERE Sample_Date BETWEEN :1 AND :2 GROUP BY Variable", (date1, date2))
    data = [{'Variable': row[0], 'min_value': row[1], 'max_value': row[2]} for row in cur.fetchall()]
    cur.close()
    return data

# Маршрут для главной страницы
@app.route('/')
def index():
    data = get_data()
    return render_template('page.html', data=data)

# Маршрут для поиска по дате
@app.route('/search', methods=['POST'])
def search():
    date_str = request.form.get('date')
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    data = search_data(date_obj)
    return render_template('page.html', data=data)

# Маршрут для поиска по диапазону дат
@app.route('/search_range', methods=['POST'])
def search_range():
    date1_str = request.form.get('date1')
    date2_str = request.form.get('date2')
    date1_obj = datetime.datetime.strptime(date1_str, '%Y-%m-%d')
    date2_obj = datetime.datetime.strptime(date2_str, '%Y-%m-%d')
    data = search_data_range(date1_obj, date2_obj)
    return render_template('page.html', data=data, date1=date1_obj, date2=date2_obj)

@app.route('/reset', methods=['POST'])
def reset():
    # Сбросить все фильтры и получить все данные из базы данных
    data = get_data()
    return render_template('page.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
