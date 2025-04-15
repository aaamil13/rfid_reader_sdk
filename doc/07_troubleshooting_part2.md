# Отстраняване на проблеми - Част 2: Обработка на данни и производителност

В този документ са описани проблеми, свързани с обработката на данни и производителността при работа с RFID читатели, както и подходи за тяхното разрешаване.

## Проблеми с обработката на данни

### 1. Проблеми с декодирането на данни от тагове

#### Симптоми
- Данните от таговете са нечетими или изглеждат повредени
- Некоректна интерпретация на данните

#### Възможни причини
1. Неправилно декодиране на буфера с данни
2. Неправилно изчисляване на позициите в буфера
3. Неправилно конвертиране на типове данни

#### Решения

**Проверка на данните байт по байт:**

```python
def inspect_tag_data(message, start_index):
    """Инспектира и извежда подробно съдържанието на съобщението."""
    # Извеждане на заглавие на съобщението
    print("Заглавие на съобщението:")
    for i in range(4):
        if start_index + i < len(message):
            print(f"Байт {i}: 0x{message[start_index + i]:02X} (десетично: {message[start_index + i]})")
    
    # Извеждане на дължина на данните
    if start_index + 4 < len(message):
        data_len = message[start_index + 4] & 0xFF
        print(f"\nДължина на данните: {data_len} байта")
    else:
        print("\nНеочакван край на съобщението")
        return
    
    # Извеждане на самите данни
    print("\nДанни:")
    for i in range(data_len):
        if start_index + 4 + i < len(message):
            byte_val = message[start_index + 4 + i]
            print(f"Байт {i}: 0x{byte_val:02X} (десетично: {byte_val}, символ: {chr(byte_val) if 32 <= byte_val <= 126 else 'не се изобразява'})")
    
    # Извеждане на данните като шестнадесетичен низ
    hex_data = ''.join([f'{message[start_index + 4 + i]:02X}' for i in range(data_len) if start_index + 4 + i < len(message)])
    print(f"\nДанни като шестнадесетичен низ: {hex_data}")
    
    # Опит за интерпретация на данните като ASCII текст
    ascii_data = ''.join([chr(message[start_index + 4 + i]) if 32 <= message[start_index + 4 + i] <= 126 else '.' 
                        for i in range(data_len) if start_index + 4 + i < len(message)])
    print(f"Данни като ASCII текст: {ascii_data}")
```

**Правилно декодиране на данните от различни формати:**

```python
def decode_tag_data(tag_data, format_type="hex"):
    """Декодира данните от тага в различни формати."""
    if not tag_data:
        return "Няма данни"
    
    if format_type == "hex":
        # Шестнадесетичен формат
        return ''.join([f'{b:02X}' for b in tag_data])
    
    elif format_type == "ascii":
        # ASCII текст (само видими символи)
        return ''.join([chr(b) if 32 <= b <= 126 else '.' for b in tag_data])
    
    elif format_type == "decimal":
        # Десетични стойности
        return ', '.join([str(b) for b in tag_data])
    
    elif format_type == "binary":
        # Двоичен формат
        return ' '.join([f'{b:08b}' for b in tag_data])
    
    elif format_type == "uint16":
        # 16-битови цели числа (little-endian)
        result = []
        for i in range(0, len(tag_data), 2):
            if i + 1 < len(tag_data):
                val = (tag_data[i+1] << 8) | tag_data[i]
                result.append(str(val))
        return ', '.join(result)
    
    elif format_type == "uint16_be":
        # 16-битови цели числа (big-endian)
        result = []
        for i in range(0, len(tag_data), 2):
            if i + 1 < len(tag_data):
                val = (tag_data[i] << 8) | tag_data[i+1]
                result.append(str(val))
        return ', '.join(result)
    
    else:
        return "Неизвестен формат"
```

### 2. Препълване на буфера

#### Симптоми
- Приложението забива или се сривя при обработка на големи обеми данни
- Грешка "IndexError: index out of range" при достъп до буфера

