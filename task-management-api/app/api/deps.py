"""This module provides dependency functions for database session management and repository access
to be used with FastAPI's dependency injection system."""

from app.db.db_manager import DatabaseManager
from app.repository.task_repository import TaskRepository

db_manager = DatabaseManager()
task_repository = TaskRepository(db_manager)


async def get_db_session():
    """
    Yield an asynchronous database session for dependency injection.

    This function provides an async SQLAlchemy session using the DatabaseManager,
    suitable for use as a FastAPI dependency.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session object.
    """

    async for session in db_manager.get_session():
        yield session


def get_task_repository() -> TaskRepository:
    """
    Provides an instance of TaskRepository for dependency injection.

    Returns:
        TaskRepository: An instance of the TaskRepository class.
    """

    return task_repository
