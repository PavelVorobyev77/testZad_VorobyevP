import re
from datetime import datetime
import configparser
import cx_Oracle
import os

# Функция для чтения конфигурационного файла
def read_config(config_file):
    if not os.path.exists(config_file):
        print(f"Конфигурационный файл {config_file} не найден.")
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)
    print("Секции, найденные в конфигурационном файле:", config.sections())
    return config

# Укажите путь к конфигурационному файлу
config_path = os.path.join('config', 'config_statistics.ini')

# Чтение конфигурационного файла
config = read_config(config_path)

try:
    db_user = config['database']['dbuser']
    db_password = config['database']['pswd_dbuser']
    db_host = config['database']['host']
    db_port = config['database']['port']
    db_service_name = config['database']['service_name']
    file_input = config['input_file']['infile']
    file_output = config['output_file']['oufile']
    lib_dir = config['oracle']['lib_dir']
    #upd_date = config['db_upd_date']['upd_date']
    upd_date = int(config['db_upd_date']['upd_date'])  # Приведение к int для уверенности
    print(f"Значение upd_date из конфигурационного файла: {upd_date}")  # Добавлено для отладки
except KeyError as e:
    print(f"Ошибка: отсутствует секция или параметр в конфигурационном файле: {e}")
    exit(1)

# Инициализация клиента Oracle
cx_Oracle.init_oracle_client(lib_dir=lib_dir)

# Функция для чтения файла
def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print('Файл не найден!')
        return []

# Функция для нахождения минимального и максимального значений в словаре
def find_min_max(dictionary_of_data_from_file):
    min_max_values = {}
    for variable, values in dictionary_of_data_from_file.items():
        min_val = min(values)
        max_val = max(values)
        min_max_values[variable] = (min_val, max_val)
    return min_max_values

# Функция для записи статистики в выходной файл
def write_statistics(day, year, category_contents, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f'{day} {year}\n')
        file.write('Переменная\tmin\tmax\n')
        min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})
        for variable, (min_val, max_val) in min_max_values.items():
            file.write(f'{variable:<10}\t{min_val}\t{max_val}\n')

# Функция для вывода статистики в консоль
def print_statistics(day, year, category_contents):
    print(f'{day} {year}')
    print('Переменная\tmin\tmax')
    min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})
    for variable, (min_val, max_val) in min_max_values.items():
        print(f'{variable:<10}\t{min_val}\t{max_val}')

# Функция для обработки файла логов
def process_log_file(file_input, day, year):
    lines = read_log_file(file_input)
    category_name = ''
    info_from_file = {}

    is_table_finished = True
    is_required_day = False

    for line in lines:
        words = re.split(r'\s+', line)

        if len(words[0].replace('-', '')) == 0:
            is_table_finished = True
            continue

        if is_table_finished and len(line) > 10:
            is_table_finished = False
            is_required_day = (day in line.replace('  ', ' ')) and line.strip().endswith(year)
            continue

        if not is_required_day:
            continue

        if len(words) >= 1 and words[0].startswith('-----'):
            category_name = ' '.join(words).strip()
            if category_name not in info_from_file:
                info_from_file[category_name] = {}
            continue

        if words[1] == '-':
            if f'{words[0]} -' in info_from_file[category_name]:
                info_from_file[category_name][f'{words[0]} -'].append(int(words[2]))
            else:
                info_from_file[category_name][f'{words[0]} -'] = [int(words[2])]
        else:
            if words[0] in info_from_file[category_name]:
                info_from_file[category_name][words[0]].append(int(words[1]))
            else:
                info_from_file[category_name][words[0]] = [int(words[1])]

    if not info_from_file:
        print('Такой даты нет в файле')
        return None

    return info_from_file

def check_date_in_db(sample_date, db_user, db_password, db_host, db_port, db_service_name):
    try:
        dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service_name)
        conn = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM statistics_sample WHERE Sample_Date = TO_DATE(:1, 'DD.MM.YYYY')", (sample_date,))
        result = cur.fetchone()[0]

        cur.close()
        conn.close()

        print(f"Проверка наличия даты {sample_date}: {'найдена' if result > 0 else 'не найдена'}")  # Добавлено для отладки
        return result > 0

    except (Exception, cx_Oracle.DatabaseError) as error:
        print('Error: ', error)
        if conn:
            conn.rollback()
        if cur:
            cur.close()
        if conn:
            conn.close()

        return False


