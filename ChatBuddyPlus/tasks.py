import dramatiq
from dramatiq.brokers.redis import RedisBroker
from common.config.settings import settings
from common.config.logging_config import logger

broker = RedisBroker(url=settings().REDIS_URL)
dramatiq.set_broker(broker)

@dramatiq.actor
def process_chat_request(user_id: str, prompt: str, conversation_id: str):
    logger.info("ChatBuddy+ Worker: Processing contextual chat request.", 
                extra={"user_id": user_id, "conversation": conversation_id})
    
    try:
        import time
        time.sleep(1) 
        
        response = f"Contextual response generated for prompt: '{prompt[:30]}...'"
        logger.info("ChatBuddy+ request processed successfully.")
        return response
    except Exception as e:
        logger.error(f"ChatBuddy+ request failed: {str(e)}", exc_info=True)
        raise