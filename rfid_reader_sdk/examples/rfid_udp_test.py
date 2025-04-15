#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Пример за тестване на RFID четец през UDP връзка.
Еквивалент на RfidUdpTest.java
"""

import time
import sys

from rfid.transport.transport_thread_manager import TransportThreadManager
from rfid.app_notify_impl.general_reader_notify_impl import GeneralReaderNotifyImpl
from rfid.reader.general_reader import GeneralReader
from rfid.reader.rfid_reader import RfidReader


def main():
    """Основна функция."""
    print("This sample is for R2000 with UDP.")

    # Инициализация на мениджъра на транспортните нишки
    TransportThreadManager.initialize_transport_manager()

    # Създаване на четец
    reader = GeneralReader()

    # Свързване към четеца през UDP
    # IP на четеца е 192.168.1.65, локален порт 12345
    result = reader.connect_physical_interface(
        "192.168.1.65",  # IP адрес на четеца
        12345,  # Порт на четеца
        "127.0.0.1",  # Локален IP адрес
        12345,  # Локален порт
        RfidReader.CONNECT_TYPE_NET_UDP  # Тип на връзката
    )

    if result == 0:
        print("Connect to the reader is OK.")
    else:
        print(f"Failed to connect to the reader. Error code: {result}")
        return

    # Задаване на обработчик на съобщения
    reader.set_app_notify(GeneralReaderNotifyImpl())

    # Добавяне на четеца към мениджъра
    manager = TransportThreadManager.get_instance()
    manager.add_rfid_reader(reader)

    print("The application start receive data from reader.")

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

                # Еднократна инвентаризация
                # reader.inventory_once()

        except KeyboardInterrupt:
            print("Stopping...")
            reader.stop()
            manager.stop()


if __name__ == "__main__":
    main()