#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Имплементация на R2000 RFID четец.
Еквивалент на R2000Reader.java
"""

from rfid.reader.rfid_reader import RfidReader


class R2000Reader(RfidReader):
    """Имплементация на R2000 RFID четец."""

    # Константи за флагове на команди
    START_RSP_FLAG = 0xBB
    START_CMD_FLAG = 0xAA

    # Константи за команди
    RFID_CMD_TAG_NOTIFY = 0x10
    RFID_CMD_STOP_INVETORY = 0x31
    RFID_CMD_START_INVENTORY = 0x32
    RFID_CMD_RESET_DEVICE = 0x65

    def __init__(self):
        """Инициализация на R2000 RFID четец."""
        super().__init__()
        self.reader_id = bytearray(2)
        self.reader_id[0] = 0
        self.reader_id[1] = 0

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
        self.send_msg_buff[self.send_index] = 0
        self.send_index += 1
        self.send_msg_buff[self.send_index] = self.reader_id[0]
        self.send_index += 1
        self.send_msg_buff[self.send_index] = self.reader_id[1]
        self.send_index += 1
        self.send_msg_buff[self.send_index] = command_code
        self.send_index += 1

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
        self.send_msg_buff[1] = 0
        self.send_msg_buff[2] = (self.send_index - 2) & 0xFF
        self.send_msg_buff[self.send_index] = self._calculate_checksum(self.send_msg_buff, 0, self.send_index)
        self.send_index += 1

    def inventory(self):
        """Започва инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_START_INVENTORY)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def inventory_once(self):
        """Започва еднократна инвентаризация на тагове.

        Returns:
            int: Резултат от операцията
        """
        print("Now R2000 does not support this function.")
        return -1

    def stop(self):
        """Спира инвентаризацията.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_STOP_INVETORY)
        self._fill_length_and_checksum()
        self.transport.send_data(self.send_msg_buff, self.send_index)
        return 0

    def reset(self):
        """Ресетиране на четеца.

        Returns:
            int: Резултат от операцията
        """
        self.build_message_header(self.RFID_CMD_RESET_DEVICE)
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
        print("Now R2000 does not support this function.")
        return -1

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
        print("Now R2000 does not support this function.")
        return -1

    def lock_tag(self, lock_type):
        """Заключва таг.

        Args:
            lock_type (int): Тип на заключване

        Returns:
            int: Резултат от операцията
        """
        print("Now R2000 does not support this function.")
        return -1

    def kill_tag(self):
        """Унищожава таг.

        Returns:
            int: Резултат от операцията
        """
        print("Now R2000 does not support this function.")
        return -1

    def handle_recv(self):
        """Обработва получени данни.

        Returns:
            int: Резултат от операцията
        """
        self.recv_msg_len = self.transport.read_data(self.recv_msg_buff)
        self.handle_message()
        return 0

    def handle_message(self):
        """Обработва съобщение."""
        message = self.recv_msg_buff
        buff_pos = 0
        rsp_len = 0

        while buff_pos <= self.recv_msg_len - 7:
            if message[buff_pos] != self.START_RSP_FLAG:
                buff_pos += 1
                continue

            rsp_len = self.get_unsigned_byte(message[buff_pos + 1])
            rsp_len = rsp_len << 8
            rsp_len += self.get_unsigned_byte(message[buff_pos + 2])

            if rsp_len > 255:
                buff_pos += 1
                continue

            checksum = message[buff_pos + rsp_len + 2]
            calculated_checksum = self._calculate_checksum(message, buff_pos, rsp_len + 2)

            if calculated_checksum == checksum:
                # Валидация на данните и обработка на съобщението
                self.notify_message_to_app(message, buff_pos)
                # Преминаване към следващата команда
                buff_pos = buff_pos + rsp_len + 3
            else:
                buff_pos += 1

    def notify_message_to_app(self, message, start_index):
        """Известява приложението за съобщение.

        Args:
            message (bytearray): Съобщение
            start_index (int): Начален индекс
        """
        app_notify = self.get_app_notify()

        if app_notify is None:
            return

        command = message[start_index + 5]

        if command == self.RFID_CMD_STOP_INVETORY:
            app_notify.notify_stop_inventory(message, start_index)
        elif command == self.RFID_CMD_RESET_DEVICE:
            app_notify.notify_reset(message, start_index)
        elif command == self.RFID_CMD_START_INVENTORY:
            app_notify.notify_start_inventory(message, start_index)
        elif command == self.RFID_CMD_TAG_NOTIFY:
            app_notify.notify_recv_tags(message, start_index)

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