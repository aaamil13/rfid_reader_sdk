# RFID Reader SDK - Общ преглед

## Въведение

RFID Reader SDK е Python библиотека, която осигурява унифициран интерфейс за комуникация с различни модели RFID четци. Библиотеката абстрахира комуникацията с хардуера и позволява на разработчиците да се фокусират върху бизнес логиката на своите приложения.

## Архитектура на библиотеката

Библиотеката е организирана в следните основни модули:

- **rfid.reader** - Съдържа базовите класове за RFID четци и специфични имплементации
- **rfid.app_notify_impl** - Имплементации на callback интерфейси за различните типове четци
- **rfid.transport** - Транспортен слой за комуникация (сериен порт, TCP, UDP)
- **rfid.message** - Помощни класове за обработка на съобщения

## Поддържани RFID четци

Библиотеката поддържа следните типове RFID четци:

- **GeneralReader** - Общ RFID четец
- **MRfidReader** - M-серия RFID четец
- **R2000Reader** - R2000 RFID четец

## Поддържани транспортни протоколи

- Сериен порт (Serial/COM)
- TCP клиент
- UDP

## Основни функционалности

- Свързване към RFID четец чрез различни методи (сериен порт, мрежа)
- Инвентаризация на RFID тагове (еднократна или непрекъсната)
- Четене на данни от специфични области на тагове
- Записване на данни в тагове
- Заключване и унищожаване на тагове
- Управление на релета (при поддържани четци)

## Основен поток на работа

1. Инициализация на TransportThreadManager
2. Създаване на подходящ RFID четец
3. Задаване на обект за известяване (AppNotify имплементация)
4. Свързване към физическия интерфейс
5. Добавяне на четеца към TransportThreadManager
6. Изпълнение на операции с четеца
7. Обработка на отговорите чрез callback методите

## Пример за базово използване

```python
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца
reader.connect_physical_interface(
    "COM4",  # Име на порта
    9600,    # Бодова скорост
    None,    # Не се използва за сериен порт
    0,       # Не се използва за сериен порт
    RfidReader.CONNECT_TYPE_SERIALPORT
)

# Задаване на обработчик на съобщения
reader.set_app_notify(GeneralReaderNotifyImpl())

# Добавяне към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

# Еднократна инвентаризация
reader.inventory_once()

# Освобождаване на ресурси при приключване
reader.stop()
manager.stop()
```