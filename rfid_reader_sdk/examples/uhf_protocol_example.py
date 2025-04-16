#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UHF Protocol Usage Example

This file demonstrates how to use the UHF Protocol implementation to interact with RFID readers.
"""

import binascii
import logging
import time
from typing import List, Optional

# UHF Protocol imports
from rfid_reader_sdk.rfid.reader.uhf_protocol import (
    UHFFrame, UHFFrameType, TLVBase,
    NotificationFrame, NotificationType,
    TagTLV, EPCTLV, RSSITLV, TimeTLV, TIDTLV, TLVType,
    StatusTLV, StatusCode, StatusError,
    CommandFrame, CommandType, CommandFactory
)

from rfid_reader_sdk.rfid.reader.uhf_protocol.commands import ResponseFrame

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("UHF_EXAMPLE")


class UHFReaderSimulator:
    """
    UHF Reader Simulator

    This class simulates a UHF RFID reader for demonstration purposes.
    It can generate mock responses and notification frames.
    """

    def __init__(self, address: int = 0x0001):
        """
        Initialize the simulator

        Args:
            address: Device address
        """
        self.address = address
        self.is_inventorying = False
        self.simulated_tags = [
            ("E2801160600002083B12C001", -65),  # (EPC, RSSI)
            ("E28011223344556677889900", -72),
            ("E280112000000000ABCD0123", -58)
        ]

    def send_command(self, command: CommandFrame) -> ResponseFrame:
        """
        Send a command to the simulated reader

        Args:
            command: Command frame

        Returns:
            ResponseFrame: Simulated response
        """
        logger.info(f"Sending command: {command}")

        # Simulate processing delay
        time.sleep(0.1)

        # Generate appropriate response based on command type
        if command.command_type == CommandType.RESET:
            return self._handle_reset(command)
        elif command.command_type == CommandType.VERSION:
            return self._handle_version(command)
        elif command.command_type == CommandType.START_INVENTORY:
            return self._handle_start_inventory(command)
        elif command.command_type == CommandType.STOP_INVENTORY:
            return self._handle_stop_inventory(command)
        elif command.command_type == CommandType.INVENTORY_ONCE:
            return self._handle_inventory_once(command)
        elif