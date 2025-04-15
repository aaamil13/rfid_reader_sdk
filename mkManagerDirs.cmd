@echo off
REM Script to create the RFID Reader Manager project structure
REM This script will create all necessary directories and empty files

echo Creating RFID Reader Manager project structure...

REM Create main project directory
mkdir rfid_reader_manager

REM Create package directories
mkdir rfid_reader_manager\config
mkdir rfid_reader_manager\core
mkdir rfid_reader_manager\gui
mkdir rfid_reader_manager\i18n
mkdir rfid_reader_manager\i18n\locale
mkdir rfid_reader_manager\i18n\locale\en
mkdir rfid_reader_manager\i18n\locale\bg
mkdir rfid_reader_manager\utils

REM Create __init__.py files
echo """
RFID Reader Manager Application
""" > rfid_reader_manager\__init__.py

echo __version__ = "1.0.0" >> rfid_reader_manager\__init__.py

echo """
RFID Reader Manager Application
Configuration package
""" > rfid_reader_manager\config\__init__.py

echo """
RFID Reader Manager Application
Core package
""" > rfid_reader_manager\core\__init__.py

echo """
RFID Reader Manager Application
GUI package
""" > rfid_reader_manager\gui\__init__.py

echo """
RFID Reader Manager Application
Internationalization package
""" > rfid_reader_manager\i18n\__init__.py

echo """
RFID Reader Manager Application
Utilities package
""" > rfid_reader_manager\utils\__init__.py

REM Create main application files
type nul > rfid_reader_manager\main.py
type nul > rfid_reader_manager\__main__.py
type nul > rfid_reader_manager\requirements.txt

REM Create config module files
type nul > rfid_reader_manager\config\app_config.py
type nul > rfid_reader_manager\config\reader_profiles.py

REM Create core module files
type nul > rfid_reader_manager\core\rfid_manager.py
type nul > rfid_reader_manager\core\reader_wrapper.py
type nul > rfid_reader_manager\core\tag_operations.py

REM Create GUI module files
type nul > rfid_reader_manager\gui\main_window.py
type nul > rfid_reader_manager\gui\connection_dialog.py
type nul > rfid_reader_manager\gui\reader_settings_widget.py
type nul > rfid_reader_manager\gui\tag_operations_widget.py
type nul > rfid_reader_manager\gui\log_viewer_widget.py
type nul > rfid_reader_manager\gui\profiles_widget.py

REM Create i18n module files
type nul > rfid_reader_manager\i18n\translations.py
type nul > rfid_reader_manager\i18n\locale\en\rfid_manager.ts
type nul > rfid_reader_manager\i18n\locale\bg\rfid_manager.ts

REM Create utilities module files
type nul > rfid_reader_manager\utils\logger.py
type nul > rfid_reader_manager\utils\async_worker.py
type nul > rfid_reader_manager\utils\error_handler.py
type nul > rfid_reader_manager\utils\port_scanner.py

REM Create README file
echo # RFID Reader Manager > rfid_reader_manager\README.md
echo. >> rfid_reader_manager\README.md
echo A cross-platform application for managing RFID readers. >> rfid_reader_manager\README.md

echo Project structure created successfully!
echo The project is located in: %CD%\rfid_reader_manager