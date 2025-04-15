# Разширени теми

В този документ са представени разширени функционалности и практики за работа с RFID Reader SDK.

## Обработка на грешки

При работа с RFID четци е важно да се обработват правилно всички възможни грешки. Ето най-честите грешки, които могат да възникнат:

### 1. Грешки при свързване

```python
from rfid.reader.rfid_reader import RfidReader
from rfid.reader.general_reader import GeneralReader

def connect_to_reader(port, baudrate):
    reader = GeneralReader()
    
    result = reader.connect_physical_interface(
        port, baudrate, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
    )
    
    if result != 0:
        if result == -1:
            raise ConnectionError(f"Не може да се намери порт {port}")
        elif result == -2:
            raise ConnectionError(f"Портът {port} е зает от друго приложение")
        else:
            raise ConnectionError(f"Грешка при свързване: код {result}")
    
    return reader
```

### 2. Таймаут при четене

```python
import time
from rfid.reader.general_reader import GeneralReader

class RfidTimeoutError(Exception):
    pass

def read_tag_with_timeout(reader, membank, addr, length, timeout_seconds=3):
    # Флаг за успешно четене
    success = [False]
    
    # Функция за известяване, която ще се използва като колбек
    def on_tag_read(message, start_index):
        # Проверка дали четенето е успешно
        if message[start_index + 1] > 3:
            success[0] = True
        return 0
    
    # Запазване на оригиналния колбек
    original_callback = reader.get_app_notify()
    
    # Създаване на временен колбек обект, който ще обработи отговора
    class TempCallback:
        def notify_read_tag_block(self, message, start_index):
            return on_tag_read(message, start_index)
        
        # Препращане на всички останали методи към оригиналния колбек
        def __getattr__(self, name):
            return getattr(original_callback, name)
    
    # Задаване на временния колбек
    reader.set_app_notify(TempCallback())
    
    try:
        # Изпращане на команда за четене
        reader.read_tag_block(membank, addr, length)
        
        # Изчакване на отговор с таймаут
        start_time = time.time()
        while not success[0]:
            time.sleep(0.1)
            if time.time() - start_time > timeout_seconds:
                raise RfidTimeoutError("Таймаут при четене на таг")
        
    finally:
        # Възстановяване на оригиналния колбек
        reader.set_app_notify(original_callback)
```

### 3. Проверка за валидност на данните

```python
def validate_epc_data(epc_data):
    """Проверка за валидност на EPC данни."""
    # Минимална дължина за EPC данни
    if len(epc_data) < 12:
        return False
    
    # Проверка на контролната сума (CRC-16)
    calculated_crc = calculate_crc16(epc_data[:-2])
    received_crc = (epc_data[-2] << 8) | epc_data[-1]
    
    return calculated_crc == received_crc

def calculate_crc16(data):
    """Изчисляване на CRC-16 за EPC данни."""
    crc = 0xFFFF
    
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc = crc >> 1
    
    return crc
```

## Поддръжка на множество четци

Библиотеката поддържа работа с множество RFID четци едновременно. Ето примерен код:

```python
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.rfid_reader import RfidReader

# Клас за управление на множество четци
class MultiReaderManager:
    def __init__(self):
        # Инициализация на мениджъра
        TransportThreadManager.initialize_transport_manager()
        self.manager = TransportThreadManager.get_instance()
        self.readers = {}
    
    def add_reader(self, reader_id, port, baudrate, notify_handler):
        """Добавя нов четец."""
        # Създаване на четец
        reader = GeneralReader()
        
        # Свързване към четеца
        result = reader.connect_physical_interface(
            port, baudrate, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
        )
        
        if result != 0:
            raise ConnectionError(f"Грешка при свързване на четец {reader_id}")
        
        # Задаване на обработчик на съобщения
        reader.set_app_notify(notify_handler)
        
        # Добавяне на четеца към мениджъра
        self.manager.add_rfid_reader(reader)
        
        # Запазване на четеца в речника
        self.readers[reader_id] = reader
        
        return reader
    
    def remove_reader(self, reader_id):
        """Премахва четец."""
        if reader_id in self.readers:
            # Спиране на четеца
            self.readers[reader_id].stop()
            # Премахване от речника
            del self.readers[reader_id]
    
    def start_inventory_all(self):
        """Стартира инвентаризация на всички четци."""
        for reader in self.readers.values():
            reader.inventory()
    
    def stop_inventory_all(self):
        """Спира инвентаризацията на всички четци."""
        for reader in self.readers.values():
            reader.stop()
    
    def shutdown(self):
        """Освобождава всички ресурси."""
        self.stop_inventory_all()
        self.readers.clear()
        self.manager.stop()
```

