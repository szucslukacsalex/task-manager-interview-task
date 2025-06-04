"""This module contains the database manager for the task management API."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from sqlmodel import SQLModel


class DatabaseManager:
    """Database manager for handling SQLAlchemy engine and sessions.

    This class manages the database connection, session creation, and table setup
    for the task management application.

    Attributes:
        database_url (str): The connection string for the database.
        engine: SQLAlchemy async engine instance.
        async_session: SQLAlchemy async session factory.

    Examples:
        ```
        db_manager = DatabaseManager()
        await db_manager.create_tables()
        async for session in db_manager.get_session():
            # Use session for database operations
        await db_manager.close()
        ```
    """

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./task_management.db"):
        self.database_url = database_url
        self.engine = create_async_engine(
            self.database_url, echo=False, future=True, pool_pre_ping=True
        )
        self.async_session = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create database tables if they do not exist.

        This method establishes a database connection and
        creates all tables defined in the SQLAlchemy models (Base.metadata).
        It executes the table creation process synchronously within
        an asynchronous context using the run_sync method.

        Returns:
            None

        Raises:
            SQLAlchemyError: If there is an error during the table creation process.
        """

        async with self.engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

    async def get_session(self):
        """Get an SQLAlchemy async session.

        This method creates and yields a new async database session
        for use in a dependency injection context.
        The session is automatically closed after use due to the context manager.

        Yields:
            AsyncSession: An asynchronous SQLAlchemy session object.

        Example:
            ```
            # In a FastAPI dependency
            async def get_db():
                async for session in database.get_session():
            ```
        """

        async with self.async_session() as session:
            yield session

    async def close(self):
        """Close the database connection by disposing of the engine.

        This method should be called when the application is shutting down
        to ensure all database connections are properly closed.

        Returns:
            None
        """

        await self.engine.dispose()
