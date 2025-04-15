#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UDP транспорт за RFID четци.
Еквивалент на TransportUdp.java
"""

import socket
from rfid.transport.transport import Transport


class TransportUdp(Transport):
    """UDP транспорт за RFID четци."""

    def __init__(self):
        """Инициализация на UDP транспорт."""
        super().__init__()
        self.remote_ip = ""
        self.remote_port = 0
        self.local_ip = ""
        self.local_port = 0
        self.socket_channel = None
        self.dst_addr = None

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
        self.dst_addr = (self.remote_ip, self.remote_port)

    def request_local_resource(self):
        """Заявка за локален ресурс.

        Returns:
            int: Резултат от операцията
        """
        if self.socket_channel:
            self.release_resource()

        try:
            self.socket_channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Направи сокета неблокиращ
            self.socket_channel.setblocking(False)

            if self.local_port != 0:
                self.socket_channel.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
                self.socket_channel.bind((self.local_ip if self.local_ip else '', self.local_port))

            self.connect_status = self.CONNECT_STATUS_GET_LOCAL_RESOURCE
            return 0
        except socket.error as e:
            print(f"UDP socket error: {e}")
            return -1

    def send_data(self, data, data_len):
        """Изпращане на данни.

        Args:
            data (bytes): Данни за изпращане
            data_len (int): Дължина на данните

        Returns:
            int: Резултат от операцията
        """
        if not self.socket_channel:
            return -1

        try:
            self.socket_channel.sendto(bytes(data[:data_len]), self.dst_addr)
            return 0
        except socket.error as e:
            print(f"UDP send error: {e}")
            return -1

    def read_data(self, data):
        """Четене на данни.

        Args:
            data (bytearray): Буфер за прочетените данни

        Returns:
            int: Брой прочетени байтове
        """
        if not self.socket_channel:
            return -1

        try:
            received, source_addr = self.socket_channel.recvfrom(len(data))
            recv_len = len(received)

            if recv_len > 0:
                for i in range(recv_len):
                    data[i] = received[i]

                print(f"Received from: {source_addr}, length: {recv_len}")

            return recv_len
        except BlockingIOError:
            # Не блокирай, ако няма данни
            return 0
        except socket.error as e:
            print(f"UDP read error: {e}")
            return -1

    def release_resource(self):
        """Освобождаване на ресурси.

        Returns:
            int: Резултат от операцията
        """
        if not self.socket_channel:
            return 0

        try:
            self.socket_channel.close()
            self.socket_channel = None
            self.connect_status = self.CONNECT_STATUS_DISCONNECT
            return 0
        except socket.error as e:
            print(f"UDP close error: {e}")
            return -1

    def __del__(self):
        """Деструктор."""
        self.release_resource()