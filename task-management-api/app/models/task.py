"""This module contains the task related models and enumerations for the task management API."""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses.

    It inherits from `str` and `Enum` to allow for string representation and
    comparison of task statuses.

    Attributes:
        PENDING: Indicates a task that has been created but not yet started.
        IN_PROGRESS: Indicates a task that is currently being worked on.
        COMPLETED: Indicates a task that has been finished.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(SQLModel):
    """TaskBase model serves as the base class for Task-related models in the application.

    This SQLModel-based class defines the core fields and validation logic for tasks
    in the task management system.

    Attributes:
        title (str): The title of the task. Must be between 1-200 characters.
        description (str): Optional description of the task. Maximum 1000 characters.
        due_date (Optional[datetime]): The date when the task is due. Cannot be in the past.
        status (TaskStatus): Current status of the task. Defaults to PENDING.

    Raises:
        ValueError: If title is empty or contains only whitespace.
        ValueError: If due_date is in the past.
    """

    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=500, description="Task description")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")

    def __init__(self, **data):
        if "title" in data and data["title"]:
            data["title"] = data["title"].strip()
            if not data["title"]:
                raise ValueError("Title cannot be empty or whitespace only")

        if "description" in data:
            data["description"] = (
                data["description"].strip() if data["description"] else ""
            )

        if (
            "due_date" in data
            and data["due_date"]
            and data["due_date"] < datetime.now(timezone.utc)
        ):
            raise ValueError("Due date cannot be in the past")

        super().__init__(**data)


class Task(TaskBase, table=True):
    """Task model representing a task in the database.

    This class defines the database schema for the Task table and includes
    fields for tracking a task's basic information and status.

    Attributes:
        id (Optional[int]): The primary key for the task.
        creation_date (datetime): The date and time when the task was created.
        title (str): The title of the task, between 1-200 characters.
        due_date (Optional[datetime]): The deadline for completing the task, if any.
        status (TaskStatus): The current status of the task (default: PENDING).
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Task ID")

    creation_date: datetime = Field(
        default=datetime.now(timezone.utc),
        description="Task creation timestamp",
        index=True,
    )

    title: str = Field(
        min_length=1, max_length=200, index=True, description="Task title"
    )

    due_date: Optional[datetime] = Field(
        default=None, index=True, description="Task due date"
    )

    status: TaskStatus = Field(
        default=TaskStatus.PENDING, index=True, description="Task status"
    )


class TaskPublic(TaskBase):
    """This model represents a public view of a task.

    This class extends TaskBase and is used for public representations of tasks,
    including automatically generated fields like ID and creation date.

    Attributes:
        id (int): Task ID, unique identifier for the task.
        creation_date (datetime): Task creation timestamp indicating when the task was created.
    """

    id: int = Field(description="Task ID")
    creation_date: datetime = Field(description="Task creation timestamp")


class TaskCreate(TaskBase):
    """This model is used for creating new tasks.

    This class inherits from TaskBase and is used to validate and parse
    task data during creation operations. It does not add any additional
    fields and omits the automatically generated fields like ID and creation date.

    Attributes:
        Inherits all attributes from TaskBase.
    """


class TaskUpdate(SQLModel):
    """This model is used for updating existing tasks.

    This class represents the schema for updating task properties. It allows for partial updates
    where only the specified fields will be modified.

    Attributes:
        title (Optional[str]): Task title with length between 1 and 200 characters.
            Will be stripped of leading/trailing whitespace.
        description (Optional[str]): Task description with maximum length of 500 characters.
            Will be stripped of leading/trailing whitespace.
        due_date (Optional[datetime]): Task due date, must be in the future.
        status (Optional[TaskStatus]): Task status enum value.

    Raises:
        ValueError: If title is empty or contains only whitespace.
        ValueError: If due date is set to a past date.
    """

    title: Optional[str] = Field(
        default=None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Task description"
    )
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    status: Optional[TaskStatus] = Field(default=None, description="Task status")

    def __init__(self, **data):
        if "title" in data and data["title"] is not None:
            data["title"] = data["title"].strip()
            if not data["title"]:
                raise ValueError("Title cannot be empty or whitespace only")

        if "description" in data and data["description"] is not None:
            data["description"] = data["description"].strip()

        if (
            "due_date" in data
            and data["due_date"]
            and data["due_date"] < datetime.now(timezone.utc)
        ):
            raise ValueError("Due date cannot be in the past")

        super().__init__(**data)
