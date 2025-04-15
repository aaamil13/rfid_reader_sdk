#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на AppNotify за стандартен RFID четец.
Еквивалент на GeneralReaderNotifyImpl.java
"""

from rfid.reader.app_notify import AppNotify


class GeneralReaderNotifyImpl(AppNotify):
    """Имплементация на AppNotify за стандартен RFID четец."""

    def notify_recv_tags(self, message, start_index):
        """Известяване за получени RFID тагове.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print(f"Uploaded tag device ID: {hex(message[start_index + 3] & 0xFF)}")
        print("Read tag data: ", end="")

        for i_index in range(message[start_index + 4] & 0xFF):
            print(f"{message[start_index + 4 + i_index]:02X} ", end="")

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
        status = message[start_index + 3]

        if status == 0:
            print("Reader stopped reading tags")
        else:
            print("Reader failed to stop reading tags")

        return 0

    def notify_reset(self, message, start_index):
        """Известяване за ресетиране на четеца.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        status = message[start_index + 3]

        if status == 0:
            print("Successfully restarted reader")
        else:
            print("Failed to restart reader")

        return 0

    def notify_read_tag_block(self, message, start_index):
        """Известяване за прочетен блок от таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        if message[start_index + 1] <= 3:
            # Само при грешка се връща дължина по-малка от 4
            print("Failed to read tag block")
        else:
            print(f"Read tag {message[start_index + 4]} area, "
                  f"address: {message[start_index + 5]}, "
                  f"length: {message[start_index + 6]}, data: ", end="")

            for i_index in range(message[start_index + 6] * 2):
                print(f"{message[start_index + 7 + i_index]:02X} ", end="")

            print()

        return 0

    def notify_write_tag_block(self, message, start_index):
        """Известяване за записан блок в таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        status = message[start_index + 3]

        if status == 0:
            print("Successfully wrote to tag")
        else:
            print("Failed to write to tag, please place the tag properly")

        return 0

    def notify_lock_tag(self, message, start_index):
        """Известяване за заключен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        status = message[start_index + 3]

        if status == 0:
            print("Successfully locked tag")
        else:
            print("Failed to lock tag")

        return 0

    def notify_kill_tag(self, message, start_index):
        """Известяване за унищожен таг.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        status = message[start_index + 3]

        if status == 0:
            print("Successfully killed tag")
        else:
            print("Failed to kill tag")

        return 0

    def notify_inventory_once(self, message, start_index):
        """Известяване за еднократна инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        if message[start_index + 1] > 3:
            # Успешно прочитане на таг
            print("Read tag data: ", end="")

            for i_index in range(message[start_index + 3] & 0xFF):
                print(f"{message[start_index + 4 + i_index]:02X} ", end="")

            print()
        else:
            print("Failed to identify tag EPC area")

        return 0

    def notify_query_muti_param(self, message, start_index):
        """Известяване за заявени множество параметри.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print("Query parameter value: ", end="")

        for i_index in range(message[start_index + 3]):
            print(f"{message[start_index + 6 + i_index]:02X} ", end="")

        print()
        return 0

    def notify_set_muti_param(self, message, start_index):
        """Известяване за зададени множество параметри.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        if message[start_index + 3] == 0x00:
            print("Successfully set parameters")
        else:
            print("Failed to set parameters")

        return 0

    def notify_start_inventory(self, message, start_index):
        """Известяване за начало на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        print("Started reading tags")
        return 0