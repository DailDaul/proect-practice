from gevent import socket #Модуль для работы с сетевыми сокетами.
from gevent.pool import Pool #Класс для управления пулом зеленых потоков, что позволяет ограничить количество одновременно выполняемых задач.
from gevent.server import StreamServer #Класс для создания сервера, который обрабатывает входящие соединения

from collections import namedtuple #позволяет создать подкласс кортежа с именованными полями
from io import BytesIO #позволяет работать с байтовыми данными так, как если бы это был файл
from socket import error as socket_error


# Мы будем использовать исключения, чтобы уведомлять цикл обработки соединений о проблемах
class CommandError(Exception): pass #Исключение, которое будет вызываться, если клиент отправляет неправильную команду
class Disconnect(Exception): pass #Исключение, которое будет вызываться, когда клиент отключается

Error = namedtuple('Error', ('message',)) #Создает неизменяемый объект, который может быть использован для хранения сообщения об ошибке


class ProtocolHandler(object): #Этот класс будет обрабатывать запросы и ответы
    def __init__(self):
        self.handlers = { #создание словаря
            b'+': self.handle_simple_string,#изменено
            b'-': self.handle_error,
            b':': self.handle_integer,
            b'$': self.handle_string,
            b'*': self.handle_array,
            b'%': self.handle_dict}

    def handle_request(self, socket_file): #Метод, который должен будет парсить запрос от клиента
        first_byte = socket_file.read(1)
        if not first_byte:
            print("No data received, disconnecting.")
            raise Disconnect()

        print(f"Received first byte: {first_byte}")
        try:
            response = self.handlers[first_byte](socket_file)
            print(f"Response generated: {response}")
            return response
        except KeyError:
            print(f"No handler for command: {first_byte}")
            raise CommandError('bad request')

    def handle_simple_string(self, socket_file):
        return socket_file.readline().rstrip(b'\r\n').decode('utf-8')# вот это все изменено

    def handle_error(self, socket_file):
        return Error(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))

    def handle_integer(self, socket_file):
        return int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))

    def handle_string(self, socket_file):
        length = int(socket_file.readline().rstrip(b'\r\n'))
        if length == -1:
            return None
        data = socket_file.read(length + 2)
        return data[:-2].decode('utf-8')

    def handle_array(self, socket_file):
        num_elements = int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))
        return [self.handle_request(socket_file) for _ in range(num_elements)]

    def handle_dict(self, socket_file):
        num_items = int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))
        elements = [self.handle_request(socket_file)
                    for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))

    def write_response(self, socket_file, data): #Метод, который будет сериализовать данные ответа и отправлять их клиенту
        buf = BytesIO()
        self._write(buf, data)
        buf.seek(0)
        socket_file.write(buf.getvalue())
        socket_file.flush()

    def _write(self, buf, data):
        if isinstance(data, str):
            data = data.encode('utf-8')  # Преобразуем строку в байты

        if isinstance(data, bytes):
            buf.write(b'$%d\r\n' % len(data))  # Записываем байты тоже изменено
            buf.write(data)  # Записываем сами байты
        elif isinstance(data, int):
            buf.write(b':%d\r\n' % data)  # Записываем целое число
        elif isinstance(data, Error):
            buf.write(b'-%s\r\n' % data.message.encode('utf-8'))  # Преобразуем сообщение об ошибке в байты
        elif isinstance(data, (list, tuple)):
            buf.write(b'*%d\r\n' % len(data))  # Записываем длину списка/кортежа
            for item in data:
                self._write(buf, item)  # Рекурсивно записываем каждый элемент
        elif isinstance(data, dict):
            buf.write(b'%%%d\r\n' % len(data))  # Записываем длину словаря
            for key in data:
                self._write(buf, key)  # Записываем ключи
                self._write(buf, data[key])  # Записываем значения
        elif data is None:
            buf.write(b'$-1\r\n')  # Специальный случай для None
        else:
            raise CommandError('unrecognized type: %s' % type(data))  # Обработка неподдерживаемых типов

class Server(object): #Основной класс, который инициализирует сервер
    def __init__(self, host='127.0.0.1', port=31337, max_clients=64): #Конструктор, который настраивает сервер
        self._pool = Pool(max_clients) #Создает пул зеленых потоков с заданным максимальным количеством клиентов
        self._server = StreamServer( #Создает экземпляр StreamServer, который будет обрабатывать входящие соединения, используя метод connection_handler
            (host, port),
            self.connection_handler,
            spawn=self._pool)

        self._protocol = ProtocolHandler() #Создает экземпляр ProtocolHandler, который будет обрабатывать запросы и ответы
        self._kv = {} #Словарь для хранения пар ключ-значение, который будет использоваться для хранения данных
        self._commands = self.get_commands()

    def get_commands(self): # возвращает словарь, который сопоставляет команды с соответствующими методами для обработки этих команд
        return {
            'GET': self.get,
            'SET': self.set,
            'DELETE': self.delete,
            'FLUSH': self.flush,
            'MGET': self.mget,
            'MSET': self.mset}

    def connection_handler(self, conn, address): #Метод, который обрабатывает каждое соединение с клиентом
        # conn: Объект сокета, представляющий соединение с клиентом, socket_file: Преобразует сокет в объект, похожий на файл, чтобы можно было легко читать и записывать данные
        socket_file = conn.makefile('rwb') #Здесь метод makefile преобразует сокет в объект, похожий на файл, что позволяет использовать стандартные
        # методы чтения и записи, такие как read, write, и flush.  Параметры 'rwb' указывают, что мы будем читать и записывать данные в бинарном режиме

        # Обрабатываем запросы клиента до тех пор, пока клиент не отключится
        while True:
            try:
                data = self._protocol.handle_request(socket_file) # Обрабатываем запрос клиента и получаем данные
            except Disconnect:
                print("Client disconnected gracefully.") # Если клиент отключается, выходим из цикла
                break

            try:
                resp = self.get_response(data) # # Получаем ответ на полученные данные
            except CommandError as exc:
                resp = Error(exc.args[0]) ## Если возникает ошибка команды, формируем объект ошибки

            self._protocol.write_response(socket_file, resp) ## Отправляем ответ клиенту

    def get_response(self, data): # предназначен для обработки данных, полученных от клиента
        if not isinstance(data, list):
            raise CommandError('Request must be a list')

        if not data:
            raise CommandError('Missing command')

        command = data[0].upper()
        if command not in self._commands:
            raise CommandError('Unrecognized command: %s' % command)

        try:
            return self._commands[command](*data[1:])
            print(f"Sending response: {result}")
        except Exception as e:
            raise CommandError(f"Error executing command: {e}")

    def run(self): #отвечает за запуск сервера и его работу в бесконечном цикле
        print(f"Сервер запущен на {self._server.address[0]}:{self._server.address[1]}")
        self._server.serve_forever()

    def get(self, key): #получение данных
        return self._kv.get(key)

    def set(self, key, value): #установка данных
        self._kv[key] = value
        return 1

    def delete(self, key):
        if key in self._kv:
            del self._kv[key]
            return 1
        return 0

    def flush(self): # может очищать хранилище
        kvlen = len(self._kv)
        self._kv.clear()
        return kvlen

    def mget(self, *keys): #множественная операция
        return [self._kv.get(key) for key in keys]

    def mset(self, *items):
        data = list(zip(items[::2], items[1::2]))
        for key, value in data:
            self._kv[key] = value
        return len(data)


if __name__ == '__main__':
    from gevent import monkey; monkey.patch_all()
    Server().run()