"""
UHF Protocol TLV Structures

This module implements various TLV (Type-Length-Value) structures used in the UHF RFID protocol.
It includes implementations for all standard TLVs including Tag TLV, EPC TLV, RSSI TLV, Time TLV, etc.
"""

import time
import struct
import binascii
import logging
from typing import List, Dict, Any, Tuple, Optional, Union, ByteString, Type, ClassVar

from .protocol_base import TLVBase, TLVType

logger = logging.getLogger(__name__)

# Registry of TLV classes by type code
_TLV_REGISTRY: Dict[int, Type['TLVBase']] = {}


def register_tlv_type(tlv_type: int):
    """
    Decorator to register TLV classes by their type code

    Args:
        tlv_type: TLV type code
    """

    def decorator(cls):
        _TLV_REGISTRY[tlv_type] = cls
        return cls

    return decorator


def create_tlv_from_type(tlv_type: int, value: bytes) -> TLVBase:
    """
    Create a TLV instance based on its type code

    Args:
        tlv_type: TLV type code
        value: Raw TLV value

    Returns:
        TLVBase: Instantiated TLV of appropriate class
    """
    if tlv_type in _TLV_REGISTRY:
        try:
            return _TLV_REGISTRY[tlv_type].from_value(value)
        except Exception as e:
            logger.warning(f"Error creating TLV type 0x{tlv_type:02X}: {e}")

    # Fall back to generic TLV
    return TLVBase(tlv_type, value)


@register_tlv_type(TLVType.EPC)
class EPCTLV(TLVBase):
    """EPC (Electronic Product Code) TLV"""

    def __init__(self, epc: Union[bytes, str]):
        """
        Initialize EPC TLV

        Args:
            epc: EPC as bytes or hex string
        """
        # Convert hex string to bytes if needed
        if isinstance(epc, str):
            epc = binascii.unhexlify(epc.replace(" ", ""))

        super().__init__(TLVType.EPC, epc)

    @property
    def epc(self) -> bytes:
        """Get the EPC value"""
        return self._value

    @epc.setter
    def epc(self, value: Union[bytes, str]):
        """Set the EPC value"""
        if isinstance(value, str):
            value = binascii.unhexlify(value.replace(" ", ""))
        self._value = value

    @classmethod
    def from_value(cls, value: bytes) -> 'EPCTLV':
        """Create EPC TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the EPC TLV"""
        epc_hex = binascii.hexlify(self._value).decode('ascii')
        return f"EPC: {epc_hex}"


@register_tlv_type(TLVType.RSSI)
class RSSITLV(TLVBase):
    """RSSI (Received Signal Strength Indicator) TLV"""

    def __init__(self, rssi: Union[int, bytes]):
        """
        Initialize RSSI TLV

        Args:
            rssi: Signal strength value (-dBm) or raw bytes
        """
        if isinstance(rssi, int):
            # Convert integer to single byte
            value = bytes([rssi & 0xFF])
        else:
            value = rssi

        super().__init__(TLVType.RSSI, value)

    @property
    def rssi(self) -> int:
        """Get the RSSI value"""
        if self._value:
            return self._value[0]
        return 0

    @rssi.setter
    def rssi(self, value: int):
        """Set the RSSI value"""
        self._value = bytes([value & 0xFF])

    @classmethod
    def from_value(cls, value: bytes) -> 'RSSITLV':
        """Create RSSI TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the RSSI TLV"""
        return f"RSSI: -{self.rssi} dBm"


@register_tlv_type(TLVType.TIME)
class TimeTLV(TLVBase):
    """Time TLV (timestamp)"""

    def __init__(self, timestamp: Union[int, bytes, float, None] = None):
        """
        Initialize Time TLV

        Args:
            timestamp: Unix timestamp, raw bytes, or None for current time
        """
        if timestamp is None:
            # Use current time
            timestamp = int(time.time())

        if isinstance(timestamp, (int, float)):
            # Convert timestamp to 4 bytes (32-bit uint)
            value = struct.pack(">I", int(timestamp))
        else:
            value = timestamp

        super().__init__(TLVType.TIME, value)

    @property
    def timestamp(self) -> int:
        """Get the timestamp value"""
        if len(self._value) >= 4:
            return struct.unpack(">I", self._value[:4])[0]
        return 0

    @timestamp.setter
    def timestamp(self, value: Union[int, float]):
        """Set the timestamp value"""
        self._value = struct.pack(">I", int(value))

    @classmethod
    def from_value(cls, value: bytes) -> 'TimeTLV':
        """Create Time TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the Time TLV"""
        return f"Time: {self.timestamp} ({time.ctime(self.timestamp)})"


@register_tlv_type(TLVType.TID)
class TIDTLV(TLVBase):
    """TID (Tag ID) TLV"""

    def __init__(self, tid: Union[bytes, str]):
        """
        Initialize TID TLV

        Args:
            tid: TID as bytes or hex string
        """
        # Convert hex string to bytes if needed
        if isinstance(tid, str):
            tid = binascii.unhexlify(tid.replace(" ", ""))

        super().__init__(TLVType.TID, tid)

    @property
    def tid(self) -> bytes:
        """Get the TID value"""
        return self._value

    @tid.setter
    def tid(self, value: Union[bytes, str]):
        """Set the TID value"""
        if isinstance(value, str):
            value = binascii.unhexlify(value.replace(" ", ""))
        self._value = value

    @classmethod
    def from_value(cls, value: bytes) -> 'TIDTLV':
        """Create TID TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the TID TLV"""
        tid_hex = binascii.hexlify(self._value).decode('ascii')
        return f"TID: {tid_hex}"


