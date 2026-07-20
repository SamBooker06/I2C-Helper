from i2c.driver import I2CDriver


class I2CDevice:
    """
    Represents an I2C (Inter-Integrated Circuit) device. This class provides functionality
    to communicate with hardware devices using the I2C protocol. It allows for reading from
    and writing to a specified address on the device using a provided I2C driver.


    :ivar device_address: The I2C address of the device to interact with.
    :type device_address: int
    """
    def __init__(self, device_address: int, driver: I2CDriver):
        self.device_address = device_address
        self._driver = driver

    def read(self, address: int, *, buffer_size: int = 4, memory_address_size: int = 2) -> bytes:
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
        return self._driver.read(self.device_address, address, buffer_size=buffer_size,
                                 memory_address_size=memory_address_size)

    def write(self, address: int, data: bytes, *, memory_address_size: int = 2) -> None:
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
        self._driver.write(self.device_address, address, data, memory_address_size=memory_address_size)
