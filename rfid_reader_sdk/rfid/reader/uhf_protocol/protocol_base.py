"""
UHF Protocol Base Implementation

This module provides base classes and structures for the UHF RFID protocol.
It defines the fundamental components like UHF frames and TLV structures.
"""

import enum
import struct
import binascii
import logging
from typing import List, Dict, Any, Tuple, Optional, Union, ByteString

logger = logging.getLogger(__name__)


class UHFFrameType(enum.IntEnum):
    """UHF Frame Types"""
    COMMAND = 0x00  # Command frame from host to reader
    RESPONSE = 0x01  # Response frame from reader to host
    NOTIFICATION = 0x02  # Asynchronous notification from reader to host

    @classmethod
    def is_valid(cls, frame_type: int) -> bool:
        """Check if the frame type is valid"""
        return frame_type in [cls.COMMAND, cls.RESPONSE, cls.NOTIFICATION]


class TLVType(enum.IntEnum):
    """TLV Types in UHF Protocol"""
    EPC = 0x01  # EPC data
    ACCESS_PWD = 0x02  # Access password
    KILL_PWD = 0x03  # Kill password
    TID = 0x04  # TID data
    RSSI = 0x05  # Signal strength
    TIME = 0x06  # Timestamp
    STATUS = 0x07  # Status code
    VERSION = 0x20  # Version information
    DEVICE_TYPE = 0x21  # Device type
    TAG = 0x50  # Tag information (compound TLV)

    @classmethod
    def get_name(cls, tlv_type: int) -> str:
        """Get the name of a TLV type"""
        try:
            return cls(tlv_type).name
        except ValueError:
            return f"UNKNOWN_TYPE(0x{tlv_type:02X})"


class TLVBase:
    """Base class for TLV (Type-Length-Value) structures"""

    def __init__(self, tlv_type: int, value: Union[bytes, List[Any], None] = None):
        """
        Initialize a TLV structure

        Args:
            tlv_type: TLV type
            value: TLV value (raw bytes or a list of sub-TLVs)
        """
        self.type = tlv_type
        self._value = value or b''

    @property
    def length(self) -> int:
        """Get the length of the value"""
        if isinstance(self._value, bytes):
            return len(self._value)
        elif isinstance(self._value, list):
            # Calculate total length of all sub-TLVs
            return sum(len(tlv.to_bytes()) for tlv in self._value)
        return 0

    @property
    def value(self) -> Union[bytes, List[Any]]:
        """Get the TLV value"""
        return self._value

    @value.setter
    def value(self, new_value: Union[bytes, List[Any]]):
        """Set the TLV value"""
        self._value = new_value

    def to_bytes(self) -> bytes:
        """
        Convert TLV to bytes

        Returns:
            bytes: Encoded TLV
        """
        if isinstance(self._value, bytes):
            # Simple TLV with byte value
            return bytes([self.type, self.length]) + self._value
        elif isinstance(self._value, list):
            # Compound TLV with sub-TLVs
            sub_tlv_data = b''.join(tlv.to_bytes() for tlv in self._value)
            return bytes([self.type, len(sub_tlv_data)]) + sub_tlv_data

        # Empty value
        return bytes([self.type, 0])

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> Tuple[Any, int]:
        """
        Parse TLV from bytes

        Args:
            data: Raw data
            offset: Starting offset in data

        Returns:
            tuple: (TLV object, new offset)
        """
        if offset + 2 > len(data):
            raise ValueError("Insufficient data for TLV header")

        tlv_type = data[offset]
        tlv_length = data[offset + 1]

        if offset + 2 + tlv_length > len(data):
            raise ValueError(f"Insufficient data for TLV value (type=0x{tlv_type:02X}, length={tlv_length})")

        value = data[offset + 2:offset + 2 + tlv_length]

        # Create specific TLV type if registered
        from .tlv_structures import create_tlv_from_type
        tlv = create_tlv_from_type(tlv_type, value)

        return tlv, offset + 2 + tlv_length

    def __str__(self) -> str:
        """String representation of the TLV"""
        tlv_name = TLVType.get_name(self.type)
        if isinstance(self._value, bytes):
            hex_value = binascii.hexlify(self._value).decode('ascii')
            return f"{tlv_name}(0x{self.type:02X}) [Len={self.length}]: {hex_value}"
        elif isinstance(self._value, list):
            sub_values = "\n  ".join(str(tlv) for tlv in self._value)
            return f"{tlv_name}(0x{self.type:02X}) [Len={self.length}]:\n  {sub_values}"
        return f"{tlv_name}(0x{self.type:02X}) [Len=0]"


