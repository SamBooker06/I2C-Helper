from i2c.driver import I2CDriver, I2COverDistanceWrapper


class I2CDevice:
    def __init__(self, device_address: int, driver: I2CDriver):
        self.device_address = device_address
        self._driver = driver

    def read(self, address: int, *, buffer_size: int = 4, memory_address_size: int = 2) -> bytes:
        return self._driver.read(self.device_address, address, buffer_size=buffer_size,
                                 memory_address_size=memory_address_size)

    def write(self, address: int, data: bytes, *, memory_address_size: int = 2) -> None:
        self._driver.write(self.device_address, address, data, memory_address_size=memory_address_size)