## Асинхронна обработка на събития

За по-ефективна обработка на събития от RFID четците, можете да използвате асинхронен подход с asyncio:

```python
import asyncio
import threading
import queue
from rfid.reader.app_notify import AppNotify

# Асинхронен обработчик на събития от RFID четци
class AsyncRfidHandler:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.running = False
        self.processing_task = None
    
    def start(self):
        """Стартира асинхронната обработка."""
        self.running = True
        self.processing_task = asyncio.create_task(self.process_events())
    
    def stop(self):
        """Спира асинхронната обработка."""
        self.running = False
        if self.processing_task:
            self.processing_task.cancel()
    
    def create_notify_handler(self):
        """Създава обработчик за RFID четеца."""
        return AsyncNotifyHandler(self)
    
    def enqueue_event(self, event_type, data):
        """Добавя събитие в опашката."""
        self.event_queue.put((event_type, data))
    
    async def process_events(self):
        """Обработва събитията от опашката."""
        while self.running:
            try:
                # Проверка за нови събития
                if not self.event_queue.empty():
                    event_type, data = self.event_queue.get()
                    await self.handle_event(event_type, data)
                    self.event_queue.task_done()
                else:
                    # Кратко изчакване
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Грешка при обработка на събитие: {e}")
    
    async def handle_event(self, event_type, data):
        """Обработва конкретно събитие."""
        if event_type == "tag":
            # Обработка на таг
            tag_id = data["tag_id"]
            await self.process_tag(tag_id)
        elif event_type == "inventory_start":
            # Обработка на начало на инвентаризация
            reader_id = data["reader_id"]
            print(f"Започната инвентаризация на четец {reader_id}")
        elif event_type == "inventory_stop":
            # Обработка на край на инвентаризация
            reader_id = data["reader_id"]
            print(f"Спряна инвентаризация на четец {reader_id}")
    
    async def process_tag(self, tag_id):
        """Обработва данни за таг."""
        # Тук може да добавите асинхронна логика
        # Например, заявка към сървър или база данни
        print(f"Обработка на таг: {tag_id}")

# Обработчик, който ще се използва от RFID четеца
class AsyncNotifyHandler(AppNotify):
    def __init__(self, async_handler):
        self.async_handler = async_handler
        self.reader_id = "unknown"
    
    def set_reader_id(self, reader_id):
        """Задава идентификатор на четеца."""
        self.reader_id = reader_id
    
    def notify_recv_tags(self, message, start_index):
        """Обработва получаване на таг."""
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Преобразуване на данните в hex string
        tag_id = ''.join([f'{b:02X}' for b in tag_data])
        
        # Добавяне на събитието в опашката
        self.async_handler.enqueue_event("tag", {
            "reader_id": self.reader_id,
            "tag_id": tag_id
        })
        
        return 0
    
    def notify_start_inventory(self, message, start_index):
        """Обработва начало на инвентаризация."""
        self.async_handler.enqueue_event("inventory_start", {
            "reader_id": self.reader_id
        })
        return 0
    
    def notify_stop_inventory(self, message, start_index):
        """Обработва край на инвентаризация."""
        self.async_handler.enqueue_event("inventory_stop", {
            "reader_id": self.reader_id
        })
        return 0
    
    # Имплементация на останалите методи от AppNotify
    # ...
```

## Оптимизация на производителността

За оптимизация на производителността при работа с RFID четци, можете да използвате следните техники:

### 1. Буфериране на данни

