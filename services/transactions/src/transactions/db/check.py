import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> None:
    database_url = os.environ["DATABASE_URL"]

    engine = create_async_engine(database_url, echo=True)

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT current_timestamp"))

            print("Database time", result.scalar_one())
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())