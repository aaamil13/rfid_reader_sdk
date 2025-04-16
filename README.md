# RFID Reader SDK

Python библиотека за работа с RFID четци.

## Описание

RFID Reader SDK е Python библиотека, която предоставя API за комуникация с различни модели RFID четци. Библиотеката поддържа следните модели:

- General RFID Reader
- M RFID Reader
- R2000 RFID Reader

Транспортните слоеве включват:
- Сериен порт
- TCP клиент
- UDP

## Инсталация

```bash
pip install rfid-reader-sdk
```

Или инсталирайте директно от source:

```bash
git clone https://github.com/yourusername/rfid-reader-sdk.git
cd rfid-reader-sdk
pip install .
```

## Изисквания

- Python 3.6+
- pyserial 3.5+

## Използване

### Пример за General RFID Reader през TCP

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация на мениджъра на транспортните нишки
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца през TCP
result = reader.connect_physical_interface(
    "192.168.1.65",  # IP адрес на четеца
    5060,            # Порт на четеца
    None,            # Локален IP адрес
    0,               # Локален порт
    RfidReader.CONNECT_TYPE_NET_TCP_CLIENT  # Тип на връзката
)

if result == 0:
    print("Connected to the reader successfully.")
    
    # Задаване на обработчик на съобщения
    reader.set_app_notify(GeneralReaderNotifyImpl())
    
    # Добавяне на четеца към мениджъра
    manager = TransportThreadManager.get_instance()
    manager.add_rfid_reader(reader)
    
    # Спиране на инвентаризацията (ако е в ход)
    reader.stop()
    
    try:
        while True:
            # Изчакване
            time.sleep(3)
            
            # Еднократна инвентаризация
            reader.inventory_once()
    except KeyboardInterrupt:
        # Прекратяване на програмата при Ctrl+C
        print("Stopping...")
        reader.stop()
        manager.stop()
else:
    print(f"Failed to connect to the reader. Error code: {result}")
```

### Пример за използване на сериен порт

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация на мениджъра на транспортните нишки
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца през сериен порт
result = reader.connect_physical_interface(
    "COM4",          # Име на серийния порт
    9600,            # Бодова скорост
    None,            # Не се използва за сериен порт
    0,               # Не се използва за сериен порт
    RfidReader.CONNECT_TYPE_SERIALPORT  # Тип на връзката
)

if result == 0:
    print("Connected to the reader successfully.")
    
    # Задаване на обработчик на съобщения
    reader.set_app_notify(GeneralReaderNotifyImpl())
    
    # Добавяне на четеца към мениджъра
    manager = TransportThreadManager.get_instance()
    manager.add_rfid_reader(reader)
    
    try:
        while True:
            # Изчакване
            time.sleep(3)
            
            # Еднократна инвентаризация
            reader.inventory_once()
    except KeyboardInterrupt:
        # Прекратяване на програмата при Ctrl+C
        print("Stopping...")
        reader.stop()
        manager.stop()
else:
    print(f"Failed to connect to the reader. Error code: {result}")
```

## Лиценз

MIT

## Автори