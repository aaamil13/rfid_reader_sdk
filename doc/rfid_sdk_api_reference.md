# RFID Reader SDK API Reference

## Константи

### Типове връзка
```python
RfidReader.CONNECT_TYPE_SERIALPORT = 0     # Сериен порт
RfidReader.CONNECT_TYPE_NET_UDP = 1        # UDP връзка
RfidReader.CONNECT_TYPE_NET_TCP_CLIENT = 2 # TCP клиент
RfidReader.CONNECT_TYPE_NET_TCP_SERVER = 3 # TCP сървър
```

### Статуси на връзка
```python
Transport.CONNECT_STATUS_DISCONNECT = 0           # Прекъсната връзка
Transport.CONNECT_STATUS_GET_LOCAL_RESOURCE = 1   # Заявен локален ресурс
Transport.CONNECT_STATUS_CONNECTED = 2            # Осъществена връзка
```

### Области на таг (при GeneralReader)
```python
GeneralReader.RFID_TAG_MEMBANK_RESERVED = 0   # Резервирана област
GeneralReader.RFID_TAG_MEMBANK_EPC = 1        # EPC област
GeneralReader.RFID_TAG_MEMBANK_TID = 2        # TID област
GeneralReader.RFID_TAG_MEMBANK_USER = 3       # Потребителска област
```

### Типове заключване (при GeneralReader)
```python
GeneralReader.RFID_LOCK_USER = 0             # Заключване на потребителска област
GeneralReader.RFID_LOCK_TID = 1              # Заключване на TID област
GeneralReader.RFID_LOCK_EPC = 2              # Заключване на EPC област
GeneralReader.RFID_LOCK_ACCESS_PASSWORD = 3  # Заключване на паролата за достъп
GeneralReader.RFID_LOCK_KILL_PASSWORD = 4    # Заключване на паролата за унищожаване
GeneralReader.RFID_LOCK_ALL = 5              # Заключване на всички области
```

## Базови класове

### Transport
Базов клас за всички транспортни слоеве.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `release_resource()` | - | `int` | Освобождава заетите ресурси |
| `request_local_resource()` | - | `int` | Заявява локални ресурси за работа |
| `send_data(data, data_len)` | `data: bytes/bytearray, data_len: int` | `int` | Изпраща данни |
| `read_data(data)` | `data: bytearray` | `int` | Чете данни в предоставения буфер |

#### Наследници
- `TransportSerialPort` - за сериен порт
- `TransportTcpClient` - за TCP връзка
- `TransportUdp` - за UDP връзка