#### Възможни причини
1. Препълване на буфера за получаване
2. Неправилно изчисляване на дължината на съобщението
3. Повредени данни в буфера

#### Решения

**Проверка на дължината на буфера преди достъп:**

```python
def safe_buffer_access(buffer, index, default=0):
    """Безопасен достъп до елемент в буфер."""
    if 0 <= index < len(buffer):
        return buffer[index]
    else:
        print(f"Предупреждение: Опит за достъп до индекс {index} в буфер с дължина {len(buffer)}")
        return default

def safe_notify_recv_tags(self, message, start_index):
    """Безопасна версия на функцията за обработка на тагове."""
    try:
        # Проверка за валидни граници
        if start_index + 4 >= len(message):
            print("Грешка: Невалидни граници на съобщението")
            return -1
        
        # Извличане на дължина на данните с проверка
        data_len = safe_buffer_access(message, start_index + 4, 0) & 0xFF
        
        if start_index + 4 + data_len > len(message):
            print(f"Грешка: Данните излизат извън буфера (нужни: {data_len}, налични: {len(message) - start_index - 4})")
            return -1
        
        # Безопасно извличане на данните
        tag_data = []
        for i in range(data_len):
            tag_data.append(safe_buffer_access(message, start_index + 4 + i))
        
        # Обработка на данните
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        print(f"Получен таг: {tag_hex}")
        
        return 0
    except Exception as e:
        print(f"Грешка при обработка на таг: {e}")
        return -1
```

**Увеличаване на размера на буфера:**

```python
def increase_buffer_size(reader, new_size=2048):
    """Увеличава размера на буфера за получаване."""
    try:
        # Създаване на нов буфер
        old_size = len(reader.recv_msg_buff)
        new_buffer = bytearray(new_size)
        
        # Копиране на данните от стария буфер
        for i in range(min(old_size, new_size)):
            new_buffer[i] = reader.recv_msg_buff[i]
        
        # Замяна на буфера
        reader.recv_msg_buff = new_buffer
        
        print(f"Размерът на буфера е увеличен от {old_size} на {new_size} байта")
        return True
    except Exception as e:
        print(f"Грешка при увеличаване на буфера: {e}")
        return False
```

## Проблеми с производителността

### 1. Високо натоварване на процесора

#### Симптоми
- Приложението използва прекалено много CPU ресурси
- Забавяне при обработка на събития

#### Възможни причини
1. Неефективни цикли за обработка на данни
2. Липса на изчакване в нишките
3. Блокиращи операции при четене/запис

#### Решения

**Оптимизиране на циклите за обработка:**

```python
def optimize_processing_loops():
    """Предоставя насоки за оптимизиране на циклите за обработка."""
    print("Насоки за оптимизиране на циклите за обработка:")
    print("1. Използвайте 'time.sleep()' в циклите, за да намалите натоварването на CPU")
    print("   Пример: time.sleep(0.01) в основния цикъл")
    print("2. Избягвайте безкрайни цикли без условия за изход")
    print("3. Използвайте неблокиращи операции за вход/изход")
    print("4. Избягвайте създаването на нови обекти в циклите")
    print("5. Избягвайте извикването на бавни операции в циклите")
    print("6. Използвайте 'threading.Event' за синхронизация вместо активно изчакване")
```

**Пример за оптимизиран цикъл за четене:**

