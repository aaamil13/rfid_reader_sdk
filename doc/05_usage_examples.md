# Примери за използване

В този документ са представени примери за използване на RFID Reader SDK с различни видове четци и транспортни протоколи.

## 1. Използване на сериен порт

### Пример за основно използване на GeneralReader чрез сериен порт

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

# Свързване към четеца чрез сериен порт
result = reader.connect_physical_interface(
    "COM4",          # Име на серийния порт
    9600,            # Бодова скорост
    None,            # Не се използва за сериен порт
    0,               # Не се използва за сериен порт
    RfidReader.CONNECT_TYPE_SERIALPORT  # Тип на връзката
)

if result != 0:
    print(f"Грешка при свързване към четеца: {result}")
    exit(1)
    
print("Успешно свързване към четеца.")

# Задаване на обработчик на съобщения
reader.set_app_notify(GeneralReaderNotifyImpl())

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

try:
    # Спиране на текуща инвентаризация, ако има такава
    reader.stop()
    
    # Еднократна инвентаризация
    print("Стартиране на еднократна инвентаризация...")
    reader.inventory_once()
    
    # Изчакване за известия
    time.sleep(2)
    
    # Четене на данни от потребителска област на таг
    print("Четене на данни от таг...")
    reader.read_tag_block(
        GeneralReader.RFID_TAG_MEMBANK_USER,  # Област на тага
        0,  # Начален адрес
        2   # Брой думи (2 байта всяка)
    )
    
    # Изчакване за известия
    time.sleep(2)
    
except KeyboardInterrupt:
    print("Прекратяване на програмата...")
finally:
    # Спиране на инвентаризацията
    reader.stop()
    
    # Освобождаване на ресурси
    manager.stop()
```

## 2. Използване на TCP връзка

### Пример за използване на MRfidReader чрез TCP

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.m_rfid_reader import MRfidReader
from rfid.app_notify_impl.m_rfid_reader_notify_impl import MRfidReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация на мениджъра на транспортните нишки
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = MRfidReader()

# Свързване към четеца чрез TCP
result = reader.connect_physical_interface(
    "192.168.1.100",  # IP адрес на четеца
    5000,             # Порт на четеца
    None,             # Локален IP (не е необходим)
    0,                # Локален порт (0 = произволен)
    RfidReader.CONNECT_TYPE_NET_TCP_CLIENT  # Тип на връзката
)

if result != 0:
    print(f"Грешка при свързване към четеца: {result}")
    exit(1)
    
print("Успешно свързване към четеца.")

# Задаване на обработчик на съобщения
reader.set_app_notify(MRfidReaderNotifyImpl())

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

try:
    # Ресетиране на четеца
    reader.reset()
    time.sleep(2)
    
    # Стартиране на непрекъсната инвентаризация
    print("Стартиране на непрекъсната инвентаризация...")
    reader.inventory()
    
    # Изчакване за известия (напр. 10 секунди)
    time.sleep(10)
    
    # Спиране на инвентаризацията
    print("Спиране на инвентаризацията...")
    reader.stop()
    
except KeyboardInterrupt:
    print("Прекратяване на програмата...")
finally:
    # Спиране на инвентаризацията
    reader.stop()
    
    # Освобождаване на ресурси
    manager.stop()
```

## 3. Използване на UDP връзка

### Пример за използване на R2000Reader чрез UDP

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.r2000_reader import R2000Reader
from rfid.app_notify_impl.r2000_reader_notify_impl import R2000ReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация на мениджъра на транспортните нишки
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = R2000Reader()

# Свързване към четеца чрез UDP
result = reader.connect_physical_interface(
    "192.168.1.100",  # IP адрес на четеца
    5000,             # Порт на четеца
    "0.0.0.0",        # Локален IP (всички интерфейси)
    6000,             # Локален порт
    RfidReader.CONNECT_TYPE_NET_UDP  # Тип на връзката
)

if result != 0:
    print(f"Грешка при свързване към четеца: {result}")
    exit(1)
    
print("Успешно свързване към четеца.")

# Задаване на обработчик на съобщения
reader.set_app_notify(R2000ReaderNotifyImpl())

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

try:
    # Стартиране на непрекъсната инвентаризация
    print("Стартиране на инвентаризация...")
    reader.inventory()
    
    # Изчакване за известия (напр. 10 секунди)
    time.sleep(10)
    
    # Спиране на инвентаризацията
    print("Спиране на инвентаризацията...")
    reader.stop()
    
