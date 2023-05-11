# import logging
# logging.basicConfig(filename='errors.log', filemode='w', level=logging.ERROR, format="%(asctime)s;%(levelname)s;%(message)s",
#                     datefmt="%Y-%m-%d %H:%M:%S")
#
from sqlitedict import SqliteDict
from common.secrets import Secrets
import os.path

ENCRYPT_REACTIVES = 0


if not os.path.isfile('configuration'):
    with SqliteDict('configuration') as mydict:
        mydict.commit()

def get_database_path():
    global DATABASE_PATH
    with SqliteDict('configuration') as mydict:
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
    with SqliteDict('configuration') as mydict:
        key = "suhoi_type"
        suhoi_type = mydict.get(key, None)
        if suhoi_type is None:
            suhoi_type = 0
        else:
            suhoi_type = Secrets().decrypt_data(suhoi_type).decode()
        return suhoi_type


def update_config_param(param_name, new_value):
        with SqliteDict("configuration") as mydict:
            new_value = Secrets().encrypt_data(new_value) if param_name != 'database_path' else new_value
            check = mydict.get(param_name, None)
            print(check)
            if check is None:
                mydict[param_name] = new_value
            else:
                mydict.update(((param_name, new_value), ))
            mydict.commit()



_general = {'Шифр': ("Шифр", 'code', 'Шифр для шифрования названия', 0, 0, {'width': 80, 'anchor': "center"}),
            'Название': ("Название", 'name', 'Уникальное название компонента', 0, 0, {'width': 250, 'anchor': 'w'}),
            'Остатки': ('Остатки', 'warehouse', 'Сколько осталось компонента (для учета наличия)', 1, 1,
                        {'width': 80, 'anchor': "center"}),
            "Цена": ("Цена", 'price', '123,45', 1, 1, {'width': 60, 'anchor': "center"}),
            'Валюта': ('Валюта', 'valuta', ['Руб', '$', '€'], 0, 1, {'width': 60, 'anchor': "center"}),
            'Поставщик': ('Поставщик', 'provider', 'Кто распространяет', 0, 0, None,),
            "Производитель": ("Производитель", 'producer', 'Кто производит', 0, 0, {'width': 150, 'anchor': "center"}),
            'Класс опасности': ('Класс опасности', 'Hazard_class', ['1', '2', '3', '4', 'Нет'], 0, 0, None,),
            'Ссылка на ТДС': ('Ссылка на ТДС', 'url', 'Ссылка на тдс http://site.ru/tds.pdf', 0, 0, None),
            'Применение': ('Применение', 'application', '', 0, 0, None),
            'Цвет': ('Цвет', 'colour',
                     ['Белый', 'Черный', 'Серый', 'Желтый', 'Красный', 'Зеленый', 'Синий', 'Фиолетовый', 'Коричневый',
                      'Серебристый', 'Бронзовый'],
                     0, 0, {'width': 100, 'anchor': 'center'}),
            'Плотность раст-ля': (
            'ρ раст-ля, г/мл', 'density_solvent', '0,89', 1, 1, {'width': 70, 'anchor': "center"}),

            }

# 0 - Название, 1 - колонка в БД, 2 - описание, 3 - числовое, 4 - используется в рассчетах, 5 - параметры отображения в таблице(None - не отображать)
SOLVENTS = [_general['Шифр'],
            _general["Название"],
            _general['Остатки'],
            ("Тип", 'type', ['Ароматическй', 'Алифатический', 'Смесевой'], 0, 0, {'width': 110, 'anchor': "center"}),
            ('Полярность', 'polarity', ['Полярный', 'Неполярный'], 0, 0, {'width': 110, 'anchor': "center"}),
            ('Состав', 'consist', 'Ксилол - 60%, Толуол - 40%', 0, 0, {'width': 150, 'anchor': "center"}),
            _general["Цена"],
            _general['Валюта'],
            _general['Поставщик'],
            _general["Производитель"],
            ("ρ, г/мл", 'density', '1,2', 1, 1, {'width': 70, 'anchor': "center"}),
            ('Tкип, °C', 'boiling_temp', 'Температура кипения в °C', 0, 0, {'width': 70, 'anchor': "center"}),
            ("σ, мН/м", 'surface_force', 'Поверхностное натяжение', 0, 0, {'width': 70, 'anchor': "center"}),
            ("Летучесть", 'flyable', 'Относительно диэтилового эфира = 1', 0, 0, {'width': 75, 'anchor': "center"}),
            _general['Класс опасности'],
            _general['Ссылка на ТДС'],
            ]

