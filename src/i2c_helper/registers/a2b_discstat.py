from dataclasses import dataclass


@dataclass
class A2B_DISCSTAT:
    address = 0x2B

    DSCACT = 0x80

    @staticmethod
    def DNODE(discstat: int) -> int:
        return discstat & 0xF
