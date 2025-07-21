
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from .logger import logger
from .schemas.database_schema import Base

# 注意：SQLite异步连接需要aiosqlite驱动
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./gtss.db"  # 异步SQLite连接字符串
# 如果是PostgreSQL应该使用：postgresql+asyncpg://user:password@localhost/dbname

# 全局变量，用于存储会话工厂
async_session_factory = None

async def create_table(engine: AsyncEngine) -> None:
    """ 创建表 """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_database_factory() -> None:
    """ 创建异步数据库会话工厂 """
    logger.info("初始化数据库连接")
    global async_session_factory
    # 如果会话工厂已经存在，则直接返回
    if async_session_factory is not None:
        return async_session_factory
    else:
        engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True)
        # 创建表
        await create_table(engine)
        async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) # type: ignore

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session_factory() as session: # type: ignore
        try:
            yield session  # 这里返回会话对象
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()