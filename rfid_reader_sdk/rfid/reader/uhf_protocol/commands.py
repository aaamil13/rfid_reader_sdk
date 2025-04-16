"""
UHF Protocol Commands

This module implements command frames and responses for the UHF RFID protocol.
It includes all commands defined in the protocol specification, along with
response handling and a command factory for easy creation.
"""

import enum
import logging
from typing import List, Dict, Any, Tuple, Optional, Union, ByteString, Type, Callable

from .protocol_base import UHFFrame, UHFFrameType, TLVBase, TLVType
from .status_codes import StatusTLV, StatusCode, StatusError

logger = logging.getLogger(__name__)


class CommandType(enum.IntEnum):
    """Command types defined in UHF protocol"""
    # System commands
    RESET = 0x01  # Reset reader
    VERSION = 0x03  # Get version information
    GET_CONFIG = 0x11  # Get configuration parameter
    SET_CONFIG = 0x12  # Set configuration parameter
    SAVE_CONFIG = 0x13  # Save configuration to non-volatile memory

    # Inventory commands
    START_INVENTORY = 0x21  # Start continuous inventory
    STOP_INVENTORY = 0x22  # Stop inventory
    INVENTORY_ONCE = 0x23  # Perform one-time inventory

    # Tag memory operation commands
    READ_TAG = 0x31  # Read tag memory
    WRITE_TAG = 0x32  # Write tag memory
    LOCK_TAG = 0x33  # Lock tag memory
    KILL_TAG = 0x34  # Kill tag permanently

    # Advanced commands
    SET_TX_POWER = 0x41  # Set transmit power
    GET_TX_POWER = 0x42  # Get transmit power
    SET_FREQUENCY = 0x45  # Set frequency configuration
    GET_FREQUENCY = 0x46  # Get frequency configuration
    SET_TX_TIME = 0x47  # Set transmission time
    GET_TX_TIME = 0x48  # Get transmission time

    @classmethod
    def get_name(cls, code: int) -> str:
        """Get the name of a command type"""
        try:
            return cls(code).name
        except ValueError:
            return f"UNKNOWN_COMMAND(0x{code:02X})"


class CommandFrame(UHFFrame):
    """
    Command Frame implementation

    Command frames are sent from the host to the reader to request an operation.
    """

    def __init__(self,
                 command_type: Union[CommandType, int],
                 address: int = 0,
                 payload: Optional[bytes] = None):
        """
        Initialize a command frame

        Args:
            command_type: Type of command
            address: Device address
            payload: Frame payload (TLV data)
        """
        # Convert enum to int if needed
        if isinstance(command_type, CommandType):
            command_type = command_type.value

        super().__init__(UHFFrameType.COMMAND, address, command_type, payload)

    @property
    def command_type(self) -> int:
        """Get the command type"""
        return self.command_code

    @command_type.setter
    def command_type(self, cmd_type: Union[CommandType, int]):
        """Set the command type"""
        if isinstance(cmd_type, CommandType):
            self.command_code = cmd_type.value
        else:
            self.command_code = cmd_type

    def add_tlv(self, tlv: TLVBase) -> None:
        """
        Add a TLV to the payload

        Args:
            tlv: TLV to add
        """
        self.payload += tlv.to_bytes()

    def __str__(self) -> str:
        """String representation of the command frame"""
        command_name = CommandType.get_name(self.command_type)

        result = [
            f"UHF Command Frame: {command_name}",
            f"  Address: 0x{self.address:04X}",
            f"  Payload: {self.payload_length} bytes"
        ]

        tlvs = self.get_tlvs()
        if tlvs:
            result.append("  TLVs:")
            for tlv in tlvs:
                result.append(f"    {tlv}")

        return "\n".join(result)