# Функция для записи статистики в базу данных
def write_to_db(day, year, category_contents, db_user, db_password, db_host, db_port, db_service_name, upd_date):
    try:
        dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service_name)
        conn = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)
        cur = conn.cursor()

        sample_date_str = f"{day} {year}"
        sample_date = datetime.strptime(sample_date_str, '%b %d %Y').strftime('%d.%m.%Y')

        date_exists = check_date_in_db(sample_date, db_user, db_password, db_host, db_port, db_service_name)

        print(f"Проверка даты {sample_date} вернула {date_exists}")  # Добавлено для отладки
        print(f"Значение upd_date: {upd_date}")  # Добавлено для отладки

        if date_exists:
            if upd_date == 0:
                print(f'Данные за {sample_date} уже существуют в базе данных. Обновление отключено.')
                cur.close()
                conn.close()
                return
            else:
                min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})

                for variable, (min_val, max_val) in min_max_values.items():
                    print(f"Обновление данных для переменной {variable} с min={min_val} и max={max_val}")  # Добавлено для отладки
                    cur.execute(
                        "UPDATE statistics_sample SET min_value = :1, max_value = :2 WHERE Variable = :3 AND Sample_Date = TO_DATE(:4, 'DD.MM.YYYY')",
                        (min_val, max_val, variable, sample_date)
                    )

                conn.commit()
                print(f'Данные за {sample_date} были успешно обновлены в базе данных {db_service_name}')
                cur.close()
                conn.close()
                return

        min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})

        for variable, (min_val, max_val) in min_max_values.items():
            print(f"Добавление данных для переменной {variable} с min={min_val} и max={max_val}")  # Добавлено для отладки
            cur.execute(
                "INSERT INTO statistics_sample (Sample_Date, Variable, min_value, max_value) VALUES (TO_DATE(:1, 'DD.MM.YYYY'), :2, :3, :4)",
                (sample_date, variable, min_val, max_val)
            )

        conn.commit()
        print(f'Данные были успешно записаны в базе данных {db_service_name}')
        cur.close()
        conn.close()

    except (Exception, cx_Oracle.DatabaseError) as error:
        print('Error: ', error)
        if conn:
            conn.rollback()
        if cur:
            cur.close()
        if conn:
            conn.close()



# Функция для проверки ввода даты и года
def input_date_and_year():
    # Проверка ввода даты
    while True:
        day = input('Введите день для поиска (формат: Nov 9): ')
        if re.match(r'^[A-Za-z]{3} \d{1,2}$', day):
            break
        else:
            print('Неверный формат даты. Пожалуйста, введите дату в формате "Nov 9"')

    # Проверка ввода года
    while True:
        year = input('Введите год: ')
        if re.match(r'^\d{4}$', year):
            break
        else:
            print('Неверный формат года. Пожалуйста, введите год в формате "2023"')

    return day, year




# Меню выбора действия
print('Выберите действие:')
print('1. Записать данные в файл')
print('2. Вывести данные в консоль')
print('3. Записать данные в базу данных (Oracle)')
action = int(input())

if action == 1:
    day, year = input_date_and_year()
    info_from_file = process_log_file(file_input, day, year)
    if info_from_file is not None:
        write_statistics(day, year, info_from_file, file_output)
        print(f'Данные были успешно записаны в файл {file_output}')
elif action == 2:
    day, year = input_date_and_year()
    info_from_file = process_log_file(file_input, day, year)
    if info_from_file is not None:
        print_statistics(day, year, info_from_file)
elif action == 3:
    day, year = input_date_and_year()
    info_from_file = process_log_file(file_input, day, year)
    if info_from_file is not None:
        write_to_db(day, year, info_from_file, db_user, db_password, db_host, db_port, db_service_name, upd_date)
else:
    print('Неверный выбор действия')
