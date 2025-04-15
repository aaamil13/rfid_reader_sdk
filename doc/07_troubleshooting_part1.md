# Отстраняване на проблеми - Част 1: Свързване и четене на тагове

В този документ са описани най-честите проблеми, които може да срещнете при свързване с RFID четци и четене на тагове, както и техните решения.

## Проблеми при свързване

### 1. Грешка при свързване към сериен порт

#### Симптоми
- Получавате грешка при опит за свързване към сериен порт
- Функцията `connect_physical_interface` връща код за грешка

#### Възможни причини
1. Серийният порт не съществува
2. Серийният порт е зает от друго приложение
3. Нямате необходимите права за достъп до порта
4. Неправилни параметри (скорост, четност и т.н.)

#### Решения

**Проверка на достъпните серийни портове:**

```python
from rfid.transport.transport_serial_port import TransportSerialPort

# Извеждане на списък с всички достъпни серийни портове
available_ports = TransportSerialPort.find_port()
print("Достъпни серийни портове:", available_ports)
```

**Проверка дали портът е зает:**

```python
import serial

def check_port_availability(port_name):
    try:
        # Опит за отваряне на порта
        ser = serial.Serial(port_name)
        ser.close()
        return True, "Портът е достъпен"
    except serial.SerialException as e:
        if "PermissionError" in str(e):
            return False, "Нямате права за достъп до порта"
        elif "FileNotFoundError" in str(e):
            return False, "Портът не съществува"
        elif "already in use" in str(e) or "Access is denied" in str(e):
            return False, "Портът е зает от друго приложение"
        else:
            return False, f"Неизвестна грешка: {e}"

# Пример за употреба
is_available, message = check_port_availability("COM4")
print(f"Статус на COM4: {message}")
```

**Затваряне на всички отворени серийни портове:**

```python
import serial.tools.list_ports

def close_all_serial_ports():
    # Списък на всички серийни портове
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        try:
            # Опит за отваряне и затваряне на порта
            ser = serial.Serial(port.device)
            ser.close()
            print(f"Затворен порт: {port.device}")
        except:
            pass
```

**Проверка на параметрите на серийния порт:**

```python
def test_serial_port_parameters(port_name, baud_rates=[9600, 19200, 38400, 57600, 115200]):
    """Тества различни параметри на серийния порт."""
    for baud_rate in baud_rates:
        try:
            print(f"Тестване на {port_name} с {baud_rate} bps...")
            ser = serial.Serial(port_name, baud_rate, timeout=1)
            ser.write(b'\x00')  # Изпращане на нулев байт
            time.sleep(0.1)
            ser.close()
            print(f"Успешно тестване с {baud_rate} bps")
        except Exception as e:
            print(f"Грешка при {baud_rate} bps: {e}")
```

### 2. Проблеми с TCP/UDP връзката

#### Симптоми
- Получавате грешка при опит за свързване чрез TCP или UDP
- Функцията `connect_physical_interface` връща код за грешка
- Няма комуникация с четеца

#### Възможни причини
1. Неправилен IP адрес или порт
2. Блокиране от защитна стена (firewall)
3. Четецът не е включен или не е в мрежата
4. Мрежови проблеми

#### Решения

**Проверка на достъпността на хоста:**

```python
import socket
import subprocess
import platform

def check_host_availability(host, port):
    """Проверява дали хостът е достъпен."""
    # Проверка с ping
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    
    try:
        ping_result = subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ping_result == 0:
            print(f"Хостът {host} отговаря на ping")
        else:
            print(f"Хостът {host} не отговаря на ping")
    except:
        print(f"Грешка при изпълнение на ping към {host}")
    
    # Проверка на TCP порта
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"Портът {port} на {host} е отворен (TCP)")
            return True
        else:
            print(f"Портът {port} на {host} е затворен (TCP)")
            return False
    except Exception as e:
        print(f"Грешка при проверка на TCP порт: {e}")
        return False
```

**Проверка на мрежови настройки:**

