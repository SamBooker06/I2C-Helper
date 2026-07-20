from dataclasses import dataclass


@dataclass
class A2B_CONTROL:
    address = 0x12

    MSTR = 0b1000000
    RESERVED = 0b01100000
    XCVRBINV = 0b00010000
    SWBYP = 0b00001000
    SOFTRST = 0b00000100
    ENDDSC = 0b00000010
    NEWSTRCT = 0b00000001