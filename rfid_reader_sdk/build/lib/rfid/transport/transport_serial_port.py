#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Сериен порт транспорт за RFID четци.
Еквивалент на TransportSerialPort.java
"""

import serial
import serial.tools.list_ports
from rfid.transport.transport import Transport


class TransportSerialPort(Transport):
    """Сериен порт транспорт за RFID четци."""

    def __init__(self):
        """Инициализация на сериен порт транспорт."""
        super().__init__()
        self.serial_port_name = None
        self.baud_rate = None
        self.serial_port_channel = None

    @staticmethod
    def find_port():
        """Намира достъпните серийни портове.

        Returns:
            list: Списък с имена на достъпни серийни портове
        """
        ports = serial.tools.list_ports.comports()
        port_name_list = []

        for port in ports:
            port_name_list.append(port.device)

        return port_name_list

    def set_serial_port_config(self, port_name, baud_rate):
        """Задаване на конфигурация на серийния порт.

        Args:
            port_name (str): Име на серийния порт
            baud_rate (int): Скорост на комуникация
        """
        self.serial_port_name = port_name
        self.baud_rate = baud_rate

    def get_serial_port_name(self):
        """Връща името на серийния порт."""
        return self.serial_port_name

    def set_serial_port_name(self, serial_port_name):
        """Задава името на серийния порт."""
        self.serial_port_name = serial_port_name

    def get_baud_rate(self):
        """Връща скоростта на комуникация."""
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        """Задава скоростта на комуникация."""
        self.baud_rate = baud_rate

    def release_resource(self):
        """Освобождаване на ресурси.

        Returns:
            int: Резултат от операцията
        """
        if not self.serial_port_channel:
            return 0

        try:
            self.serial_port_channel.close()
            self.serial_port_channel = None
            self.connect_status = self.CONNECT_STATUS_DISCONNECT
            return 0
        except serial.SerialException as e:
            print(f"Serial port close error: {e}")
            return -1

    def send_data(self, data, data_len):
        """Изпращане на данни.

        Args:
            data (bytes): Данни за изпращане
            data_len (int): Дължина на данните

        Returns:
            int: Резултат от операцията
        """
        if not self.serial_port_channel:
            return -1

        try:
            self.serial_port_channel.write(bytes(data[:data_len]))
            self.serial_port_channel.flush()
            return 0
        except serial.SerialException as e:
            print(f"Serial port write error: {e}")
            return -1

    def read_data(self, data):
        """Четене на данни.

        Args:
            data (bytearray): Буфер за прочетените данни

        Returns:
            int: Брой прочетени байтове
        """
        if not self.serial_port_channel:
            return -1

        try:
            available = self.serial_port_channel.in_waiting
            if available == 0:
                return 0

            received = self.serial_port_channel.read(min(available, len(data)))
            recv_len = len(received)

            if recv_len > 0:
                for i in range(recv_len):
                    data[i] = received[i]

            return recv_len
        except serial.SerialException as e:
            print(f"Serial port read error: {e}")
            return -1

    def __del__(self):
        """Деструктор."""
        self.release_resource()

    def request_local_resource(self):
        """Заявка за локален ресурс.

        Returns:
            int: Резултат от операцията
        """
        if self.serial_port_channel:
            self.release_resource()

        try:
            self.serial_port_channel = serial.Serial(
                port=self.serial_port_name,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5
            )

            if not self.serial_port_channel.is_open:
                self.serial_port_channel.open()

            self.connect_status = self.CONNECT_STATUS_CONNECTED
            return 0
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            return -1