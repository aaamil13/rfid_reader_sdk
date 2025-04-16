"""
UHF Protocol Notification Frames

This module implements the notification frames functionality in the UHF RFID protocol.
Notification frames are asynchronous messages sent from the reader to the host,
typically containing information about detected tags.
"""

import enum
import logging
from typing import List, Dict, Any, Tuple, Optional, Union, ByteString

from .protocol_base import UHFFrame, UHFFrameType, TLVBase, TLVType

logger = logging.getLogger(__name__)


class NotificationType(enum.IntEnum):
    """Types of notification frames"""
    TAGS_UPLOADED = 0x80  # Tags have been uploaded from reader
    INVENTORY_STATE_CHANGED = 0x81  # Inventory state has changed
    READER_EXCEPTION = 0x82  # Reader encountered an exception
    BATTERY_STATUS = 0x83  # Battery status notification
    BUTTON_TRIGGER = 0x84  # Button was triggered
    TEMPERATURE_ALERT = 0x85  # Temperature alert notification

    @classmethod
    def get_name(cls, code: int) -> str:
        """Get the name of a notification type"""
        try:
            return cls(code).name
        except ValueError:
            return f"UNKNOWN_NOTIFICATION(0x{code:02X})"


class NotificationFrame(UHFFrame):
    """
    Notification Frame implementation

    Notification frames are asynchronous messages sent from the reader to the host.
    They typically contain information about detected tags or reader status changes.
    """

    def __init__(self,
                 notification_type: Union[NotificationType, int],
                 address: int = 0,
                 payload: Optional[bytes] = None):
        """
        Initialize a notification frame

        Args:
            notification_type: Type of notification
            address: Device address
            payload: Frame payload (TLV data)
        """
        # Convert enum to int if needed
        if isinstance(notification_type, NotificationType):
            notification_type = notification_type.value

        super().__init__(UHFFrameType.NOTIFICATION, address, notification_type, payload)

    @property
    def notification_type(self) -> int:
        """Get the notification type"""
        return self.command_code

    @notification_type.setter
    def notification_type(self, ntype: Union[NotificationType, int]):
        """Set the notification type"""
        if isinstance(ntype, NotificationType):
            self.command_code = ntype.value
        else:
            self.command_code = ntype

    @classmethod
    def from_raw_frame(cls, address: int, notification_type: int, payload: bytes) -> 'NotificationFrame':
        """
        Create a notification frame from raw frame data

        Args:
            address: Device address
            notification_type: Notification type code
            payload: Raw payload data

        Returns:
            NotificationFrame: Created notification frame
        """
        return cls(notification_type, address, payload)

    def get_tags(self) -> List['TagTLV']:
        """
        Get tags from the notification frame

        Returns:
            list: List of TagTLV objects
        """
        from .tlv_structures import TagTLV

        tags = []

        # Process only tag upload notifications
        if self.notification_type != NotificationType.TAGS_UPLOADED:
            return tags

        # Extract Tag TLVs
        for tlv in self.get_tlvs():
            if tlv.type == TLVType.TAG:
                tags.append(tlv)

        return tags

    def __str__(self) -> str:
        """String representation of the notification frame"""
        notification_name = NotificationType.get_name(self.notification_type)

        result = [
            f"UHF Notification Frame: {notification_name}",
            f"  Address: 0x{self.address:04X}",
            f"  Payload: {self.payload_length} bytes"
        ]

        # For tag upload notifications, show tag details
        if self.notification_type == NotificationType.TAGS_UPLOADED:
            tags = self.get_tags()
            if tags:
                result.append(f"  Tags: {len(tags)}")
                for tag in tags:
                    result.append(f"    {tag}")
            else:
                result.append("  Tags: None")

        # For other notifications, show TLVs
        else:
            tlvs = self.get_tlvs()
            if tlvs:
                result.append("  TLVs:")
                for tlv in tlvs:
                    result.append(f"    {tlv}")

        return "\n".join(result)