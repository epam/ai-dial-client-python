from typing import Literal


class NotGiven:
    """
    A sentinel singleton class used to distinguish omitted keyword arguments
    from those passed in with the value None
    (which may have different behavior).
    """

    def __bool__(self) -> Literal[False]:
        return False


NOT_GIVEN = NotGiven()
