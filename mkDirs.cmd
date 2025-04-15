@echo off
setlocal enabledelayedexpansion

:: Създаване на базовата структура на директориите
echo Creating directory structure...
mkdir rfid_reader_sdk
cd rfid_reader_sdk
mkdir rfid
cd rfid
mkdir reader
mkdir app_notify_impl
mkdir transport
mkdir message
cd ..
mkdir examples

:: Създаване на файловете

:: Основни __init__.py файлове
echo Creating __init__.py files...
echo # -*- coding: utf-8 -*-> rfid\__init__.py
echo """RFID Reader SDK - библиотека за работа с RFID четци.""">> rfid\__init__.py
echo __version__ = '0.1.0'>> rfid\__init__.py

echo # -*- coding: utf-8 -*-> rfid\reader\__init__.py
echo """Модул за RFID четци.""">> rfid\reader\__init__.py
echo from .app_notify import AppNotify>> rfid\reader\__init__.py
echo from .rfid_reader import RfidReader>> rfid\reader\__init__.py

echo # -*- coding: utf-8 -*-> rfid\app_notify_impl\__init__.py
echo """Модул за имплементации на AppNotify.""">> rfid\app_notify_impl\__init__.py

echo # -*- coding: utf-8 -*-> rfid\transport\__init__.py
echo """Модул за транспортни протоколи.""">> rfid\transport\__init__.py
echo from .transport import Transport>> rfid\transport\__init__.py
echo from .transport_serial_port import TransportSerialPort>> rfid\transport\__init__.py
echo from .transport_tcp_client import TransportTcpClient>> rfid\transport\__init__.py
echo from .transport_udp import TransportUdp>> rfid\transport\__init__.py
echo from .transport_thread_manager import TransportThreadManager>> rfid\transport\__init__.py

echo # -*- coding: utf-8 -*-> rfid\message\__init__.py
echo """Модул за съобщения.""">> rfid\message\__init__.py
echo from .reader_adapt import ReaderAdapt>> rfid\message\__init__.py

:: Базови класове и интерфейси
echo Creating base classes...

:: 1. Транспортен слой
echo Creating transport layer...
echo # -*- coding: utf-8 -*-> rfid\transport\transport.py
echo """Базов абстрактен клас за транспортни протоколи.""">> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo from abc import ABC, abstractmethod>> rfid\transport\transport.py
echo import io>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo class Transport(ABC):>> rfid\transport\transport.py
echo     """Абстрактен базов клас за различни транспортни протоколи.""">> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     # Константи за статус на връзка>> rfid\transport\transport.py
echo     CONNECT_STATUS_DISCONNECT = 0>> rfid\transport\transport.py
echo     CONNECT_STATUS_GET_LOCAL_RESOURCE = 1>> rfid\transport\transport.py
echo     CONNECT_STATUS_CONNECTED = 2>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     def __init__(self):>> rfid\transport\transport.py
echo         """Инициализация на транспортния обект.""">> rfid\transport\transport.py
echo         self.connect_status = self.CONNECT_STATUS_DISCONNECT>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     @abstractmethod>> rfid\transport\transport.py
echo     def release_resource(self):>> rfid\transport\transport.py
echo         """Освобождаване на ресурса.""">> rfid\transport\transport.py
echo         pass>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     @abstractmethod>> rfid\transport\transport.py
echo     def request_local_resource(self):>> rfid\transport\transport.py
echo         """Заявка за локален ресурс.""">> rfid\transport\transport.py
echo         pass>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     @abstractmethod>> rfid\transport\transport.py
echo     def send_data(self, data, data_len):>> rfid\transport\transport.py
echo         """Изпращане на данни.""">> rfid\transport\transport.py
echo         pass>> rfid\transport\transport.py
echo.>> rfid\transport\transport.py
echo     @abstractmethod>> rfid\transport\transport.py
echo     def read_data(self, data):>> rfid\transport\transport.py
echo         """Четене на данни.""">> rfid\transport\transport.py
echo         pass>> rfid\transport\transport.py