PIGMENTS = [_general['Шифр'],
            _general['Название'],
            _general['Остатки'],
            _general['Цвет'],
            ('Тип', 'type', ['Органический', 'Неорганический', 'Смесевой', 'Металлический'], 0, 0,
             {'width': 150, 'anchor': "center"}),
            ('Хим. класс', 'chem_class',
             ['Железоокисный', 'Диоксид титана (рутил)', 'Окись хрома', 'Фталоцианиновый', 'Азопигмент', 'Крон',
              'Ультрамарин', 'Диоксид титана (анатаз)', 'Сплав металлов',
              'Алюминиевый', 'Сажа'], 0, 0, {'width': 150, 'anchor': "center"}),
            _general['Цена'],
            _general['Валюта'],
            _general['Поставщик'],
            _general['Производитель'],
            ('ρ, г/мл', 'density', '1,2', 1, 1, {'width': 70, 'anchor': "center"}),
            ('Маслоемкость 1 рода г/100г', 'maslo', '12,34', 1, 1, {'width': 110, 'anchor': "center"}),
            ('Интенсивность', 'intensity', 'Разбеливающая/красящая способность', 0, 0,
             {'width': 100, 'anchor': "center"}),
            ('Укрывистость, г/м²', 'hiding', '123,45', 1, 1, {'width': 100, 'anchor': "center"}),
            ('Показатель преломления', 'refractive', '1,23', 0, 0, {'width': 100, 'anchor': "center"}),
            ('Размер частиц', 'size', '10нм, 100мкм,  120-200нм', 0, 0, {'width': 110, 'anchor': "center"}),
            ('Термостабильность', 'thermal', '700°C - 3 часа, 500°C - 20 часов', 0, 0,
             {'width': 110, 'anchor': "center"}),
            _general['Класс опасности'],
            _general['Ссылка на ТДС'],
            _general['Применение'],
            ]

PIGM_PASTS = [_general['Шифр'],
              _general['Название'],
              _general['Остатки'],
              _general['Цвет'],
              ('Состав', 'consist', 'TiOx 25%, Фталоциан. голубой 35%, Слюда 40%', 0, 0,
               {'width': 150, 'anchor': 'center'}),
              _general['Цена'],
              _general['Валюта'],
              _general['Поставщик'],
              _general['Производитель'],
              ('Растворитель', 'solvent', 'Растворитель, используемый в пасте', 0, 0,
               {'width': 100, 'anchor': 'center'}),
              ('Масс.д.н.в.', 'suhoi', 'Масс доля нелетучих веществ в сотых долях: 0,75', 1, 1,
               {'width': 110, 'anchor': 'center'}),
              ('Масс.д. пигм.', 'suhoi_pigm', 'Массовая доля пигмента и наполнителя в сотых долях: 0,45', 1, 1,
               {'width': 110, 'anchor': 'center'}),
              ('Масс.д. ПО', 'suhoi_film', 'Массовая доля пленкообразователя в сотых долях: 0,3', 1, 1,
               {'width': 110, 'anchor': 'center'}),
              ('Маслоемкость 1 рода, г/100г', 'maslo', '12,34', 1, 1, {'width': 110, 'anchor': 'center'}),
              ('ρ пасты, г/мл', 'density', '1,6', 1, 1, {'width': 100, 'anchor': 'center'}),
              ('ρ пигм., г/мл', 'density_pigm', '2,5', 1, 1, {'width': 100, 'anchor': 'center'}),
              ('ρ сух.ПО, г/мл', 'density_dry', '1,2', 1, 1, {'width': 100, 'anchor': 'center'}),
              _general['Плотность раст-ля'],
              ('Укрывистость, г/м²', 'hiding', '123,45', 1, 1, {'width': 100, 'anchor': 'center'}),
              ('Размер частиц', 'size', '10нм, 100мкм,  120-200нм', 0, 0, {'width': 110, 'anchor': 'center'}),
              ('Термостабильность', 'thermal', '700°C - 3 часа, 500°C - 20 часов', 0, 0,
               {'width': 110, 'anchor': 'center'}),
              _general['Класс опасности'],
              _general['Ссылка на ТДС'],
              _general['Применение'],
              ]

