from abc import ABC, ABCMeta, abstractmethod
from time import sleep
from typing import Optional

from i2c_helper import I2CDriver


class SequenceCommand(ABC, metaclass=ABCMeta):
    @abstractmethod
    def execute(self) -> Optional[bytes]:
        raise NotImplementedError()


class I2CCommand(SequenceCommand, metaclass=ABCMeta):
    def __init__(self, driver: I2CDriver, device_address: int, memory_address: int, memory_address_size: int, ):
        self.driver = driver

        self.device_address = device_address
        self.memory_address = memory_address

        self.memory_address_size = memory_address_size


class I2CReadCommand(I2CCommand):
    def __init__(self, driver: I2CDriver, device_address: int, memory_address: int, memory_address_size: int,
                 buffer_size: int) -> None:
        super().__init__(driver, device_address, memory_address, memory_address_size)

        self.buffer_size = buffer_size

    def execute(self) -> bytes:
        return self.driver.read(self.device_address, self.memory_address, buffer_size=self.buffer_size,
                                memory_address_size=self.memory_address_size)


class I2CWriteCommand(I2CCommand):
    def __init__(self, driver: I2CDriver, device_address: int, memory_address: int, memory_address_size: int,
                 data: bytes):
        super().__init__(driver, device_address, memory_address, memory_address_size)

        self.data = data

    def execute(self) -> None:
        self.driver.write(self.device_address, self.memory_address, self.data,
                          memory_address_size=self.memory_address_size)


class NoOpCommand(SequenceCommand):
    def execute(self) -> None:
        # Do nothing
        return


class DelayCommand(SequenceCommand):
    def __init__(self, delay_ms: int) -> None:
        self.delay_ms = delay_ms

    def execute(self) -> None:
        sleep(self.delay_ms / 1_000)
