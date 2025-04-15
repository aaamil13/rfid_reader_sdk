#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на AppNotify за M RFID четец.
Еквивалент на MRfidReaderNotifyImpl.java
"""

from rfid.reader.app_notify import AppNotify


class MRfidReaderNotifyImpl(AppNotify):
    """Имплементация на AppNotify за M RFID четец."""

    # Константи за TLV атрибути
    TLV_ONE_TAG_DATA = 0x50
    TLV_EPC = 0x01

    def get_tlv_position(self, message, start_index, param_len, tlv_type):
        """Търси TLV в съобщението.

        Args:
            message (bytes): Съобщение
            start_index (int): Начален индекс
            param_len (int): Дължина на параметрите
            tlv_type (int): Тип на TLV

        Returns:
            int: Позиция на TLV или -1 ако не е намерен
        """
        pos = -1
        index = 0

        while index < param_len:
            if message[start_index] == tlv_type:
                pos = start_index
                break
            else:
                index = index + message[start_index + 1] + 2
                start_index = start_index + message[start_index + 1] + 2

        return pos

    def notify_recv_tags(self, message, start_index):
        """Известяване за получени RFID тагове.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        start_tlv_pos = start_index + 8
        param_len = 0
        tag_tlv_pos = 0
        epc_tlv = 0

        param_len = message[start_index + 6] & 0xFF
        param_len = param_len << 8
        param_len = param_len | (message[start_index + 7] & 0xFF)

        tag_tlv_pos = self.get_tlv_position(message, start_tlv_pos, param_len, self.TLV_ONE_TAG_DATA)
        if tag_tlv_pos < 0:
            # Няма данни за таг
            return -1

        # Получава начална позиция на под-TLV
        start_tlv_pos = tag_tlv_pos + 2
        param_len = message[start_tlv_pos + 1]
        epc_tlv = self.get_tlv_position(message, start_tlv_pos, param_len, self.TLV_EPC)

        if epc_tlv < 0:
            # Няма EPC данни
            return -2

        print(f"Uploaded tag device ID: {hex(message[start_index + 3] & 0xFF)} "
              f"{hex(message[start_index + 4] & 0xFF)}")
        print("Read tag data: ", end="")

        for i_index in range(message[epc_tlv + 1] & 0xFF):
            print(f"{message[epc_tlv + 2 + i_index]:02X} ", end="")

        print()
        return 0

    def notify_start_inventory(self, message, start_index):
        """Известяване за начало на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_stop_inventory(self, message, start_index):
        """Известяване за край на инвентаризация.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
        return 0

    def notify_reset(self, message, start_index):
        """Известяване за ресетиране на четеца.

        Args:
            message (bytes): Съобщение от четеца
            start_index (int): Начален индекс в съобщението

        Returns:
            int: Резултат от операцията
        """
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