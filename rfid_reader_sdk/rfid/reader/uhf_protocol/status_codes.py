"""
UHF Protocol Status Codes

This module defines the status codes used in the UHF RFID protocol responses.
It includes a comprehensive set of status code definitions and error handling.
"""

import enum
import logging
from typing import Optional, Dict, Any, Union

from .protocol_base import TLVBase, TLVType

logger = logging.getLogger(__name__)

class StatusCode(enum.IntEnum):
    """Status codes defined in UHF protocol"""
    SUCCESS = 0x00                 # Operation successful
    GENERAL_ERROR = 0x01           # General error
    MEMORY_OVERRUN = 0x02          # Memory overrun
    MEMORY_LOCKED = 0x03           # Memory locked
    AUTH_FAIL = 0x04               # Authentication failed
    NO_TAG = 0x0B                  # No tag responding
    RF_TIMEOUT = 0x0C              # RF communication timeout
    PARAMETER_UNSUPPORTED = 0x14   # Parameter unsupported
    PARAMETER_LENGTH_ERROR = 0x15  # Parameter length error
    PARAMETER_CONTEXT_ERROR = 0x16 # Parameter context error
    UNSUPPORTED_COMMAND = 0x17     # Unsupported command
    ADDRESS_ERROR = 0x18           # Address error
    CHECKSUM_ERROR = 0x20          # Checksum error
    UNSUPPORTED_TLV_TYPE = 0x21    # Unsupported TLV Type
    FLASH_ERROR = 0x22             # Flash error
    INTERNAL_ERROR = 0xFF          # Internal error

    @classmethod
    def get_description(cls, code: int) -> str:
        """Get the description of a status code"""
        try:
            return cls(code).name.replace('_', ' ').title()
        except ValueError:
            return f"Unknown Status (0x{code:02X})"

    @classmethod
    def is_success(cls, code: int) -> bool:
        """Check if the status code indicates success"""
        return code == cls.SUCCESS


class StatusError(Exception):
    """Exception for UHF protocol status errors"""

    def __init__(self, status_code: int, message: Optional[str] = None, language: Optional[str] = None):
        """
        Initialize status error

        Args:
            status_code: Status code
            message: Optional additional message
            language: Optional language code for error message
        """
        self.status_code = status_code

        # Import here to avoid circular imports
        from .status_translations import get_error_message

        # Get translated description
        description = get_error_message(status_code, language)

        if message:
            super().__init__(f"{description} (0x{status_code:02X}): {message}")
        else:
            super().__init__(f"{description} (0x{status_code:02X})")


class StatusTLV(TLVBase):
    """Status TLV"""

    def __init__(self, status_code: Union[int, bytes]):
        """
        Initialize Status TLV

        Args:
            status_code: Status code or raw bytes
        """
        if isinstance(status_code, int):
            value = bytes([status_code])
        else:
            value = status_code

        super().__init__(TLVType.STATUS, value)

    @property
    def status_code(self) -> int:
        """Get the status code"""
        if self._value:
            return self._value[0]
        return 0xFF  # Default to internal error

    @status_code.setter
    def status_code(self, code: int):
        """Set the status code"""
        self._value = bytes([code & 0xFF])

    @property
    def is_success(self) -> bool:
        """Check if the status indicates success"""
        return StatusCode.is_success(self.status_code)

    @property
    def description(self) -> str:
        """Get the status description"""
        return StatusCode.get_description(self.status_code)

    def get_error_message(self, language: Optional[str] = None) -> str:
        """
        Get translated error message

        Args:
            language: Language code (or None for default)

        Returns:
            str: Translated error message
        """
        # Import here to avoid circular imports
        from .status_translations import get_error_message
        return get_error_message(self.status_code, language)

    def raise_for_error(self, language: Optional[str] = None):
        """
        Raise an exception if the status indicates an error

        Args:
            language: Optional language code for error message

        Raises:
            StatusError: If the status is not success
        """
        if not self.is_success:
            raise StatusError(self.status_code, language=language)

    @classmethod
    def from_value(cls, value: bytes) -> 'StatusTLV':
        """Create Status TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the Status TLV"""
        return f"Status: {self.description} (0x{self.status_code:02X})"


def get_error_description(status_code: int, language: Optional[str] = None) -> str:
    """
    Get translated error description for a status code

    Args:
        status_code: Status code
        language: Optional language code

    Returns:
        str: Translated error description
    """
    # Import here to avoid circular imports
    from .status_translations import get_error_message
    return get_error_message(status_code, language)