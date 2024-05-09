from flask import Flask, render_template
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


# Маршрут для главной страницы
@app.route('/')
def index():
    data = get_data()
    return render_template('page.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