except KeyboardInterrupt:
    print("Прекратяване на програмата...")
finally:
    # Спиране на инвентаризацията
    reader.stop()
    
    # Освобождаване на ресурси
    manager.stop()
```

## 4. Пример за запис в таг

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация и свързване към четеца (пропуснати за краткост)
# ...

# Създаване на данни за запис (4 байта)
data_to_write = bytearray([0x12, 0x34, 0x56, 0x78])

# Запис в потребителската област на тага
reader.write_tag_block(
    GeneralReader.RFID_TAG_MEMBANK_USER,  # Област на тага
    0,  # Начален адрес
    2,  # Брой думи (2 байта всяка) = 4 байта общо
    data_to_write,  # Данни за запис
    0   # Начален индекс в масива с данни
)

# Изчакване за известие
time.sleep(2)

# Четене на записаните данни за проверка
reader.read_tag_block(
    GeneralReader.RFID_TAG_MEMBANK_USER,  # Област на тага
    0,  # Начален адрес
    2   # Брой думи (2 байта всяка)
)
```

## 5. Пример за управление на релета

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.m_rfid_reader import MRfidReader
from rfid.app_notify_impl.m_rfid_reader_notify_impl import MRfidReaderNotifyImpl
from rfid.reader.rfid_reader import RfidReader

# Инициализация и свързване към четеца (пропуснати за краткост)
# ...

# Задействане на реле 1 за 5 секунди
reader.relay_operation(
    1,  # Номер на релето (1)
    1,  # Операция (1 = включване)
    5   # Време в секунди
)

# Изчакване за известие
time.sleep(1)

# Задействане на реле 2 за 3 секунди
reader.relay_operation(
    2,  # Номер на релето (2)
    1,  # Операция (1 = включване)
    3   # Време в секунди
)

# Изчакване
time.sleep(3)

# Изключване на реле 1
reader.relay_operation(
    1,  # Номер на релето (1)
    0,  # Операция (0 = изключване)
    0   # Не се използва при изключване
)

# Задействане на двете релета едновременно
reader.relay_operation(
    3,  # Номер на релето (3 = 1|2 = реле 1 и 2)
    1,  # Операция (1 = включване)
    2   # Време в секунди
)
```

## 6. Пример за използване на собствена имплементация на AppNotify

```python
import time
from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.app_notify import AppNotify
from rfid.reader.rfid_reader import RfidReader

# Собствена имплементация на AppNotify
class MyCustomNotify(AppNotify):
    def __init__(self):
        self.tags = []  # Списък за съхранение на прочетените тагове
    
    def notify_recv_tags(self, message, start_index):
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Преобразуване на данните в hex string
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        # Изпращане на сигнал към GUI
        self.signals.tag_found.emit(tag_hex)
        
        return 0
    
    def notify_start_inventory(self, message, start_index):
        self.signals.inventory_started.emit()
        return 0
    
    def notify_stop_inventory(self, message, start_index):
        self.signals.inventory_stopped.emit()
        return 0
    
    # Имплементация на останалите методи от AppNotify
    # ...