```python
class TagBuffer:
    def __init__(self, max_size=100):
        self.buffer = []
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def add_tag(self, tag_data):
        """Добавя таг в буфера."""
        with self.lock:
            # Ако тагът вече съществува, не го добавяме отново
            if tag_data not in self.buffer:
                self.buffer.append(tag_data)
                
                # Ако буферът е пълен, премахваме най-стария таг
                if len(self.buffer) > self.max_size:
                    self.buffer.pop(0)
    
    def get_tags(self):
        """Връща копие на буфера."""
        with self.lock:
            return self.buffer.copy()
    
    def clear(self):
        """Изчиства буфера."""
        with self.lock:
            self.buffer.clear()
```

### 2. Настройка на параметрите на четеца

```python
def optimize_reader_params(reader):
    """Оптимизира параметрите на четеца за по-добра производителност."""
    # Настройка на мощност на антена (стойностите зависят от модела на четеца)
    # Пример за General Reader
    params = [0x05, 0x10, 0x00, 0x18]  # 24 dBm мощност (0x18 = 24)
    reader.set_muti_parameter(0x01, len(params), params)
    
    # Настройка на скорост на комуникация с таговете
    params = [0x04, 0x10, 0x00, 0x02]  # Tari = 12.5us (по-бърза комуникация)
    reader.set_muti_parameter(0x02, len(params), params)
    
    # Настройка на режим на четене (само за определени модели)
    params = [0x01, 0x10, 0x00, 0x01]  # Dense Reader Mode (при много тагове)
    reader.set_muti_parameter(0x03, len(params), params)
```

### 3. Използване на пула от нишки

```python
import concurrent.futures

class TagProcessor:
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.processed_tags = set()
    
    def submit_tag(self, tag_data):
        """Подава таг за обработка в пула от нишки."""
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        # Проверка дали тагът вече е обработен
        if tag_hex not in self.processed_tags:
            # Подаване на задачата към пула
            future = self.executor.submit(self.process_tag, tag_hex)
            future.add_done_callback(self.on_tag_processed)
    
    def process_tag(self, tag_hex):
        """Обработва таг (изпълнява се в отделна нишка)."""
        # Извършване на времеемки операции
        # Например валидация, заявка към база данни, др.
        print(f"Обработка на таг: {tag_hex}")
        return tag_hex
    
    def on_tag_processed(self, future):
        """Извиква се, когато обработката на таг приключи."""
        try:
            tag_hex = future.result()
            self.processed_tags.add(tag_hex)
            print(f"Тагът {tag_hex} е обработен успешно")
        except Exception as e:
            print(f"Грешка при обработка на таг: {e}")
    
    def shutdown(self):
        """Освобождава ресурсите на пула."""
        self.executor.shutdown()
```

## Работа с различни видове тагове

RFID технологията поддържа различни типове тагове. Ето как да работите с тях:

### 1. Идентифициране на типа на тага

```python
def identify_tag_type(epc_data):
    """Идентифицира типа на тага по EPC данните."""
    if len(epc_data) < 2:
        return "Unknown"
    
    # Проверка на Header (първи байт)
    header = epc_data[0] >> 2
    
    if header == 0x30:
        return "SGTIN-96"  # Serialized Global Trade Item Number
    elif header == 0x31:
        return "SSCC-96"   # Serial Shipping Container Code
    elif header == 0x32:
        return "SGLN-96"   # Global Location Number with Serial
    elif header == 0x33:
        return "GRAI-96"   # Global Returnable Asset Identifier
    elif header == 0x34:
        return "GIAI-96"   # Global Individual Asset Identifier
    elif header == 0x35:
        return "GID-96"    # General Identifier
    else:
        return "Unknown"
```

### 2. Декодиране на данни от конкретен тип таг