```python
def check_network_settings():
    """Извежда основни мрежови настройки."""
    try:
        # Получаване на IP адреса на машината
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Локален IP адрес: {local_ip}")
        
        # Проверка на gateway
        if platform.system().lower() == 'windows':
            proc = subprocess.Popen(["ipconfig"], stdout=subprocess.PIPE)
            gateway_line = None
            for line in proc.stdout:
                line = line.decode('utf-8', errors='ignore').strip()
                if "Default Gateway" in line:
                    gateway_line = line
                    break
            
            if gateway_line:
                gateway = gateway_line.split(":")[-1].strip()
                print(f"Gateway: {gateway}")
                
        elif platform.system().lower() == 'linux':
            proc = subprocess.Popen(["ip", "route"], stdout=subprocess.PIPE)
            for line in proc.stdout:
                line = line.decode('utf-8').strip()
                if "default" in line:
                    gateway = line.split("via")[1].split()[0]
                    print(f"Gateway: {gateway}")
                    break
    except Exception as e:
        print(f"Грешка при проверка на мрежови настройки: {e}")
```

## Проблеми при четене на тагове

### 1. Не се откриват тагове

#### Симптоми
- Четецът е свързан, но не се известява за открити тагове
- Методът `notify_recv_tags` не се извиква

#### Възможни причини
1. Таговете са извън обхвата на четеца
2. Неправилна ориентация на антената
3. Неправилни настройки на мощността
4. Интерференция от други RF източници

#### Решения

**Проверка на настройките на мощността:**

```python
def check_reader_power(reader):
    """Проверява и коригира настройките на мощността."""
    try:
        # Запитване за текущата мощност
        reader.query_parameter(0x01, 4)
        
        # Задаване на максимална мощност
        params = [0x05, 0x10, 0x00, 0x1F]  # 31 dBm (максимална стойност)
        reader.set_muti_parameter(0x01, len(params), params)
        
        print("Мощността е настроена на максимум")
        return True
    except Exception as e:
        print(f"Грешка при настройка на мощността: {e}")
        return False
```

**Тестване с различни настройки:**

```python
def test_reader_settings(reader):
    """Тества различни настройки на четеца."""
    try:
        # Спиране на текуща инвентаризация
        reader.stop()
        time.sleep(1)
        
        # Ресетиране на четеца
        reader.reset()
        time.sleep(2)
        
        # Настройка на различни параметри
        
        # 1. Максимална мощност
        params = [0x05, 0x10, 0x00, 0x1F]  # 31 dBm
        reader.set_muti_parameter(0x01, len(params), params)
        
        # 2. Увеличаване на времето за сканиране
        params = [0x02, 0x10, 0x00, 0x0A]  # 10 x 100ms = 1 секунда
        reader.set_muti_parameter(0x04, len(params), params)
        
        # 3. Настройка на RF параметри
        params = [0x04, 0x10, 0x00, 0x01]  # Dense Reader Mode
        reader.set_muti_parameter(0x02, len(params), params)
        
        # Стартиране на инвентаризация
        reader.inventory()
        
        print("Настройките са приложени, тестване на инвентаризация...")
        return True
    except Exception as e:
        print(f"Грешка при тестване на настройки: {e}")
        return False
```

### 2. Непостоянно четене на тагове

#### Симптоми
- Таговете се откриват непостоянно
- Някои тагове се откриват, други не
- Таговете се откриват само когато са много близо до четеца

#### Възможни причини
1. Интерференция от метални обекти
2. Неправилно позициониране на антената
3. Недостатъчна мощност
4. Проблеми с таговете

#### Решения

**Проверка на околната среда:**

1. Преместете металните обекти от зоната на четене
2. Тествайте четеца в различни позиции и ориентации
3. Проверете дали таговете работят с друг четец

**Настройка на параметрите на четене:**

```python
def optimize_reading_parameters(reader):
    """Оптимизира параметрите за по-добро четене на тагове."""
    try:
        # Спиране на текуща инвентаризация
        reader.stop()
        time.sleep(1)
        
        # 1. Увеличаване на мощността
        params = [0x05, 0x10, 0x00, 0x1F]  # 31 dBm (максимум)
        reader.set_muti_parameter(0x01, len(params), params)
        
        # 2. Увеличаване на времето за четене
        params = [0x02, 0x10, 0x00, 0x14]  # 20 x 100ms = 2 секунди
        reader.set_muti_parameter(0x04, len(params), params)
        
        # 3. Настройка на RF параметри
        params = [0x04, 0x10, 0x00, 0x00]  # Normal Mode
        reader.set_muti_parameter(0x02, len(params), params)
        
        # 4. Настройка на Q параметър
        params = [0x01, 0x10, 0x00, 0x04]  # Q=4 (балансирано)
        reader.set_muti_parameter(0x05, len(params), params)
        
        # Стартиране на инвентаризация
        reader.inventory()
        
        print("Параметрите са оптимизирани за по-добро четене")
        return True
    except Exception as e:
        print(f"Грешка при оптимизация: {e}")
        return False
```