```python
def optimized_reading_loop(reader, max_duration=30):
    """Оптимизиран цикъл за четене на тагове."""
    try:
        # Създаване на събитие за край
        stop_event = threading.Event()
        
        # Функция за обработка на прекъсването с клавиатура
        def handle_interrupt():
            stop_event.set()
            print("Прекъсване получено, спиране...")
        
        # Регистриране на обработчик за Ctrl+C
        import signal
        original_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda sig, frame: handle_interrupt())
        
        try:
            # Стартиране на инвентаризация
            reader.inventory()
            
            # Начално време
            start_time = time.time()
            
            # Цикъл с проверка на времето и събитието за край
            while not stop_event.is_set() and (time.time() - start_time < max_duration):
                # Изчакване с малък интервал, за да се освободи CPU
                time.sleep(0.05)
            
            # Спиране на инвентаризацията
            reader.stop()
            
        finally:
            # Възстановяване на оригиналния обработчик
            signal.signal(signal.SIGINT, original_handler)
        
        print(f"Четенето е приключено след {time.time() - start_time:.2f} секунди")
        return True
    except Exception as e:
        print(f"Грешка в цикъла за четене: {e}")
        return False
```

### 2. Изтичане на памет

#### Симптоми
- Приложението използва все повече и повече памет с времето
- Забавяне на производителността след продължителна работа

#### Възможни причини
1. Натрупване на данни без освобождаване
2. Създаване на нови обекти без изчистване на старите
3. Циклични референции между обекти

#### Решения

**Периодично почистване на кеша:**

```python
class CachedTagReader:
    def __init__(self, reader, max_cache_size=1000):
        self.reader = reader
        self.max_cache_size = max_cache_size
        self.tags_cache = {}
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 60  # секунди
    
    def add_tag(self, tag_id, tag_data):
        """Добавя таг в кеша с проверка за размера."""
        # Проверка дали е време за почистване
        current_time = time.time()
        if current_time - self.last_cleanup_time > self.cleanup_interval:
            self.cleanup_cache()
            self.last_cleanup_time = current_time
        
        # Проверка за максимален размер
        if len(self.tags_cache) >= self.max_cache_size:
            # Премахване на най-стария елемент
            oldest_key = next(iter(self.tags_cache))
            del self.tags_cache[oldest_key]
        
        # Добавяне на новия елемент
        self.tags_cache[tag_id] = {
            'data': tag_data,
            'timestamp': current_time
        }
    
    def cleanup_cache(self):
        """Почиства стари елементи от кеша."""
        if len(self.tags_cache) == 0:
            return
        
        # Текущо време
        current_time = time.time()
        
        # Стари елементи (по-стари от 5 минути)
        old_threshold = current_time - 300
        
        # Елементи за премахване
        keys_to_remove = [k for k, v in self.tags_cache.items() 
                         if v['timestamp'] < old_threshold]
        
        # Премахване на елементите
        for key in keys_to_remove:
            del self.tags_cache[key]
        
        print(f"Почистени {len(keys_to_remove)} стари елемента от кеша")
```

**Използване на слаби референции:**

```python
import weakref

class TagsManager:
    def __init__(self):
        # Използване на слаби референции за временни данни
        self.temporary_tags = weakref.WeakValueDictionary()
        # Нормален речник за постоянните данни
        self.permanent_tags = {}
    
    def add_temporary_tag(self, tag_id, tag_obj):
        """Добавя временен таг, който може да бъде освободен от GC."""
        self.temporary_tags[tag_id] = tag_obj
    
    def add_permanent_tag(self, tag_id, tag_obj):
        """Добавя постоянен таг, който не се освобождава автоматично."""
        self.permanent_tags[tag_id] = tag_obj
    
    def get_tag(self, tag_id):
        """Връща таг по ID, първо проверява в постоянните, после в временните."""
        if tag_id in self.permanent_tags:
            return self.permanent_tags[tag_id]
        
        if tag_id in self.temporary_tags:
            return self.temporary_tags[tag_id]
        
        return None
    
    def clear_temporary_tags(self):
        """Изчиства всички временни тагове."""
        self.temporary_tags.clear()
```

### 3. Загуба на събития

#### Симптоми
- Някои събития от четеца не се обработват
- Непоследователно регистриране на тагове

#### Възможни причини
1. Липса на буфериране на събитията
2. Бавна обработка на събитията, която води до пропускане на нови
3. Претоварване с твърде много тагове едновременно