:: 2. AppNotify интерфейс
echo Creating AppNotify interface...
echo # -*- coding: utf-8 -*-> rfid\reader\app_notify.py
echo """Интерфейс за известяване на приложението.""">> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo from abc import ABC, abstractmethod>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo class AppNotify(ABC):>> rfid\reader\app_notify.py
echo     """Интерфейс за известяване при получаване на отговор от RFID четеца.""">> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_recv_tags(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за получени RFID тагове.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_start_inventory(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за начало на инвентаризация.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_stop_inventory(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за край на инвентаризация.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_reset(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за ресетиране на четеца.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_read_tag_block(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за прочетен блок от таг.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_write_tag_block(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за записан блок в таг.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_lock_tag(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за заключен таг.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_kill_tag(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за унищожен таг.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py
echo.>> rfid\reader\app_notify.py
echo     @abstractmethod>> rfid\reader\app_notify.py
echo     def notify_inventory_once(self, message, start_index):>> rfid\reader\app_notify.py
echo         """Известяване за еднократна инвентаризация.""">> rfid\reader\app_notify.py
echo         pass>> rfid\reader\app_notify.py

:: 3. RfidReader абстрактен клас
echo Creating RfidReader abstract class...

:: 4. ReaderAdapt клас
echo Creating ReaderAdapt class...
echo # -*- coding: utf-8 -*-> rfid\message\reader_adapt.py
echo """Абстрактен клас за адаптер на четец.""">> rfid\message\reader_adapt.py
echo.>> rfid\message\reader_adapt.py
echo from abc import ABC>> rfid\message\reader_adapt.py
echo.>> rfid\message\reader_adapt.py
echo.>> rfid\message\reader_adapt.py
echo class ReaderAdapt(ABC):>> rfid\message\reader_adapt.py
echo     """Абстрактен клас за адаптер на четец.""">> rfid\message\reader_adapt.py
echo.>> rfid\message\reader_adapt.py
echo     def __init__(self):>> rfid\message\reader_adapt.py
echo         """Инициализация на адаптера.""">> rfid\message\reader_adapt.py
echo         pass>> rfid\message\reader_adapt.py

:: Създаване на setup.py
echo Creating setup.py...
echo # -*- coding: utf-8 -*-> setup.py
echo """Конфигурационен файл за инсталиране на библиотеката.""">> setup.py
echo.>> setup.py
echo from setuptools import setup, find_packages>> setup.py
echo.>> setup.py
echo setup(>> setup.py
echo     name="rfid_reader_sdk",>> setup.py
echo     version="0.1.0",>> setup.py
echo     description="Python SDK for RFID readers",>> setup.py
echo     author="YourName",>> setup.py
echo     author_email="your.email@example.com",>> setup.py
echo     packages=find_packages(),>> setup.py
echo     install_requires=[>> setup.py
echo         "pyserial>=3.5",>> setup.py
echo     ],>> setup.py
echo     classifiers=[>> setup.py
echo         "Development Status :: 3 - Alpha",>> setup.py
echo         "Intended Audience :: Developers",>> setup.py
echo         "License :: OSI Approved :: MIT License",>> setup.py
echo         "Programming Language :: Python :: 3",>> setup.py
echo         "Programming Language :: Python :: 3.6",>> setup.py
echo         "Programming Language :: Python :: 3.7",>> setup.py
echo         "Programming Language :: Python :: 3.8",>> setup.py
echo         "Programming Language :: Python :: 3.9",>> setup.py
echo         "Programming Language :: Python :: 3.10",>> setup.py
echo     ],>> setup.py
echo     python_requires=">=3.6",>> setup.py
echo )>> setup.py

:: Създаване на README.md
echo Creating README.md...
echo # RFID Reader SDK> README.md
echo.>> README.md
echo Python библиотека за работа с RFID четци.>> README.md
echo.>> README.md
echo ## Описание>> README.md
echo.>> README.md
echo RFID Reader SDK е Python библиотека, която предоставя API за комуникация с различни модели RFID четци. Библиотеката поддържа следните модели:>> README.md
echo.>> README.md
echo - General RFID Reader>> README.md
echo - M RFID Reader>> README.md
echo - R2000 RFID Reader>> README.md
echo.>> README.md
echo Транспортните слоеве включват:>> README.md
echo - Сериен порт>> README.md
echo - TCP клиент>> README.md
echo - UDP>> README.md
echo.>> README.md
echo ## Инсталация>> README.md
echo.>> README.md
echo ```bash>> README.md
echo pip install rfid-reader-sdk>> README.md
echo ```>> README.md
echo.>> README.md
echo Или инсталирайте директно от source:>> README.md
echo.>> README.md
echo ```bash>> README.md
echo git clone https://github.com/yourusername/rfid-reader-sdk.git>> README.md
echo cd rfid-reader-sdk>> README.md
echo pip install .>> README.md
echo ```>> README.md
echo.>> README.md
echo ## Изисквания>> README.md
echo.>> README.md
echo - Python 3.6+>> README.md
echo - pyserial 3.5+>> README.md
echo.>> README.md
echo ## Използване>> README.md
echo.>> README.md
echo За примери вижте файловете в директорията examples/.>> README.md

:: Примерни файлове
echo Creating example files...
mkdir examples
:: Тук ще добавите кода на примерните файлове

echo Project structure created successfully!
cd ..

echo Running the following command will install the required packages:
echo pip install -e rfid_reader_sdk

endlocal