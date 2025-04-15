#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Пример за тестване на RFID четец през TCP връзка.
Еквивалент на RfidInventoryTest.java
"""

import time
import sys


from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.app_notify_impl.m_rfid_reader_notify_impl import MRfidReaderNotifyImpl
from rfid.reader.general_reader import GeneralReader
from rfid.reader.m_rfid_reader import MRfidReader
from rfid.reader.rfid_reader import RfidReader


def main():
    """Основна функция."""
    print("This is an example for general reader test with TCP")

    # Инициализация на мениджъра на транспортните нишки
    TransportThreadManager.initialize_transport_manager()

    # Избор на тип четец
    # reader = GeneralReader()
    reader = MRfidReader()

    # Свързване към четеца
    result = reader.connect_physical_interface(
        "192.168.1.65",  # IP адрес на четеца
        5060,  # Порт на четеца
        None,  # Локален IP адрес
        0,  # Локален порт
        RfidReader.CONNECT_TYPE_NET_TCP_CLIENT  # Тип на връзката
    )

    if result == 0:
        print("Connect to the reader is OK, and the app will receive data.")
    else:
        print(f"Failed to connect to the reader. Error code: {result}")
        return

    # Задаване на обработчик на съобщения
    # reader.set_app_notify(GeneralReaderNotifyImpl())
    reader.set_app_notify(MRfidReaderNotifyImpl())

    # Добавяне на четеца към мениджъра
    manager = TransportThreadManager.get_instance()
    manager.add_rfid_reader(reader)

    # Избор на режим на тестване
    is_inventory_test = False

    if is_inventory_test:
        # Ресетиране на четеца, което също така стартира инвентаризация
        reader.reset()

        try:
            while True:
                time.sleep(3)
        except KeyboardInterrupt:
            print("Stopping...")
            reader.stop()
            manager.stop()
    else:
        # Спиране на инвентаризацията
        reader.stop()

        try:
            while True:
                time.sleep(3)

                # Коментирайте/декоментирайте функциите, които искате да тествате

                # Спиране на инвентаризацията
                # reader.stop()

                # Запис на данни в таг
                # written_data = bytearray([i for i in range(4)])
                # reader.write_tag_block(GeneralReader.RFID_TAG_MEMBANK_USER, 0, 2, written_data, 0)

                # Четене на данни от таг
                # reader.read_tag_block(GeneralReader.RFID_TAG_MEMBANK_USER, 0, 2)

                # Заключване на EPC област
                # reader.lock_tag(GeneralReader.RFID_LOCK_EPC)

                # Унищожаване на таг
                # reader.kill_tag()

                # Управление на релета
                # reader.relay_operation(1, 1, 10)  # Включване на реле 1 за 10 секунди
                # reader.relay_operation(2, 1, 10)  # Включване на реле 2 за 10 секунди
                # reader.relay_operation(1, 0, 0)   # Изключване на реле 1
                # reader.relay_operation(2, 0, 0)   # Изключване на реле 2
                # reader.relay_operation(3, 0, 0)   # Изключване на реле 1 и 2
                # reader.relay_operation(3, 1, 10)  # Включване на реле 1 и 2 за 10 секунди

                # Еднократна инвентаризация
                reader.inventory_once()

        except KeyboardInterrupt:
            print("Stopping...")
            reader.stop()
            manager.stop()


if __name__ == "__main__":
    main()