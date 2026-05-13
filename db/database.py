import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.models import Base

engine = create_async_engine("sqlite+aiosqlite:///db/db.db", echo=True)
session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
