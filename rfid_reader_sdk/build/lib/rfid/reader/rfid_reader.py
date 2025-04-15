#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Базов абстрактен клас за RFID четци.
Еквивалент на RfidReader.java
"""

from abc import ABC, abstractmethod
import socket
import serial

from rfid.transport.transport import Transport
from rfid.transport.transport_serial_port import TransportSerialPort
from rfid.transport.transport_tcp_client import TransportTcpClient
from rfid.transport.transport_udp import TransportUdp


class RfidReader(ABC):
    """Абстрактен базов клас за RFID четци."""

    # Константи за типове връзка
    CONNECT_TYPE_SERIALPORT = 0
    CONNECT_TYPE_NET_UDP = 1
    CONNECT_TYPE_NET_TCP_CLIENT = 2
    CONNECT_TYPE_NET_TCP_SERVER = 3

    MAX_RECV_BUFF_SIZE = 1024
    MAX_SEND_BUFF_SIZE = 128

    def __init__(self):
        """Инициализация на RFID четеца."""
        self.key = None
        self.recv_msg_buff = bytearray(self.MAX_RECV_BUFF_SIZE)
        self.recv_msg_len = 0
        self.app_notify = None
        self.send_msg_buff = bytearray(self.MAX_SEND_BUFF_SIZE)
        self.send_index = 0
        self.recv_len = 0
        self.transport = None
        self.connect_type = 0

    def get_app_notify(self):
        """Връща обекта за известяване."""
        return self.app_notify

    def set_app_notify(self, app_notify):
        """Задава обекта за известяване."""
        self.app_notify = app_notify

    def get_key(self):
        """Връща ключа на четеца."""
        return self.key

    def connect_physical_interface(self, physical_name, physical_param, local_addr_str, local_addr_port, connect_type):
        """Свързване към физически интерфейс.

        Args:
            physical_name (str): Име на физическия интерфейс (порт или IP)
            physical_param (int): Параметър (скорост или порт)
            local_addr_str (str): Локален IP адрес
            local_addr_port (int): Локален порт
            connect_type (int): Тип на връзка

        Returns:
            int: Резултат от операцията
        """
        result = -1
        self.connect_type = connect_type

        if connect_type == self.CONNECT_TYPE_NET_TCP_CLIENT:
            tcp_transport = TransportTcpClient()
            tcp_transport.set_config(physical_name, physical_param, local_addr_str, local_addr_port)
            result = tcp_transport.request_local_resource()
            self.key = f"TCP:{local_addr_str}:{local_addr_port}"
            if result == 0:
                self.transport = tcp_transport

        elif connect_type == self.CONNECT_TYPE_NET_UDP:
            udp_transport = TransportUdp()
            udp_transport.set_config(physical_name, physical_param, local_addr_str, local_addr_port)
            result = udp_transport.request_local_resource()
            self.key = f"UDP:{local_addr_str}:{local_addr_port}"
            if result == 0:
                self.transport = udp_transport

        elif connect_type == self.CONNECT_TYPE_SERIALPORT:
            serial_port = TransportSerialPort()
            serial_port.set_serial_port_config(physical_name, physical_param)
            result = serial_port.request_local_resource()
            self.key = physical_name
            if result == 0:
                self.transport = serial_port

        elif connect_type == self.CONNECT_TYPE_NET_TCP_SERVER:
            # Не реализирано
            pass

        return result

    @staticmethod
    def get_unsigned_byte(data):
        """Преобразува signed byte към unsigned byte (0-255)."""
        return data & 0xFF

    @abstractmethod
    def inventory(self):
        """Започва инвентаризация на тагове."""
        pass

    @abstractmethod
    def inventory_once(self):
        """Започва еднократна инвентаризация на тагове."""
        pass

    @abstractmethod
    def stop(self):
        """Спира инвентаризацията."""
        pass

    @abstractmethod
    def relay_operation(self, relay_no, operation_type, time):
        """Операция с релета."""
        pass

    @abstractmethod
    def reset(self):
        """Ресетиране на четеца."""
        pass

    @abstractmethod
    def read_tag_block(self, membank, addr, length):
        """Прочита блок данни от таг."""
        pass

    @abstractmethod
    def write_tag_block(self, membank, addr, length, written_data, write_start_index):
        """Записва блок данни в таг."""
        pass

    @abstractmethod
    def lock_tag(self, lock_type):
        """Заключва таг."""
        pass

    @abstractmethod
    def kill_tag(self):
        """Унищожава таг."""
        pass

    @abstractmethod
    def handle_recv(self):
        """Обработва получени данни."""
        pass

    @abstractmethod
    def handle_message(self):
        """Обработва съобщение."""
        pass

    @abstractmethod
    def notify_message_to_app(self, message, start_index):
        """Известява приложението за съобщение."""
        pass

    def get_transport(self):
        """Връща транспортния обект."""
        return self.transport