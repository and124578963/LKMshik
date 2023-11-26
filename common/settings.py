# import logging
# logging.basicConfig(filename='errors.log', filemode='w', level=logging.ERROR, format="%(asctime)s;%(levelname)s;%(message)s",
#                     datefmt="%Y-%m-%d %H:%M:%S")
#
from sqlitedict import SqliteDict
from common.secrets import Secrets
import os.path

ENCRYPT_REACTIVES = 0

if not os.path.isfile('./configuration'):
    with SqliteDict('./configuration') as mydict:
        mydict.commit()

def get_app_version():
    return "2.0 от 01.07.2023"

def get_database_path():
    global DATABASE_PATH
    with SqliteDict('./configuration') as mydict:
        key = "database_path"
        database_path = mydict.get(key, "reactives.db")
        # if database_path is None:
        #     database_path = "reactives.db"
        # else:
        #     # database_path = Secrets().decrypt_data(database_path).decode()
        #
        DATABASE_PATH = database_path
        return database_path


def get_suhoi_type():
    with SqliteDict('./configuration') as mydict:
        key = "suhoi_type"
        suhoi_type = mydict.get(key, None)
        if suhoi_type is None:
            suhoi_type = "1"
        else:
            suhoi_type = Secrets().decrypt_data(suhoi_type).decode()
        return suhoi_type

def get_config_param(name:str, password=None):
    with SqliteDict('./configuration') as mydict:
        param_value = mydict.get(name, None)
        if param_value is not None:
            param_value = Secrets().decrypt_data(param_value, password=password).decode()
        return param_value


def update_config_param(param_name, new_value, password=None):
        with SqliteDict("./configuration") as mydict:
            new_value = Secrets().encrypt_data(new_value, password=password) if param_name != 'database_path' else new_value
            check = mydict.get(param_name, None)
            if check is None:
                mydict[param_name] = new_value
            else:
                mydict.update(((param_name, new_value), ))
            mydict.commit()



_general = {
            'Название': ("Название", 'name', 'Уникальное название компонента', 0, 0, {'width': 250, 'anchor': 'w'}),
            'Остатки': ('Остатки', 'warehouse', 'Сколько осталось компонента (для учета наличия)', 1, 1,
                        {'width': 80, 'anchor': "center"}),
            "Цена": ("Цена", 'price', '123,45', 1, 1, {'width': 60, 'anchor': "center"}),
            'Поставщик': ('Поставщик', 'provider', 'Кто распространяет', 0, 0, None,),
            "Производитель": ("Производитель", 'producer', 'Кто производит', 0, 0, {'width': 150, 'anchor': "center"}),
            'Ссылка на покупку': ('Ссылка на ТДС', 'url', 'Ссылка на тдс http://site.ru/tds.pdf', 0, 0, None),
            'Цвет': ('Цвет', 'colour',
                     ['Белый', 'Черный', 'Серый', 'Желтый', 'Красный', 'Зеленый', 'Синий', 'Фиолетовый', 'Коричневый',
                      'Серебристый', 'Бронзовый'],
                     0, 0, {'width': 100, 'anchor': 'center'}),
            'Белки': ('Белки', 'protein', '', 1, 1, {'width': 80, 'anchor': 'center'}),
'Жиры': ('Жиры', 'oil', '', 1, 1, {'width': 80, 'anchor': 'center'}),
'Углеводы': ('Углеводы', 'carbon', '', 1, 1, {'width': 80, 'anchor': 'center'}),
'Ккал': ('Ккал', 'energy', '', 1, 1, {'width': 80, 'anchor': 'center'}),
'Тип массы':('Тип массы', 'mass_type', ["Штучный", 'Весовой'], 0, 1, {'width': 80, 'anchor': 'center'}),
'Количество в упаковке':('Количество в упаковке', 'mass_per_tar', "Количество продукта за указанную стоимость", 1, 1, {'width': 80, 'anchor': 'center'}),





            }

# 0 - Название, 1 - колонка в БД, 2 - описание, 3 - числовое, 4 - используется в рассчетах, 5 - параметры отображения в таблице(None - не отображать)
COMPONENTS = [_general["Название"],
            _general['Остатки'],
            _general["Цена"],
            _general["Тип массы"],
            _general["Количество в упаковке"],
            _general['Поставщик'],
            _general["Производитель"],
            _general['Ссылка на покупку'],
            _general["Белки"],
            _general["Жиры"],
            _general["Углеводы"],
            _general["Ккал"],
            ]


PROVIDERS = [("Поставщик", "provider", 'Название кампании', 0, 0, {'width': 80, 'anchor': 'center'}),
             ('Менеджер', 'manager', 'ФИО менеджера дл связи', 0, 0, {'width': 150, 'anchor': 'w'}),
             ("Телефон", "phone", '+7(987)654-32-10', 0, 0, {'width': 100, 'anchor': 'center'}),
             ("E-Mail", "email", 'example@yandex.ru', 0, 0, {'width': 100, 'anchor': 'center'}),
             ("Сайт", "site", 'http://example.ru', 0, 0, {'width': 80, 'anchor': 'center'}),
             ]

PASSPORT = []

CATEGORY_DICT = {
    'Components': COMPONENTS,
    'Producer': PROVIDERS,
    'Passport': PASSPORT,
}

NOT_GLOBAL_PARAMS = ['code', 'warehouse', 'hexcolor']


def get_category(table, gloval_check=False, table_view=False):
    result = list(CATEGORY_DICT[table])

    if gloval_check:
        result = list(filter(lambda x: x[1].lower() not in NOT_GLOBAL_PARAMS, result))
    if table_view:
        result = list(filter(lambda x: not x[5] is None, result))
    return result


def get_lables(category, global_check=False, table_view=False):
    return [i[0] for i in get_category(category, gloval_check=global_check, table_view=table_view)]


def get_columns(category, global_check=False, table_view=False):
    return [i[1] for i in get_category(category, gloval_check=global_check, table_view=table_view)]


def get_desc(category, global_check=False, table_view=False):
    return [i[2] for i in get_category(category, gloval_check=global_check, table_view=table_view)]


TABLE_DICT = {"Компоненты": 'Components',
              "Поставщики": 'Producer'
              }