class UHFFrame:
    """Base class for UHF Protocol Frames"""

    # Frame header: 'R' 'F'
    HEADER = b'RF'

    def __init__(self,
                 frame_type: UHFFrameType,
                 address: int = 0,
                 command_code: int = 0,
                 payload: Optional[bytes] = None):
        """
        Initialize a UHF frame

        Args:
            frame_type: Frame type
            address: Device address
            command_code: Command or notification code
            payload: Frame payload (TLV data)
        """
        self.frame_type = frame_type
        self.address = address
        self.command_code = command_code
        self.payload = payload or b''

    @property
    def payload_length(self) -> int:
        """Get the length of the payload"""
        return len(self.payload)

    def calculate_checksum(self, data: bytes) -> int:
        """
        Calculate checksum for frame data

        Args:
            data: Data to calculate checksum for

        Returns:
            int: Calculated checksum
        """
        # Simple XOR-based checksum
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def to_bytes(self) -> bytes:
        """
        Convert frame to bytes

        Returns:
            bytes: Encoded frame
        """
        # Prepare frame data (without header and checksum)
        frame_data = bytes([
            self.frame_type,  # Frame type
            self.address >> 8, self.address & 0xFF,  # Address (high byte, low byte)
            self.command_code,  # Command code
            self.payload_length >> 8, self.payload_length & 0xFF  # Payload length
        ]) + self.payload

        # Calculate checksum including header
        checksum_data = self.HEADER + frame_data
        checksum = self.calculate_checksum(checksum_data)

        # Construct complete frame
        return self.HEADER + frame_data + bytes([checksum])

    @classmethod
    def from_bytes(cls, data: bytes) -> 'UHFFrame':
        """
        Parse frame from bytes

        Args:
            data: Raw data

        Returns:
            UHFFrame: Parsed frame
        """
        # Check minimum length
        if len(data) < 9:  # Header(2) + Type(1) + Addr(2) + Code(1) + Length(2) + Checksum(1)
            raise ValueError(f"Frame too short: {len(data)} bytes")

        # Check header
        if data[0:2] != cls.HEADER:
            raise ValueError(f"Invalid header: {data[0:2]}")

        # Extract fields
        frame_type = data[2]
        if not UHFFrameType.is_valid(frame_type):
            raise ValueError(f"Invalid frame type: 0x{frame_type:02X}")

        address = (data[3] << 8) | data[4]
        command_code = data[5]
        payload_length = (data[6] << 8) | data[7]

        # Check total length
        expected_length = 9 + payload_length  # Header to checksum + payload
        if len(data) != expected_length:
            raise ValueError(f"Invalid frame length: {len(data)}, expected {expected_length}")

        # Extract payload and checksum
        payload = data[8:8 + payload_length]
        received_checksum = data[-1]

        # Verify checksum
        calculated_checksum = cls().calculate_checksum(data[:-1])
        if calculated_checksum != received_checksum:
            raise ValueError(
                f"Checksum mismatch: calculated 0x{calculated_checksum:02X}, received 0x{received_checksum:02X}")

        # Create appropriate frame type
        if frame_type == UHFFrameType.NOTIFICATION:
            from .notification_frames import NotificationFrame
            return NotificationFrame.from_raw_frame(address, command_code, payload)
        elif frame_type == UHFFrameType.RESPONSE:
            from .commands import ResponseFrame
            return ResponseFrame.from_raw_frame(address, command_code, payload)
        else:
            # Default to base frame
            return cls(UHFFrameType(frame_type), address, command_code, payload)

    def get_tlvs(self) -> List[TLVBase]:
        """
        Extract TLVs from payload

        Returns:
            list: List of TLV objects
        """
        tlvs = []
        offset = 0

        while offset < len(self.payload):
            try:
                tlv, offset = TLVBase.from_bytes(self.payload, offset)
                tlvs.append(tlv)
            except ValueError as e:
                logger.error(f"Error parsing TLV at offset {offset}: {e}")
                break

        return tlvs

    def find_tlv(self, tlv_type: int) -> Optional[TLVBase]:
        """
        Find first TLV of specified type

        Args:
            tlv_type: TLV type to find

        Returns:
            TLVBase: Found TLV, or None if not found
        """
        for tlv in self.get_tlvs():
            if tlv.type == tlv_type:
                return tlv
        return None

    def __str__(self) -> str:
        """String representation of the frame"""
        frame_type_name = UHFFrameType(self.frame_type).name

        result = [
            f"UHF {frame_type_name} Frame:",
            f"  Address: 0x{self.address:04X}",
            f"  Command: 0x{self.command_code:02X}",
            f"  Payload: {self.payload_length} bytes"
        ]

        tlvs = self.get_tlvs()
        if tlvs:
            result.append("  TLVs:")
            for tlv in tlvs:
                result.append(f"    {tlv}")

        return "\n".join(result)