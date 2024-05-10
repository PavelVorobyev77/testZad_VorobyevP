import datetime
from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="pr_practice_VorobyevP",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)

# Функция для получения данных из базы данных
def get_data():
    cur = conn.cursor()
    cur.execute("SELECT Date, Variable, min, max FROM statistics_sample")
    data = [{'Date': row[0], 'Variable': row[1], 'min': row[2], 'max': row[3]} for row in cur.fetchall()]
    cur.close()
    return data

# Функция для поиска данных по дате
def search_data(date):
    cur = conn.cursor()
    cur.execute("SELECT Variable, min, max, Date FROM statistics_sample WHERE Date = %s", (date,))
    data = [{'Variable': row[0], 'min': row[1], 'max': row[2], 'Date': row[3]} for row in cur.fetchall()]
    cur.close()
    return data


# Функция для поиска данных по диапазону дат
def search_data_range(date1, date2):
    cur = conn.cursor()
    cur.execute("SELECT Variable, SUM(min), SUM(max) FROM statistics_sample WHERE Date BETWEEN %s AND %s GROUP BY Variable", (date1, date2))
    data = [{'Variable': row[0], 'min': row[1], 'max': row[2]} for row in cur.fetchall()]
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

if __name__ == '__main__':
    app.run(debug=True)

