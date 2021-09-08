from typing import Any
import numpy as np


def isnan(item: Any) -> bool:
    """Custom `isnan` that evaluates all `str` to False"""
    if isinstance(item, str):
        return False
    return np.isnan(item)
