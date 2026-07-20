from dataclasses import dataclass


@dataclass
class A2B_DNMASK0:
    address = 0x65

    RXDNSLOT00 = 0x1
    RXDNSLOT01 = 0x2
    RXDNSLOT02 = 0x4
    RXDNSLOT03 = 0x8
    RXDNSLOT04 = 0x10
    RXDNSLOT05 = 0x20
    RXDNSLOT06 = 0x40
    RXDNSLOT07 = 0x80

    @staticmethod
    def invert(mask: int):
        return ~mask & 0xFF