FILLERS = [_general['Шифр'],
           _general['Название'],
           _general['Остатки'],
           ('Тип', 'type', ['Силикатный', 'Карбонатный', 'Сульфатный', 'Гидроксидный', 'Фосфатный', 'Реология'], 0, 0,
            {'width': 100, 'anchor': 'center'}),
           ('Форма', 'form', ['Пластинчатая', 'Чешуйчатая', 'Сферическа', 'Игольчатая'], 0, 0,
            {'width': 120, 'anchor': 'center'}),
           _general['Цвет'],
           _general['Цена'],
           _general['Валюта'],
           _general['Поставщик'],
           _general['Производитель'],
           ('Маслоемкость 1 рода г/100г', 'maslo', '123,45', 1, 1, {'width': 110, 'anchor': 'center'}),
           ('ρ, г/мл', 'density', '1,23', 1, 1, {'width': 70, 'anchor': 'center'}),
           ('Размер частиц', 'size', '10нм, 100мкм,  120-200нм', 0, 0, {'width': 110, 'anchor': 'center'}),
           ('Термостабильность', 'thermal', '700°C - 3 часа, 500°C - 20 часов', 0, 0,
            {'width': 110, 'anchor': 'center'}),
           _general['Класс опасности'],
           _general['Ссылка на ТДС'],
           _general['Применение'],

           ]

FILMS = [_general['Шифр'],
         _general['Название'],
         _general['Остатки'],
         ('Тип', 'type',
          ['Акрилат', 'Тощий алкид', 'Средний алкид', 'Толстый алкид', 'Уралкид', 'Эпоксид', 'Изоционат', 'Полиол',
           'Нефтеполимер', 'Активный разбавитель'], 0, 0,
          {'width': 150, 'anchor': 'center'}),
         ('Растворитель', 'solvent', 'Название растворителя или смеси', 0, 0, {'width': 100, 'anchor': 'center'}),
         _general['Цена'],
         _general['Валюта'],
         _general['Поставщик'],
         _general['Производитель'],
         ('Масс. д.н.в.', 'suhoi', 'Массовая доля нелетучих веществ в сотых долях: 0,65', 1, 1,
          {'width': 80, 'anchor': 'center'}),
         ('ρ р-ра, г/мл', 'density', 'Плотность продукта в форме поставки: 1,01', 1, 1,
          {'width': 90, 'anchor': 'center'}),
         ('ρ пленки, г/мл', 'density_dry', 'Плотность сухой пленки: 1,2', 1, 1, {'width': 110, 'anchor': 'center'}),
         _general['Плотность раст-ля'],
         ('Показатель преломления', 'refractive', '1,2', 0, 0, {'width': 110, 'anchor': 'center'}),
         ('Вязкость', 'viscosity', 'Перечисление различных вязкостей', 0, 0, {'width': 110, 'anchor': 'center'}),
         ('Блеск', 'glass', 'Высогоглянцевая, высокоматовая, 50 у.е. 60°', 0, 0, {'width': 100, 'anchor': 'center'}),
         ('Твердость', 'hardness', 'Твердость по маятнику или карандашу', 0, 0, {'width': 100, 'anchor': 'center'}),
         ('σ полим., мН/м', 'surface_force', 'Поверхностное натяжение полимера', 0, 0,
          {'width': 110, 'anchor': 'center'}),
         ('Кислотное число', 'acid', '20 мг KOH', 0, 0, {'width': 130, 'anchor': 'center'}),
         ('Цвет', 'colour', 'Цвет по йодометрической шкале или др.', 0, 0, {'width': 150, 'anchor': 'center'}),
         ('Время высыхания', 'time', 'Время высыхания с указанием степени', 0, 0, {'width': 150, 'anchor': 'center'}),
         ('Тст, °C', 'temp_glass', 'Температура стеклования или кристаллизации', 0, 0,
          {'width': 100, 'anchor': 'center'}),
         ('Тпл, °C', 'temp_melt', 'Температура плавления (для порошковых покрытий)', 0, 0,
          {'width': 100, 'anchor': 'center'}),
         ('Растворимость', 'solubility', 'Растворимость в растворителях', 0, 0, {'width': 150, 'anchor': 'center'}),
         ('Термостабильность', 'thermal', '700°C - 3 часа, 500°C - 20 часов', 0, 0, {'width': 130, 'anchor': 'center'}),
         ('Содерж. функц. групп, г/экв', 'func_groups', '12,34', 1, 1, {'width': 180, 'anchor': 'center'}),
         ('Условия стабильности', 'stability', 'Условия стабильности полимера или дисперсии', 0, 0,
          {'width': 180, 'anchor': 'center'}),
         _general['Класс опасности'],
         _general['Ссылка на ТДС'],
         _general['Применение'],

         ]

