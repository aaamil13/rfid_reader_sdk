#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Базов абстрактен клас за транспортни протоколи.
Еквивалент на Transport.java
"""

from abc import ABC, abstractmethod
import io


class Transport(ABC):
    """Абстрактен базов клас за различни транспортни протоколи."""

    # Константи за статус на връзка
    CONNECT_STATUS_DISCONNECT = 0
    CONNECT_STATUS_GET_LOCAL_RESOURCE = 1
    CONNECT_STATUS_CONNECTED = 2

    def __init__(self):
        """Инициализация на транспортния обект."""
        self.connect_status = self.CONNECT_STATUS_DISCONNECT

    @abstractmethod
    def release_resource(self):
        """Освобождаване на ресурса."""
        pass

    @abstractmethod
    def request_local_resource(self):
        """Заявка за локален ресурс."""
        pass

    @abstractmethod
    def send_data(self, data, data_len):
        """Изпращане на данни.

        Args:
            data (bytes): Данни за изпращане
            data_len (int): Дължина на данните

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def read_data(self, data):
        """Четене на данни.

        Args:
            data (bytearray): Буфер за прочетените данни

        Returns:
            int: Брой прочетени байтове
        """
        pass