import re

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
    min_val = min(dictionary_of_data_from_file.values())
    max_val = max(dictionary_of_data_from_file.values())
    min_names = [key for key, val in dictionary_of_data_from_file.items() if val == min_val]
    max_names = [key for key, val in dictionary_of_data_from_file.items() if val == max_val]
    return min_val, min_names, max_val, max_names

# Функция для записи статистики в выходной файл
def write_statistics(day, year, category_contents, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f'{day} {year}\n')
        # Нахождение минимального и максимального значений во всем файле
        min_val, min_names, max_val, max_names = find_min_max({item: count for contents in category_contents.values() for item, count in contents.items()})
        file.write(f' MIN\t\t{min_val}\t\t{" ".join(min_names)}\n')
        file.write(f' MAX\t\t{max_val}\t\t{" ".join(max_names)}\n')


file_input = input('Выберите входной файл: ') #"C:/Users/pasch/Desktop/sample.txt"
file_output = input('Выберите выходной файл: ') #"C:/Users/pasch/Desktop/output_file.txt"

day = input('Введите день для поиска (формат: Nov 9): ')
year = input('Введите год: ')

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
            info_from_file[category_name][f'{words[0]} -'] += int(words[2])
        else:
            info_from_file[category_name][f'{words[0]} -'] = int(words[2])
    else:
        if words[0] in info_from_file[category_name]:
            info_from_file[category_name][words[0]] += int(words[1])
        else:
            info_from_file[category_name][words[0]] = int(words[1])

write_statistics(day, year, info_from_file, file_output)
print(f'Данные были успешно записаны в файл {file_output}')