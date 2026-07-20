from dataclasses import dataclass


@dataclass
class A2B_NODEADR:
    address = 0x01

    BRCST = 0b10000000
    PERI = 0b00100000
    RESERVED = 0b01010000

    @staticmethod
    def NODE(node_number: int) -> int:
        return node_number
