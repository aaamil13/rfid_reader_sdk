# RFID Четци

## Базов клас `RfidReader`

`RfidReader` е абстрактен базов клас, който дефинира общия интерфейс за всички RFID четци.

### Константи

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `CONNECT_TYPE_SERIALPORT` | 0 | Свързване чрез сериен порт |
| `CONNECT_TYPE_NET_UDP` | 1 | Свързване чрез UDP |
| `CONNECT_TYPE_NET_TCP_CLIENT` | 2 | Свързване чрез TCP клиент |
| `CONNECT_TYPE_NET_TCP_SERVER` | 3 | Свързване чрез TCP сървър |
| `MAX_RECV_BUFF_SIZE` | 1024 | Максимален размер на приемния буфер |
| `MAX_SEND_BUFF_SIZE` | 128 | Максимален размер на изпращащия буфер |

### Полета

| Поле | Тип | Описание |
|------|-----|----------|
| `key` | str | Уникален идентификатор на четеца |
| `recv_msg_buff` | bytearray | Буфер за получени съобщения |
| `recv_msg_len` | int | Дължина на получените данни |
| `app_notify` | AppNotify | Обект за известяване на приложението |
| `send_msg_buff` | bytearray | Буфер за изпращани съобщения |
| `send_index` | int | Текущ индекс за запис в изпращащия буфер |
| `recv_len` | int | Брой байтове, получени от последното четене |
| `transport` | Transport | Транспортен обект |
| `connect_type` | int | Тип на връзката |

### Методи

#### Инициализация и управление на връзката

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `__init__()` | - | - | Инициализира RFID четеца |
| `get_app_notify()` | - | AppNotify | Връща обекта за известяване |
| `set_app_notify(app_notify)` | app_notify: AppNotify | - | Задава обект за известяване |
| `get_key()` | - | str | Връща ключа на четеца |
| `connect_physical_interface(physical_name, physical_param, local_addr_str, local_addr_port, connect_type)` | physical_name: str, physical_param: int, local_addr_str: str, local_addr_port: int, connect_type: int | int | Свързва се към физически интерфейс |
| `get_unsigned_byte(data)` | data: int | int | Преобразува signed byte към unsigned byte (0-255) |
| `get_transport()` | - | Transport | Връща транспортния обект |

#### Операции с RFID четец

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `inventory()` | - | int | Започва непрекъсната инвентаризация |
| `inventory_once()` | - | int | Изпълнява еднократна инвентаризация |
| `stop()` | - | int | Спира инвентаризацията |
| `relay_operation(relay_no, operation_type, time)` | relay_no: int, operation_type: int, time: int | int | Извършва операция с реле |
| `reset()` | - | int | Ресетира четеца |
| `read_tag_block(membank, addr, length)` | membank: int, addr: int, length: int | int | Чете блок от данни от таг |
| `write_tag_block(membank, addr, length, written_data, write_start_index)` | membank: int, addr: int, length: int, written_data: bytearray, write_start_index: int | int | Записва данни в таг |
| `lock_tag(lock_type)` | lock_type: int | int | Заключва таг |
| `kill_tag()` | - | int | Унищожава таг |

#### Обработка на съобщения

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `handle_recv()` | - | int | Обработва получени данни |
| `handle_message()` | - | - | Обработва съобщение |
| `notify_message_to_app(message, start_index)` | message: bytearray, start_index: int | - | Известява приложението за съобщение |

## Клас `GeneralReader`

`GeneralReader` е конкретна имплементация на `RfidReader` за стандартни RFID четци.

### Константи

#### Флагове на команди

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `START_CMD_FLAG` | 0xA0 | Флаг за начало на команда |
| `START_RSP_FLAG` | 0xE4 | Флаг за начало на отговор |
| `START_NOTIFY_FLAG` | 0xE0 | Флаг за начало на известие |

