"""This module defines enums for sorting tasks in the task management API."""

from enum import Enum

class SortOrder(str, Enum):
    """Enumeration for sort order.

    This enum defines the possible sorting orders for query results.

    Attributes:
        ASC (str): Ascending sort order.
        DESC (str): Descending sort order.
    """

    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    """Enumeration for sorting options.

    This enumeration defines the possible sorting criteria for tasks.

    Attributes:
        CREATION_DATE (str): Sort by the creation date of tasks.
        DUE_DATE (str): Sort by the due date of tasks.
    """
    CREATION_DATE = "creation_date"
    DUE_DATE = "due_date"