# Главен прозорец на приложението
class RfidMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("RFID Reader Application")
        self.setGeometry(100, 100, 600, 400)
        
        # Създаване на централен widget и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Създаване на елементи на интерфейса
        self.status_label = QLabel("Статус: Не е свързан")
        layout.addWidget(self.status_label)
        
        self.tags_list = QListWidget()
        layout.addWidget(self.tags_list)
        
        # Бутони
        self.connect_button = QPushButton("Свързване")
        self.connect_button.clicked.connect(self.connect_reader)
        layout.addWidget(self.connect_button)
        
        self.inventory_button = QPushButton("Започни инвентаризация")
        self.inventory_button.clicked.connect(self.toggle_inventory)
        self.inventory_button.setEnabled(False)
        layout.addWidget(self.inventory_button)
        
        self.clear_button = QPushButton("Изчисти списъка")
        self.clear_button.clicked.connect(self.clear_tags)
        layout.addWidget(self.clear_button)
        
        # Сигнали от RFID четеца
        self.rfid_signals = RfidSignals()
        self.rfid_signals.tag_found.connect(self.on_tag_found)
        self.rfid_signals.inventory_started.connect(self.on_inventory_started)
        self.rfid_signals.inventory_stopped.connect(self.on_inventory_stopped)
        
        # RFID обекти
        self.reader = None
        self.manager = None
        self.rfid_thread = None
        self.is_inventory_running = False
        
        # Списък с тагове
        self.tags = []
    
    def connect_reader(self):
        if self.reader is None:
            # Стартиране на RFID четеца в отделна нишка
            self.rfid_thread = threading.Thread(target=self.start_rfid_reader)
            self.rfid_thread.daemon = True
            self.rfid_thread.start()
            
            self.connect_button.setText("Прекъсване на връзката")
            self.inventory_button.setEnabled(True)
            self.status_label.setText("Статус: Свързан")
        else:
            self.stop_rfid_reader()
            self.connect_button.setText("Свързване")
            self.inventory_button.setEnabled(False)
            self.status_label.setText("Статус: Не е свързан")
    
    def start_rfid_reader(self):
        # Инициализация на мениджъра
        TransportThreadManager.initialize_transport_manager()
        
        # Създаване на четец
        self.reader = GeneralReader()
        
        # Свързване към четеца
        result = self.reader.connect_physical_interface(
            "COM4", 9600, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
        )
        
        if result != 0:
            self.status_label.setText(f"Статус: Грешка при свързване ({result})")
            self.reader = None
            return
        
        # Задаване на обработчик на съобщения
        self.reader.set_app_notify(GuiAppNotify(self.rfid_signals))
        
        # Добавяне на четеца към мениджъра
        self.manager = TransportThreadManager.get_instance()
        self.manager.add_rfid_reader(self.reader)
    
    def stop_rfid_reader(self):
        if self.reader:
            if self.is_inventory_running:
                self.reader.stop()
                self.is_inventory_running = False
            
            self.manager.stop()
            self.reader = None
            self.manager = None
    
    def toggle_inventory(self):
        if not self.reader:
            return
        
        if not self.is_inventory_running:
            # Започване на инвентаризация
            self.reader.inventory()
            self.inventory_button.setText("Спри инвентаризация")
            self.is_inventory_running = True
        else:
            # Спиране на инвентаризация
            self.reader.stop()
            self.inventory_button.setText("Започни инвентаризация")
            self.is_inventory_running = False
    
    def on_tag_found(self, tag_hex):
        if tag_hex not in self.tags:
            self.tags.append(tag_hex)
            self.tags_list.addItem(tag_hex)
    
    def on_inventory_started(self):
        self.status_label.setText("Статус: Инвентаризация в ход")
        self.is_inventory_running = True
        self.inventory_button.setText("Спри инвентаризация")
    
    def on_inventory_stopped(self):
        self.status_label.setText("Статус: Свързан")
        self.is_inventory_running = False
        self.inventory_button.setText("Започни инвентаризация")
    
    def clear_tags(self):
        self.tags.clear()
        self.tags_list.clear()
    
    def closeEvent(self, event):
        self.stop_rfid_reader()
        event.accept()

# Стартиране на приложението
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RfidMainWindow()
    window.show()
    sys.exit(app.exec_())
```
 ID на устройството
        device_id = message[start_index + 3] & 0xFF
        
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Преобразуване на данните в hex string
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        print(f"Открит таг: {tag_hex}")
        
        # Добавяне към списъка с тагове, ако не съществува
        if tag_hex not in self.tags:
            self.tags.append(tag_hex)
            print(f"Нов таг! Общо уникални тагове: {len(self.tags)}")
        
        return 0
    
    # Имплементация на останалите методи от AppNotify
    def notify_start_inventory(self, message, start_index):
        print("Започната инвентаризация")
        return 0
    
    def notify_stop_inventory(self, message, start_index):
        print("Спряна инвентаризация")
        return 0
    
    # ... (имплементация на останалите методи)

# Инициализация на мениджъра
TransportThreadManager.initialize_transport_manager()

# Създаване на четец
reader = GeneralReader()

# Свързване към четеца
reader.connect_physical_interface(
    "COM4", 9600, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
)

# Задаване на собствен обработчик на съобщения
custom_notify = MyCustomNotify()
reader.set_app_notify(custom_notify)

# Добавяне на четеца към мениджъра
manager = TransportThreadManager.get_instance()
manager.add_rfid_reader(reader)

try:
    # Непрекъсната инвентаризация за 30 секунди
    reader.inventory()
    
    start_time = time.time()
    while time.time() - start_time < 30:
        time.sleep(1)
        print(f"Текущо открити уникални тагове: {len(custom_notify.tags)}")
    
    # Спиране на инвентаризацията
    reader.stop()
    
    # Извеждане на всички открити тагове
    print("\nСписък на всички открити тагове:")
    for i, tag in enumerate(custom_notify.tags):
        print(f"{i+1}. {tag}")
    
except KeyboardInterrupt:
    print("Прекратяване на програмата...")
finally:
    # Спиране на инвентаризацията
    reader.stop()
    
    # Освобождаване на ресурси
    manager.stop()
```