### AppNotify
Интерфейс за известяване при събития от RFID четеца.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `notify_recv_tags(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при получаване на данни за таг |
| `notify_start_inventory(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при начало на инвентаризация |
| `notify_stop_inventory(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при край на инвентаризация |
| `notify_reset(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при ресетиране на четеца |
| `notify_read_tag_block(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при прочитане на блок от таг |
| `notify_write_tag_block(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при записване на блок в таг |
| `notify_lock_tag(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при заключване на таг |
| `notify_kill_tag(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при унищожаване на таг |
| `notify_inventory_once(message, start_index)` | `message: bytes, start_index: int` | `int` | Извиква се при еднократна инвентаризация |

#### Имплементации
- `GeneralReaderNotifyImpl` - за стандартни RFID четци
- `MRfidReaderNotifyImpl` - за M-серия RFID четци
- `R2000ReaderNotifyImpl` - за R2000 RFID четци

### RfidReader
Базов клас за всички RFID четци.

#### Полета
| Поле | Тип | Описание |
|------|-----|----------|
| `key` | `str` | Уникален идентификатор на четеца |
| `recv_msg_buff` | `bytearray` | Буфер за получени съобщения |
| `recv_msg_len` | `int` | Дължина на получените данни |
| `app_notify` | `AppNotify` | Обект за известяване на приложението |
| `send_msg_buff` | `bytearray` | Буфер за изпращани съобщения |
| `send_index` | `int` | Текущ индекс в буфера за изпращане |
| `transport` | `Transport` | Транспортен обект |
| `connect_type` | `int` | Тип на връзката |

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `get_app_notify()` | - | `AppNotify` | Връща обекта за известяване |
| `set_app_notify(app_notify)` | `app_notify: AppNotify` | - | Задава обект за известяване |
| `get_key()` | - | `str` | Връща ключа на четеца |
| `connect_physical_interface()` | `physical_name: str, physical_param: int, local_addr_str: str, local_addr_port: int, connect_type: int` | `int` | Свързва се към физически интерфейс |
| `inventory()` | - | `int` | Започва непрекъсната инвентаризация |
| `inventory_once()` | - | `int` | Изпълнява еднократна инвентаризация |
| `stop()` | - | `int` | Спира инвентаризацията |
| `reset()` | - | `int` | Ресетира четеца |
| `read_tag_block()` | `membank: int, addr: int, length: int` | `int` | Чете блок данни от таг |
| `write_tag_block()` | `membank: int, addr: int, length: int, written_data: bytearray, write_start_index: int` | `int` | Записва данни в таг |
| `lock_tag(lock_type)` | `lock_type: int` | `int` | Заключва таг |
| `kill_tag()` | - | `int` | Унищожава таг |
| `handle_recv()` | - | `int` | Обработва получени данни |
| `handle_message()` | - | - | Обработва съобщение |
| `get_transport()` | - | `Transport` | Връща транспортния обект |

#### Наследници
- `GeneralReader` - за стандартни RFID четци
- `MRfidReader` - за M-серия RFID четци
- `R2000Reader` - за R2000 RFID четци

## Конкретни класове

### TransportSerialPort
Имплементация на транспорт за сериен порт.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `find_port()` | - | `list` | Статичен метод, връща списък с достъпни серийни портове |
| `set_serial_port_config()` | `port_name: str, baud_rate: int` | - | Задава конфигурация на серийния порт |

### TransportTcpClient
Имплементация на транспорт за TCP клиент.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `set_config()` | `remote_ip: str, remote_port: int, local_ip: str, local_port: int` | - | Задава конфигурация |

### TransportUdp
Имплементация на транспорт за UDP.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `set_config()` | `remote_ip: str, remote_port: int, local_ip: str, local_port: int` | - | Задава конфигурация |

### GeneralReader
Имплементация за стандартен RFID четец.

#### Специфични методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `query_parameter()` | `mem_address: int, query_len: int` | `int` | Заявява параметри на четеца |
| `set_muti_parameter()` | `mem_address: int, param_len: int, params: list` | `int` | Задава множество параметри на четеца |

### TransportThreadManager
Управлява нишки за комуникация с RFID четци.

#### Методи
| Метод | Параметри | Връща | Описание |
|-------|-----------|-------|----------|
| `get_instance()` | - | `TransportThreadManager` | Статичен метод, връща инстанция на мениджъра |
| `initialize_transport_manager()` | - | - | Статичен метод, инициализира мениджъра |
| `initialize_threads()` | - | - | Статичен метод, инициализира нишките |
| `add_rfid_reader()` | `reader: RfidReader` | `int` | Добавя RFID четец към мениджъра |
| `stop()` | - | - | Спира мениджъра и всички нишки |

## Кодове за връщане

### Общи кодове за връщане
| Код | Описание |
|-----|----------|
| `0` | Успех |
| `-1` | Обща грешка |

### Кодове при свързване
| Код | Описание |
|-----|----------|
| `0` | Успешно свързване |
| `-1` | Грешка при отваряне на порт/сокет |
| `-2` | Портът/сокетът е зает |
| `-3` | Грешка при конфигуриране |

### Кодове при операции с тагове
| Код | Описание |
|-----|----------|
| `0` | Успешна операция |
| `-1` | Няма отговор от тага |
| `-2` | Грешка при четене/запис |

## Структура на данните за таг

### GeneralReader формат
```
Байт 0: Флаг за начало (0xA0/0xE4)
Байт 1: Дължина на съобщението
Байт 2: Код на командата
Байт 3: ID на устройството
Байт 4: Дължина на данните за тага
Байт 5-N: Данни за тага
Байт N+1: Контролна сума
```

### MRfidReader формат (TLV)
```
Байт 0-1: "RF" (ASCII)
Байт 2: Флаг
Байт 3-4: ID на четеца
Байт 5: Команда
Байт 6-7: Дължина
Байт 8-N: TLV данни
  - Тип (1 байт)
  - Дължина (1 байт)
  - Стойност (променлива дължина)
Байт N+1: Контролна сума
```

### R2000Reader формат
```
Байт 0: Флаг за начало (0xAA/0xBB)
Байт 1-2: Дължина
Байт 3-4: ID на четеца
Байт 5: Команда
Байт 6-N: Данни
Байт N+1: Контролна сума
```