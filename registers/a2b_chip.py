from dataclasses import dataclass


@dataclass
class A2B_CHIP:
    address: int = 0x0

    RESERVED = 0b10000000

    @staticmethod
    def CHIPADR(device_address: int) -> int:
        return device_address