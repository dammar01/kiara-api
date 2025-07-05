from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Callable, Dict, AsyncGenerator
from contextlib import asynccontextmanager

from app.core.settings import settings

async_engines: Dict[str, any] = {}
async_session_factories: Dict[str, async_sessionmaker] = {}

for db_name in settings.db_names:
    engine = create_async_engine(
        settings.get_db_url(db_name=db_name, sync=False),
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )
    async_engines[db_name] = engine
    async_session_factories[db_name] = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_session_factory(db_name: str) -> async_sessionmaker:
    if db_name not in async_session_factories:
        raise ValueError(f"Database '{db_name}' tidak terdaftar")
    return async_session_factories[db_name]


@asynccontextmanager
async def get_async_session(db_name: str) -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_session_db(db_name: str) -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db(db_name: str) -> Callable:
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        async for session in get_session_db(db_name):
            yield session

    return _get_db


async def close_all_engines():
    for engine in async_engines.values():
        await engine.dispose()


Base = declarative_base()
