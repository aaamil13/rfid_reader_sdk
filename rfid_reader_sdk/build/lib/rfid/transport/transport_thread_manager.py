#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Мениджър на транспортни нишки за RFID четци.
Еквивалент на TransportThreadManager.java
"""

import threading
import selectors
import time
from socket import socket


class TransportThreadManager:
    """Мениджър на транспортни нишки за RFID четци."""

    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self):
        """Инициализация на мениджъра на транспортни нишки."""
        self.selector = selectors.DefaultSelector()
        self.reader_map = {}  # Речник с четци
        self._receive_thread = None
        self._running = False

    @classmethod
    def get_instance(cls):
        """Връща инстанция на мениджъра на транспортни нишки.

        Returns:
            TransportThreadManager: Инстанция на мениджъра
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls.initialize_transport_manager()
        return cls._instance

    @classmethod
    def initialize_transport_manager(cls):
        """Инициализация на мениджъра на транспортни нишки."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()

        cls.initialize_threads()

    @classmethod
    def initialize_threads(cls):
        """Инициализация на нишките."""
        instance = cls.get_instance()
        if instance._receive_thread is None:
            instance._running = True
            instance._receive_thread = ReceiveThread(instance)
            instance._receive_thread.start()

    def get_reader_iterator(self):
        """Връща итератор за речника с четци."""
        return self.reader_map.items()

    def get_selector(self):
        """Връща селектора за неблокиращо I/O."""
        return self.selector

    def add_rfid_reader(self, reader):
        """Добавя RFID четец към мениджъра.

        Args:
            reader: RFID четецът за добавяне

        Returns:
            int: Резултат от операцията
        """
        result = 0

        if reader.connect_type == reader.CONNECT_TYPE_NET_TCP_CLIENT:
            transport = reader.get_transport()
            if hasattr(transport, 'client_socket') and transport.client_socket:
                self.selector.register(transport.client_socket, selectors.EVENT_READ, reader)

        elif reader.connect_type == reader.CONNECT_TYPE_NET_TCP_SERVER:
            # Не е реализирано
            pass

        elif reader.connect_type == reader.CONNECT_TYPE_NET_UDP:
            transport = reader.get_transport()
            if hasattr(transport, 'socket_channel') and transport.socket_channel:
                self.selector.register(transport.socket_channel, selectors.EVENT_READ, reader)

        elif reader.connect_type == reader.CONNECT_TYPE_SERIALPORT:
            # Серийните портове се проверяват в цикъла на нишката
            pass

        self.reader_map[reader.get_key()] = reader
        return result

    def stop(self):
        """Спира мениджъра и неговите нишки."""
        self._running = False
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(2.0)  # Изчаква нишката да приключи

        # Затваря всички селектори
        if self.selector:
            self.selector.close()

        # Освобождава ресурси на четците
        for reader in self.reader_map.values():
            if reader.transport:
                reader.transport.release_resource()

        self.reader_map.clear()


class ReceiveThread(threading.Thread):
    """Нишка за получаване на данни от RFID четци."""

    def __init__(self, manager):
        """Инициализация на нишката.

        Args:
            manager (TransportThreadManager): Мениджърът на транспортни нишки
        """
        super().__init__()
        self.daemon = True  # Нишката ще се прекрати автоматично при изход
        self.manager = manager

    def run(self):
        """Изпълнява се при стартиране на нишката."""
        while self.manager._running:
            # Проверява за събития в селектора
            selector = self.manager.get_selector()
            if selector:
                events = selector.select(0.01)  # Малко изчакване за да не натоварва CPU

                for key, mask in events:
                    if mask & selectors.EVENT_READ:
                        reader = key.data
                        try:
                            reader.handle_recv()
                        except Exception as e:
                            print(f"Error handling receive: {e}")

            # Проверява сериен порт
            for reader in self.manager.reader_map.values():
                if reader.connect_type == reader.CONNECT_TYPE_SERIALPORT:
                    transport = reader.get_transport()
                    if hasattr(transport, 'serial_port_channel') and transport.serial_port_channel:
                        try:
                            if transport.serial_port_channel.in_waiting > 0:
                                time.sleep(0.05)  # Малко изчакване за натрупване на данни
                                reader.handle_recv()
                        except Exception as e:
                            print(f"Error handling serial port: {e}")

            time.sleep(0.01)  # Предотвратява 100% натоварване на CPU