## Проблеми при запис в тагове

### 1. Неуспешен запис в таг

#### Симптоми
- Методът `write_tag_block` връща грешка
- Получавате съобщение за неуспешен запис в колбека `notify_write_tag_block`

#### Възможни причини
1. Тагът е защитен или заключен
2. Тагът е извън обхвата на четеца
3. Неправилни параметри на запис
4. Тагът не поддържа запис в указаната област

#### Решения

**Проверка на статуса на тага:**

```python
def check_tag_status(reader):
    """Проверява статуса на тага преди запис."""
    try:
        # Четене на EPC данни
        reader.read_tag_block(reader.RFID_TAG_MEMBANK_EPC, 0, 6)
        time.sleep(1)
        
        # Четене на достъп и заключващи битове
        reader.read_tag_block(reader.RFID_TAG_MEMBANK_RESERVED, 0, 4)
        time.sleep(1)
        
        print("Проверката на статуса е завършена")
        return True
    except Exception as e:
        print(f"Грешка при проверка на статуса: {e}")
        return False
```

**Тестване на запис с минимални данни:**

```python
def test_minimal_write(reader):
    """Тества запис с минимални данни."""
    try:
        # Минимални данни за запис (2 байта)
        write_data = bytearray([0x12, 0x34])
        
        # Опит за запис в потребителската област
        reader.write_tag_block(
            reader.RFID_TAG_MEMBANK_USER,
            0,  # Начален адрес
            1,  # Една дума (2 байта)
            write_data,
            0   # Начален индекс в масива с данни
        )
        
        print("Тестов запис е изпратен")
        return True
    except Exception as e:
        print(f"Грешка при тестов запис: {e}")
        return False
```

### 2. Непостоянен запис в тагове

#### Симптоми
- Записът в тагове е непостоянен
- Понякога успява, понякога не
- Записът успява само когато тагът е много близо до четеца

#### Възможни причини
Същите като при непостоянно четене, плюс:
1. Недостатъчна енергия за запис (изисква се повече енергия, отколкото за четене)
2. Интерференция от други RF източници

#### Решения

**Увеличаване на мощността и оптимизиране на параметрите за запис:**

```python
def optimize_write_parameters(reader):
    """Оптимизира параметрите за по-добър запис в тагове."""
    try:
        # Спиране на текуща инвентаризация
        reader.stop()
        time.sleep(1)
        
        # 1. Увеличаване на мощността до максимум
        params = [0x05, 0x10, 0x00, 0x1F]  # 31 dBm (максимум)
        reader.set_muti_parameter(0x01, len(params), params)
        
        # 2. Увеличаване на времето за задържане на RF сигнала
        params = [0x03, 0x10, 0x00, 0x32]  # 50 x 10ms = 500ms
        reader.set_muti_parameter(0x08, len(params), params)
        
        # 3. Настройка на RF параметри за запис
        params = [0x02, 0x10, 0x00, 0x01]  # Write Mode
        reader.set_muti_parameter(0x09, len(params), params)
        
        print("Параметрите са оптимизирани за по-добър запис")
        return True
    except Exception as e:
        print(f"Грешка при оптимизация: {e}")
        return False
```

**Последователни опити за запис с постепенно приближаване:**

```python
def persistent_write_attempt(reader, membank, addr, data, max_attempts=5):
    """Прави множество опити за запис с увеличаване на времето между опитите."""
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Опит {attempt}/{max_attempts} за запис...")
            
            # Опит за запис
            reader.write_tag_block(
                membank,
                addr,
                len(data) // 2,  # Брой думи (2 байта всяка)
                data,
                0
            )
            
            # Изчакване за по-дълго време с всеки следващ опит
            wait_time = 0.5 + (attempt * 0.5)
            time.sleep(wait_time)
            
            # Проверка дали записът е успешен чрез четене
            reader.read_tag_block(membank, addr, len(data) // 2)
            time.sleep(1)
            
            print(f"Опит {attempt} завършен")
        except Exception as e:
            print(f"Грешка при опит {attempt}: {e}")
    
    print("Всички опити са завършени")
```