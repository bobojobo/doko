from typing import AsyncGenerator
from functools import cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from doko import logging, exception, settings


def engine_from_env(test_connection: bool = True) -> AsyncEngine:
    """Creates an SQLAlchemy engine from the variables in the .env file."""
    engine = create_async_engine(settings.DB_URL)  # , echo='debug'
    if test_connection:
        _test_connection(engine)
    return engine


def _test_connection(engine: AsyncEngine) -> None:
    """Raises an error if the engine can't connect to the database."""
    try:
        engine.connect()
    except OperationalError as e:
        # Avoiding the mile-long tracback. Error is quite clear.
        import sys

        sys.tracebacklimit = 0
        raise exception.NoDatabaseConnection(exception.NoDatabaseConnection.doc) from e


@cache
def engine() -> AsyncEngine:
    """Cached engine"""
    engine = engine_from_env()
    return engine


get_session = async_sessionmaker(bind=engine(), autocommit=False, autoflush=False, expire_on_commit=False)


async def session() -> AsyncGenerator[AsyncSession, None]:
    """Session generator/ factory"""
    session_ = get_session()
    try:
        logging.debug(f"yielding session: {session_}")
        yield session_
    finally:
        logging.debug(f"closing session: {session_}")
        await session_.close()
