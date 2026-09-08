from dataclasses import dataclass
from enum import IntEnum


class SwitchStatusFaultCode(IntEnum):
    NO_FAULT = 0
    GND_SHORT = 1
    VBAT_SHORT = 2
    TERMINAL_SHORT = 3
    OPEN_CIRCUIT = 4
    REVERSE_CONNECTION = 5
    UNDETERMINED = 7


@dataclass
class A2B_SWSTAT:
    address = 0x14

    FAULT_NLOC = 0x80
    FAULT = 0x02
    FIN = 0x01

    @staticmethod
    def FAULT_CODE(swstat: int) -> SwitchStatusFaultCode:
        return SwitchStatusFaultCode(
            (swstat & 0x70) >> 4
        )
