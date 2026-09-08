import functools
from abc import ABC, abstractmethod
from typing import Optional

from i2c_helper.registers.a2b_chip import A2B_CHIP
from i2c_helper.registers.a2b_discstat import A2B_DISCSTAT
from i2c_helper.registers.a2b_nodeadr import A2B_NODEADR
from i2c_helper.registers.a2b_swstat import A2B_SWSTAT


class I2CException(Exception):
    pass


class I2CAddressingError(I2CException):
    pass


class I2CTimeoutError(I2CException):
    pass


class SlaveDiscoveryException(I2CException):
    pass


class I2CDriver(ABC):
    """
    Interface for I2C communication drivers.
    """

    @abstractmethod
    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:
        """
        Reads a block of data from a specified device.

        :param device_address: Target device address from which the data is to be read.
        :type device_address: int
        :param memory_address: Starting memory address on the target device to read data from.
        :type memory_address: int
        :param buffer_size: Number of bytes to read. Defaults to 4.
        :type buffer_size: int, optional
        :param memory_address_size: Size of the memory address in bytes. Defaults to 2.
        :type memory_address_size: int, optional
        :return: A bytes object containing the data read from the device memory.
        :rtype: bytes
        """
        pass

    @abstractmethod
    def write(self, device_address: int, memory_address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        """
        Writes data to a device's memory location.

        :param device_address: The address of the target device.
            Type must be an integer.
        :param memory_address: The memory address within the device where the data
            will be written. Type must be an integer.
        :param data: The data to be written to the specified memory address.
            Must be provided in bytes format.
        :param memory_address_size: Optional. The size (in bytes) of the memory
            address field. The default value is 2.
        :return: None. The method does not return any value.
        """
        pass

    @abstractmethod
    def direct_read(self, device_address: int, *, buffer_size: int = 4) -> bytes:
        """
        Performs a direct read operation from a device using its address and retrieves
        data of a specified size.

        :param device_address: The address of the device to read data from.
        :type device_address: int
        :param buffer_size: The size of the buffer to use for reading the data. Defaults to 4.
        :type buffer_size: int, optional
        :return: The data read from the device.
        :rtype: Any
        """
        pass

    @abstractmethod
    def direct_write(self, device_address: int, data: bytes) -> None:
        """
        Writes data directly to a specified device.

        :param device_address: The numeric address of the target device.
        :param data: The byte sequence to be written directly to the device.
        :return: This method does not return a value.
        """
        pass


class MCP2221Driver(I2CDriver):
    """
    Driver for interacting with I2C devices using the MCP2221 chip.

    :ivar _mcp2221: Internal instance of the MCP2221 communication interface.
    :type _mcp2221: diag_test_common.mcp2221.MCP2221
    """

    def __init__(self):
        super().__init__()

        try:
            from diag_test_common.mcp2221 import MCP2221
            self._mcp2221 = MCP2221()

        except ImportError as e:
            raise ImportError("Could not import MCP2221 library. Are you missing the diag_test_common package?") from e

        except OSError:
            raise OSError("Could not connect to MCP2221. Is it connected?")

    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:

        buffer = bytearray(buffer_size)
        try:
            self._mcp2221.write_read(device_address, memory_address.to_bytes(memory_address_size, "big"), buffer)

            return buffer

        except OSError as e:
            raise I2CAddressingError(f"MCP connected, but could not locate device with address {device_address}") from e

        except RuntimeError as e:
            raise I2CTimeoutError("Max retries reached for read") from e

    def direct_read(self, device_address: int, *, buffer_size: int = 4):
        buffer = bytearray(buffer_size)
        try:
            self._mcp2221.read(device_address, buffer)

        except OSError as e:
            raise I2CAddressingError(f"MCP connected, but could not locate device with address {device_address}") from e

        except RuntimeError as e:
            raise I2CTimeoutError("Max retries reached for direct read") from e

    def write(self, device_address: int, memory_address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        memory_address_bytes = memory_address.to_bytes(memory_address_size, "big")
        payload = memory_address_bytes + data

        try:
            self._mcp2221.write(device_address, payload)

        except OSError as e:
            raise I2CAddressingError(f"MCP connected, but could not locate device with address {device_address}") from e

        except RuntimeError as e:
            raise I2CTimeoutError("Max retries reached for write") from e

    def direct_write(self, device_address: int, data: bytes) -> None:
        try:
            self._mcp2221.write(device_address, data)

        except OSError as e:
            raise I2CAddressingError(f"MCP connected, but could not locate device with address {device_address}") from e

        except RuntimeError as e:
            raise I2CTimeoutError("Max retries reached for direct write") from e


class I2COverDistanceWrapper(I2CDriver):
    """
    Handles I2C communication over the A2B protocol


    :ivar slave_number: Identifier for the slave node being managed.
    :type slave_number: int
    """
    ACCESS_TRANSCEIVER = object()

    @property
    def transceiver_address(self) -> int:
        return self._transceiver_address

    @transceiver_address.setter
    def transceiver_address(self, transceiver_address: int) -> None:
        self._transceiver_address = transceiver_address

    @property
    def bus_address(self) -> int:
        return self.transceiver_address + 1

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _get_switch_status(driver: I2CDriver, transceiver_address: int):
        return int.from_bytes(
            driver.read(transceiver_address, A2B_SWSTAT.address, buffer_size=1, memory_address_size=1),
            "big")

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _is_switch_active() -> bool:
        return bool(I2COverDistanceWrapper._get_switch_status() & A2B_SWSTAT.FIN)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _did_switch_fail() -> bool:
        return not bool(I2COverDistanceWrapper._get_switch_status() & A2B_SWSTAT.FAULT)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _get_slave_count(driver: I2CDriver, transceiver_address: int) -> int:
        discovery_status = int.from_bytes(driver.read(transceiver_address, A2B_DISCSTAT.address), "big")
        last_discovered_node_number = A2B_DISCSTAT.DNODE(discovery_status)

        return last_discovered_node_number + 1 if I2COverDistanceWrapper._is_switch_active() and not I2COverDistanceWrapper._did_switch_fail() else 0

    def __init__(self, i2c_driver: I2CDriver, slave_number: int, transceiver_address: int = 0x68):
        self._driver = i2c_driver
        self.slave_number = slave_number

        self._transceiver_address = transceiver_address

        self._node_reserved_bits: Optional[int] = None
        self._peripheral_reserved_bits: dict[int, int] = {}

        if self._get_slave_count(self._driver, self.transceiver_address) - 1 < self.slave_number:
            raise SlaveDiscoveryException(
                f"Could not find slave {self.slave_number}. Switch status {self._get_switch_status(self._driver, self.transceiver_address):08b} ")

    def _get_node_reserved_bits(self) -> int:
        if self._node_reserved_bits is None:
            self._node_reserved_bits = int.from_bytes(
                self._driver.read(self.transceiver_address, A2B_NODEADR.address, buffer_size=1,
                                  memory_address_size=1), "big") & A2B_NODEADR.RESERVED

        assert self._node_reserved_bits is not None, "Could not get node reserved bits"
        return self._node_reserved_bits

    def _get_peripheral_reserved_bits(self, device_address: int) -> int:
        if device_address not in self._peripheral_reserved_bits:
            self._peripheral_reserved_bits[device_address] = A2B_CHIP.RESERVED & int.from_bytes(
                self._driver.read(self.bus_address, A2B_CHIP.address, buffer_size=1,
                                  memory_address_size=1), "big")

        return self._peripheral_reserved_bits[device_address]

    def _select_node(self, *, peripheral: bool = False, broadcast: bool = False) -> None:
        reserved_bits = self._get_node_reserved_bits()

        nodeadr_value = reserved_bits | A2B_NODEADR.NODE(
            self.slave_number) | peripheral * A2B_NODEADR.PERI | broadcast * A2B_NODEADR.BRCST

        self._driver.write(self.transceiver_address, A2B_NODEADR.address, nodeadr_value.to_bytes(1, "big"),
                           memory_address_size=1)

    def _deselect_node(self) -> None:
        reserved_bits = self._get_node_reserved_bits()

        self._driver.write(self.transceiver_address, A2B_NODEADR.address, reserved_bits.to_bytes(1, "big"),
                           memory_address_size=1)

    def _select_peripheral(self, device_address: int) -> None:
        self._select_node()

        reserved_bits_peripheral = self._get_peripheral_reserved_bits(device_address)

        payload = A2B_CHIP.CHIPADR(device_address) | reserved_bits_peripheral

        # Select the peripheral to read from
        self._driver.write(self.bus_address, A2B_CHIP.address, payload.to_bytes(1, "big"),
                           memory_address_size=1)
        self._select_node(peripheral=True)

    def _deselect_peripheral(self, device_address: int):
        self._select_node()

        reserved_bits_peripheral = self._get_peripheral_reserved_bits(device_address)
        self._driver.write(self.bus_address, A2B_CHIP.address, reserved_bits_peripheral.to_bytes(1, "big"),
                           memory_address_size=1)
        self._deselect_node()

    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:
        if device_address == I2COverDistanceWrapper.ACCESS_TRANSCEIVER or device_address == self.transceiver_address:
            return self.read_from_transceiver(memory_address, buffer_size=buffer_size)

        self._select_peripheral(device_address)

        result = self._driver.read(self.bus_address, memory_address, buffer_size=buffer_size,
                                   memory_address_size=memory_address_size)

        self._deselect_peripheral(device_address)

        return result

    def read_from_transceiver(self, memory_address: int, *, buffer_size: int = 4) -> bytes:
        self._select_node()

        result = self._driver.read(self.bus_address, memory_address, buffer_size=buffer_size, memory_address_size=1)

        self._deselect_node()

        return result

    def direct_read(self, device_address: int, *, buffer_size: int = 4) -> bytes:
        self._select_peripheral(device_address)

        result = self._driver.direct_read(device_address, buffer_size=buffer_size)

        self._deselect_peripheral(device_address)
        return result

    def write(self, device_address: int, memory_address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        if device_address == I2COverDistanceWrapper.ACCESS_TRANSCEIVER or device_address == self.transceiver_address:
            self.write_to_transceiver(memory_address, data)
            return

        self._select_peripheral(device_address)

        self._driver.write(self.bus_address, memory_address, data, memory_address_size=memory_address_size)

        self._deselect_peripheral(device_address)

    def write_to_transceiver(self, memory_address: int, data: bytes) -> None:
        self._select_node()

        self._driver.write(self.bus_address, memory_address, data, memory_address_size=1)

        self._deselect_node()

    def direct_write(self, device_address: int, data: bytes) -> None:
        self._select_peripheral(device_address)

        self._driver.direct_write(self.bus_address, data)

        self._deselect_peripheral(device_address)

    def broadcast(self, memory_address: int, data: bytes) -> None:
        self._select_node(broadcast=True)

        self._driver.write(self.bus_address, memory_address, data, memory_address_size=1)

        self._deselect_node()
