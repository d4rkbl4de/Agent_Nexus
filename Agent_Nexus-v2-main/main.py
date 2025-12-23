import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from common.logger import logger
from common.config.settings import settings
from common.db.postgres import db_client
from common.data_sdk.vector_client import vector_client
from gateway.router import router as gateway_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NEXUS_BOOT: Initializing infrastructure...")
    try:
        await db_client.connect()
        await vector_client.connect()
        logger.info("NEXUS_BOOT: Infrastructure online.")
        yield
    finally:
        logger.info("NEXUS_SHUTDOWN: Cleaning up resources...")
        await db_client.disconnect()
        await vector_client.disconnect()
        logger.info("NEXUS_SHUTDOWN: Offline.")

app = FastAPI(
    title="Agent Nexus Hive Mind",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.WORKER_COUNT
    )