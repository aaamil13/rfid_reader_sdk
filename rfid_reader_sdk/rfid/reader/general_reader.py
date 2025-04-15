#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на стандартен RFID четец.
Еквивалент на GeneralReader.java
"""

from rfid.reader.rfid_reader import RfidReader
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl


class GeneralReader(RfidReader):
    """Имплементация на стандартен RFID четец."""

    # Константи за флагове на команди
    START_CMD_FLAG = 0xA0
    START_RSP_FLAG = 0xE4
    START_NOTIFY_FLAG = 0xE0

    # Константи за команди
    CMD_NOTIFY_TAG = 0xFF
    RFID_CMD_QUERY_SINGLE_PARAM = 0x61
    RFID_CMD_SET_MUTI_PARAM = 0x62
    RFID_CMD_QUERY_MUTI_PARAM = 0x63
    RFID_CMD_RESET_DEVICE = 0x65
    RFID_CMD_QUERY_VERSION = 0x6A
    RFID_CMD_STOP_INVETORY = 0xFE
    RFID_CMD_READ_TAG_BLOCK = 0x80
    RFID_CMD_WRITE_TAG_BLOCK = 0x81
    RFID_CMD_IDENTIFY_TAG = 0x82
    RFID_CMD_ENCRYPT_TAG = 0x83
    RFID_CMD_KILL_TAG = 0x86
    RFID_CMD_LOCK_TAG = 0x87

    # Константи за области на таг
    RFID_TAG_MEMBANK_RESERVED = 0
    RFID_TAG_MEMBANK_USER = 3
    RFID_TAG_MEMBANK_EPC = 1
    RFID_TAG_MEMBANK_TID = 2

    # Константи за заключване
    RFID_LOCK_USER = 0
    RFID_LOCK_TID = 1
    RFID_LOCK_EPC = 2
    RFID_LOCK_ACCESS_PASSWORD = 3
    RFID_LOCK_KILL_PASSWORD = 4
    RFID_LOCK_ALL = 5

    def __init__(self):
        """Инициализация на стандартен RFID четец."""
        super().__init__()

    def build_message_header(self, command_code):
        """Изгражда заглавие на съобщение.

        Args:
            command_code (int): Код на командата
        """
        self.send_index = 0
        self.send_msg_buff[self.send_index] = self.START_CMD_FLAG
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0
        self.send_index += 1
        self.send_msg_buff[self.send_index] = command_code
        self.send_index += 1

    def inventory(self):
        """Започва инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        return 0

    def inventory_once(self):
        """Започва еднократна инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_IDENTIFY_TAG)
        self.send_msg_buff[self.send_index] = 0x04
        self.send_index += 1
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def stop(self):
        """Спира инвентаризацията.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_STOP_INVETORY)
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def reset(self):
        """Ресетиране на четеца.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_RESET_DEVICE)
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def handle_message(self):
        """Обработва съобщение."""
        message = self.recv_msg_buff
        buff_pos = 0
        rsp_len = 0

        while buff_pos <= self.recv_msg_len - 4:
            if message[buff_pos] != self.START_RSP_FLAG and message[buff_pos] != self.START_NOTIFY_FLAG:
                buff_pos += 1
                continue

            rsp_len = self.get_unsigned_byte(message[buff_pos + 1])
            checksum = message[buff_pos + rsp_len + 1]
            calculated_checksum = self._calculate_checksum(message, buff_pos, rsp_len + 1)

            if calculated_checksum == checksum:
                # Валидация на данните и обработка на съобщението
                self.notify_message_to_app(message, buff_pos)
                # Преминаване към следващата команда
                buff_pos = buff_pos + rsp_len + 2
            else:
                buff_pos += 1

    def handle_recv(self):
        """Обработва получени данни.

        Returns:
            int: Резултат от операцията
        """
        self.recv_msg_len = self.transport.read_data(self.recv_msg_buff)
        self.handle_message()
        return 0

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

    def notify_message_to_app(self, message, start_index):
        """Известява приложението за съобщение.

        Args:
            message (bytearray): Съобщение
            start_index (int): Начален индекс
        """
        app_notify = self.get_app_notify()

        if not app_notify or not isinstance(app_notify, GeneralReaderNotifyImpl):
            return

        command = message[start_index + 2]

        if command == self.CMD_NOTIFY_TAG:
            app_notify.notify_recv_tags(message, start_index)
        elif command == self.RFID_CMD_STOP_INVETORY:
            app_notify.notify_stop_inventory(message, start_index)
        elif command == self.RFID_CMD_RESET_DEVICE:
            app_notify.notify_reset(message, start_index)
        elif command == self.RFID_CMD_READ_TAG_BLOCK:
            app_notify.notify_read_tag_block(message, start_index)
        elif command == self.RFID_CMD_WRITE_TAG_BLOCK:
            app_notify.notify_write_tag_block(message, start_index)
        elif command == self.RFID_CMD_LOCK_TAG:
            app_notify.notify_lock_tag(message, start_index)
        elif command == self.RFID_CMD_KILL_TAG:
            app_notify.notify_kill_tag(message, start_index)
        elif command == self.RFID_CMD_IDENTIFY_TAG:
            app_notify.notify_inventory_once(message, start_index)
        elif command == self.RFID_CMD_QUERY_SINGLE_PARAM:
            app_notify.notify_query_muti_param(message, start_index)
        elif command == self.RFID_CMD_SET_MUTI_PARAM:
            app_notify.notify_set_muti_param(message, start_index)

    def read_tag_block(self, membank, addr, length):
        """Прочита блок данни от таг.

        Args:
            membank (int): Област на памет
            addr (int): Адрес
            length (int): Дължина

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_READ_TAG_BLOCK)
        self.send_msg_buff[self.send_index] = 0x04
        self.send_index += 1
        self.send_msg_buff[self.send_index] = membank
        self.send_index += 1
        self.send_msg_buff[self.send_index] = addr
        self.send_index += 1
        self.send_msg_buff[self.send_index] = length
        self.send_index += 1
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
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
        self.build_message_header(self.RFID_CMD_WRITE_TAG_BLOCK)
        self.send_msg_buff[self.send_index] = 0x04
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x01
        self.send_index += 1
        self.send_msg_buff[self.send_index] = membank
        self.send_index += 1
        self.send_msg_buff[self.send_index] = addr
        self.send_index += 1
        self.send_msg_buff[self.send_index] = length
        self.send_index += 1

        # Запълване на данните за запис
        for i in range(length * 2):
            self.send_msg_buff[self.send_index] = written_data[write_start_index + i]
            self.send_index += 1

        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def lock_tag(self, lock_type):
        """Заключва таг.

        Args:
            lock_type (int): Тип на заключване

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_LOCK_TAG)
        self.send_msg_buff[self.send_index] = 0x04
        self.send_index += 1
        self.send_msg_buff[self.send_index] = lock_type
        self.send_index += 1
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def kill_tag(self):
        """Унищожава таг.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_KILL_TAG)
        self.send_msg_buff[self.send_index] = 0x04
        self.send_index += 1
        # Парола по подразбиране е 0
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def query_parameter(self, mem_address, query_len):
        """Заявява параметри на четеца.

        Args:
            mem_address (int): Адрес на паметта
            query_len (int): Дължина на заявката

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_QUERY_MUTI_PARAM)
        self.send_msg_buff[self.send_index] = query_len
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[self.send_index] = mem_address
        self.send_index += 1
        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def set_muti_parameter(self, mem_address, param_len, params):
        """Задава множество параметри на четеца.

        Args:
            mem_address (int): Адрес на паметта
            param_len (int): Дължина на параметрите
            params (list): Списък с параметри

        Returns:
            int: Резултат от операцията
        """
        if params is None or param_len > len(params):
            return -1

        self.build_message_header(self.RFID_CMD_SET_MUTI_PARAM)
        self.send_msg_buff[self.send_index] = param_len
        self.send_index += 1
        self.send_msg_buff[self.send_index] = 0x00
        self.send_index += 1
        self.send_msg_buff[self.send_index] = mem_address
        self.send_index += 1

        for param_index in range(param_len):
            self.send_msg_buff[self.send_index] = params[param_index]
            self.send_index += 1

        self.send_msg_buff[1] = self.send_index - 1
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def relay_operation(self, relay_no, operation_type, time):
        """Операция с релета.

        Args:
            relay_no (int): Номер на релето
            operation_type (int): Тип на операцията
            time (int): Време за операцията

        Returns:
            int: Резултат от операцията
        """
        return 0