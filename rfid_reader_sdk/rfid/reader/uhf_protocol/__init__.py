"""
UHF RFID Protocol Implementation Package

This package implements the UHF RFID protocol based on version 4.0.1 (2019-07-02).
It extends the basic rfid_reader_sdk with full support for notification frames,
TLV structures, and comprehensive status codes handling.
"""

__version__ = "1.0.0"

# Import main components for easy access
from .protocol_base import UHFFrame, UHFFrameType, TLVBase
from .notification_frames import NotificationFrame, NotificationType
from .tlv_structures import (
    TagTLV,
    EPCTLV,
    RSSITLV,
    TimeTLV,
    TIDTLV,
    DeviceTypeTLV,
    TLVType
)
from .status_codes import StatusTLV, StatusCode, StatusError, get_error_description
from .status_translations import (
    Language,
    get_error_message,
    set_default_language,
    add_translation,
    StatusTranslator
)
from .commands import CommandFrame, CommandType, CommandFactory

# Export essential elements
__all__ = [
    'UHFFrame',
    'UHFFrameType',
    'TLVBase',
    'NotificationFrame',
    'NotificationType',
    'TagTLV',
    'EPCTLV',
    'RSSITLV',
    'TimeTLV',
    'TIDTLV',
    'DeviceTypeTLV',
    'TLVType',
    'StatusTLV',
    'StatusCode',
    'StatusError',
    'CommandFrame',
    'CommandType',
    'CommandFactory',
    'Language',
    'get_error_message',
    'get_error_description',
    'set_default_language',
    'add_translation',
    'StatusTranslator'
]