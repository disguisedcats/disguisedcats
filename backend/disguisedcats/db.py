from motor.motor_asyncio import AsyncIOMotorClient

from disguisedcats.settings import settings
from disguisedcats.log import logger

db_client: AsyncIOMotorClient | None = None


async def get() -> AsyncIOMotorClient:
    db_name = settings.DB_NAME
    return db_client[db_name]


async def connect():
    global db_client
    if db_client:
        logger.warning("DB client is already initialized.")
    try:
        db_client = AsyncIOMotorClient(
            settings.DB_URL,
            username=settings.DB_USER,
            password=settings.DB_PASSWORD.get_secret_value(),
            uuidRepresentation="standard",
        )
        logger.info("Connected to DB.")
    except Exception as e:
        logger.exception("Could not connect to DB: %s", e)
        raise


async def close():
    global db_client
    if db_client is None:
        logger.warning("DB connection is `None`, nothing to close.")
        return
    db_client.close()
    db_client = None
    logger.info("DB connection closed.")


async def ping(*_):
    try:
        await db_client.admin.command("ping")
    except Exception as e:
        logger.error(e)
        raise
