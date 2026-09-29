# Developer Documentation

## Scope

This document describes the current repository layout and development workflow for:

- Packaging `i2c-helper` from `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper`
- Working with MCP2221 and A2B wrapper code in `i2c_helper.i2c`
- Working with SigmaStudio parsing and execution in `i2c_helper.sigmastudio`

## Repository layout

- `/home/runner/work/I2C-Helper/I2C-Helper/pyproject.toml`  
  Build backend (`hatchling`), package metadata, and dependency source mapping.
- `/home/runner/work/I2C-Helper/I2C-Helper/uv.lock`  
  Locked dependency graph.
- `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper/__init__.py`  
  Public top-level exports (`I2CDriver`, `MCP2221Driver`, `I2COverDistanceWrapper`, `I2CDeviceInterface`).
- `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper/i2c/`  
  Core drivers and transaction helper.
- `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper/registers/`  
  A2B register constants.
- `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper/sigmastudio/`  
  XML sequence commands and execution.

## Local dependency requirement (gap fix)

`pyproject.toml` maps `keygen` and `diag-test-common` to local wheel files in `../../Local Libraries/`.

To get a reproducible setup, ensure these exact files exist before running dependency sync:

- `../../Local Libraries/keygen-1.2.0-py3-none-any.whl`
- `../../Local Libraries/diag_test_common-0.0.9-py3-none-any.whl`

Then run:

```bash
uv sync
```

Without these wheel files, environment setup fails because the configured source paths cannot be resolved.

## Build workflow

From repository root:

```bash
uv build
```

The wheel target is configured in `pyproject.toml`:

- `[tool.hatch.build.targets.wheel]`
- `packages = ["src/i2c_helper"]`

## Versioning workflow

Version is currently duplicated in:

- `/home/runner/work/I2C-Helper/I2C-Helper/pyproject.toml` (`[project].version`)
- `/home/runner/work/I2C-Helper/I2C-Helper/src/i2c_helper/__version__.py`

When cutting a release, update both locations in the same change to keep package metadata and runtime version aligned.

## Notes on validation

There are currently no test scripts, CI workflow files, or lint configuration files in this repository snapshot.  
After modifying Python modules, run the project’s existing checks available in your environment (for example, import/packaging checks) and keep changes scoped to this package.