ADDITIVES = [_general['Шифр'],
             _general['Название'],
             _general['Остатки'],
             ('Тип', 'type',
              ['Сиккатив', 'Пластификатор', 'Диспергатор', 'Тиксотроп', 'Катализатор', 'Воск', 'Антиоксидант'], 0, 1,
              {'width': 100, 'anchor': 'center'}),
             # Для сиккатива и пластификатора обязательно необходимомо указывать тип, т.к. у сиккатива своя форма расчета функциональных добавок, а пластификатор участвуется в расчете СП\\ОКП\\КОКП
             (
             'Форма поставки', 'form', ['Порошок', 'Паста', 'Вязкая жидкость', 'Жидкость', 'Водный раствор', 'Гранулы'],
             0, 0, {'width': 100, 'anchor': 'center'}),
             _general['Цена'],
             _general['Валюта'],
             _general['Поставщик'],
             _general['Производитель'],
             ('ρ, г/мл', 'density', 'Плотность компонента в форме поставки: 1,25', 1, 1,
              {'width': 100, 'anchor': 'center'}),
             _general['Плотность раст-ля'],
             ('масс.д.н.в', 'suhoi', 'Массовая доля нелетучих веществ в сотых долях: 0,99', 1, 1,
              {'width': 80, 'anchor': 'center'}),
             _general['Цвет'],
             ('Дозировка', 'dosage', 'Для сиккатива дополнительно указать мас.д. металла', 0, 1,
              {'width': 200, 'anchor': 'center'}),
             _general['Класс опасности'],
             _general['Ссылка на ТДС'],
             _general['Применение'],
             ]

HARDENERS = [_general['Шифр'],
             _general['Название'],
             _general['Остатки'],
             ('Тип', 'type', ['Кислотный', 'Аминный', 'Ангидридный', 'Полиамид'], 0, 0,
              {'width': 100, 'anchor': 'center'}),
             ('Цвет', 'colour', 'Цвет по йодометрической шкале или др.', 0, 0, {'width': 100, 'anchor': 'center'}),
             _general['Цена'],
             _general['Валюта'],
             _general['Поставщик'],
             _general['Производитель'],
             ('Форма поставки', 'form', ['Порошок', 'Вязкая жидкость', 'Низковязкая жидкость'], 0, 0,
              {'width': 150, 'anchor': 'center'}),
             ('масс.д.н.в', 'suhoi', 'Массовая доля нелетучих веществ: 0,95', 1, 1, {'width': 80, 'anchor': 'center'}),
             ('ρ в форме поставки, г/мл', 'density', 'Плотность в форме поставки: 1,4', 1, 1,
              {'width': 100, 'anchor': 'center'}),
             ('ρ сух. в-ва, г/мл', 'density_dry', 'Плотность сухого остатка(чистого в-ва): 1,2 ', 1, 1,
              {'width': 100, 'anchor': 'center'}),
             _general['Плотность раст-ля'],
             ('Эквивалентные массы', 'func_groups', 'г/экв для различных условий отверждения', 0, 1,
              {'width': 150, 'anchor': 'center'}),
             ('Такт, °C', 'temp_activity', 'Температура начала реакции отверждения', 0, 0,
              {'width': 100, 'anchor': 'center'}),
             ('Тпл, °C', 'temp_melt', 'Температура плавления', 0, 0, {'width': 100, 'anchor': 'center'}),
             ('Вязкость', 'viscosity', 'Перечисление различных вязкостей', 0, 0, {'width': 150, 'anchor': 'center'}),
             ('Показатель преломления', 'refractive', '1,3', 0, 0, {'width': 100, 'anchor': 'center'}),
             ('Выделение теплоты', 'exothermic', 'Экзотермичность реакций отверждения', 0, 0,
              {'width': 100, 'anchor': 'center'}),
             ('Учитывать в расчете ОКП/КОКП/СП', 'countable', ['Да', 'Нет'], 0, 1, None),
             _general['Класс опасности'],
             _general['Ссылка на ТДС'],
             _general['Применение'],
             ]

