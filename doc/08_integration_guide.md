# Ръководство за интеграция

В този документ са представени насоки и стратегии за интегриране на RFID Reader SDK с други системи и платформи.

## Интеграция с бази данни

### 1. Интеграция с SQLite

SQLite е лека SQL база данни, която не изисква отделен сървър и е подходяща за вградени приложения.

```python
import sqlite3
import time
import threading

class RfidDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        
        # Инициализация на базата данни
        self.initialize_database()
    
    def initialize_database(self):
        """Инициализира базата данни и създава необходимите таблици."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Създаване на таблица за тагове
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    reader_id TEXT,
                    count INTEGER DEFAULT 1
                )
            ''')
            
            # Създаване на индекс по tag_id за по-бързо търсене
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tag_id ON tags(tag_id)
            ''')
            
            # Създаване на таблица за четци
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reader_id TEXT NOT NULL,
                    reader_type TEXT,
                    location TEXT,
                    last_active TIMESTAMP
                )
            ''')
            
            # Запазване на промените
            conn.commit()
            conn.close()
            
            print("Базата данни е инициализирана успешно")
        except Exception as e:
            print(f"Грешка при инициализация на базата данни: {e}")
    
    def connect(self):
        """Създава нова връзка към базата данни."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # За достъп по име на колона
        return self.connection
    
    def close(self):
        """Затваря връзката към базата данни."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def add_or_update_tag(self, tag_id, reader_id=None):
        """Добавя нов таг или обновява съществуващ."""
        with self.lock:
            try:
                conn = self.connect()
                cursor = conn.cursor()
                
                # Проверка дали тагът вече съществува
                cursor.execute(
                    "SELECT id, count FROM tags WHERE tag_id = ?",
                    (tag_id,)
                )
                row = cursor.fetchone()
                
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                
                if row:
                    # Обновяване на съществуващ таг
                    cursor.execute(
                        "UPDATE tags SET last_seen = ?, reader_id = ?, count = ? WHERE id = ?",
                        (current_time, reader_id, row['count'] + 1, row['id'])
                    )
                else:
                    # Добавяне на нов таг
                    cursor.execute(
                        "INSERT INTO tags (tag_id, first_seen, last_seen, reader_id) VALUES (?, ?, ?, ?)",
                        (tag_id, current_time, current_time, reader_id)
                    )
                
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Грешка при добавяне/обновяване на таг: {e}")
                if conn:
                    conn.rollback()
                return False
    
    def get_tag_history(self, tag_id):
        """Връща историята на тага."""
        with self.lock:
            try:
                conn = self.connect()
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM tags WHERE tag_id = ?",
                    (tag_id,)
                )
                
                return cursor.fetchone()
                
            except Exception as e:
                print(f"Грешка при извличане на история на таг: {e}")
                return None
    
    def register_reader(self, reader_id, reader_type, location=None):
        """Регистрира нов четец в базата данни."""
        with self.lock:
            try:
                conn = self.connect()
                cursor = conn.cursor()
                
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Проверка дали четецът вече съществува
                cursor.execute(
                    "SELECT id FROM readers WHERE reader_id = ?",
                    (reader_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    # Обновяване на съществуващ четец
                    cursor.execute(
                        "UPDATE readers SET reader_type = ?, location = ?, last_active = ? WHERE reader_id = ?",
                        (reader_type, location, current_time, reader_id)
                    )
                else:
                    # Добавяне на нов четец
                    cursor.execute(
                        "INSERT INTO readers (reader_id, reader_type, location, last_active) VALUES (?, ?, ?, ?)",
                        (reader_id, reader_type, location, current_time)
                    )
                
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Грешка при регистриране на четец: {e}")
                if conn:
                    conn.rollback()
                return False
    
    def get_tag_count(self):
        """Връща общия брой на таговете в базата данни."""
        with self.lock:
            try:
                conn = self.connect()
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) as count FROM tags")
                result = cursor.fetchone()
                
                return result['count'] if result else 0
                
            except Exception as e:
                print(f"Грешка при извличане на брой тагове: {e}")
                return 0
```

### 2. Интеграция с MySQL/PostgreSQL

За по-големи приложения, които изискват по-мощна база данни:

