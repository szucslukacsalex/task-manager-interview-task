"""This module sets up the FastAPI app, configures CORS middleware,
manages the application lifespan, and includes the tasks router."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import db_manager
from app.api.endpoints.tasks import tasks_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manages the application lifespan events.

    This function creates database tables on startup and closes the database connection on shutdown.

    Args:
        _: The FastAPI application instance (unused).

    Yields:
        None
    """

    await db_manager.create_tables()
    yield
    await db_manager.close()


app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with FastAPI and SQLite",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint for the Task Management API.

    Returns:
        dict: A welcome message for the API root.
    """

    return {"message": "Welcome to the Task Management API!"}
