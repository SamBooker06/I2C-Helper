from abc import ABC, abstractmethod
from typing import Optional

from registers.a2b_chip import A2B_CHIP
from registers.a2b_nodeadr import A2B_NODEADR


class I2CDriver(ABC):
    @abstractmethod
    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:
        pass

    @abstractmethod
    def write(self, device_address: int, memory_address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        pass

    @abstractmethod
    def direct_write(self, device_address: int, data: bytes) -> None:
        pass


class MCP2221Driver(I2CDriver):
    def __init__(self):
        super().__init__()

        from diag_test_common.mcp2221 import MCP2221
        self._mcp2221 = MCP2221()

    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:
        buffer = bytearray(buffer_size)

        self._mcp2221.write_read(device_address, memory_address.to_bytes(memory_address_size, "big"), buffer)

        return buffer

    def write(self, device_address: int, memory_address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        memory_address_bytes = memory_address.to_bytes(memory_address_size, "big")
        payload = memory_address_bytes + data

        self._mcp2221.write(device_address, payload)

    def direct_write(self, device_address: int, data: bytes) -> None:
        self._mcp2221.write(device_address, data)


class I2COverDistanceWrapper(I2CDriver):
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

    def __init__(self, i2c_driver: I2CDriver, slave_number: int, transceiver_address: int = 0x68):
        self._driver = i2c_driver
        self.slave_number = slave_number

        self._transceiver_address = transceiver_address

        self._node_reserved_bits: Optional[int] = None
        self._peripheral_reserved_bits: dict[int, int] = {}

    def read(self, device_address: int, memory_address: int, *, buffer_size: int = 4,
             memory_address_size: int = 2) -> bytes:
        if device_address == I2COverDistanceWrapper.ACCESS_TRANSCEIVER:
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

    def write(self, device_address: int, memory_address: int, data: bytes, *,
              memory_address_size: int = 2) -> None:
        if device_address == I2COverDistanceWrapper.ACCESS_TRANSCEIVER:
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

    def broadcast(self, device_address: int, memory_address: int, data: bytes) -> None:
        raise NotImplementedError()

    def broadcast_to_transceivers(self, memory_address: int, data: bytes) -> None:
        raise NotImplementedError()