```python
import pymysql
import threading
import time

class RfidMySQLDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.lock = threading.Lock()
        
        # Инициализация на базата данни
        self.initialize_database()
    
    def initialize_database(self):
        """Инициализира базата данни и създава необходимите таблици."""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = conn.cursor()
            
            # Създаване на таблица за тагове
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tag_id VARCHAR(50) NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    reader_id VARCHAR(50),
                    count INT DEFAULT 1,
                    INDEX (tag_id)
                )
            ''')
            
            # Създаване на таблица за четци
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    reader_id VARCHAR(50) NOT NULL,
                    reader_type VARCHAR(50),
                    location VARCHAR(100),
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX (reader_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("Базата данни е инициализирана успешно")
        except Exception as e:
            print(f"Грешка при инициализация на базата данни: {e}")
    
    def connect(self):
        """Създава нова връзка към базата данни."""
        if self.connection is None:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor  # За достъп по име на колона
            )
        return self.connection
    
    def close(self):
        """Затваря връзката към базата данни."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def add_or_update_tag(self, tag_id, reader_id=None):
        """Добавя нов таг или обновява съществуващ."""
        with self.lock:
            conn = None
            try:
                conn = self.connect()
                cursor = conn.cursor()
                
                # Проверка дали тагът вече съществува
                cursor.execute(
                    "SELECT id, count FROM tags WHERE tag_id = %s",
                    (tag_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    # Обновяване на съществуващ таг
                    cursor.execute(
                        "UPDATE tags SET last_seen = NOW(), reader_id = %s, count = %s WHERE id = %s",
                        (reader_id, row['count'] + 1, row['id'])
                    )
                else:
                    # Добавяне на нов таг
                    cursor.execute(
                        "INSERT INTO tags (tag_id, reader_id) VALUES (%s, %s)",
                        (tag_id, reader_id)
                    )
                
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Грешка при добавяне/обновяване на таг: {e}")
                if conn:
                    conn.rollback()
                return False
            finally:
                if conn:
                    conn.close()
                    self.connection = None
    
    # [други методи както в SQLite примера]
```

## Интеграция с уеб приложения

### 1. Интеграция с Flask

