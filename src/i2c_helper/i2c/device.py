from typing import Optional, Union

from i2c_helper.i2c.driver import I2CDriver


class I2CDeviceInterface:
    """
    Represents an interface to an I2C (Inter-Integrated Circuit) device. This class provides functionality
    to communicate with hardware devices using the I2C protocol. It allows for reading from
    and writing to a specified address on the device using a provided I2C driver.


    :ivar device_address: The I2C address of the device to interact with.
    :type device_address: int
    """
    def __init__(self, device_address: int, driver: I2CDriver, *,  memory_address_size: int = 2, default_buffer_size: int = 4):
        self.device_address = device_address
        self.driver = driver
        self.memory_address_size = memory_address_size
        self.default_buffer_size = default_buffer_size

    def read(self, address: int, *, buffer_size: Optional[int] = None) -> bytes:
        """
        Reads data from the specified memory address of the device.

        :param address: The memory address to read from.
        :type address: int
        :param buffer_size: The number of bytes to read. Defaults to 4.
        :type buffer_size: int, optional
        :param memory_address_size: The size, in bytes, of the memory address. Defaults to 2.
        :type memory_address_size: int, optional
        :return: The bytes read from the specified memory address.
        :rtype: bytes
        """
        return self.driver.read(self.device_address, address, buffer_size=buffer_size if buffer_size is not None else self.default_buffer_size,
                                memory_address_size=self.memory_address_size)

    def direct_read(self, *, buffer_size: Optional[int] = None) -> bytes:
        return self.driver.direct_read(self.device_address, buffer_size=buffer_size)

    def write(self, address: int, data: Union[bytes, int]) -> None:
        """
        Writes data to a specified memory address of a device.

        :param address: The memory address where the data will be written.
        :type address: int
        :param data: The data to write to the specified memory address.
        :type data: bytes
        :param memory_address_size: The size, in bytes, of the memory address.
            Defaults to 2.
        :type memory_address_size: int
        :return: None
        """
        if isinstance(data, int):
            data = data.to_bytes(self.default_buffer_size, "big")
        self.driver.write(self.device_address, address, data, memory_address_size=self.memory_address_size)

    def direct_write(self, data: bytes) -> None:
        self.driver.direct_write(self.device_address, data)