```python
def decode_sgtin_96(epc_data):
    """Декодира SGTIN-96 (Serialized Global Trade Item Number)."""
    if len(epc_data) != 12:  # SGTIN-96 е 96 бита = 12 байта
        return None
    
    # Извличане на филтър стойност (3 бита)
    filter_value = (epc_data[0] & 0x07) << 1 | ((epc_data[1] & 0x80) >> 7)
    
    # Извличане на разделение (3 бита)
    partition = (epc_data[1] & 0x78) >> 3
    
    # Извличане на Company Prefix и Item Reference
    # (дължините зависят от partition)
    company_prefix_bits = [12, 11, 10, 9, 8, 7, 6][partition]
    item_ref_bits = [24, 25, 26, 27, 28, 29, 30][partition]
    
    # Изчисляване на Company Prefix
    company_prefix = 0
    bit_pos = 4  # Начална позиция след partition
    
    for i in range(company_prefix_bits):
        byte_pos = bit_pos // 8
        bit_in_byte = 7 - (bit_pos % 8)
        bit_value = (epc_data[byte_pos] >> bit_in_byte) & 0x01
        company_prefix = (company_prefix << 1) | bit_value
        bit_pos += 1
    
    # Изчисляване на Item Reference
    item_reference = 0
    for i in range(item_ref_bits):
        byte_pos = bit_pos // 8
        bit_in_byte = 7 - (bit_pos % 8)
        bit_value = (epc_data[byte_pos] >> bit_in_byte) & 0x01
        item_reference = (item_reference << 1) | bit_value
        bit_pos += 1
    
    # Изчисляване на Serial Number (38 бита)
    serial_number = 0
    for i in range(38):
        byte_pos = bit_pos // 8
        bit_in_byte = 7 - (bit_pos % 8)
        bit_value = (epc_data[byte_pos] >> bit_in_byte) & 0x01
        serial_number = (serial_number << 1) | bit_value
        bit_pos += 1
    
    return {
        "filter_value": filter_value,
        "partition": partition,
        "company_prefix": company_prefix,
        "item_reference": item_reference,
        "serial_number": serial_number,
        "gtin": f"{company_prefix}{item_reference}"
    }
```

## Интеграция с други системи

### 1. Експорт на данни в CSV формат

```python
import csv
import os
import datetime

def export_tags_to_csv(tags, filename=None):
    """Експортира тагове в CSV файл."""
    if filename is None:
        # Генериране на име на файл с текуща дата и час
        now = datetime.datetime.now()
        filename = f"rfid_tags_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Проверка дали файлът съществува
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['tag_id', 'timestamp', 'reader_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Запис на заглавия, ако файлът е нов
        if not file_exists:
            writer.writeheader()
        
        # Текущо време
        now = datetime.datetime.now().isoformat()
        
        # Запис на таговете
        for tag in tags:
            writer.writerow({
                'tag_id': tag['tag_id'],
                'timestamp': now,
                'reader_id': tag['reader_id']
            })
    
    return filename
```

### 2. Интеграция с REST API

```python
import requests
import json
import time
import threading

class ApiIntegration:
    def __init__(self, api_url, auth_token=None):
        self.api_url = api_url
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        
        self.send_queue = []
        self.queue_lock = threading.Lock()
        self.sending_thread = None
        self.running = False
    
    def start(self):
        """Стартира процеса на изпращане."""
        self.running = True
        self.sending_thread = threading.Thread(target=self.send_worker)
        self.sending_thread.daemon = True
        self.sending_thread.start()
    
    def stop(self):
        """Спира процеса на изпращане."""
        self.running = False
        if self.sending_thread:
            self.sending_thread.join(timeout=5.0)
    
    def send_worker(self):
        """Функция, която изпълнява изпращането на данни."""
        while self.running:
            items_to_send = []
            
            # Извличане на елементи от опашката
            with self.queue_lock:
                if self.send_queue:
                    items_to_send = self.send_queue.copy()
                    self.send_queue.clear()
            
            # Изпращане на данни, ако има такива
            if items_to_send:
                try:
                    self.bulk_send(items_to_send)
                except Exception as e:
                    print(f"Грешка при изпращане: {e}")
                    
                    # Връщане на елементите в опашката
                    with self.queue_lock:
                        self.send_queue = items_to_send + self.send_queue
            
            # Изчакване преди следваща проверка
            time.sleep(0.5)
    
    def queue_tag(self, tag_data):
        """Добавя таг в опашката за изпращане."""
        with self.queue_lock:
            self.send_queue.append(tag_data)
    
    def bulk_send(self, items):
        """Изпраща множество елементи наведнъж."""
        try:
            response = requests.post(
                f"{self.api_url}/tags/bulk",
                headers=self.headers,
                data=json.dumps({'tags': items}),
                timeout=10.0
            )
            
            if response.status_code not in (200, 201, 202):
                print(f"Грешка при изпращане: {response.status_code} - {response.text}")
                return False
            
            return True
        except Exception as e:
            print(f"Изключение при изпращане: {e}")
            raise
    
    def send_tag(self, tag_data):
        """Изпраща единичен таг към API."""
        try:
            response = requests.post(
                f"{self.api_url}/tags",
                headers=self.headers,
                data=json.dumps(tag_data),
                timeout=5.0
            )
            
            if response.status_code not in (200, 201, 202):
                print(f"Грешка при изпращане: {response.status_code} - {response.text}")
                return False
            
            return True
        except Exception as e:
            print(f"Изключение при изпращане: {e}")
            raise
```

