# Транспортен слой

Транспортният слой в RFID Reader SDK осигурява абстракция за комуникация с RFID четци чрез различни типове физически интерфейси - сериен порт, TCP или UDP. Това позволява на приложенията да използват един и същи API, независимо от начина на свързване с четеца.

## Базов клас `Transport`

`Transport` е абстрактен базов клас, който дефинира интерфейс за всички транспортни слоеве.

### Константи

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `CONNECT_STATUS_DISCONNECT` | 0 | Състояние на прекъсната връзка |
| `CONNECT_STATUS_GET_LOCAL_RESOURCE` | 1 | Състояние на заявени локални ресурси |
| `CONNECT_STATUS_CONNECTED` | 2 | Състояние на установена връзка |

### Полета

| Поле | Тип | Описание |
|------|-----|----------|
| `connect_status` | int | Текущо състояние на връзката |

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `__init__()` | - | - | Инициализира транспортния обект |
| `release_resource()` | - | int | Освобождава заетите ресурси |
| `request_local_resource()` | - | int | Заявява локални ресурси за работа |
| `send_data(data, data_len)` | data: bytes/bytearray, data_len: int | int | Изпраща данни |
| `read_data(data)` | data: bytearray | int | Чете данни |

## Клас `TransportSerialPort`

`TransportSerialPort` е имплементация на `Transport` за комуникация чрез сериен порт.

### Полета

| Поле | Тип | Описание |
|------|-----|----------|
| `serial_port_name` | str | Име на серийния порт |
| `baud_rate` | int | Скорост на комуникация (бод) |
| `serial_port_channel` | serial.Serial | Обект за сериен порт |

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `find_port()` | - | list | Статичен метод, връща списък с достъпни серийни портове |
| `set_serial_port_config(port_name, baud_rate)` | port_name: str, baud_rate: int | - | Задава конфигурация на серийния порт |
| `get_serial_port_name()` | - | str | Връща името на серийния порт |
| `set_serial_port_name(serial_port_name)` | serial_port_name: str | - | Задава името на серийния порт |
| `get_baud_rate()` | - | int | Връща скоростта на комуникация |
| `set_baud_rate(baud_rate)` | baud_rate: int | - | Задава скоростта на комуникация |
| `release_resource()` | - | int | Освобождава ресурси на серийния порт |
| `request_local_resource()` | - | int | Инициализира серийния порт |
| `send_data(data, data_len)` | data: bytes/bytearray, data_len: int | int | Изпраща данни през серийния порт |
| `read_data(data)` | data: bytearray | int | Чете данни от серийния порт |

### Пример за използване

```python
from rfid.transport.transport_serial_port import TransportSerialPort

# Създаване на транспортен обект за сериен порт
serial_port = TransportSerialPort()

# Задаване на конфигурация
serial_port.set_serial_port_config("COM4", 9600)

# Инициализация
result = serial_port.request_local_resource()
if result == 0:
    # Успешна инициализация
    data_to_send = bytearray([0xA0, 0x03, 0x01, 0x02, 0x03])
    serial_port.send_data(data_to_send, len(data_to_send))
    
    # Четене на данни
    receive_buffer = bytearray(128)
    bytes_read = serial_port.read_data(receive_buffer)
    
    # Освобождаване на ресурса
    serial_port.release_resource()
```

## Клас `TransportTcpClient`

`TransportTcpClient` е имплементация на `Transport` за комуникация чрез TCP клиент.

### Полета

| Поле | Тип | Описание |
|------|-----|----------|
| `remote_ip` | str | IP адрес на отдалечения сървър |
| `remote_port` | int | Порт на отдалечения сървър |
| `local_ip` | str | Локален IP адрес |
| `local_port` | int | Локален порт |
| `client_socket` | socket.socket | Сокет обект |
| `recv_buffer` | ByteBuffer | Буфер за получаване на данни |

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `set_config(remote_ip, remote_port, local_ip, local_port)` | remote_ip: str, remote_port: int, local_ip: str, local_port: int | - | Задава конфигурация |
| `request_local_resource()` | - | int | Инициализира TCP връзка |
| `send_data(data, data_len)` | data: bytes/bytearray, data_len: int | int | Изпраща данни чрез TCP |
| `read_data(data)` | data: bytearray | int | Чете данни от TCP връзка |
| `release_resource()` | - | int | Освобождава TCP ресурси |