PROVIDERS = [("Поставщик", "provider", 'Название кампании', 0, 0, {'width': 80, 'anchor': 'center'}),
             ('Менеджер', 'manager', 'ФИО менеджера дл связи', 0, 0, {'width': 150, 'anchor': 'w'}),
             ("Телефон", "phone", '+7(987)654-32-10', 0, 0, {'width': 100, 'anchor': 'center'}),
             ("E-Mail", "email", 'example@yandex.ru', 0, 0, {'width': 100, 'anchor': 'center'}),
             ("Сайт", "site", 'http://example.ru', 0, 0, {'width': 80, 'anchor': 'center'}),
             ]

PASSPORT = [('Название для ПБ', 'name_pb',
             'Если в материале несколько компонентов, которые необходимо указать раздельно в ПБ, разделите названия через ;'),
            ('ПДК р.з. мг/м3', 'pdk', 'Для нескольких компонентов разделите ;'),
            ('№CAS', 'cas', 'Для нескольких компонентов разделите ;'),
            ('№ЕС', 'es', 'Для нескольких компонентов разделите ;'),
            ('H-коды', 'key_n', 'Только цифры кода через запятую: 205, 206, 207 '),
            ('Р-коды', 'key_r', 'Только цифры кода через запятую: 250, 260, 370 '),
            ('Температура вспышки', 't_flash', 'Для нескольких компонентов разделите ;'),
            ('Температура самовосп.', 't_self_fire', 'Для нескольких компонентов разделите ;'),
            ('Темп. пределы воспл.', 't_flammable_limits', 'Для нескольких компонентов разделите ;'),
            ('Конц. пределы воспл.', 'c_flammable_limits', 'Для нескольких компонентов разделите ;'),
            ('ПДК/ОБУВ атм.в.', 'pdk_atm', 'Для нескольких компонентов разделите ;'),
            ('ПДК/ОБУВ вода', 'pdk_water', 'Для нескольких компонентов разделите ;'),
            ('ПДК/ОБУВ почва', 'pdk_fish', 'Для нескольких компонентов разделите ;'),
            ('ПДК/ОБУВ рыб.хоз.', 'pdk_soil', 'Для нескольких компонентов разделите ;'),
            ('Показатели остр. токсич.', 'toxicity', 'Показатели острой токсичности через запятую'),
            ('Показатели экотоксич.', 'eco_toxicity', 'Показатели экотоксичности через запятую')]

CATEGORY_DICT = {
    'Solvents': SOLVENTS,
    'Pigments': PIGMENTS,
    'PigmPast': PIGM_PASTS,
    'Fillers': FILLERS,
    'Films': FILMS,
    'Additives': ADDITIVES,
    'Hardener': HARDENERS,
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


TABLE_DICT = {"Растворители": 'Solvents',
              "Пигменты": 'Pigments',
              "Пигментные пасты": 'PigmPast',
              "Наполнители": 'Fillers',
              "Пленкообразователи": 'Films',
              "Функц. добавки": 'Additives',
              "Отвердители": 'Hardener',
              "Поставщики": 'Producer'
              }
