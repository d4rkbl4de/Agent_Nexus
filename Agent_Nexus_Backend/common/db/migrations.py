import os
import sys
from alembic.config import Config
from alembic import command
from common.config.logging import logger

def run_migrations():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        alembic_cfg_path = os.path.join(base_dir, "alembic.ini")
        
        if not os.path.exists(alembic_cfg_path):
            logger.error(f"MIGRATION_ERROR | alembic.ini not found at {alembic_cfg_path}")
            return

        alembic_cfg = Config(alembic_cfg_path)
        
        # Rule 5: Ensure common DB migrations are tracked globally
        logger.info("MIGRATION_START | Running Alembic 'upgrade head'")
        command.upgrade(alembic_cfg, "head")
        logger.info("MIGRATION_SUCCESS | Database schema is up to date")
        
    except Exception as e:
        logger.critical(f"MIGRATION_FATAL | Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()