#### Решения

**Имплементиране на опашка за събития:**

```python
import queue
import threading
import time

class EventQueueManager:
    def __init__(self, max_queue_size=1000, processing_interval=0.1):
        # Опашка за събитията
        self.events_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_interval = processing_interval
        self.is_running = False
        self.processing_thread = None
        
        # Колбек функции за различни типове събития
        self.event_handlers = {
            'tag_read': [],
            'inventory_start': [],
            'inventory_stop': [],
            'tag_write': [],
            'error': []
        }
    
    def start(self):
        """Стартира обработката на събития."""
        if self.is_running:
            return False
            
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_events)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        return True
    
    def stop(self):
        """Спира обработката на събития."""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
    
    def add_event(self, event_type, event_data):
        """Добавя събитие в опашката."""
        try:
            # Не блокирай ако опашката е пълна, просто пропусни събитието
            self.events_queue.put_nowait({
                'type': event_type,
                'data': event_data,
                'timestamp': time.time()
            })
            return True
        except queue.Full:
            print(f"Предупреждение: Опашката за събития е пълна, събитие {event_type} е пропуснато")
            return False
    
    def register_handler(self, event_type, handler_func):
        """Регистрира обработчик за определен тип събития."""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler_func)
            return True
        return False
    
    def _process_events(self):
        """Обработва събитията от опашката."""
        while self.is_running:
            try:
                # Таймаут за да може нишката да бъде спряна
                event = self.events_queue.get(timeout=0.5)
                
                # Извикване на всички регистрирани обработчици
                if event['type'] in self.event_handlers:
                    for handler in self.event_handlers[event['type']]:
                        try:
                            handler(event['data'])
                        except Exception as e:
                            print(f"Грешка в обработчик за {event['type']}: {e}")
                
                self.events_queue.task_done()
            except queue.Empty:
                # Няма събития, просто продължаваме
                pass
            
            # Кратко изчакване за намаляване на натоварването
            time.sleep(self.processing_interval)
```

**Пример за използване с RFID AppNotify:**

```python
class QueuedRfidNotify(AppNotify):
    def __init__(self, event_queue):
        self.event_queue = event_queue
    
    def notify_recv_tags(self, message, start_index):
        # Извличане на данните за тага
        tag_length = message[start_index + 4] & 0xFF
        tag_data = []
        
        for i in range(tag_length):
            tag_data.append(message[start_index + 4 + i])
        
        # Преобразуване на данните в hex string
        tag_hex = ''.join([f'{b:02X}' for b in tag_data])
        
        # Добавяне на събитието в опашката
        self.event_queue.add_event('tag_read', {
            'tag_id': tag_hex,
            'raw_data': tag_data
        })
        
        return 0
    
    def notify_start_inventory(self, message, start_index):
        self.event_queue.add_event('inventory_start', {})
        return 0
    
    def notify_stop_inventory(self, message, start_index):
        self.event_queue.add_event('inventory_stop', {})
        return 0
    
    # Други notify методи...
```

### 4. Проблеми с многонишковата обработка

#### Симптоми
- Приложението забива или се блокира при интензивно използване
- Данните от таговете се объркват или припокриват
- Изключения, свързани със синхронизацията на нишки

#### Възможни причини
1. Неправилна синхронизация на достъпа до споделени ресурси
2. Deadlock при използване на множество заключвания
3. Race conditions при паралелна обработка на данни

#### Решения

**Използване на thread-safe структури от данни:**

