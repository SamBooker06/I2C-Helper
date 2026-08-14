from enum import Enum

from i2c_helper import I2CDriver
from i2c_helper.sigmastudio.command import SequenceCommand, NoOpCommand, DelayCommand, I2CWriteCommand


class SequenceInstruction(Enum):
    Write = "writeXbytes"
    Read = "read"
    Delay = "delay"
    NoOp = "noop"


class Sequence:
    @staticmethod
    def from_xml(
            xml: str,
            driver: I2CDriver, replace_reads: bool = True
    ) -> list["Sequence"]:
        from xml.etree import ElementTree

        root = ElementTree.fromstring(xml)

        sequences = []

        for page in root.findall("page"):
            commands = []

            mode_type = page.get("modetype", None)
            assert mode_type is not None, "modetype field missing"

            # Typically used for selecting the bus during A2B bring-up
            addr_increment = page.get("AddrIncr", 0)

            for action in page.findall("action"):
                instruction = action.get("instr")
                assert instruction is not None, "instruction field not found"

                instruction = SequenceInstruction(instruction)

                if instruction == SequenceInstruction.Write:
                    i2caddr = action.get("i2caddr")
                    addr = action.get("addr")
                    addr_width = action.get("addr_width")

                    assert i2caddr is not None, "i2caddr not found"
                    assert addr is not None, "addr not found"
                    assert addr_width is not None, "addr_width not found"

                    device_address = int(i2caddr, 10) + addr_increment
                    memory_address = int(addr, 10)
                    memory_address_size = int(addr_width, 10)

                    data = bytes.fromhex(action.text or "")

                    commands.append(
                        I2CWriteCommand(
                            driver=driver,
                            device_address=device_address,
                            memory_address=memory_address,
                            memory_address_size=memory_address_size,
                            data=data,
                        )
                    )

                elif instruction == SequenceInstruction.Delay:
                    delay_ms = int.from_bytes(
                        bytes.fromhex(action.text or ""),
                        byteorder="big",
                    )

                    commands.append(
                        DelayCommand(delay_ms=delay_ms)
                    )

                elif instruction == SequenceInstruction.NoOp:
                    commands.append(NoOpCommand())

                elif instruction == "read":
                    if replace_reads:
                        commands.append(NoOpCommand())

                    else:
                        raise ValueError("Read command present, and not told to skip")

                else:
                    raise ValueError(
                        f"Unsupported SigmaStudio instruction: {instruction!r}"
                    )

            sequences.append(Sequence(*commands, mode_type=mode_type))

        return sequences

    def __init__(self, *commands: SequenceCommand, mode_type: str):
        self.commands = commands
        self.mode_type = mode_type

    @property
    def mode(self):
        return self.mode_type

    def execute(self) -> None:
        for command in self.commands:
            command.execute()
