# I2C Helper

`i2c-helper` is a Python package that wraps low-level I2C operations for:

- Direct MCP2221-based device access (`MCP2221Driver`)
- A2B transceiver and remote-node access (`I2COverDistanceWrapper`)
- Device-level read/write helpers (`I2CDeviceInterface`)
- Bulk transaction scoping (`BulkTransaction`)
- SigmaStudio XML sequence parsing and execution (`i2c_helper.sigmastudio`)

## Repository contents

- `src/i2c_helper/i2c/driver.py`  
  Driver abstractions, MCP2221 implementation, and A2B wrapper logic.
- `src/i2c_helper/i2c/device.py`  
  Device-level convenience API for memory-addressed and direct I2C access.
- `src/i2c_helper/i2c/bulk.py`  
  Context manager that keeps the transaction lock and node selection stable.
- `src/i2c_helper/sigmastudio/`  
  SigmaStudio command and sequence parsing/execution support.
- `src/i2c_helper/registers/`  
  Register constants and masks used by the A2B wrapper.

## Installation

This project uses `uv` and defines local wheel sources in `pyproject.toml`:

- `../../Local Libraries/keygen-1.2.0-py3-none-any.whl`
- `../../Local Libraries/diag_test_common-0.0.9-py3-none-any.whl`

Before syncing dependencies, place those wheels at the exact relative paths (from the repository root), then run:

```bash
uv sync
```

## Quick usage

```python
from i2c_helper import MCP2221Driver
from i2c_helper.i2c.device import I2CDeviceInterface

driver = MCP2221Driver()
codec = I2CDeviceInterface(device_address=0x38, driver=driver, memory_address_size=1)

codec.write(0x12, b"\x01")
value = codec.read(0x12, buffer_size=1)
```

For A2B remote access:

```python
from i2c_helper import MCP2221Driver, I2COverDistanceWrapper

base_driver = MCP2221Driver()
remote_driver = I2COverDistanceWrapper(base_driver, slave_number=0, transceiver_address=0x68)
```

## SigmaStudio sequence execution

```python
from i2c_helper import MCP2221Driver
from i2c_helper.sigmastudio.sequence import Sequence

driver = MCP2221Driver()
sequences = Sequence.from_xml_file("program.xml", driver, replace_reads_with_noop=True)
for sequence in sequences:
    sequence.execute()
```

## Developer documentation

See `docs/developer.md` for development setup, packaging, and release details.
