from types import TracebackType
from typing import Optional

from i2c_helper import I2CDriver, I2COverDistanceWrapper


class BulkTransaction:
    def __init__(self, driver: I2CDriver):
        self._driver = driver

    def __enter__(self):
        self._driver.transaction().acquire()

        if isinstance(self._driver, I2COverDistanceWrapper):
            self._driver.keep_current_node_selected()

        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[
        TracebackType]):

        if isinstance(self._driver, I2COverDistanceWrapper):
            self._driver.deselect_node()

        self._driver.transaction().release()
