import logging
import traceback

from Crypto.Cipher import AES  # алгоритм шифрования
from Crypto.Hash import SHA256  # Для хеширования данных используем также популярный алгоритм SHA.
from Crypto.Hash import MD5
from Crypto import Random

class Secrets:
    password = None

    def encrypt_data(self, data, password=None):
        try:
            if password is None:
                password = "Hello, Интерлакокраска!"

            encrypted_data = self.symmetric_encrypt(data.encode(), password)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

        return encrypted_data


    def decrypt_data(self, bytes, password=None):
        try:
            if password is None:
                password = "Hello, Интерлакокраска!"
            decrypted_data = self.symmetric_decrypt(bytes, password)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e
            # print(decrypted_data)
        return decrypted_data


    def transform_password(self, password_str):
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
            #     f"Success!\nEncrypted hash is {decrypted_message_with_hesh[-dsize:].decode()}\nDecrypted hash is {digest}")
            return decrypted_message
        else:
            raise ValueError

