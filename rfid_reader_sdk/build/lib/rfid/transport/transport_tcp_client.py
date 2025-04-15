#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TCP клиент транспорт за RFID четци.
Еквивалент на TransportTcpClient.java
"""

import socket
import time
from rfid.transport.transport import Transport


class TransportTcpClient(Transport):
    """TCP клиент транспорт за RFID четци."""

    def __init__(self):
        """Инициализация на TCP клиент транспорт."""
        super().__init__()
        self.remote_ip = None
        self.remote_port = 0
        self.local_ip = None
        self.local_port = 0
        self.client_socket = None
        self.recv_buffer = None

    def set_config(self, remote_ip, remote_port, local_ip, local_port):
        """Задаване на конфигурация.

        Args:
            remote_ip (str): Отдалечен IP адрес
            remote_port (int): Отдалечен порт
            local_ip (str): Локален IP адрес
            local_port (int): Локален порт
        """
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.local_ip = local_ip
        self.local_port = local_port

    def request_local_resource(self):
        """Заявка за локален ресурс.

        Returns:
            int: Резултат от операцията
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.local_ip is not None and self.local_port != 0:
                self.client_socket.bind((self.local_ip, self.local_port))

            print(f"Connecting to {self.remote_ip}:{self.remote_port}...")
            self.client_socket.connect((self.remote_ip, self.remote_port))
            print("Connected!")

            # Направи сокета неблокиращ
            self.client_socket.setblocking(False)

            self.connect_status = self.CONNECT_STATUS_CONNECTED
            return 0
        except socket.error as e:
            print(f"TCP client connection error: {e}")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            return -1

    def send_data(self, data, data_len):
        """Изпращане на данни.

        Args:
            data (bytes): Данни за изпращане
            data_len (int): Дължина на данните

        Returns:
            int: Резултат от операцията
        """
        if not self.client_socket:
            return -1

        try:
            self.client_socket.sendall(bytes(data[:data_len]))
            return 0
        except socket.error as e:
            print(f"TCP send error: {e}")
            return -1

    def read_data(self, data):
        """Четене на данни.

        Args:
            data (bytearray): Буфер за прочетените данни

        Returns:
            int: Брой прочетени байтове
        """
        if not self.client_socket:
            return -1

        try:
            received = self.client_socket.recv(len(data))
            recv_len = len(received)

            if recv_len > 0:
                for i in range(recv_len):
                    data[i] = received[i]

            return recv_len
        except BlockingIOError:
            # Не блокирай, ако няма данни
            return 0
        except socket.error as e:
            print(f"TCP read error: {e}")
            return -1

    def release_resource(self):
        """Освобождаване на ресурси.

        Returns:
            int: Резултат от операцията
        """
        if not self.client_socket:
            return 0

        try:
            self.client_socket.close()
            self.client_socket = None
            self.connect_status = self.CONNECT_STATUS_DISCONNECT
            return 0
        except socket.error as e:
            print(f"TCP close error: {e}")
            return -1

    def __del__(self):
        """Деструктор."""
        self.release_resource()