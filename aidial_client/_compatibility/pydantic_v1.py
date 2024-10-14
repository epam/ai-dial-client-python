try:
    from pydantic.v1 import *  # type: ignore # noqa
except ImportError:
    from pydantic import *  # type: ignore # noqa