#### Команди

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `CMD_NOTIFY_TAG` | 0xFF | Известие за таг |
| `RFID_CMD_QUERY_SINGLE_PARAM` | 0x61 | Заявка за единичен параметър |
| `RFID_CMD_SET_MUTI_PARAM` | 0x62 | Задаване на множество параметри |
| `RFID_CMD_QUERY_MUTI_PARAM` | 0x63 | Заявка за множество параметри |
| `RFID_CMD_RESET_DEVICE` | 0x65 | Ресетиране на устройството |
| `RFID_CMD_QUERY_VERSION` | 0x6A | Заявка за версия |
| `RFID_CMD_STOP_INVETORY` | 0xFE | Спиране на инвентаризацията |
| `RFID_CMD_READ_TAG_BLOCK` | 0x80 | Четене на блок от таг |
| `RFID_CMD_WRITE_TAG_BLOCK` | 0x81 | Запис на блок в таг |
| `RFID_CMD_IDENTIFY_TAG` | 0x82 | Идентифициране на таг |
| `RFID_CMD_ENCRYPT_TAG` | 0x83 | Криптиране на таг |
| `RFID_CMD_KILL_TAG` | 0x86 | Унищожаване на таг |
| `RFID_CMD_LOCK_TAG` | 0x87 | Заключване на таг |

#### Области на таг

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `RFID_TAG_MEMBANK_RESERVED` | 0 | Резервирана област |
| `RFID_TAG_MEMBANK_USER` | 3 | Потребителска област |
| `RFID_TAG_MEMBANK_EPC` | 1 | EPC област |
| `RFID_TAG_MEMBANK_TID` | 2 | TID област |

#### Типове заключване

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `RFID_LOCK_USER` | 0 | Заключване на потребителска област |
| `RFID_LOCK_TID` | 1 | Заключване на TID област |
| `RFID_LOCK_EPC` | 2 | Заключване на EPC област |
| `RFID_LOCK_ACCESS_PASSWORD` | 3 | Заключване на паролата за достъп |
| `RFID_LOCK_KILL_PASSWORD` | 4 | Заключване на паролата за унищожаване |
| `RFID_LOCK_ALL` | 5 | Заключване на всички области |

### Специфични методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `build_message_header(command_code)` | command_code: int | - | Изгражда заглавие на съобщение |
| `_calculate_checksum(message, start_pos, length)` | message: bytearray, start_pos: int, length: int | int | Изчислява контролна сума |
| `query_parameter(mem_address, query_len)` | mem_address: int, query_len: int | int | Заявява параметри на четеца |
| `set_muti_parameter(mem_address, param_len, params)` | mem_address: int, param_len: int, params: list | int | Задава множество параметри на четеца |

## Клас `MRfidReader`

`MRfidReader` е имплементация на `RfidReader` за M-серия RFID четци.

### Константи

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `MREADER_CMD_RESET` | 0x10 | Команда за ресетиране |
| `MREADER_NOTIFY_TAG` | 0x80 | Известие за таг |

### Специфични методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `_calculate_checksum(message, start_pos, length)` | message: bytearray, start_pos: int, length: int | int | Изчислява контролна сума |
| `_fill_length_and_checksum()` | - | - | Запълва дължината и контролната сума |
| `build_message_header(command_code)` | command_code: int | - | Изгражда заглавие на съобщение |

## Клас `R2000Reader`

`R2000Reader` е имплементация на `RfidReader` за R2000 RFID четци.

### Константи

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `START_RSP_FLAG` | 0xBB | Флаг за начало на отговор |
| `START_CMD_FLAG` | 0xAA | Флаг за начало на команда |
| `RFID_CMD_TAG_NOTIFY` | 0x10 | Известие за таг |
| `RFID_CMD_STOP_INVETORY` | 0x31 | Спиране на инвентаризация |
| `RFID_CMD_START_INVENTORY` | 0x32 | Започване на инвентаризация |
| `RFID_CMD_RESET_DEVICE` | 0x65 | Ресетиране на устройството |

### Специфични методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `build_message_header(command_code)` | command_code: int | - | Изгражда заглавие на съобщение |
| `_calculate_checksum(message, start_pos, length)` | message: bytearray, start_pos: int, length: int | int | Изчислява контролна сума |
| `_fill_length_and_checksum()` | - | - | Запълва дължината и контролната сума |