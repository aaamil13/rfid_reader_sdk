#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на AppNotify за R2000 RFID четец.
Еквивалент на R2000ReaderNotifyImpl.java
"""

from rfid.reader.app_notify import AppNotify


class R2000ReaderNotifyImpl(AppNotify):
    """Имплементация на AppNotify за R2000 RFID четец."""

    def notify_recv_tags(self, message, start_index):
        """Известяване за получени RFID тагове.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        tag_count = 0
        tag_count = message[start_index + 7]
        tag_count = tag_count << 8
        tag_count = tag_count + message[start_index + 8]

        print(f"Total tags received: {tag_count}")
        print("Received tag data:")

        for i_index in range(tag_count):
            for j_index in range(12):
                print(f"{message[start_index + 9 + i_index * 12 + j_index]:02X} ", end="")
            print()

        return 0

    def notify_stop_inventory(self, message, start_index):
        """Известяване за край на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print("Reader stopped reading tags")
        return 0

    def notify_reset(self, message, start_index):
        """Известяване за ресетиране на четеца.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print("Reader reset successful")
        return 0

    def notify_read_tag_block(self, message, start_index):
        """Известяване за прочетен блок от таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_write_tag_block(self, message, start_index):
        """Известяване за записан блок в таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_lock_tag(self, message, start_index):
        """Известяване за заключен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_kill_tag(self, message, start_index):
        """Известяване за унищожен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_inventory_once(self, message, start_index):
        """Известяване за еднократна инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_start_inventory(self, message, start_index):
        """Известяване за начало на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print("R2000 started scanning tags")
        return 0