## 7. Пример за интеграция с Flask приложение

```python
from flask import Flask, jsonify
import threading
import time

from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.app_notify import AppNotify
from rfid.reader.rfid_reader import RfidReader

app = Flask(__name__)

# Глобален списък с тагове
tags_database = []

# Клас за синхронизиран достъп до тагове
class TagsManager:
    def __init__(self):
        self.tags = []
        self.lock = threading.Lock()
    
    def add_tag(self, tag):
        with self.lock:
            if tag not in self.tags:
                self.tags.append(tag)
                return True
            return False
    
    def get_tags(self):
        with self.lock:
            return self.tags.copy()
    
    def clear_tags(self):
        with self.lock:
            old_count = len(self.tags)
            self.tags.clear()
            return old_count

# Създаване на мениджър
tags_manager = TagsManager()

# Собствена имплементация на AppNotify
class WebAppNotify(AppNotify):
    def notify_recv_tags(self, message, start_index):
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Преобразуване на данните в hex string
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        # Добавяне към мениджъра
        if tags_manager.add_tag(tag_hex):
            print(f"Нов таг: {tag_hex}")
        
        return 0
    
    # Имплементация на останалите методи от AppNotify
    # ...

# Функция за стартиране на RFID четеца
def start_rfid_reader():
    # Инициализация на мениджъра
    TransportThreadManager.initialize_transport_manager()
    
    # Създаване на четец
    reader = GeneralReader()
    
    # Свързване към четеца
    reader.connect_physical_interface(
        "COM4", 9600, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
    )
    
    # Задаване на обработчик на съобщения
    reader.set_app_notify(WebAppNotify())
    
    # Добавяне на четеца към мениджъра
    manager = TransportThreadManager.get_instance()
    manager.add_rfid_reader(reader)
    
    # Стартиране на непрекъсната инвентаризация
    reader.inventory()
    
    # Връщане на обекти за управление
    return reader, manager

# Функция за спиране на RFID четеца
def stop_rfid_reader(reader, manager):
    reader.stop()
    manager.stop()

# Стартиране на RFID четеца в отделна нишка
reader = None
manager = None

@app.before_first_request
def start_background_thread():
    global reader, manager
    
    def start_reader_thread():
        global reader, manager
        reader, manager = start_rfid_reader()
        print("RFID четецът е стартиран")
    
    thread = threading.Thread(target=start_reader_thread)
    thread.daemon = True
    thread.start()

# API endpoints
@app.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify({
        'count': len(tags_manager.get_tags()),
        'tags': tags_manager.get_tags()
    })

@app.route('/api/tags/clear', methods=['POST'])
def clear_tags():
    old_count = tags_manager.clear_tags()
    return jsonify({
        'status': 'success',
        'cleared_count': old_count
    })

@app.route('/api/inventory/once', methods=['POST'])
def inventory_once():
    global reader
    if reader:
        reader.inventory_once()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Reader not initialized'})

if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    finally:
        if reader and manager:
            stop_rfid_reader(reader, manager)
```

## 8. Интеграция с библиотеката PyQt5

```python
import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import pyqtSignal, QObject

from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.app_notify import AppNotify
from rfid.reader.rfid_reader import RfidReader

# Сигнални класове за комуникация между нишките
class RfidSignals(QObject):
    tag_found = pyqtSignal(str)
    inventory_started = pyqtSignal()
    inventory_stopped = pyqtSignal()

# Собствена имплементация на AppNotify
class GuiAppNotify(AppNotify):
    def __init__(self, signals):
        self.signals = signals
    
    def notify_recv_tags(self, message, start_index):
        # Извличане на