"""This module defines TaskRepository, which provides methods to interact with the database."""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc, asc

from app.db.db_manager import DatabaseManager
from app.models.task import TaskCreate, TaskPublic, Task, TaskStatus, TaskUpdate
from app.models.sort_enum import SortBy, SortOrder


class TaskRepository:
    """Repository class for handling task-related database operations.

    This class provides methods to create, retrieve, update and delete tasks in the database.
    It uses SQLAlchemy's async ORM to interact with the database.

    Attributes:
        db_manager (DatabaseManager): The database manager to handle database connections.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def create_task(
        self, task_data: TaskCreate, session: AsyncSession
    ) -> TaskPublic:
        """Creates a new task in the database.

        Args:
            task_data (TaskCreate): The task data model containing information for the new task.
            session (AsyncSession): The database session to use for the transaction.

        Returns:
            TaskPublic: The created task model that's ready for public consumption.

        Raises:
            SQLAlchemyError: If there's a database error during task creation.
            ValidationError: If the provided task data does not conform to the expected model.
        """

        db_task = Task.model_validate(task_data)

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        return TaskPublic.model_validate(db_task)

    async def get_task(
        self, task_id: int, session: AsyncSession
    ) -> Optional[TaskPublic]:
        """Retrieves a task by its ID.

        Args:
            task_id (int): The ID of the task to retrieve.
            session (AsyncSession): The database session to use for the transaction.

        Returns:
            Optional[TaskPublic]: The task model if found, otherwise None.

        Raises:
            SQLAlchemyError: If there's a database error during task retrieval.
            ValidationError: If the retrieved task does not conform to the expected model.
        """

        task = await session.get(Task, task_id)

        if task:
            return TaskPublic.model_validate(task)
        return None

    async def get_tasks(
        self,
        session: AsyncSession,
        status: Optional[TaskStatus] = None,
        due_date: Optional[datetime] = None,
        sort_by: SortBy = SortBy.CREATION_DATE,
        sort_order: SortOrder = SortOrder.ASC,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[TaskPublic]:
        """Retrieves a list of tasks with optional filtering and sorting.

        Args:
            session (AsyncSession): The database session to use for the transaction.
            status (Optional[TaskStatus], optional): Filter tasks by their status. Defaults to None.
            due_date (Optional[datetime], optional): Filter tasks by their due date.
                Defaults to None.
            sort_by (SortBy, optional): The field to sort results by.
                Defaults to SortBy.CREATION_DATE.
            sort_order (SortOrder, optional): The order to sort results. Defaults to SortOrder.ASC.
            limit (Optional[int], optional): Maximum number of tasks to return. Defaults to None.
            offset (int, optional): Number of tasks to skip for pagination. Defaults to 0.

        Returns:
            List[TaskPublic]: A list of task models that match the criteria.

        Raises:
            SQLAlchemyError: If there's a database error during task retrieval.
            ValidationError: If the retrieved tasks do not conform to the expected model.
        """

        statement = select(Task)

        if status:
            statement = statement.where(Task.status == status)
        if due_date:
            statement = statement.where(Task.due_date == due_date)

        sort_column = getattr(Task, sort_by.value)
        if sort_order == SortOrder.DESC:
            statement = statement.order_by(desc(sort_column))
        else:
            statement = statement.order_by(asc(sort_column))

        if offset > 0:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)

        tasks = await session.scalars(statement)
        tasks = tasks.all()

        return [TaskPublic.model_validate(task) for task in tasks]

    async def update_task(
        self, task_id: int, task_update: TaskUpdate, session: AsyncSession
    ) -> Optional[TaskPublic]:
        """Updates an existing task in the database.

        Args:
            task_id (int): The ID of the task to update.
            task_update (TaskUpdate): The task update model containing the fields to be updated.
            session (AsyncSession): The database session to use for the transaction.

        Returns:
            Optional[TaskPublic]: The updated task model if the task was found and updated,
                otherwise None.

        Raises:
            SQLAlchemyError: If there's a database error during task update.
            ValidationError:
                If the provided task update data does not conform to the expected model.
        """

        task = await session.get(Task, task_id)

        if not task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return TaskPublic.model_validate(task)

    async def delete_task(self, task_id: int, session: AsyncSession) -> bool:
        """Deletes a task by its ID.

        Args:
            task_id (int): The ID of the task to delete.
            session (AsyncSession): The database session to use for the transaction.

        Returns:
            bool: True if the task was successfully deleted, False if the task was not found.
        
        Raises:
            SQLAlchemyError: If there's a database error during task deletion.
            ValidationError: If the task ID does not conform to the expected model.
        """

        task = await session.get(Task, task_id)

        if not task:
            return False

        await session.delete(task)
        await session.commit()
        return True