### 3. Интеграция с MQTT

```python
import paho.mqtt.client as mqtt
import json
import threading
import time

class MqttIntegration:
    def __init__(self, broker_host, broker_port=1883, username=None, password=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        
        self.client = mqtt.Client()
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Задаване на callback функции
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        self.connected = False
        self.connection_lock = threading.Lock()
        self.last_reconnect_attempt = 0
        self.reconnect_interval = 5  # секунди
    
    def connect(self):
        """Свързва се към MQTT брокера."""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Грешка при свързване към MQTT брокера: {e}")
            return False
    
    def disconnect(self):
        """Прекъсва връзката с MQTT брокера."""
        self.client.loop_stop()
        self.client.disconnect()
    
    def on_connect(self, client, userdata, flags, rc):
        """Извиква се при успешно свързване."""
        if rc == 0:
            print(f"Успешно свързване към MQTT брокера: {self.broker_host}:{self.broker_port}")
            with self.connection_lock:
                self.connected = True
        else:
            print(f"Грешка при свързване към MQTT брокера: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Извиква се при прекъсване на връзката."""
        print(f"Прекъсната връзка с MQTT брокера: {rc}")
        with self.connection_lock:
            self.connected = False
    
    def on_publish(self, client, userdata, mid):
        """Извиква се при успешно публикуване."""
        pass
    
    def ensure_connection(self):
        """Проверява и възстановява връзката, ако е необходимо."""
        with self.connection_lock:
            if not self.connected:
                current_time = time.time()
                if current_time - self.last_reconnect_attempt > self.reconnect_interval:
                    self.last_reconnect_attempt = current_time
                    try:
                        self.client.reconnect()
                    except Exception as e:
                        print(f"Грешка при опит за повторно свързване: {e}")
    
    def publish_tag(self, tag_data, topic="rfid/tags"):
        """Публикува данни за таг в MQTT."""
        # Проверка на връзката
        self.ensure_connection()
        
        with self.connection_lock:
            if not self.connected:
                print("Не може да се публикува: няма връзка с MQTT брокера")
                return False
        
        # Преобразуване на данните в JSON
        payload = json.dumps(tag_data)
        
        # Публикуване
        result = self.client.publish(topic, payload, qos=1)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def subscribe_to_commands(self, callback, topic="rfid/commands"):
        """Абонира се за команди от MQTT."""
        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                callback(payload)
            except Exception as e:
                print(f"Грешка при обработка на съобщение: {e}")
        
        self.client.on_message = on_message
        self.client.subscribe(topic, qos=1)
```

## Сигурност и автентикация

### 1. Защита на данните при предаване

