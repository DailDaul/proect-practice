# Мини-Redis на языке Python для баз данных
Проект демонстрирует процесс создания Redis для управления работой баз данных, СУБД.

## 1. Исследование предметной области
### Что такое Redis?
Remote Dictionary Service (или сокращённо Redis) — это СУБД типа ключ-значение, используемое в качестве базы данных, кэша и брокера сообщений. 

В отличие от баз данных, таких как PostgreSQL, SQL Server и других, все данные Redis находятся в основной памяти сервера, а не на жёстком диске. Благодаря этому Redis отличается более быстрым времем отклика, что, в свою очередь, приводит к высокой производительности при работе со средними операциями чтения и записи и, соответственно, поддержке миллионов операций в секунду.

Redis предоставляет пользователю общую систему, которая имеет системы кэширования в обеих типах архитектур — монолитных и распределенных, тем самым делая извлечение данных быстрее, поскольку операция прямого доступа по ключу в памяти уменьшит общую сложность чтения данных из исходной базы данных SQL.

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
* встроенные модули Pyhon: ```io``` (работа с потоками) и ```collections``` (дополнительные контейнеры);
* библиотека ```Gevent```.

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
![](https://github.com/DailDaul/proect-practice/blob/master/src/screens/Web_Photo_Editor.jpg)

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
