# Мини-Redis на языке Python для баз данных
Проект демонстрирует процесс создания Redis для управления работой баз данных, СУБД.

## 1. Исследование предметной области
### Что такое Redis?
Remote Dictionary Service (или сокращённо Redis) — это СУБД типа ключ-значение, используемое в качестве базы данных, кэша и брокера сообщений. 

В отличие от баз данных, таких как PostgreSQL, SQL Server и других, все данные Redis находятся в основной памяти сервера, а не на жёстком диске. Благодаря этому Redis отличается более быстрым времем отклика, что, в свою очередь, приводит к высокой производительности при работе со средними операциями чтения и записи и, соответственно, поддержке миллионов операций в секунду.

Redis предоставляет пользователю общую систему, которая имеет системы кэширования в обеих типах архитектур — монолитных и распределенных, тем самым делая извлечение данных быстрее, поскольку операция прямого доступа по ключу в памяти уменьшит общую сложность чтения данных из исходной базы данных SQL.

![](https://github.com/DailDaul/proect-practice/blob/master/src/screens/Frame-102-1525x963.png)

### Основные типы данных Redis
1. Строки (Strings) - простейший тип данных, представляющий собой последовательность байтов.
2. Списки (Lists) - упорядоченный набор строк, позволяющий добавлять и удалять элементы как с начала, так и с конца списка.
3. Множества (Sets) - неупорядоченный набор уникальных строк.
4. Хэши (Hashes) - структура данных, представляющая собой набор пар “поле-значение”, где поля являются строками, а значения могут быть любыми типами данных Redis.
5. Сортированные множества (Sorted Sets) - множество, где каждый элемент связан с числовым значением (score). Элементы сортируются по score, позволяя выполнять быстрые запросы по диапазону значений.

### Применение Redis на Python
* Кэширование - самое распространенное применение Redis. Используется для кэширования часто используемых данных (например, результатов запросов к базе данных) для повышения производительности;
* управление сессиями, или же хранение информации о сессиях пользователей, что позволяет масштабировать веб-приложения;
* рреализация очередей задач для асинхронной обработки (например, с использованием Celery);
* использование Redis для реализации распределенных блокировок для координации работы нескольких процессов или серверов.

### Как создать свой Redis?
Для создания своего Redis необходимы:
1. Базовые знания в создании своего сервера в формате TCP (для работы с ним можно использовать любые программы, которые поддерживают создание сервера такого формата, например, Qt Creator).
2. Также, продолжая тему сервера, умение создавать связи запрос - ответ (он же ping & echo), а если говорить проще, то умение прописывать ответы сервера на действия пользователя.
3. Уже после идётнепосредственное прописывание функционала Redis, которое будет описано ниже в руководстве.

## 2. Техническое руководство
### Предварительные требования
* Базовые знания в программировании на Python;
* установить Python версии 3 и выше (можно установить с [официального сайта](https://www.python.org/));
* среда разработки PyCharm (или любая другая удобная среда разработки, позволяющая работать на Python. Далее - тех.руководство будет написано для работы с PyCharm);
* встроенные модули Python: ```io``` (работа с потоками) и ```collections``` (дополнительные контейнеры);
* библиотека ```Gevent```.

### Модификации
В рамках выбранной темы для вариативной части мы следовали [этой инструкции](https://charlesleifer.com/blog/building-a-simple-redis-server-with-python/). Однако, код в ней
либо неполный, либо неактульный для среды разработки PyCharm, из-за чего оказался нерабочим. 

Из-за этого в клиентском файле client.py была добавлена новая часть кода начиная с ```if name == `main` ```, а также была дописан метод ```execute```, который отвечает за запрос к Redis-серверу и получение ответа. Помимо этого был целиком добавлены новые методы ```encode_resp_array``` и ```read_response``` - первый нужен для кодирования массива данных в формат RESP, а второй - для чтения ответа с сервера и преобразования его в соотвестсвующий тип данных Python.

В файле сервера server.py в тех частях кода, где учавствовали строки, была добавлена ```b```, которая предполагает, что строки являются байтовыми (для примера, это добавлена в методе ```init```, отвечающий за словарь).

Были полностью изменены функции ```handle_error```, ```handle_integer```, ```handle_string```, ```handle_array```, ```handle_dict```, а также ```run```, который отвечал за сообщение, которое показывало, что сервер запущен.

### Создание технологии

#### 1. Создание проекта
Перед началом работы необходимо создать новый проект в выбранной среде разработки. В PyCharm это делается в три действия:
* в верхней панели программы нажать на ```File```, после чего откроется остальная панель, в которой уже нужно выбрать ```New project```;
* далее откроется новое окно, в котором нужно указать название проекта и его расположение. Далее на скринах проект будет называться ```Redis_project```. После указания всех настроек нужно нажать на кнопку ```Create```, после чего на панели слева появятся файлы проекта;
* при правильной установке, помимо файлов проекта, должны быть также и файлы библиотеки, которую мы установили ранее.

![](https://github.com/DailDaul/proect-practice/blob/master/src/screens/MyCollages%20(1).jpg)

#### 2. Установка библиотеки Gevent
Библиотека ```Gevent``` для Python - это, простыми словами, библиотека, которая позволяет одновременно обрабатывать данные и организовывает работу с сетью. В нашем же случае, эта библиотека позволит обрабатывать несколько клиентских соединений одновременно. 
Существует несколько способов установки, но мы устанавливали через ```командную строку``` без дополнительных скачиваний файлов.
Для установки библиотеки нужно открыть ```командную строку``` и с помощью ```cd``` подключиться к виртуальному окружению проекта с помощью пути. Для примера, как это будет выглядеть:
```
cd "C:\Python\Redis_project\.venv"
```
После того, как удалось успешно попасть в виртуальное окружение, что можно будет понять по названию окна командной строки, нужно будет ввести следующую команду:
```
pip install gevent
```

#### 3. Файлы проекта
При правильном создании проекта в файлах должны были быть автоматически созданы два файла: server.py и client.py. Если же этого не случилось по каким-то причинам, то просто нажимаем на проект, после чего высвечивается окно, в котором нажимаем на ```New```, а уже в новом окне ```Python file```. Таких нужно два - один для сервера, другой - для клиента соотвественно.

![](https://github.com/DailDaul/proect-practice/blob/master/src/screens/Web_Photo_Editor21.jpg)

#### 4. Server.py
Теперь начинаем работу с кодом. 
Прежде, чем начинать писать код, необходимо подключить всё нужное для работы (а именно модули и установленную ранее библиотеку):
```
from gevent import socket 
from gevent.pool import Pool
from gevent.server import StreamServer

from collections import namedtuple
from io import BytesIO
from socket import error as socket_error
```

* Из библитеки ```gevent``` этими командами мы подключили модуль ```socket```, который отвечает за работу с с сетевыми сокетами, а также два класса ```Pool``` и ```SreamServer```; первый необходим для работы с потоками (а именно - ограничить количество одновременно выполняемых задач), а второй для непосредственного создания сервера;
* зачем нужны модули ```io``` и ```collections``` было объяснено выше.

Далее в коде мы будем использовать исключения для того, чтобы уведомлять цикл обработки соединений о проблемах:
```
class CommandError(Exception): pass
class Disconnect(Exception): pass

Error = namedtuple('Error', ('message',))
```

* Класс ```CommandError``` нужен, как исключение, которое будет вызываться каждый раз, когда клиент отправляет неверную запрос или команду;
* класс ```Disconnect``` будет вызываться, когда клиент отключается;
* ```Error = namedtuple``` же создаёт неизменяемый объект, который хранит сообщение об ошибке.

Теперь можно приступать к созданию классов и методов, который нужны для непосредственной работы сервера с клиентом. Для этого создаём класс ```ProtocolHandler```, который будет отвечать за обработку сервером запросов и ответов от клиента. Помимо него также будет создан словарь ```self.handlers``` в методе ```def _init_```:
```
class ProtocolHandler(object):
    def __init__(self):
        self.handlers = {
            b'+': self.handle_simple_string,
            b'-': self.handle_error,
            b':': self.handle_integer,
            b'$': self.handle_string,
            b'*': self.handle_array,
            b'%': self.handle_dict}
```

После создания словаря и класса, мы также создаём метод ```handle_request```, который будет запрашивать запросы от клиента, а также в его рмках методы, которые будут обрабатывать разные типы символов (вроде ```integer```, ```string``` и т.д.):
```
def handle_request(self, socket_file):
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
        return socket_file.readline().rstrip(b'\r\n').decode('utf-8')

    def handle_error(self, socket_file):
        return Error(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))

    def handle_integer(self, socket_file):
        return int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))

    def handle_string(self, socket_file):
        # First read the length ($<length>\r\n).
        length = int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))
        if length == -1:
            return None  # Special-case for NULLs.
        length += 2  # Include the trailing \r\n in count.
        return socket_file.read(length)[:-2].decode('utf-8')

    def handle_array(self, socket_file):
        num_elements = int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))
        return [self.handle_request(socket_file) for _ in range(num_elements)]

    def handle_dict(self, socket_file):
        num_items = int(socket_file.readline().rstrip(b'\r\n').decode('utf-8'))
        elements = [self.handle_request(socket_file)
                    for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))
```

Следующий метод, необходимый для корректной работы сервера - это метод ```write_response``` для сериализации данных ответа или, простыми словами, для преобразования сложных структур в более простой формат, который уже можно передать по сети и отправить клиенту.
```
def write_response(self, socket_file, data): #Метод, который будет сериализовать данные ответа и отправлять их клиенту
        buf = BytesIO()
        self._write(buf, data)
        buf.seek(0)
        socket_file.write(buf.getvalue())
        socket_file.flush()
```

Оставшийся метод в этом классе необходим для работы с запросами клиента - метод ```_write``` отвечает за запись данных в буфер, предназначенный для отправки клиенту. Все команды типа ```if``` и ```elif``` нужны, в свою очередь, для записи.
```
def _write(self, buf, data):
        if isinstance(data, str):
            data = data.encode('utf-8')

        if isinstance(data, bytes):
            buf.write(b'$%d\r\n' % len(data))
            buf.write(data)
        elif isinstance(data, int):
            buf.write(b':%d\r\n' % data)
        elif isinstance(data, Error):
            buf.write(b'-%s\r\n' % data.message.encode('utf-8'))
        elif isinstance(data, (list, tuple)):
            buf.write(b'*%d\r\n' % len(data))
            for item in data:
                self._write(buf, item)
        elif isinstance(data, dict):
            buf.write(b'%%%d\r\n' % len(data))
            for key in data:
                self._write(buf, key)
                self._write(buf, data[key])
        elif data is None:
            buf.write(b'$-1\r\n')
        else:
            raise CommandError('unrecognized type: %s' % type(data))
```

На этом работу с классом ```ProtocolHandler``` мы закончили. Следующий основной класс, необходимый для сервера, мы назовём ```Server``` соотвественно, который будет инициализировать работу сервера. В рамках этого класса необходимо создать ```конструктор``` для найстройки сервера, а также методы, которые создают по экземпляру для ```StreamServer``` и ```ProtocolHandler```.
```
class Server(object): #Основной класс, который инициализирует сервер
    def __init__(self, host='127.0.0.1', port=31337, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer(
            (host, port),
            self.connection_handler,
            spawn=self._pool)

        self._protocol = ProtocolHandler()
        self._kv = {}
        self._commands = self.get_commands()

   def get_commands(self):
        return {
            'GET': self.get,
            'SET': self.set,
            'DELETE': self.delete,
            'FLUSH': self.flush,
            'MGET': self.mget,
            'MSET': self.mset}

```

Далее создаём метод ```connection_handler```, который будет отвечать за обработку каждого соединения с клиентом. В его рамках также необходимо прописать объект ```socket_file```, который преобразует сокет в объект, похожий на файл, чтобы можно было легко читать и записывать данные.
```
   def connection_handler(self, conn, address):
        socket_file = conn.makefile('rwb')
        while True:
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                print("Client disconnected gracefully.")
                break

            try:
                resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])

            self._protocol.write_response(socket_file, resp)
```

Далее метод ```get_response```, который предназначен для обработки данных, которые сервер получил от клиента.
```
 def get_response(self, data):
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
```

Оставшиеся методы в коде нужны для непосредственной работы сервера, ```run``` - для беспрерывной работы сервера; ```get``` - за получение данных сервером; ```set``` - за установку сервера, ```delete``` - удаление ключей из внутреннего словаря; ```flush``` - для очищения хранилища; ```mget``` - предназначен для нескольких ключей из хранилища данных, а ```mset``` - для установки пар значений.
```
    def run(self):
        print(f"Сервер запущен на {self._server.address[0]}:{self._server.address[1]}")
        self._server.serve_forever()

    def get(self, key):
        return self._kv.get(key)

    def set(self, key, value):
        self._kv[key] = value
        return 1

    def delete(self, key):
        if key in self._kv:
            del self._kv[key]
            return 1
        return 0

    def flush(self):
        kvlen = len(self._kv)
        self._kv.clear()
        return kvlen

    def mget(self, *keys):
        return [self._kv.get(key) for key in keys]

    def mset(self, *items):
        data = list(zip(items[::2], items[1::2]))
        for key, value in data:
            self._kv[key] = value
        return len(data)


if __name__ == '__main__':
    from gevent import monkey; monkey.patch_all()
    Server().run()
```

#### 5. Client.py
Как и в файле сервера, в файле клиента, первым делом, нужно расписать импорты, но в случае клиента они будут из файла server.py. Из этого файла добавляем классы ```ProtocolHandler``` для словаря и ```Error```, ```CommandError```, которые, что понятно по названию, отвечают за ошибки.
```
from server import ProtocolHandler
import socket
from server import Error
from server import CommandError
```

Теперь прописываем основной класс и метод для работы клиента: первым делом в нём нужно написать ```ip-адрес``` и ```порт```, которые будут использоваться для подключения к Redis через командную строку. В коде используем стандратные ```ip 127.0.0.1``` и ```порт 31337```. Помимо назначения данных, по которым будем подключаться, мы дописываем объекты, которые нужны для инициализации основных компонентов, необходимых для установления и поддержания соединения Redis.
```
class Client(object)
    def __init__(self, host='127.0.0.1', port=31337):
        self._protocol = ProtocolHandler()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._fh = self._socket.makefile('rwb')
```

Следующий метод ```execute``` является центральным для взаимодействия с Redis и отвечает за отправку команд Redis на сервер, получение ответа и обработку результата.
```
    def execute(self, command, *args):
        try:
            print(f"Sending command: {command} {args}")
            request = self.encode_resp_array(
                [command.encode('utf-8')] + [arg.encode('utf-8') if isinstance(arg, str) else str(arg).encode('utf-8')
                                             for arg in args])
            self._fh.write(request)
            self._fh.flush()
            print("Waiting for response...")
            resp = self.read_response()
            print(f"Received response: {resp}")
            if isinstance(resp, Error):
                raise CommandError(resp.message)
            return resp
        except Exception as e:
            print(f"An error occurred during execution: {e}")
            raise
```
Метод ```encode_resp_array```, которую был подвержен модификации, как и было сказано ранее, отвечает за кодирование массива данных в формат RESP. В случае, если элемент массива уже является байтовой строкой, он кодируется напрямую. В противном случае элемент преобразуется в строку, затем кодируется в байты с использованием UTF-8 и включается в результат.
```
    def encode_resp_array(self, data):
        result = b'*%d\r\n' % len(data)
        for item in data:
            if isinstance(item, bytes):
                result += b'$%d\r\n%b\r\n' % (len(item), item)
            else:
                item_bytes = str(item).encode('utf-8')
                result += b'$%d\r\n%b\r\n' % (len(item_bytes), item_bytes)
        return result
```

Дальше идёт массивная часть кода, принадлежащая одному-единственному методу - ```read_response```. Данный метод выполняет множество действий, краткая структура которых выглядит следующим образом:

* метод читает первый байт из сокета, чтобы определить тип RESP-ответа;
* на основе типа ответа, читает оставшиеся данные из сокета и декодирует их;
* преобразует данные в соответствующие типы Python (строки, целые числа, списки, словари, объекты Error);
* возвращает полученный результат.

Более подробная информация о том, какая строка за что отвечает, находится в файле [client.py](https://github.com/DailDaul/proect-practice/blob/master/src/client.py)
```
    def read_response(self):
        first_byte = self._fh.read(1)
        if not first_byte:
            return None
        if first_byte == b'+':
            return self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8')
        elif first_byte == b'-':
            return Error(self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8'))
        elif first_byte == b':':
            return int(self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8'))
        elif first_byte == b'$':
            length = int(self._fh.readline().rstrip(b'\r\n'))
            print(f"Length: {length}")
            if length == -1:
                return None
            return self._fh.read(length).decode(
                'utf-8')
        elif first_byte == b'*':
            length = int(self._fh.readline().rstrip(b'\r\n'))
            return [self.read_response() for _ in
                    range(length)]
        elif first_byte == b'%':
            length = int(self._fh.readline().rstrip(b'\r\n'))
            return {self.read_response(): self.read_response() for _ in
                    range(length)}
        else:
            raise Exception('Unknown response type: %s' % first_byte)
```

Следующие методы почти полностью повторяют те же методы, что и на сервере - как минимум, выполняют те же действия, потому объяснения будут опущены.
```
    def get(self, key):
        return self.execute('GET', key)

    def set(self, key, value):
        return self.execute('SET', key, value)

    def delete(self, key):
        return self.execute('DELETE', key)

    def flush(self):
        return self.execute('FLUSH')

    def mget(self, *keys):
        return self.execute('MGET', *keys)

    def mset(self, *items):
        return self.execute('MSET', *items)
```

Последний блок кода содержит примеры использования класса Client на практике. Он демонстрирует основные операции Redis, такие как SET, GET, DELETE, MSET, MGET и FLUSH, и обрабатывает возможные ошибки. О том, как это будет выглядеть в самой командной строке, будет описано в следующем пункте.
```
if __name__ == '__main__':
    client = Client()
    try:
        client.set('mykey', 'myvalue')
        print(f"SET: {client.get('mykey')}")
        client.delete('mykey')
        print(f"DELETE: {client.get('mykey')}")
        client.mset('key1', 'value1', 'key2', 'value2')
        print(f"MGET: {client.mget('key1', 'key2')}")
        client.flush()
        print(f"FLUSH: {client.mget('key1', 'key2')}")

    except CommandError as e:
        print(f"CommandError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

#### 6. Работа с Redis
Чтобы проверить, как работает созданный нами Redis, первым делом, необходимо запустить файл server.py и client.py. Делается это через боковую панель PyCharm под первым значком. Когда файлы успешно запущены, необходимо подключиться к серверу через командную строку, введя команду:
```
telnet 127.0.0.1 31337
```
```Ip``` и ```порт```, указанный в команде, это тот же самый ```ip-адрес``` и ```порт```, который мы установили в методе ```_init_```. Если вы установили другой, то, соотвественно, в команде должен быть тот же ```ip``` и ```порт```, который вы установили самостоятельно.

**ВАЖНО!** В Windows, версия которого выше 7 и XP, отсутствует встроенная поддержка telnet, поэтому, чтобы к нему подключиться, необходимо отдельно установить пакеты данных. Сделать это можно через ```Панель управления``` в пункте ```Программы и компоненты```. Там нужно нажать на пункт ```Включение или отключение компнентов Windows```, после чего откроется новое окно, в котором, в свою очередь, нужно найти пакет ```Клиент Telnet```, отметить его галочкой и нажать ```ОК```. После этого начнется установка пакета.

![](https://github.com/DailDaul/proect-practice/blob/master/src/screens/Web_Photo_Editor.jpg)

После введённой команды командная строка обновляется и предоставляет нам доступ к управлению.