@register_tlv_type(TLVType.DEVICE_TYPE)
class DeviceTypeTLV(TLVBase):
    """Device Type TLV"""

    # Device type constants
    DEVICE_TYPES = {
        0x01: "Fixed RFID Reader",
        0x02: "Handheld RFID Reader",
        0x03: "Mobile RFID Reader",
        0x04: "RFID Module",
        0xFF: "Development Board"
    }

    def __init__(self, device_type: Union[int, bytes]):
        """
        Initialize Device Type TLV

        Args:
            device_type: Device type code or raw bytes
        """
        if isinstance(device_type, int):
            value = bytes([device_type & 0xFF])
        else:
            value = device_type

        super().__init__(TLVType.DEVICE_TYPE, value)

    @property
    def device_type(self) -> int:
        """Get the device type code"""
        if self._value:
            return self._value[0]
        return 0

    @device_type.setter
    def device_type(self, value: int):
        """Set the device type code"""
        self._value = bytes([value & 0xFF])

    @property
    def device_type_name(self) -> str:
        """Get the device type name"""
        return self.DEVICE_TYPES.get(self.device_type, f"Unknown Type (0x{self.device_type:02X})")

    @classmethod
    def from_value(cls, value: bytes) -> 'DeviceTypeTLV':
        """Create Device Type TLV from raw value"""
        return cls(value)

    def __str__(self) -> str:
        """String representation of the Device Type TLV"""
        return f"Device Type: {self.device_type_name} (0x{self.device_type:02X})"


@register_tlv_type(TLVType.TAG)
class TagTLV(TLVBase):
    """
    Tag TLV (compound TLV containing tag information)

    This is a container for tag-related TLVs like EPC, RSSI, Time, and TID.
    It's typically used in notification frames to report tags.
    """

    def __init__(self, sub_tlvs: Optional[List[TLVBase]] = None):
        """
        Initialize Tag TLV

        Args:
            sub_tlvs: List of sub-TLVs
        """
        super().__init__(TLVType.TAG, sub_tlvs or [])

    @property
    def sub_tlvs(self) -> List[TLVBase]:
        """Get the sub-TLVs"""
        if isinstance(self._value, list):
            return self._value
        return []

    def add_tlv(self, tlv: TLVBase) -> None:
        """
        Add a sub-TLV

        Args:
            tlv: TLV to add
        """
        if not isinstance(self._value, list):
            self._value = []
        self._value.append(tlv)

    def get_epc(self) -> Optional[str]:
        """
        Get the EPC from the tag

        Returns:
            str: EPC as hex string, or None if not present
        """
        for tlv in self.sub_tlvs:
            if tlv.type == TLVType.EPC:
                return binascii.hexlify(tlv.value).decode('ascii')
        return None

    def get_rssi(self) -> Optional[int]:
        """
        Get the RSSI from the tag

        Returns:
            int: RSSI value, or None if not present
        """
        for tlv in self.sub_tlvs:
            if tlv.type == TLVType.RSSI and tlv.value:
                return tlv.value[0]
        return None

    def get_timestamp(self) -> Optional[int]:
        """
        Get the timestamp from the tag

        Returns:
            int: Timestamp, or None if not present
        """
        for tlv in self.sub_tlvs:
            if tlv.type == TLVType.TIME and len(tlv.value) >= 4:
                return struct.unpack(">I", tlv.value[:4])[0]
        return None

    def get_tid(self) -> Optional[str]:
        """
        Get the TID from the tag

        Returns:
            str: TID as hex string, or None if not present
        """
        for tlv in self.sub_tlvs:
            if tlv.type == TLVType.TID:
                return binascii.hexlify(tlv.value).decode('ascii')
        return None

    @classmethod
    def from_value(cls, value: bytes) -> 'TagTLV':
        """
        Create Tag TLV from raw value

        This method parses the raw value as a sequence of TLVs
        """
        tag_tlv = cls()
        offset = 0

        while offset < len(value):
            try:
                tlv, new_offset = TLVBase.from_bytes(value, offset)
                tag_tlv.add_tlv(tlv)
                offset = new_offset
            except ValueError as e:
                logger.error(f"Error parsing sub-TLV at offset {offset}: {e}")
                break

        return tag_tlv

    def __str__(self) -> str:
        """String representation of the Tag TLV"""
        epc = self.get_epc() or "N/A"
        rssi = self.get_rssi()
        timestamp = self.get_timestamp()
        tid = self.get_tid()

        result = [f"Tag: EPC={epc}"]

        if rssi is not None:
            result.append(f"RSSI=-{rssi} dBm")

        if timestamp is not None:
            result.append(f"Time={timestamp}")

        if tid is not None:
            result.append(f"TID={tid}")

        return ", ".join(result)