class ResponseFrame(UHFFrame):
    """
    Response Frame implementation

    Response frames are sent from the reader to the host in response to commands.
    """

    def __init__(self,
                 command_type: Union[CommandType, int],
                 address: int = 0,
                 payload: Optional[bytes] = None):
        """
        Initialize a response frame

        Args:
            command_type: Type of command being responded to
            address: Device address
            payload: Frame payload (TLV data)
        """
        # Convert enum to int if needed
        if isinstance(command_type, CommandType):
            command_type = command_type.value

        super().__init__(UHFFrameType.RESPONSE, address, command_type, payload)

    @property
    def command_type(self) -> int:
        """Get the command type"""
        return self.command_code

    @classmethod
    def from_raw_frame(cls, address: int, command_type: int, payload: bytes) -> 'ResponseFrame':
        """
        Create a response frame from raw frame data

        Args:
            address: Device address
            command_type: Command type code
            payload: Raw payload data

        Returns:
            ResponseFrame: Created response frame
        """
        return cls(command_type, address, payload)

    def get_status(self) -> Optional[StatusTLV]:
        """
        Get status TLV from the response

        Returns:
            StatusTLV: Status TLV, or None if not found
        """
        status_tlv = self.find_tlv(TLVType.STATUS)
        if status_tlv:
            from .status_codes import StatusTLV
            if not isinstance(status_tlv, StatusTLV):
                # Convert generic TLV to StatusTLV
                status_tlv = StatusTLV(status_tlv.value)
            return status_tlv
        return None

    def check_status(self) -> bool:
        """
        Check if the response status indicates success

        Returns:
            bool: True if success, False otherwise
        """
        status_tlv = self.get_status()
        if status_tlv:
            return status_tlv.is_success
        return False

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response status indicates an error

        Raises:
            StatusError: If the status is not success
        """
        status_tlv = self.get_status()
        if status_tlv:
            status_tlv.raise_for_error()

    def __str__(self) -> str:
        """String representation of the response frame"""
        command_name = CommandType.get_name(self.command_type)

        result = [
            f"UHF Response Frame: {command_name}",
            f"  Address: 0x{self.address:04X}",
            f"  Payload: {self.payload_length} bytes"
        ]

        # Show status if present
        status_tlv = self.get_status()
        if status_tlv:
            result.append(f"  Status: {status_tlv.description} (0x{status_tlv.status_code:02X})")

        # Show other TLVs
        tlvs = self.get_tlvs()
        if tlvs:
            result.append("  TLVs:")
            for tlv in tlvs:
                if tlv.type != TLVType.STATUS:  # Skip status TLV as it's shown above
                    result.append(f"    {tlv}")

        return "\n".join(result)


# Registry of command factories by command type
_COMMAND_FACTORIES: Dict[int, Callable[..., CommandFrame]] = {}


def register_command(command_type: Union[CommandType, int]):
    """
    Decorator to register command factory functions

    Args:
        command_type: Command type
    """

    def decorator(func):
        if isinstance(command_type, CommandType):
            _COMMAND_FACTORIES[command_type.value] = func
        else:
            _COMMAND_FACTORIES[command_type] = func
        return func

    return decorator


class CommandFactory:
    """Factory for creating command frames"""

    @staticmethod
    @register_command(CommandType.RESET)
    def create_reset_command(address: int = 0) -> CommandFrame:
        """
        Create a reset command

        Args:
            address: Device address

        Returns:
            CommandFrame: Reset command frame
        """
        return CommandFrame(CommandType.RESET, address)

    @staticmethod
    @register_command(CommandType.VERSION)
    def create_version_command(address: int = 0) -> CommandFrame:
        """
        Create a version query command

        Args:
            address: Device address

        Returns:
            CommandFrame: Version command frame
        """
        return CommandFrame(CommandType.VERSION, address)

    @staticmethod
    @register_command(CommandType.START_INVENTORY)
    def create_start_inventory_command(address: int = 0) -> CommandFrame:
        """
        Create a start inventory command

        Args:
            address: Device address

        Returns:
            CommandFrame: Start inventory command frame
        """
        return CommandFrame(CommandType.START_INVENTORY, address)

    @staticmethod
    @register_command(CommandType.STOP_INVENTORY)
    def create_stop_inventory_command(address: int = 0) -> CommandFrame:
        """
        Create a stop inventory command

        Args:
            address: Device address

        Returns:
            CommandFrame: Stop inventory command frame
        """
        return CommandFrame(CommandType.STOP_INVENTORY, address)

    @staticmethod
    @register_command(CommandType.INVENTORY_ONCE)
    def create_inventory_once_command(address: int = 0) -> CommandFrame:
        """
        Create an inventory once command

        Args:
            address: Device address

        Returns:
            CommandFrame: Inventory once command frame
        """
        return CommandFrame(CommandType.INVENTORY_ONCE, address)

    @staticmethod
    @register_command(CommandType.READ_TAG)
    def create_read_tag_command(
            mem_bank: int,
            address: int = 0,
            word_ptr: int = 0,
            word_count: int = 1,
            password: Optional[bytes] = None,
            reader_addr: int = 0
    ) -> CommandFrame:
        """
        Create a read tag command

        Args:
            mem_bank: Memory bank (0=Reserved, 1=EPC, 2=TID, 3=User)
            address: Device address
            word_ptr: Starting word address
            word_count: Number of words to read
            password: Access password (4 bytes) or None
            reader_addr: Reader address

        Returns:
            CommandFrame: Read tag command frame
        """
        from .tlv_structures import TLVBase

        command = CommandFrame(CommandType.READ_TAG, reader_addr)

        # Memory bank TLV (custom TLV type 0x41)
        command.add_tlv(TLVBase(0x41, bytes([mem_bank])))

        # Word pointer TLV (custom TLV type 0x42)
        word_ptr_bytes = word_ptr.to_bytes(2, byteorder='big')
        command.add_tlv(TLVBase(0x42, word_ptr_bytes))

        # Word count TLV (custom TLV type 0x43)
        word_count_bytes = word_count.to_bytes(2, byteorder='big')
        command.add_tlv(TLVBase(0x43, word_count_bytes))

        # Add access password if provided
        if password:
            from .tlv_structures import TLVType
            command.add_tlv(TLVBase(TLVType.ACCESS_PWD, password))

        return command

    @staticmethod
    @register_command(CommandType.WRITE_TAG)
    def create_write_tag_command(
            mem_bank: int,
            word_ptr: int,
            data: bytes,
            password: Optional[bytes] = None,
            address: int = 0
    ) -> CommandFrame:
        """
        Create a write tag command

        Args:
            mem_bank: Memory bank (0=Reserved, 1=EPC, 2=TID, 3=User)
            word_ptr: Starting word address
            data: Data to write (must be a multiple of 2 bytes)
            password: Access password (4 bytes) or None
            address: Device address

        Returns:
            CommandFrame: Write tag command frame
        """
        from .tlv_structures import TLVBase

        # Validate data length (must be multiple of 2 bytes)
        if len(data) % 2 != 0:
            raise ValueError("Data length must be a multiple of 2 bytes (word aligned)")

        command = CommandFrame(CommandType.WRITE_TAG, address)

        # Memory bank TLV (custom TLV type 0x41)
        command.add_tlv(TLVBase(0x41, bytes([mem_bank])))

        # Word pointer TLV (custom TLV type 0x42)
        word_ptr_bytes = word_ptr.to_bytes(2, byteorder='big')
        command.add_tlv(TLVBase(0x42, word_ptr_bytes))

        # Data TLV (custom TLV type 0x44)
        command.add_tlv(TLVBase(0x44, data))

        # Add access password if provided
        if password:
            from .tlv_structures import TLVType
            command.add_tlv(TLVBase(TLVType.ACCESS_PWD, password))

        return command

    @staticmethod
    @register_command(CommandType.LOCK_TAG)
    def create_lock_tag_command(
            lock_type: int,
            password: bytes,
            address: int = 0
    ) -> CommandFrame:
        """
        Create a lock tag command

        Args:
            lock_type: Lock type (0=User, 1=TID, 2=EPC, 3=Access PWD, 4=Kill PWD, 5=All)
            password: Access password (4 bytes)
            address: Device address

        Returns:
            CommandFrame: Lock tag command frame
        """
        from .tlv_structures import TLVBase, TLVType

        command = CommandFrame(CommandType.LOCK_TAG, address)

        # Lock type TLV (custom TLV type 0x45)
        command.add_tlv(TLVBase(0x45, bytes([lock_type])))

        # Access password TLV
        command.add_tlv(TLVBase(TLVType.ACCESS_PWD, password))

        return command

    @staticmethod
    @register_command(CommandType.KILL_TAG)
    def create_kill_tag_command(
            password: bytes,
            address: int = 0
    ) -> CommandFrame:
        """
        Create a kill tag command

        Args:
            password: Kill password (4 bytes)
            address: Device address

        Returns:
            CommandFrame: Kill tag command frame
        """
        from .tlv_structures import TLVBase, TLVType

        command = CommandFrame(CommandType.KILL_TAG, address)

        # Kill password TLV
        command.add_tlv(TLVBase(TLVType.KILL_PWD, password))

        return command

    @staticmethod
    def create_command(
            command_type: Union[CommandType, int],
            address: int = 0,
            **kwargs
    ) -> CommandFrame:
        """
        Create a command frame using registered factories

        Args:
            command_type: Command type
            address: Device address
            **kwargs: Additional parameters for specific commands

        Returns:
            CommandFrame: Created command frame
        """
        # Convert enum to int if needed
        if isinstance(command_type, CommandType):
            command_code = command_type.value
        else:
            command_code = command_type

        # Check if command has a factory
        if command_code in _COMMAND_FACTORIES:
            # Pass address to factory function
            kwargs['address'] = address
            return _COMMAND_FACTORIES[command_code](**kwargs)

        # Default to basic command frame
        return CommandFrame(command_type, address)