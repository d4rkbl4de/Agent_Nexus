from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from AutoAgent_Hub.api.routes import router
from common.config.logging_config import logger

app = FastAPI(
    title="AutoAgent Hub Lobe API",
    description="The flagship Agent Lobe for Hierarchical Planning and Orchestration.",
    version="1.0.0"
)

logger.info("AutoAgent Hub Lobe starting up.")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/autoagenthub", tags=["AutoAgentHub"])