#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на M RFID четец.
Еквивалент на MRfidReader.java
"""

from rfid.reader.rfid_reader import RfidReader
from rfid.app_notify_impl.m_rfid_reader_notify_impl import MRfidReaderNotifyImpl


class MRfidReader(RfidReader):
    """Имплементация на M RFID четец."""

    # Константи за команди
    MREADER_CMD_RESET = 0x10
    MREADER_NOTIFY_TAG = 0x80

    def __init__(self):
        """Инициализация на M RFID четец."""
        super().__init__()
        self.reader_id = bytearray(2)
        self.reader_id[0] = 0
        self.reader_id[1] = 0

    def _calculate_checksum(self, message, start_pos, length):
        """Изчислява контролна сума.

        Args:
            message (bytearray): Съобщение
            start_pos (int): Начална позиция
            length (int): Дължина

        Returns:
            int: Контролна сума
        """
        checksum = 0

        for i in range(length):
            checksum += self.get_unsigned_byte(message[start_pos + i])

        checksum = (~checksum + 1) & 0xFF
        return checksum

    def _fill_length_and_checksum(self):
        """Запълва дължината и контролната сума."""
        indeed_len = self.send_index + 1 - 6
        self.send_msg_buff[6] = (indeed_len >> 8) & 0xFF
        self.send_msg_buff[7] = indeed_len & 0xFF
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1

    def build_message_header(self, command_code):
        """Изгражда заглавие на съобщение.

        Args:
            command_code (int): Код на командата
        """
        self.send_index = 0
        self.send_msg_buff[self.send_index] = ord('R')
        self.send_index += 1
        self.send_msg_buff[self.send_index] = ord('F')
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0
        self.send_index += 1
        self.send_msg_buff[self.send_index] = self.reader_id[0]
        self.send_index += 1
        self.send_msg_buff[self.send_index] = self.reader_id[1]
        self.send_index += 1
        self.send_msg_buff[self.send_index] = command_code
        self.send_index += 1
        # Запълване на дължината със 0
        self.send_msg_buff[self.send_index] = 0
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0
        self.send_index += 1

    def inventory(self):
        """Започва инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        if self.transport is None:
            return -1

        self.build_message_header(0x21)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def inventory_once(self):
        """Започва еднократна инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        if self.transport is None:
            return -1

        self.build_message_header(0x22)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def stop(self):
        """Спира инвентаризацията.

        Returns:
            int: Резултат от операцията
        """
        if self.transport is None:
            return -1

        self.build_message_header(0x23)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def reset(self):
        """Ресетиране на четеца.

        Returns:
            int: Резултат от операцията
        """
        if self.transport is None:
            return -1

        self.build_message_header(0x10)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def read_tag_block(self, membank, addr, length):
        """Прочита блок данни от таг.

        Args:
            membank (int): Област на памет
            addr (int): Адрес
            length (int): Дължина

        Returns:
            int: Резултат от операцията
        """
        return 0

    def write_tag_block(self, membank, addr, length, written_data, write_start_index):
        """Записва блок данни в таг.

        Args:
            membank (int): Област на памет
            addr (int): Адрес
            length (int): Дължина
            written_data (bytearray): Данни за запис
            write_start_index (int): Начален индекс за запис

        Returns:
            int: Резултат от операцията
        """
        return 0

    def lock_tag(self, lock_type):
        """Заключва таг.

        Args:
            lock_type (int): Тип на заключване

        Returns:
            int: Резултат от операцията
        """
        return 0

    def kill_tag(self):
        """Унищожава таг.

        Returns:
            int: Резултат от операцията
        """
        return 0

    def handle_message(self):
        """Обработва съобщение."""
        message = self.recv_msg_buff
        buff_pos = 0
        param_len = 0

        while buff_pos <= self.recv_msg_len - 9:
            if message[buff_pos] != ord('R') or message[buff_pos + 1] != ord('F'):
                buff_pos += 1
                continue

            param_len = self.get_unsigned_byte(message[buff_pos + 6])
            param_len = param_len << 8
            param_len += self.get_unsigned_byte(message[buff_pos + 7])

            if param_len > 255:
                buff_pos += 1
                continue

            checksum = message[buff_pos + param_len + 8]
            calculated_checksum = self._calculate_checksum(message, buff_pos, param_len + 8)

            if calculated_checksum == checksum:
                # Валидация на данните и обработка на съобщението
                self.notify_message_to_app(message, buff_pos)
                # Преминаване към следващата команда
                buff_pos = buff_pos + param_len + 9
            else:
                buff_pos += 1

    def notify_message_to_app(self, message, start_index):
        """Известява приложението за съобщение.

        Args:
            message (bytearray): Съобщение
            start_index (int): Начален индекс
        """
        app_notify = self.get_app_notify()

        if not app_notify or not isinstance(app_notify, MRfidReaderNotifyImpl):
            return

        if message[start_index + 2] == 1:
            if message[start_index + 5] == self.MREADER_CMD_RESET:
                app_notify.notify_reset(message, start_index)
        elif message[start_index + 2] == 2:
            if message[start_index + 5] == self.MREADER_NOTIFY_TAG:
                app_notify.notify_recv_tags(message, start_index)

    def relay_operation(self, relay_no, operation_type, op_time):
        """Операция с релета.

        Args:
            relay_no (int): Номер на релето
            operation_type (int): Тип на операцията
            op_time (int): Време за операцията

        Returns:
            int: Резултат от операцията
        """
        index = 0

        if self.transport is None:
            return -1

        self.build_message_header(0x4C)
        # Добавяне на TLV
        self.send_msg_buff[self.send_index] = 0x27
        self.send_index += 1
        index = self.send_index
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1

        if (relay_no & 0x01) != 0:
            self.send_msg_buff[self.send_index] = 1
            self.send_index += 1
            self.send_msg_buff[self.send_index] = operation_type
            self.send_index += 1
            self.send_msg_buff[self.send_index] = op_time
            self.send_index += 1

        if (relay_no & 0x02) != 0:
            self.send_msg_buff[self.send_index] = 2
            self.send_index += 1
            self.send_msg_buff[self.send_index] = operation_type
            self.send_index += 1
            self.send_msg_buff[self.send_index] = op_time
            self.send_index += 1

        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0