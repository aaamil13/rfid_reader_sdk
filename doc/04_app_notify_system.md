# Система за известяване на приложения

Системата за известяване в RFID Reader SDK използва callback подход, чрез който приложението получава информация за събития от RFID четеца. Това се осъществява чрез интерфейса `AppNotify` и неговите имплементации.

## Интерфейс `AppNotify`

`AppNotify` е абстрактен базов клас, който дефинира методи, извиквани при получаване на различни съобщения от RFID четеца.

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `notify_recv_tags(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при получаване на данни за таг |
| `notify_start_inventory(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при начало на инвентаризация |
| `notify_stop_inventory(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при край на инвентаризация |
| `notify_reset(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при ресетиране на четеца |
| `notify_read_tag_block(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при прочитане на блок от таг |
| `notify_write_tag_block(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при записване на блок в таг |
| `notify_lock_tag(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при заключване на таг |
| `notify_kill_tag(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при унищожаване на таг |
| `notify_inventory_once(message, start_index)` | message: bytearray, start_index: int | int | Извиква се при еднократна инвентаризация |

## Клас `GeneralReaderNotifyImpl`

`GeneralReaderNotifyImpl` е имплементация на `AppNotify` за общи RFID четци.

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `notify_recv_tags(message, start_index)` | message: bytearray, start_index: int | int | Обработва данни за таг |
| `notify_start_inventory(message, start_index)` | message: bytearray, start_index: int | int | Обработва начало на инвентаризация |
| `notify_stop_inventory(message, start_index)` | message: bytearray, start_index: int | int | Обработва край на инвентаризация |
| `notify_reset(message, start_index)` | message: bytearray, start_index: int | int | Обработва ресетиране на четеца |
| `notify_read_tag_block(message, start_index)` | message: bytearray, start_index: int | int | Обработва прочитане на блок от таг |
| `notify_write_tag_block(message, start_index)` | message: bytearray, start_index: int | int | Обработва записване на блок в таг |
| `notify_lock_tag(message, start_index)` | message: bytearray, start_index: int | int | Обработва заключване на таг |
| `notify_kill_tag(message, start_index)` | message: bytearray, start_index: int | int | Обработва унищожаване на таг |
| `notify_inventory_once(message, start_index)` | message: bytearray, start_index: int | int | Обработва еднократна инвентаризация |
| `notify_query_muti_param(message, start_index)` | message: bytearray, start_index: int | int | Обработва заявка за множество параметри |
| `notify_set_muti_param(message, start_index)` | message: bytearray, start_index: int | int | Обработва задаване на множество параметри |

## Клас `MRfidReaderNotifyImpl`

`MRfidReaderNotifyImpl` е имплементация на `AppNotify` за M-серия RFID четци.

### Константи

| Константа | Стойност | Описание |
|-----------|----------|----------|
| `TLV_ONE_TAG_DATA` | 0x50 | TLV тип за данни от един таг |
| `TLV_EPC` | 0x01 | TLV тип за EPC данни |

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `get_tlv_position(message, start_index, param_len, tlv_type)` | message: bytearray, start_index: int, param_len: int, tlv_type: int | int | Търси TLV в съобщението |
| `notify_recv_tags(message, start_index)` | message: bytearray, start_index: int | int | Обработва данни за таг |
| [други методи от AppNotify] | ... | ... | ... |

## Клас `R2000ReaderNotifyImpl`

`R2000ReaderNotifyImpl` е имплементация на `AppNotify` за R2000 RFID четци.

### Методи

| Метод | Аргументи | Връща | Описание |
|-------|-----------|-------|----------|
| `notify_recv_tags(message, start_index)` | message: bytearray, start_index: int | int | Обработва данни за таг |
| `notify_start_inventory(message, start_index)` | message: bytearray, start_index: int | int | Обработва начало на инвентаризация |
| `notify_stop_inventory(message, start_index)` | message: bytearray, start_index: int | int | Обработва край на инвентаризация |
| `notify_reset(message, start_index)` | message: bytearray, start_index: int | int | Обработва ресетиране на четеца |
| [други методи от AppNotify] | ... | ... | ... |

## Пример за създаване на собствена имплементация на AppNotify

Можете да създадете собствена имплементация на `AppNotify`, за да обработвате съобщения от RFID четеца според нуждите на вашето приложение:

```python
from rfid.reader.app_notify import AppNotify

class MyCustomNotifyImpl(AppNotify):
    """Собствена имплементация на AppNotify."""
    
    def notify_recv_tags(self, message, start_index):
        """Обработка при получаване на данни за таг."""
        # Извличане на ID на устройството
        device_id = message[start_index + 3] & 0xFF
        
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Обработка според нуждите на приложението
        print(f"Получен нов таг от устройство {hex(device_id)}")
        print(f"EPC: {' '.join([f'{b:02X}' for b in tag_data])}")
        
        # Уведомяване на базата данни или друг компонент на приложението
        self.on_new_tag_received(device_id, tag_data)
        
        return 0
    
    def on_new_tag_received(self, device_id, tag_data):
        """Метод, специфичен за приложението."""
        # Вашата логика тук
        pass
    
    # Имплементация на останалите методи от AppNotify...
```

## Пример за използване на AppNotify системата

```python
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.rfid_reader import RfidReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl

# Създаване на обект за известяване
notify_handler = GeneralReaderNotifyImpl()

# Инициализация на мениджъра
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца
reader.connect_physical_interface(
    "COM4", 9600, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
)

# Задаване на обработчик на съобщения
reader.set_app_notify(notify_handler)

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

# Стартиране на еднократна инвентаризация
reader.inventory_once()

# Приложението получава известия чрез методите на notify_handler
```