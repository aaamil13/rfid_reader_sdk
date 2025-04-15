#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интерфейс за известяване на приложението.
Еквивалент на AppNotify.java
"""

from abc import ABC, abstractmethod


class AppNotify(ABC):
    """Интерфейс за известяване при получаване на отговор от RFID четеца."""

    @abstractmethod
    def notify_recv_tags(self, message, start_index):
        """Известяване за получени RFID тагове.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_start_inventory(self, message, start_index):
        """Известяване за начало на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_stop_inventory(self, message, start_index):
        """Известяване за край на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_reset(self, message, start_index):
        """Известяване за ресетиране на четеца.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_read_tag_block(self, message, start_index):
        """Известяване за прочетен блок от таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_write_tag_block(self, message, start_index):
        """Известяване за записан блок в таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_lock_tag(self, message, start_index):
        """Известяване за заключен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_kill_tag(self, message, start_index):
        """Известяване за унищожен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass

    @abstractmethod
    def notify_inventory_once(self, message, start_index):
        """Известяване за еднократна инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        pass