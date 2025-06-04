"""This module defines the API endpoints for task management operations."""

from typing import List, Optional
from datetime import datetime

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.models.task import (
    TaskPublic,
    TaskCreate,
    TaskStatus,
    TaskUpdate,
    TaskSuggestion,
)
from app.models.sort_enum import SortBy, SortOrder
from app.api.routers import tasks_router
from app.api.deps import get_db_session, get_task_repository, get_suggestion_service
from app.repository.task_repository import TaskRepository
from app.services.smart_suggestion_service import SmartSuggestionService


@tasks_router.post(
    "/tasks", response_model=TaskPublic, status_code=201, summary="Create a new task"
)
async def post_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_db_session),
    repository: TaskRepository = Depends(get_task_repository),
):
    """Create a new task.

    Args:
        task_data: The data for the task to create.
        session: Database session dependency.
        repository: Task repository dependency.

    Returns:
        The created task as a TaskPublic model.

    Raises:
        HTTPException: If validation or database errors occur.
    """

    try:
        return await repository.create_task(task_data, session)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@tasks_router.get(
    "/tasks",
    response_model=List[TaskPublic],
    summary="Get all tasks with filtering and sorting",
)
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    due_date: Optional[datetime] = Query(None, description="Filter by due date"),
    sort_by: SortBy = Query(SortBy.CREATION_DATE, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Maximum number of tasks to return"
    ),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    session: AsyncSession = Depends(get_db_session),
    repository: TaskRepository = Depends(get_task_repository),
):
    """Retrieve all tasks with optional filtering and sorting.

    Args:
        status: Optional filter for task status.
        due_date: Optional filter for due date.
        sort_by: Field to sort by.
        sort_order: Sort order (ascending or descending).
        limit: Maximum number of tasks to return.
        offset: Number of tasks to skip.
        session: Database session dependency.
        repository: Task repository dependency.

    Returns:
        A list of TaskPublic models.

    Raises:
        HTTPException: If validation or database errors occur.
    """

    try:
        return await repository.get_tasks(
            session=session,
            status=status,
            due_date=due_date,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@tasks_router.get(
    "/tasks/suggest",
    response_model=List[TaskSuggestion],
    summary="Get smart task suggestions",
)
async def get_smart_suggestions(
    limit: int = Query(
        5, ge=1, le=10, description="Maximum number of suggestions to return"
    ),
    session: AsyncSession = Depends(get_db_session),
    service: SmartSuggestionService = Depends(get_suggestion_service),
):
    """
    Generate smart task suggestions.

    This endpoint provides a list of smart suggestions for tasks,
    based on the current user's context and preferences.

    Args:
        limit: Maximum number of suggestions to return. Must be between 1 and 10. Defaults to 5.
        session: Database session dependency.
        service: Service for generating smart suggestions.

    Returns:
        List[TaskSuggestion]: A list of suggested tasks.

    Raises:
        HTTPException: If validation fails or if there are database errors.
    """

    try:
        return await service.generate_suggestions(session, limit)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@tasks_router.get(
    "/tasks/{task_id}", response_model=TaskPublic, summary="Get a specific task by ID"
)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_db_session),
    repository: TaskRepository = Depends(get_task_repository),
):
    """Retrieve a specific task by its ID.

    Args:
        task_id: The ID of the task to retrieve.
        session: Database session dependency.
        repository: Task repository dependency.

    Returns:
        The requested task as a TaskPublic model.

    Raises:
        HTTPException: If the task is not found or if validation/database errors occur.
    """

    try:
        task = await repository.get_task(task_id, session)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@tasks_router.patch(
    "/tasks/{task_id}", response_model=TaskPublic, summary="Update a task"
)
async def patch_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_db_session),
    repository: TaskRepository = Depends(get_task_repository),
):
    """Update an existing task.

    Args:
        task_id: The ID of the task to update.
        task_update: The update data for the task.
        session: Database session dependency.
        repository: Task repository dependency.

    Returns:
        The updated task as a TaskPublic model.

    Raises:
        HTTPException: If the task is not found or if validation/database errors occur.
    """

    try:
        updated_task = await repository.update_task(task_id, task_update, session)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@tasks_router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_db_session),
    repository: TaskRepository = Depends(get_task_repository),
):
    """Delete a task by its ID.

    Args:
        task_id: The ID of the task to delete.
        session: Database session dependency.
        repository: Task repository dependency.

    Raises:
        HTTPException: If the task is not found or if validation/database errors occur.
    """

    try:
        deleted = await repository.delete_task(task_id, session)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