```python
import threading
import collections

class ThreadSafeTagsStorage:
    def __init__(self, max_tags=10000):
        self.max_tags = max_tags
        self.tags = collections.OrderedDict()
        self.lock = threading.RLock()  # Рекурсивно заключване
    
    def add_tag(self, tag_id, tag_data):
        """Добавя таг по потокобезопасен начин."""
        with self.lock:
            # Ако тагът съществува, обновяваме го
            if tag_id in self.tags:
                self.tags[tag_id]['count'] += 1
                self.tags[tag_id]['last_seen'] = time.time()
                self.tags[tag_id]['data'] = tag_data
            else:
                # Ако достигнем максималния размер, премахваме най-стария таг
                if len(self.tags) >= self.max_tags:
                    self.tags.popitem(last=False)  # Премахване на най-стария елемент
                
                # Добавяне на новия таг
                self.tags[tag_id] = {
                    'data': tag_data,
                    'first_seen': time.time(),
                    'last_seen': time.time(),
                    'count': 1
                }
    
    def get_tag(self, tag_id):
        """Връща таг по ID по потокобезопасен начин."""
        with self.lock:
            return self.tags.get(tag_id)
    
    def get_all_tags(self):
        """Връща копие на всички тагове по потокобезопасен начин."""
        with self.lock:
            return dict(self.tags)
    
    def clear_all(self):
        """Изчиства всички тагове по потокобезопасен начин."""
        with self.lock:
            old_count = len(self.tags)
            self.tags.clear()
            return old_count
```

**Използване на locks за критични секции:**

```python
def thread_safe_reader_operation(reader, operation_type, *args, **kwargs):
    """Изпълнява операция с четеца по потокобезопасен начин."""
    # Глобално заключване за достъп до четеца
    # Забележка: За реално приложение е добре да има заключване на ниво обект
    reader_lock = getattr(reader, '_lock', None)
    
    if reader_lock is None:
        reader._lock = threading.RLock()
        reader_lock = reader._lock
    
    try:
        with reader_lock:
            if operation_type == 'inventory':
                return reader.inventory()
            elif operation_type == 'stop':
                return reader.stop()
            elif operation_type == 'read_block':
                membank = args[0] if len(args) > 0 else kwargs.get('membank')
                addr = args[1] if len(args) > 1 else kwargs.get('addr')
                length = args[2] if len(args) > 2 else kwargs.get('length')
                return reader.read_tag_block(membank, addr, length)
            elif operation_type == 'write_block':
                membank = args[0] if len(args) > 0 else kwargs.get('membank')
                addr = args[1] if len(args) > 1 else kwargs.get('addr')
                length = args[2] if len(args) > 2 else kwargs.get('length')
                data = args[3] if len(args) > 3 else kwargs.get('data')
                start_idx = args[4] if len(args) > 4 else kwargs.get('start_idx', 0)
                return reader.write_tag_block(membank, addr, length, data, start_idx)
            else:
                raise ValueError(f"Неизвестен тип операция: {operation_type}")
    except Exception as e:
        print(f"Грешка при операция {operation_type}: {e}")
        raise
```

**Използване на thread pools за паралелна обработка:**

```python
import concurrent.futures

class ParallelTagProcessor:
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []
        
    def process_tag(self, tag_data):
        """Обработва таг в отделна нишка."""
        # Добавяне на нова задача в пула
        future = self.executor.submit(self._process_tag_impl, tag_data)
        self.futures.append(future)
        
        # Почистване на приключилите задачи
        self.futures = [f for f in self.futures if not f.done()]
        
    def _process_tag_impl(self, tag_data):
        """Имплементация на обработката на таг."""
        # Тук може да добавите вашата логика за обработка
        print(f"Обработка на таг: {tag_data}")
        # Симулация на продължителна обработка
        time.sleep(0.5)
        return True
        
    def wait_all(self, timeout=None):
        """Изчаква приключването на всички задачи."""
        done, not_done = concurrent.futures.wait(
            self.futures, 
            timeout=timeout, 
            return_when=concurrent.futures.ALL_COMPLETED
        )
        
        if not_done:
            print(f"Предупреждение: {len(not_done)} задачи не приключиха в рамките на таймаута")
            
        return len(done), len(not_done)
        
    def shutdown(self):
        """Освобождава ресурсите на пула."""
        self.executor.shutdown(wait=True)
```