```python
import hashlib
import hmac
import base64
import time
import random
import string

class SecureTransmission:
    def __init__(self, shared_secret):
        """Инициализира обект за защитено предаване на данни."""
        self.shared_secret = shared_secret.encode('utf-8')
    
    def generate_nonce(self, length=16):
        """Генерира случаен низ."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def create_signature(self, payload, nonce, timestamp):
        """Създава подпис за данните."""
        # Конкатенация на данните за подписване
        data_to_sign = f"{payload}{nonce}{timestamp}".encode('utf-8')
        
        # Създаване на HMAC подпис
        signature = hmac.new(
            self.shared_secret,
            data_to_sign,
            hashlib.sha256
        ).digest()
        
        # Кодиране в base64
        return base64.b64encode(signature).decode('utf-8')
    
    def secure_payload(self, data):
        """Подготвя данните за защитено предаване."""
        # Преобразуване на данните в JSON
        payload = json.dumps(data)
        
        # Генериране на случаен низ
        nonce = self.generate_nonce()
        
        # Текущо време
        timestamp = str(int(time.time()))
        
        # Създаване на подпис
        signature = self.create_signature(payload, nonce, timestamp)
        
        # Резултат
        return {
            'payload': payload,
            'meta': {
                'nonce': nonce,
                'timestamp': timestamp,
                'signature': signature
            }
        }
    
    def verify_payload(self, secure_data):
        """Проверява автентичността на получените данни."""
        try:
            payload = secure_data['payload']
            nonce = secure_data['meta']['nonce']
            timestamp = secure_data['meta']['timestamp']
            signature = secure_data['meta']['signature']
            
            # Проверка на времевия интервал
            current_time = int(time.time())
            received_time = int(timestamp)
            
            # Проверка за изтекъл таймаут (напр. 5 минути)
            if current_time - received_time > 300:
                return False, "Изтекъл срок на данните"
            
            # Изчисляване на очаквания подпис
            expected_signature = self.create_signature(payload, nonce, timestamp)
            
            # Проверка на подписа
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Невалиден подпис"
            
            # Данните са валидни
            return True, json.loads(payload)
        
        except Exception as e:
            return False, f"Грешка при проверка: {e}"
```

## Известяване и логване

### 1. Конфигуриране на логване

```python
import logging
import logging.handlers
import os
import sys

def setup_logging(log_file=None, log_level=logging.INFO):
    """Конфигурира система за логване."""
    # Създаване на логер
    logger = logging.getLogger("rfid_reader_sdk")
    logger.setLevel(log_level)
    
    # Формат на съобщенията
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Конзолен изход
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файлов изход (ако е зададен)
    if log_file:
        # Създаване на директорията, ако не съществува
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Ротиращ файлов обработчик (макс. 5 файла по 5 MB)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Пример за използване
logger = setup_logging("logs/rfid_reader.log")
logger.info("RFID Reader SDK е стартиран")
logger.warning("Предупреждение: ниско ниво на батерията")
logger.error("Грешка при свързване към четеца")
```

### 2. Известяване чрез email

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, username, password, from_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        
        # Опашка за изпращане на съобщения
        self.email_queue = []
        self.queue_lock = threading.Lock()
        
        # Нишка за изпращане
        self.send_thread = None
        self.running = False
    
    def start(self):
        """Стартира процеса на изпращане на известия."""
        self.running = True
        self.send_thread = threading.Thread(target=self.send_worker)
        self.send_thread.daemon = True
        self.send_thread.start()
    
    def stop(self):
        """Спира процеса на изпращане на известия."""
        self.running = False
        if self.send_thread:
            self.send_thread.join(timeout=5.0)
    
    def send_worker(self):
        """Функция, която изпълнява изпращането на email съобщения."""
        while self.running:
            email_to_send = None
            
            # Извличане на съобщение от опашката
            with self.queue_lock:
                if self.email_queue:
                    email_to_send = self.email_queue.pop(0)
            
            # Изпращане на съобщението, ако има такова
            if email_to_send:
                try:
                    self.send_email_now(**email_to_send)
                except Exception as e:
                    print(f"Грешка при изпращане на email: {e}")
                    
                    # Връщане на съобщението в опашката
                    with self.queue_lock:
                        self.email_queue.append(email_to_send)
            
            # Изчакване преди следваща проверка
            time.sleep(1.0)
    
    def queue_email(self, to_email, subject, body, html=False):
        """Добавя email в опашката за изпращане."""
        with self.queue_lock:
            self.email_queue.append({
                'to_email': to_email,
                'subject': subject,
                'body': body,
                'html': html
            })
    
    def send_email_now(self, to_email, subject, body, html=False):
        """Изпраща email незабавно."""
        # Създаване на съобщение
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Добавяне на тяло
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Изпращане на съобщението
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Грешка при изпращане на email: {e}")
            raise
```