### Пример за използване

```python
from rfid.transport.transport_tcp_client import TransportTcpClient

# Създаване на TCP клиент
tcp_client = TransportTcpClient()

# Задаване на конфигурация
tcp_client.set_config(
    "192.168.1.100",  # IP на RFID четеца
    5000,            # Порт на RFID четеца
    None,            # Локален IP
    0                # Локален порт
)

# Инициализация
result = tcp_client.request_local_resource()
if result == 0:
    # Успешна инициализация
    data_to_send = bytearray([0xA0, 0x03, 0x01, 0x02, 0x03])
    tcp_client.send_data(data_to_send, len(data_to_send))
    
    # Четене на данни
    receive_buffer = bytearray(128)
    bytes_read = tcp_client.read_data(receive_buffer)
    
    # Освобождаване на ресурса
    tcp_client.release_resource()
```

## Клас `TransportUdp`

`TransportUdp` е имплементация на `Transport` за комуникация чрез UDP.

### Полета

| Поле | Тип | Описание |
|------|-----|----------|
| `remote_ip` | str | IP адрес на отдалечената точка |
| `remote_port` | int | Порт на отдалечената точка |
| `local_ip` | str | Локален IP адрес |
| `local_port` | int | Локален порт |
| `socket_channel` | socket.socket | Сокет обект |
| `dst_addr` | tuple | Адрес на получателя (IP, порт) |

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `set_config(remote_ip, remote_port, local_ip, local_port)` | remote_ip: str, remote_port: int, local_ip: str, local_port: int | - | Задава конфигурация |
| `request_local_resource()` | - | int | Инициализира UDP сокет |
| `send_data(data, data_len)` | data: bytes/bytearray, data_len: int | int | Изпраща данни чрез UDP |
| `read_data(data)` | data: bytearray | int | Чете данни от UDP |
| `release_resource()` | - | int | Освобождава UDP ресурси |

### Пример за използване

```python
from rfid.transport.transport_udp import TransportUdp

# Създаване на UDP транспорт
udp_transport = TransportUdp()

# Задаване на конфигурация
udp_transport.set_config(
    "192.168.1.100",  # IP на RFID четеца
    5000,            # Порт на RFID четеца
    "0.0.0.0",       # Локален IP (всички интерфейси)
    6000             # Локален порт
)

# Инициализация
result = udp_transport.request_local_resource()
if result == 0:
    # Успешна инициализация
    data_to_send = bytearray([0xA0, 0x03, 0x01, 0x02, 0x03])
    udp_transport.send_data(data_to_send, len(data_to_send))
    
    # Четене на данни
    receive_buffer = bytearray(128)
    bytes_read = udp_transport.read_data(receive_buffer)
    
    # Освобождаване на ресурса
    udp_transport.release_resource()
```

## Клас `TransportThreadManager`

`TransportThreadManager` е сингълтън клас, който управлява нишките за комуникация с RFID четците.

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `get_instance()` | - | TransportThreadManager | Статичен метод, връща инстанция на мениджъра |
| `initialize_transport_manager()` | - | - | Статичен метод, инициализира мениджъра |
| `initialize_threads()` | - | - | Статичен метод, инициализира нишките |
| `get_reader_iterator()` | - | iterator | Връща итератор за регистрираните четци |
| `get_selector()` | - | selector | Връща селектора за неблокиращо I/O |
| `add_rfid_reader(reader)` | reader: RfidReader | int | Добавя RFID четец към мениджъра |
| `stop()` | - | - | Спира мениджъра и всички нишки |

### Пример за използване

```python
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.rfid_reader import RfidReader

# Инициализация на мениджъра
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца
reader.connect_physical_interface(
    "COM4",                          # Порт или IP
    9600,                            # Скорост или порт
    None,                            # Локален IP (само за мрежи)
    0,                               # Локален порт (само за мрежи)
    RfidReader.CONNECT_TYPE_SERIALPORT  # Тип на връзката
)

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

# При приключване
manager.stop()
```

## Клас `ReceiveThread`

`ReceiveThread` е нишка, която се използва от `TransportThreadManager` за получаване на данни от RFID четци.

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `__init__(manager)` | manager: TransportThreadManager | - | Инициализира нишката |
| `run()` | - | - | Изпълнява се при стартиране на нишката |