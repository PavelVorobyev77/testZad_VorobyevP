import datetime
import configparser
from flask import Flask, render_template, request
import cx_Oracle
import os

# Чтение конфигурационного файла
def read_config(config_file):
    if not os.path.exists(config_file):
        print(f"Конфигурационный файл {config_file} не найден.")
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Укажите путь к конфигурационному файлу
config_path = os.path.join('config', 'config_statistics.ini')

# Чтение конфигурационного файла
config = read_config(config_path)

# Получение параметров подключения к базе данных из конфигурационного файла
try:
    db_user = config['database']['dbuser']
    db_password = config['database']['pswd_dbuser']
    db_host = config['database']['host']
    db_port = config['database']['port']
    db_service_name = config['database']['service_name']
    lib_dir = config['oracle']['lib_dir']
except KeyError as e:
    print(f"Ошибка: отсутствует секция или параметр в конфигурационном файле: {e}")
    exit(1)

# Инициализация клиента Oracle
cx_Oracle.init_oracle_client(lib_dir=lib_dir)

app = Flask(__name__)

# Подключение к базе данных
dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service_name)
conn = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)

# Функция для получения данных из базы данных
def get_data():
    cur = conn.cursor()
    cur.execute("select Sample_Date, Variable, min_value, max_value from (SELECT Variable, min_value, max_value, Sample_Date, decode(variable, 'ff -',1, 'fl',2, 'pt',3, 'lf -', 4, 'll', 5, 'tp -', 6, 'tt', 7, 'ff.lit -', 8, 'fl.lit', 9, 'pt.lit', 10, 'lf.lit -', 11, 'll.lit', 12, 'tp.lit -', 13, 'tt.lit', 14, 999) ord FROM statistics_sample) order by ord")
    data = [{'Sample_Date': row[0], 'Variable': row[1], 'min_value': row[2], 'max_value': row[3]} for row in cur.fetchall()]
    cur.close()
    #print(f"Полученные данные: {data}")  # Отладочное сообщение
    return data

# Функция для поиска данных по дате
def search_data(date):
    cur = conn.cursor()
    cur.execute("select Variable, min_value, max_value, Sample_Date from (SELECT Variable, min_value, max_value, Sample_Date, decode(variable, 'ff -',1, 'fl',2, 'pt',3, 'lf -', 4, 'll', 5, 'tp -', 6, 'tt', 7, 'ff.lit -', 8, 'fl.lit', 9, 'pt.lit', 10, 'lf.lit -', 11, 'll.lit', 12, 'tp.lit -', 13, 'tt.lit', 14, 999) ord FROM statistics_sample WHERE Sample_Date = :1) order by ord", (date,))
    data = [{'Variable': row[0], 'min_value': row[1], 'max_value': row[2], 'Sample_Date': row[3]} for row in cur.fetchall()]
    cur.close()
    return data

# Функция для поиска данных по диапазону дат
def search_data_range(date1, date2):
    cur = conn.cursor()
    cur.execute("select Variable, SUM(min_value), SUM(max_value) from (SELECT Variable, min_value, max_value, decode(variable, 'ff -',1, 'fl',2, 'pt',3, 'lf -', 4, 'll', 5, 'tp -', 6, 'tt', 7, 'ff.lit -', 8, 'fl.lit', 9, 'pt.lit', 10, 'lf.lit -', 11, 'll.lit', 12, 'tp.lit -', 13, 'tt.lit', 14, 999) ord FROM statistics_sample WHERE Sample_Date BETWEEN :1 AND :2) GROUP BY Variable, ord order by ord", (date1, date2))
    data = [{'Variable': row[0], 'min_value': row[1], 'max_value': row[2]} for row in cur.fetchall()]
    cur.close()
    return data

# Маршрут для главной страницы
@app.route('/')
def index():
    data = get_data()
    if not data:
        print("Нет данных для отображения на главной странице")  # Отладочное сообщение
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

    if date2_str:
        date2_obj = datetime.datetime.strptime(date2_str, '%Y-%m-%d')
    else:
        date2_obj = None

    if date2_obj:
        data = search_data_range(date1_obj, date2_obj)
    else:
        data = search_data(date1_obj)

    return render_template('page.html', data=data, date1=date1_obj, date2=date2_obj)

@app.route('/reset', methods=['POST'])
def reset():
    # Сбросить все фильтры и получить все данные из базы данных
    data = get_data()
    return render_template('page.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