[Flask](https://flask.palletsprojects.com/) е лек уеб фреймуърк за Python, подходящ за създаване на API и уеб интерфейси.

```python
from flask import Flask, jsonify, request, render_template
import threading
import time

from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.reader.general_reader import GeneralReader
from rfid.reader.rfid_reader import RfidReader
from rfid.reader.app_notify import AppNotify

# Създаване на Flask приложение
app = Flask(__name__)

# Глобални променливи
tags_data = {}
reader_status = {
    'connected': False,
    'reader_type': None,
    'last_read_time': None,
    'total_tags': 0
}
tags_lock = threading.Lock()

# Клас за известяване
class WebAppNotify(AppNotify):
    def notify_recv_tags(self, message, start_index):
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        with tags_lock:
            if tag_hex not in tags_data:
                tags_data[tag_hex] = {
                    'first_seen': time.time(),
                    'count': 1
                }
            else:
                tags_data[tag_hex]['count'] += 1
                tags_data[tag_hex]['last_seen'] = time.time()
            
            reader_status['total_tags'] = len(tags_data)
            reader_status['last_read_time'] = time.time()
        
        return 0
    
    def notify_start_inventory(self, message, start_index):
        reader_status['status'] = 'Инвентаризация в ход'
        return 0
    
    def notify_stop_inventory(self, message, start_index):
        reader_status['status'] = 'Готов'
        return 0
    
    # Имплементация на останалите методи от AppNotify...

# RFID четец и мениджър
reader = None
manager = None

# Функция за инициализация на четеца
def initialize_reader():
    global reader, manager
    
    # Инициализация на мениджъра
    TransportThreadManager.initialize_transport_manager()
    
    # Създаване на четец
    reader = GeneralReader()
    
    # Свързване към четеца (заменете параметрите с вашите)
    result = reader.connect_physical_interface(
        "COM4", 9600, None, 0, RfidReader.CONNECT_TYPE_SERIALPORT
    )
    
    if result == 0:
        print("Успешно свързване към четеца")
        reader_status['connected'] = True
        reader_status['reader_type'] = 'GeneralReader'
        reader_status['status'] = 'Готов'
        
        # Задаване на обработчик на съобщения
        reader.set_app_notify(WebAppNotify())
        
        # Добавяне на четеца към мениджъра
        manager = TransportThreadManager.get_instance()
        manager.add_rfid_reader(reader)
        
        return True
    else:
        print(f"Грешка при свързване към четеца: {result}")
        return False

# Flask маршрути
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(reader_status)

@app.route('/api/tags')
def get_tags():
    with tags_lock:
        return jsonify({
            'count': len(tags_data),
            'tags': tags_data
        })

@app.route('/api/tags/clear', methods=['POST'])
def clear_tags():
    with tags_lock:
        old_count = len(tags_data)
        tags_data.clear()
        reader_status['total_tags'] = 0
    
    return jsonify({
        'status': 'success',
        'cleared_count': old_count
    })

@app.route('/api/inventory/start', methods=['POST'])
def start_inventory():
    global reader
    
    if reader and reader_status['connected']:
        reader.inventory()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Четецът не е свързан'})

@app.route('/api/inventory/stop', methods=['POST'])
def stop_inventory():
    global reader
    
    if reader and reader_status['connected']:
        reader.stop()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Четецът не е свързан'})

# Инициализация преди стартиране на приложението
@app.before_first_request
def before_first_request():
    thread = threading.Thread(target=initialize_reader)
    thread.daemon = True
    thread.start()

# При затваряне на приложението
@app.teardown_appcontext
def shutdown_reader(exception=None):
    global reader, manager
    
    if reader:
        reader.stop()
    
    if manager:
        manager.stop()

# Стартиране на приложението
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
```

### 2. Интеграция с Django

[Django](https://www.djangoproject.com/) е по-голям уеб фреймуърк, подходящ за по-сложни приложения:

```python
# Примерен файл models.py
from django.db import models

class Tag(models.Model):
    tag_id = models.CharField(max_length=50, unique=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    reader_id = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField(default=1)
    
    def __str__(self):
        return self.tag_id

class Reader(models.Model):
    reader_id = models.CharField(max_length=50, unique=True)
    reader_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100, null=True, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.reader_type} - {self.reader_id}"

# Примерен файл views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tag, Reader
import json
import time
import threading

# [Имплементация на RFID функционалност подобна на Flask примера]

def index(request):
    """Главна страница."""
    return render(request, 'rfid/index.html')

def get_tags(request):
    """API за получаване на всички тагове."""
    tags = Tag.objects.all()
    data = {
        'count': tags.count(),
        'tags': list(tags.values())
    }
    return JsonResponse(data)

@csrf_exempt
def clear_tags(request):
    """API за изчистване на всички тагове."""
    if request.method == 'POST':
        count = Tag.objects.count()
        Tag.objects.all().delete()
        return JsonResponse({
            'status': 'success',
            'cleared_count': count
        })
    return JsonResponse({'status': 'error', 'message': 'Неправилен метод'})

@csrf_exempt
def start_inventory(request):
    """API за стартиране на инвентаризация."""
    if request.method == 'POST':
        # [Логика за стартиране на инвентаризация]
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Неправилен метод'})
```

## Интеграция с мобилни приложения

### 1. RESTful API за мобилни приложения

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import jwt
import datetime

# [Импортиране на RFID библиотеки]

app = Flask(__name__)
CORS(app)  # Разрешаване на Cross-Origin заявки

# Секретен ключ за JWT токени
app.config['SECRET_KEY'] = 'your-secret-key'

# Функция за генериране на JWT токен
def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )

# Декоратор за проверка на JWT токен
def token_required(f):
    def decorator(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    
    return decorator

# API маршрути

@app.route('/api/login', methods=['POST'])
def login():
    """API за влизане и получаване на токен."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Липсват данни за вход'}), 400
    
    # Проверка на потребителското име и парола (заместете с вашата логика)
    if data.get('username') == 'admin' and data.get('password') == 'password':
        token = generate_token(data.get('username'))
        return jsonify({'token': token})
    
    return jsonify({'message': 'Невалидни данни за вход'}), 401

@app.route('/api/readers', methods=['GET'])
@token_required
def get_readers():
    """API за получаване на всички четци."""
    # [Логика за извличане на четци]
    
    return jsonify({
        'readers': [
            {'id': 1, 'name': 'Reader 1', 'status': 'active'},
            {'id': 2, 'name': 'Reader 2', 'status': 'inactive'}
        ]
    })

@app.route('/api/readers/<int:reader_id>/tags', methods=['GET'])
@token_required
def get_reader_tags(reader_id):
    """API за получаване на всички тагове от определен четец."""
    # [Логика за извличане на тагове от определен четец]
    
    return jsonify({
        'reader_id': reader_id,
        'tags': [
            {'id': 'AABBCC', 'last_seen': '2023-01-01T12:00:00Z'},
            {'id': 'DDEEFF', 'last_seen': '2023-01-01T12:05:00Z'}
        ]
    })

@app.route('/api/readers/<int:reader_id>/inventory', methods=['POST'])
@token_required
def start_reader_inventory(reader_id):
    """API за стартиране на инвентаризация на определен четец."""
    # [Логика за стартиране на инвентаризация]
    
    return jsonify({
        'status': 'success',
        'message': f'Инвентаризацията на четец {reader_id} е стартирана'
    })

# Стартиране на приложението
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

## Интеграция със системи за складово управление

### 1. Експорт на данни към ERP системи

```python
import requests
import json
import time
import hmac
import hashlib
import base64

class ErpIntegration:
    def __init__(self, api_url, api_key, api_secret):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
    
    def generate_signature(self, data, timestamp):
        """Генерира подпис за API заявка."""
        message = f"{self.api_key}:{timestamp}:{json.dumps(data)}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def send_inventory_data(self, inventory_data):
        """Изпраща данни от инвентаризация към ERP системата."""
        timestamp = str(int(time.time()))
        
        data = {
            'inventory_data': inventory_data,
            'timestamp': timestamp
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Timestamp': timestamp,
            'X-Signature': self.generate_signature(data, timestamp)
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/inventory",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Грешка: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Изключение: {e}"
    
    def get_product_info(self, product_id):
        """Получава информация за продукт от ERP системата."""
        timestamp = str(int(time.time()))
        
        data = {
            'product_id': product_id
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Timestamp': timestamp,
            'X-Signature': self.generate_signature(data, timestamp)
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/products/{product_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Грешка: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Изключение: {e}"
```

### 2. Интеграция с Excel и CSV файлове

```python
import pandas as pd
import os
import datetime

class InventoryExport:
    def __init__(self, output_dir="exports"):
        self.output_dir = output_dir
        
        # Създаване на директорията, ако не съществува
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def export_to_excel(self, tags_data, reader_info=None, filename=None):
        """Експортира данни за тагове в Excel файл."""
        if filename is None:
            # Генериране на име на файл с текуща дата и час
            now = datetime.datetime.now()
            filename = f"inventory_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Пълен път до файла
        filepath = os.path.join(self.output_dir, filename)
        
        # Подготовка на данните
        tags_list = []
        for tag_id, info in tags_data.items():
            tags_list.append({
                'tag_id': tag_id,
                'first_seen': datetime.datetime.fromtimestamp(info.get('first_seen', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'last_seen': datetime.datetime.fromtimestamp(info.get('last_seen', 0)).strftime('%Y-%m-%d %H:%M:%S') 
                              if 'last_seen' in info else '',
                'count': info.get('count', 1),
                'reader_id': info.get('reader_id', '')
            })
        
        # Създаване на DataFrame
        df = pd.DataFrame(tags_list)
        
        # Създаване на Excel писател
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Запис на данните за тагове
            df.to_excel(writer, sheet_name='Tags', index=False)
            
            # Добавяне на информация за четеца (ако е предоставена)
            if reader_info:
                reader_df = pd.DataFrame([reader_info])
                reader_df.to_excel(writer, sheet_name='Reader Info', index=False)
        
        print(f"Данните са експортирани в {filepath}")
        return filepath
    
    def export_to_csv(self, tags_data, filename=None):
        """Експортира данни за тагове в CSV файл."""
        if filename is None:
            # Генериране на име на файл с текуща дата и час
            now = datetime.datetime.now()
            filename = f"inventory_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Пълен път до файла
        filepath = os.path.join(self.output_dir, filename)
        
        # Подготовка на данните
        tags_list = []
        for tag_id, info in tags_data.items():
            tags_list.append({
                'tag_id': tag_id,
                'first_seen': datetime.datetime.fromtimestamp(info.get('first_seen', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'last_seen': datetime.datetime.fromtimestamp(info.get('last_seen', 0)).strftime('%Y-%m-%d %H:%M:%S') 
                              if 'last_seen' in info else '',
                'count': info.get('count', 1),
                'reader_id': info.get('reader_id', '')
            })
        
        # Създаване на DataFrame и експорт в CSV
        df = pd.DataFrame(tags_list)
        df.to_csv(filepath, index=False)
        
        print(f"Данните са експортирани в {filepath}")
        return filepath
    
    def import_from_excel(self, filepath):
        """Импортира данни за тагове от Excel файл."""
        try:
            # Четене на Excel файл
            df = pd.read_excel(filepath, sheet_name='Tags')
            
            # Конвертиране в речник
            tags_data = {}
            for _, row in df.iterrows():
                tag_id = row['tag_id']
                
                # Конвертиране на дати от низ към timestamp
                first_seen = datetime.datetime.strptime(row['first_seen'], '%Y-%m-%d %H:%M:%S').timestamp()
                last_seen = datetime.datetime.strptime(row['last_seen'], '%Y-%m-%d %H:%M:%S').timestamp() \
                            if pd.notna(row['last_seen']) else first_seen
                
                tags_data[tag_id] = {
                    'first_seen': first_seen,
                    'last_seen': last_seen,
                    'count': int(row['count']),
                    'reader_id': row['reader_id'] if pd.notna(row['reader_id']) else None
                }
            
            return tags_data
        
        except Exception as e:
            print(f"Грешка при импортиране от Excel: {e}")
            return {}
```