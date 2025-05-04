from server import ProtocolHandler
import socket
from server import Error
from server import CommandError

class Client(object):
    def __init__(self, host='127.0.0.1', port=31337):
        self._protocol = ProtocolHandler()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Создается сокет с использованием IPv4 (AF_INET) и TCP (SOCK_STREAM)
        self._socket.connect((host, port)) #Сокет подключается к указанному хосту и порту
        self._fh = self._socket.makefile('rwb')

    def execute(self, command, *args):
        try:
            print(f"Sending command: {command} {args}")
            # Создаем RESP-совместимый запрос
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

    def encode_resp_array(self, data):
        result = b'*%d\r\n' % len(data)
        for item in data:
            if isinstance(item, bytes):
                result += b'$%d\r\n%b\r\n' % (len(item), item)
            else:
                item_bytes = str(item).encode('utf-8')
                result += b'$%d\r\n%b\r\n' % (len(item_bytes), item_bytes)
        return result

    def read_response(self):  # Читает ответ с сервера и преобразует его в соответствующий тип данных Python
        first_byte = self._fh.read(1)  # Читает первый байт ответа.
        if not first_byte:
            return None
        if first_byte == b'+':  # Если первый байт '+', это простой строковый ответ.
            return self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8')  # Читает строку, удаляет завершающие символы новой строки и возвращает ее.
        elif first_byte == b'-':  # Если первый байт '-', это сообщение об ошибке.
            return Error(self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8'))  # Читает сообщение об ошибке, удаляет завершающие символы новой строки и возвращает объект Error.
        elif first_byte == b':':  # Если первый байт ':', это целочисленный ответ.
            return int(self._fh.readline().rstrip(b'\r\n').decode(
                'utf-8'))  # Читает число, удаляет завершающие символы новой строки и возвращает его как целое число.
        elif first_byte == b'$':  # Если первый байт '$', это строковый ответ.
            length = int(self._fh.readline().rstrip(b'\r\n'))  # Читает длину строки.
            print(f"Length: {length}")
            if length == -1:
                return None  # Если длина равна -1, возвращает None (null).
            return self._fh.read(length).decode(
                'utf-8')  # Читает строку указанной длины, удаляет завершающие символы \r\n и возвращает ее.
        elif first_byte == b'*':  # Если первый байт '*', это массив ответов.
            length = int(self._fh.readline().rstrip(b'\r\n'))  # Читает количество элементов в массиве.
            return [self.read_response() for _ in
                    range(length)]  # Рекурсивно читает каждый элемент массива и возвращает массив ответов.
        elif first_byte == b'%':  # Если первый байт '%', это словарь ответов.
            length = int(self._fh.readline().rstrip(b'\r\n'))  # Читает количество пар ключ-значение в словаре.
            return {self.read_response(): self.read_response() for _ in
                    range(length)}  # Рекурсивно читает каждую пару ключ-значение и возвращает словарь ответов.
        else:
            raise Exception('Unknown response type: %s' % first_byte)

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