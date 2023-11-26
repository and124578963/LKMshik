import logging
import sqlite3
import traceback
import urllib.request
from functools import wraps
from Crypto.Cipher import AES  # алгоритм шифрования
from Crypto.Hash import SHA256  # Для хеширования данных используем также популярный алгоритм SHA.
from Crypto.Hash import MD5
from Crypto import Random

from common.secrets import Secrets
from common.settings import ENCRYPT_REACTIVES, get_database_path


def connect_db_decorator(func):
    @wraps(func)
    def _impl(self, *args):
        try:
            if self.global_check:
                self.conn = sqlite3.connect("global_reactives.gdb")
            else:
                DATABASE_PATH = get_database_path()
                self.conn = sqlite3.connect(DATABASE_PATH)
            self.conn.create_function("LOWER", 1, self.sqlite_lower)
            self.conn.create_function("DECODE", 1, self.sqlite_decode)
            self.c = self.conn.cursor()

            values = func(self, *args)  # Сама функция

        except Exception as e:
            logging.error(e, exc_info=True)
            traceback.print_exc()
        finally:

            self.c.close()
            self.conn.close()


        return values

    return _impl


class DB:
    def __init__(self, global_check=False):
        self.global_check = global_check

    def transform_password(cls, password_str):
        h = MD5.new()
        h.update(password_str.encode())
        return h.hexdigest()[5:21]

    def symmetric_encrypt(self, message, key):

        key_MD5 = self.transform_password(key).encode()  # Приводим произвольный пароль к длине 32 бита
        message_hash = SHA256.new(message)
        message_with_hash = message + message_hash.hexdigest().encode()  # Добавим в конец сообщения его хеш. он понадобится нам при расшифровки
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key_MD5, AES.MODE_CFB,
                         iv)  # Создаем объект с заданными параметрами. AES.MODE_CFB - надежный режим шифрования, который предполагает наличие вектора инициализации iv. https://www.dlitz.net/software/pycrypto/api/current/Crypto.Cipher.blockalgo-module.html#MODE_CFB
        encrypted_message = iv + cipher.encrypt(
            message_with_hash)  # Включаем случайную последовательность в начало шифруемого сообщения. Это необходимо, чтобы в случае кодирования нескольких блоков текста, аналогичные блоки не давали одинаковые кодированные сообщения.

        return encrypted_message

    def symmetric_decrypt(self, encr_message, key):

        key_MD5 = self.transform_password(key).encode()

        # Размеры боков нужны, для извлечения их из текста
        bsize = AES.block_size
        dsize = SHA256.digest_size * 2

        iv = Random.new().read(bsize)
        cipher = AES.new(key_MD5, AES.MODE_CFB, iv)
        decrypted_message_with_hesh = cipher.decrypt(encr_message)[
                                      bsize:]  # Извлекаем из блока случайные символу, которые мы добавляли при шифровании
        decrypted_message = decrypted_message_with_hesh[
                            :-dsize]  # Извлекаем хеш сообщения, который мы присоединяли при шифровании
        digest = SHA256.new(
            decrypted_message).hexdigest()  # хеш расшифрованной части сообщения. Он будет сравниваться с хешем, который мы присоединили при шифровании.

        if digest == decrypted_message_with_hesh[
                     -dsize:].decode():  # Если хеш расшифровааного сообщения и хеш, который мы добавили при шифровании равны, расшифровка правильная
            # print(
            #     f"Success!")
            return decrypted_message
        else:
            raise ValueError

    def sqlite_lower(self, value_):
        if value_ is None:
            value_ = ""
        return value_.lower()

    def sqlite_decode(self, value_):
        password = Secrets.password
        if ENCRYPT_REACTIVES:
            value = self.symmetric_decrypt(bytes(value_), password).decode()
        else:
            value = value_
        return value

    @connect_db_decorator
    def load_reactives(self, group, name_params):
        global password
        self.c.execute(f'''SELECT {name_params} FROM {group}''')
        fetchall = self.c.fetchall()[:]
        decode_fetchall = []
        if self.global_check:
            return fetchall

        for item in fetchall:
            item_list = []
            for value in item:
                if type(value) != int:
                    if ENCRYPT_REACTIVES:
                        item_list.append(self.symmetric_decrypt(bytes(value), password).decode())
                    else:
                        item_list.append(value)
                else:
                    item_list.append(value)
            decode_fetchall.append(item_list)

        return decode_fetchall


    def insert_data_glob(self, group, name_params, id, args ):
        global password
        self.conn_global = sqlite3.connect("global_reactives.gdb")
        self.c_global = self.conn_global.cursor()

        DATABASE_PATH = get_database_path()
        self.conn = sqlite3.connect(DATABASE_PATH)

        self.conn.create_function("DECODE", 1, self.sqlite_decode)
        self.conn.create_function("LOWER", 1, self.sqlite_lower)
        self.c = self.conn.cursor()

        self.c_global.execute(f'''SELECT provider FROM {group} WHERE name = ? ''', (id,), )
        name = self.c_global.fetchall()
        self.conn_global.commit()

        self.c_global.execute(f'''SELECT provider, manager, phone, site, email, note  FROM Producer WHERE provider = ? ''', (name[0][0],), )
        company_info = self.c_global.fetchall()
        self.conn_global.commit()
        if group != 'Producer':
            company_info_for_check = [company_info[0][0], company_info[0][1]]
            if self.check_unique(company_info_for_check, 'Producer'):
                list_company_info = []
                for info in company_info[0]:
                    if ENCRYPT_REACTIVES:
                        list_company_info.append(self.symmetric_encrypt(info.encode(), password))
                    else:
                        list_company_info.append(info)

                self.c.execute(f'''INSERT INTO Producer ({'provider, manager, phone, site, email, note'}) VALUES (?, ?, ?, ?, ?, ?)''', list_company_info, )
                self.conn.commit()

        if self.check_unique(args[0:2], group):
            enc_args = []
            for i in args:
                if ENCRYPT_REACTIVES:
                    enc_args.append(self.symmetric_encrypt(i.encode(), password))
                else:
                    enc_args.append(i)

            self.c_global.execute(f'''SELECT note FROM {group} WHERE name = ? ''', (id,), )
            notes = self.c_global.fetchone()
            self.conn_global.commit()
            # для note, code, warehouse

            if ENCRYPT_REACTIVES:
                enc_args.append(self.symmetric_encrypt(notes[0].encode(), password))
            else:
                enc_args.append(notes[0])
            name_params +=', note'
            name_params = name_params.replace('=?,', ',')
            amount_params = ''

            for i in range(len(args)):
                amount_params += '?, '

            amount_params += '?'
            print(name_params)
            print(amount_params)
            print(enc_args)
            self.c.execute(f'''INSERT INTO {group} ({name_params}) VALUES ({amount_params})''', enc_args, )

            self.conn.commit()
            check = True
        else:
            check = False

        self.c.close()
        self.conn.close()
        self.c_global.close()
        self.conn_global.close()
        return check


    @connect_db_decorator
    def insert_data(self, group: str, name_params: list, args: list):
        global password

        if self.check_unique(args[0:2], group):
            name_params += ', note'
            enc_args = []
            for i in args:
                if ENCRYPT_REACTIVES:
                    enc_args.append(self.symmetric_encrypt(i.encode(), password))
                else:
                    enc_args.append(i)
            if ENCRYPT_REACTIVES:
                enc_args.append(self.symmetric_encrypt(' '.encode(), password))
            else:
                enc_args.append(' ')
            amount_params = ''

            for i in range(len(args) - 1):
                amount_params += '?, '
            amount_params += '?, ?'

            self.c.execute(f'''INSERT INTO {group} ({name_params}) VALUES ({amount_params})''', enc_args, )
            self.conn.commit()
            return True
        else:
            return False

    @connect_db_decorator
    def new_insert_data(self, group: str, name_params: str, args: list):
        global password

        if self.check_unique(args[0:2], group):

            amount_params = ''
            for i in range(len(args) - 1):
                amount_params += '?, '
            amount_params += '?'
            print(f'''INSERT INTO {group} ({name_params}) VALUES ({amount_params})''')
            print(args)
            self.c.execute(f'''INSERT INTO {group} ({name_params}) VALUES ({amount_params})''', args, )
            self.conn.commit()
            return True
        else:
            return False

    @connect_db_decorator
    def update_record(self, group, params, id, args):
        global password
        if group != 'Producer':
            code_name = args[0:2]
            code_name[0] = code_name[0].lower()
            code_name[1] = code_name[1].lower()
            self.c.execute(f'''SELECT code, name FROM {group} WHERE id=? ''', (id,), )
            fetchall = self.c.fetchone()
            dec_fetchall = []
            for i in fetchall:
                if ENCRYPT_REACTIVES:
                    dec_fetchall.append(self.symmetric_decrypt(bytes(i), password).decode())
                else:
                    dec_fetchall.append(i)

            check_repeat_code = code_name[0] == dec_fetchall[0].lower() or code_name[0] == '' or code_name[0] == ' '
            check_repeat_name = code_name[1] == dec_fetchall[1].lower()

            check = check_repeat_code and check_repeat_name
            if check == False and code_name[1] == dec_fetchall[1].lower():
                check = self.check_unique([code_name[0], code_name[0]], 'reactives')
            elif check == False and code_name[0] == dec_fetchall[0].lower():
                check = self.check_unique([code_name[1], code_name[1]], 'reactives')
            elif check == False:
                check = self.check_unique(args[0:2], group)


        else:
            code_name = args[0]
            code_name = code_name.lower()
            self.c.execute(f'''SELECT provider FROM {group} WHERE id=? ''', (id,), )
            fetchall = self.c.fetchone()
            dec_fetchall = []
            for i in fetchall:
                if ENCRYPT_REACTIVES:
                    dec_fetchall.append(self.symmetric_decrypt(bytes(i), password).decode())
                else:
                    dec_fetchall.append(i)

            check = code_name == dec_fetchall[0].lower()
            if check == False:
                check = self.check_unique(args[0:2], group)

        if check:
            enc_args = []
            for i in args:
                if ENCRYPT_REACTIVES:
                    enc_args.append(self.symmetric_encrypt(i.encode(), password))
                else:
                    enc_args.append(i)

            self.listargs = [*enc_args, id, ]

            self.c.execute(f'''UPDATE {group} SET {params} WHERE ID=?''',
                           (self.listargs))
            self.conn.commit()

        else:
            raise Exception

    @connect_db_decorator
    def new_update_record(self, group, params, id, args):
        global password
        # if group != 'Producer':
        #     code_name = args[0:2]
        #     code_name[0] = code_name[0].lower()
        #     code_name[1] = code_name[1].lower()
        #     self.c.execute(f'''SELECT name FROM {group} WHERE name=? ''', (id,), )
        #     fetchall = self.c.fetchone()
        #     dec_fetchall = []
        #     for i in fetchall:
        #         if ENCRYPT_REACTIVES:
        #             dec_fetchall.append(self.symmetric_decrypt(bytes(i), password).decode())
        #         else:
        #             dec_fetchall.append(i)
        #
        #     check_repeat_code = code_name[0] == dec_fetchall[0].lower() or code_name[0] == '' or code_name[0] == ' '
        #     check_repeat_name = code_name[1] == dec_fetchall[1].lower()
        #
        #     check = check_repeat_code and check_repeat_name
        #     if check == False and code_name[1] == dec_fetchall[1].lower():
        #         check = self.check_unique([code_name[0], code_name[0]], 'reactives')
        #     elif check == False and code_name[0] == dec_fetchall[0].lower():
        #         check = self.check_unique([code_name[1], code_name[1]], 'reactives')
        #     elif check == False:
        #         check = self.check_unique(args[0:2], group)
        #
        #
        # else:
        #     code_name = args[0]
        #     code_name = code_name.lower()
        #     self.c.execute(f'''SELECT provider FROM {group} WHERE provider=? ''', (id,), )
        #     fetchall = self.c.fetchone()
        #     dec_fetchall = []
        #     for i in fetchall:
        #         if ENCRYPT_REACTIVES:
        #             dec_fetchall.append(self.symmetric_decrypt(bytes(i), password).decode())
        #         else:
        #             dec_fetchall.append(i)
        #
        #     check = code_name == dec_fetchall[0].lower()
        #     if check == False:
        #         check = self.check_unique(args[0:2], group)
        #
        # if check:
        enc_args = []
        for i in args:
            if ENCRYPT_REACTIVES:
                enc_args.append(self.symmetric_encrypt(i.encode(), password))
            else:
                enc_args.append(i)

        self.listargs = [*enc_args, id, ]
        if group != 'Producer':
            print(f'''UPDATE {group} SET {params} WHERE name=?''')
            self.c.execute(f'''UPDATE {group} SET {params} WHERE name=?''',
                           (self.listargs))
        else:
            self.c.execute(f'''UPDATE {group} SET {params} WHERE provider=?''',
                           (self.listargs))

        self.conn.commit()
        return True


    @connect_db_decorator
    def delete_records(self, group, name):
        if group != "Producer":
            self.c.execute(f'''DELETE FROM {group} WHERE NAME=?''', (name,))
        else:
            self.c.execute(f'''DELETE FROM {group} WHERE manager=?''', (name,))
        self.conn.commit()

    @connect_db_decorator
    def default_data(self, group, name_params, id):
        global password
        self.c.execute(f'''SELECT {name_params} FROM {group} WHERE ID = ?''', (id,))
        fetchall = self.c.fetchall()[0]
        if self.global_check:
            return fetchall
        decode_fetchall = []
        for item in fetchall:
            if type(item) != int and item != ' ':
                if ENCRYPT_REACTIVES:
                    decode_fetchall.append(self.symmetric_decrypt(bytes(item), password).decode())
                else:
                    decode_fetchall.append(item)
            else:
                decode_fetchall.append(item)

        return decode_fetchall

    @connect_db_decorator
    def insert_note(self, group, id, note):
        global password
        note = note.rstrip('\n')
        if ENCRYPT_REACTIVES and not self.global_check:
            note = self.symmetric_encrypt(note.encode(), password)

        self.c.execute(f'''UPDATE {group} SET note=? WHERE ID=?''', [note, id])
        self.conn.commit()

    @connect_db_decorator
    def search_records(self, columns, group, search, requests):
        global password
        print(f'''SELECT {columns} FROM {group} WHERE {requests}''')
        self.c.execute(f'''SELECT {columns} FROM {group} WHERE {requests}''', search, )
        fetchall = self.c.fetchall()
        if self.global_check:
            return fetchall

        decode_fetchall = []
        for item in fetchall:
            item_list = []
            for value in item:
                if type(value) != int:
                    if ENCRYPT_REACTIVES:
                        item_list.append(self.symmetric_decrypt(bytes(value), password).decode())
                    else:
                        item_list.append(value)
                else:
                    item_list.append(value)
            decode_fetchall.append(item_list)
        return decode_fetchall

    def check_unique(self, code_name, category):
        return True
        # if self.global_check:
        #     if category != 'Producer':
        #         code_name[0] = code_name[0].lower()
        #
        #         list_group = ['Solvents', 'Pigments', 'PigmPast', 'Fillers', 'Films', 'Additives', 'Hardener']
        #         validate = []
        #
        #         if code_name[0] != '' and code_name[0] != ' ':
        #             for group in list_group:
        #
        #                 self.c.execute(f'''SELECT * FROM {group} WHERE LOWER(DECODE(name))=? ''', (code_name[0],), )
        #                 fetchall = self.c.fetchone()
        #
        #                 validate.append(True) if fetchall == None else validate.append(False)
        #                 check = all(validate)
        #                 if check and code_name[1] != '' and code_name[1] != ' ':
        #                     check = True
        #                 else:
        #                     check = False
        #             return check
        #
        #         else:
        #             for group in list_group:
        #
        #                 self.c.execute(f'''SELECT * FROM {group} WHERE LOWER(DECODE(name))=? ''', (code_name[1],), )
        #                 fetchall = self.c.fetchone()
        #
        #                 validate.append(True) if fetchall == None else validate.append(False)
        #                 check = all(validate)
        #                 if check and code_name[1] != '' and code_name[1] != ' ':
        #                     check = True
        #                 else:
        #                     check = False
        #             return check
        #
        #
        #     else:
        #         code_name[0] = code_name[0].lower()
        #         self.c.execute(f'''SELECT * FROM producer WHERE LOWER(DECODE(provider))=?''', (code_name[0],), )
        #         fetchall = self.c.fetchone()
        #         check = True if fetchall == None else False
        #         return check
        # else:
        #     if category != 'Producer':
        #         code_name[0] = code_name[0].lower()
        #         code_name[1] = code_name[1].lower()
        #
        #         list_group = ['Solvents', 'Pigments', 'PigmPast', 'Fillers', 'Films', 'Additives', 'Hardener']
        #         validate = []
        #
        #         if code_name[0] != '' and code_name[0] != ' ':
        #             for group in list_group:
        #                 self.c.execute(f'''SELECT * FROM {group} WHERE LOWER(DECODE(code))=? OR LOWER(DECODE(name))=? ''',
        #                                code_name, )
        #                 fetchall = self.c.fetchone()
        #
        #                 validate.append(True) if fetchall == None else validate.append(False)
        #                 check = all(validate)
        #                 if check and code_name[1] != '' and code_name[1] != ' ':
        #                     check = True
        #                 else:
        #                     check = False
        #
        #             return check
        #
        #         else:
        #             for group in list_group:
        #
        #                 self.c.execute(f'''SELECT * FROM {group} WHERE LOWER(DECODE(name))=? ''', (code_name[1],), )
        #                 fetchall = self.c.fetchone()
        #
        #                 validate.append(True) if fetchall == None else validate.append(False)
        #                 check = all(validate)
        #                 if check and code_name[1] != '' and code_name[1] != ' ':
        #                     check = True
        #                 else:
        #                     check = False
        #
        #             return check
        #
        #
        #     else:
        #         code_name[0] = code_name[0].lower()
        #         self.c.execute(f'''SELECT * FROM producer WHERE LOWER(DECODE(provider))=?''', (code_name[0],), )
        #         fetchall = self.c.fetchone()
        #         check = True if fetchall == None else False
        #         return check



    @connect_db_decorator
    def check_group_reactives(self, group, search1):
        self.c.execute(f'''SELECT Name FROM {group} WHERE LOWER(DECODE(Name)) LIKE LOWER(?)''', [search1])
        fetchall = self.c.fetchall()
        decode_fetchall = []
        for item in fetchall:
            item_list = []
            for value in item:
                if type(value) != int:
                    if ENCRYPT_REACTIVES:
                        item_list.append(self.symmetric_decrypt(bytes(value), password).decode())
                    else:
                        item_list.append(value)
                else:
                    item_list.append(value)
            decode_fetchall.append(item_list)
        return decode_fetchall


    @connect_db_decorator
    def update_reactives_base(self):
        url = 'http://and124xw.beget.tech/export'
        urllib.request.urlretrieve(url, 'global_reactives.gdb')

        list_old_name = ['reactives_solvents', 'reactives_additives', 'reactives_fillers', 'reactives_films',
                         'reactives_hardeners',
                         'reactives_pigments', 'reactives_pigmpast', 'reactives_producer']
        list_new_name = ['Solvents', 'Additives', 'Fillers', 'Films', 'Hardener', 'Pigments', 'PigmPast', 'Producer']

        for new, old in zip(list_new_name, list_old_name):

            self.c.execute(f'''ALTER TABLE {old} RENAME TO {new}''')
            if new != 'Producer':
                self.c.execute(f'''ALTER TABLE {new} ADD COLUMN Provider text;''')
        self.conn.commit()

        for table in list_new_name[0:7]:
            self.c.execute(f'''SELECT id, provider_id FROM {table}''')
            all_data = self.c.fetchall()

            for data in all_data:
                data_id_producer = data[1]
                data_id_reactive = data[0]
                self.c.execute(f'''SELECT provider FROM Producer where id = {data_id_producer}''')
                data = self.c.fetchall()

                provider = data[0][0]
                self.c.execute(f'''UPDATE {table} SET provider = ? where id = ?''', (provider, data_id_reactive,), )
                self.conn.commit()
        self.c.execute(f'''DELETE FROM Producer where active = 0''')
        self.conn.commit()

    @connect_db_decorator
    def search(self, search):
        global password
        search = search.lower()
        search = ('%' + search + '%')
        self.c.execute('''SELECT Name FROM Components WHERE LOWER(DECODE(Name)) LIKE ? ''',
                       [search,])
        fetchall = self.c.fetchall()
        decode_fetchall = []
        for item in fetchall:
            item_list = []
            for value in item:
                if type(value) != int:
                    if ENCRYPT_REACTIVES:
                        item_list.append(self.symmetric_decrypt(bytes(value), password).decode())
                    else:
                        item_list.append(value)
                else:
                    item_list.append(value)
            decode_fetchall.append(item_list)

        decode_fetchall = list(map(lambda x: x[0], decode_fetchall))

        return decode_fetchall


    @connect_db_decorator
    def get_info_reactive(self, group, name, values):
        # print(f'''SELECT {values} FROM {group} WHERE LOWER(DECODE(Name)) LIKE LOWER(?)''')
        self.c.execute(f'''SELECT {values} FROM {group} WHERE LOWER(DECODE(Name)) LIKE LOWER(?)''', [name])
        fetchall = self.c.fetchall()
        decode_fetchall = []
        for item in fetchall:
            item_list = []
            for value in item:
                if type(value) != int:
                    if ENCRYPT_REACTIVES:
                        item_list.append(self.symmetric_decrypt(bytes(value), password).decode())
                    else:
                        item_list.append(value)
                else:
                    item_list.append(value)
            decode_fetchall.append(item_list)
        return decode_fetchall

    @connect_db_decorator
    def update_warehouse(self, group, name, warehouse):
        global password
        if ENCRYPT_REACTIVES:
            warehouse = self.symmetric_encrypt(warehouse.encode(), password)

        self.c.execute(f'''UPDATE {group} SET warehouse=? WHERE DECODE(name)=?''',
                       (warehouse, name,), )
        self.conn.commit()
