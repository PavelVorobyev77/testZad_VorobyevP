import re
import psycopg2

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
        # Нахождение минимального и максимального значений для каждой переменной
        min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})
        for variable, (min_val, max_val) in min_max_values.items():
            file.write(f'{variable:<10}\t{min_val}\t{max_val}\n')

# Функция для вывода статистики в консоль
def print_statistics(day, year, category_contents):
    print(f'{day} {year}')
    print('Переменная\tmin\tmax')
    # Нахождение минимального и максимального значений для каждой переменной
    min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})
    for variable, (min_val, max_val) in min_max_values.items():
        print(f'{variable:<10}\t{min_val}\t{max_val}')

# Функция для обработки файла логов
def process_log_file(file_input, day, year):
    lines = read_log_file(file_input)
    category_name = ''
    info_from_file = {}

    is_table_finished = True # Флаг, показывающий, что таблица в файле закончилась
    is_required_day = False # Флаг, показывающий, что день в файле совпадает с выбранным днем

    # Цикл по всем строкам файла
    for line in lines:
        words = re.split(r'\s+', line)

        if len(words[0].replace('-', '')) == 0: # Если строка содержит только дефисы, значит таблица закончилась
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

        # Если строка содержит данные, сохраняем их в словаре
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

# Функция для записи статистики в базу данных
def write_to_db(day, year, category_contents, db_name, db_user, db_password, db_host, db_port):
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        # Создание курсора для выполнения SQL-запросов
        cur = conn.cursor()

        # Нахождение минимального и максимального значений для каждой переменной
        min_max_values = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})

        # Запись данных в базу данных
        for variable, (min_val, max_val) in min_max_values.items():
            cur.execute(
                "INSERT INTO statistics_sample (Date, Variable, min, max) VALUES (%s, %s, %s, %s)",
                (f"{year}-{day.replace(' ', '-')}", variable, min_val, max_val)
            )
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cur.close()
        conn.close()

        print(f'Данные были успешно записаны в базу данных {db_name}')

    except (Exception, psycopg2.DatabaseError) as error:
        print('Error: ', error)
        conn.rollback()
        cur.close()
        conn.close()


# Меню выбора действия
print('Выберите действие:')
print('1. Записать данные в файл')
print('2. Вывести данные в консоль')
print('3. Записать данные в базу данных (PostgreSQL)')
action = int(input())

if action == 1:
    file_input = input('Выберите входной файл: ') #"C:/Users/pasch/Desktop/sample.txt"
    file_output = input('Выберите выходной файл: ') #"C:/Users/pasch/Desktop/output_file.txt"

    day, year = input_date_and_year()

    info_from_file = process_log_file(file_input, day, year)

    if info_from_file is not None:
        write_statistics(day, year, info_from_file, file_output)
        print(f'Данные были успешно записаны в файл {file_output}')
elif action == 2:
    file_input = input('Выберите входной файл: ') #"C:/Users/pasch/Desktop/sample.txt"

    day, year = input_date_and_year()

    info_from_file = process_log_file(file_input, day, year)

    if info_from_file is not None:
        print_statistics(day, year, info_from_file)

elif action == 3:

    file_input = input('Выберите входной файл: ')  # "C:/Users/pasch/Desktop/sample.txt"
    # Запись данных в базу данных PostgreSQL
    # Ввод параметров соединения с базой данных
    db_name = input('Введите имя базы данных: ') #pr_practice_VorobyevP
    db_user = input('Введите имя пользователя базы данных: ') #postgres
    db_password = input('Введите пароль пользователя базы данных: ') #admin
    db_host = input('Введите хост базы данных: ') #localhost
    db_port = input('Введите порт базы данных: ') #5432

    # Ввод даты и года
    day, year = input_date_and_year()

    # Обработка файла логов и запись данных в базу данных
    info_from_file = process_log_file(file_input, day, year)
    if info_from_file is not None:
        write_to_db(day, year, info_from_file, db_name, db_user, db_password, db_host, db_port)
else:
    print('Неверный выбор действия')
