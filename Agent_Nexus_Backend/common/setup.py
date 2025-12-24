from setuptools import setup, find_packages

setup(
    name="agent_nexus_common",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy",
        "psycopg2-binary",
        "httpx",
        "redis",
        "qdrant-client",
        "dramatiq",
        "python-dotenv",
        "langgraph",
        "langchain-core"
    ],
    python_requires=">=3.10",
)