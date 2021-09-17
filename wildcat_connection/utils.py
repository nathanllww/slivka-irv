from typing import Any, Callable
import numpy as np


def isnan(item: Any) -> bool:
    """Custom `isnan` that evaluates all `str` to False"""
    if isinstance(item, str):
        return False
    return np.isnan(item)


def wc_update_catcher(func: Callable) -> Callable:
    def decorator(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ParsingException(f"""
Error encountered when parsing CSV from Wildcat Connection.

The WC CSV format may have changed in an update.
If this is the case, open an issue on the github repo:
https://github.com/nathanllww/slivka-irv/issues/new

Error that occurred: {str(e)}
""")

    return decorator


class ParsingException(Exception):
    """Exception for when the WildcatConnectionCSV parsing fails"""
    pass
