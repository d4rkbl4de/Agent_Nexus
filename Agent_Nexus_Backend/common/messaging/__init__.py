
from common.messaging.broker import message_broker, MessageBroker
from common.messaging.publisher import event_publisher, EventPublisher
from common.messaging.consumer import event_consumer, EventConsumer
from common.messaging.schemas import BaseMessage, EventPriority

class MessagingManifest:
    def __init__(self):
        self.broker = message_broker
        self.publisher = event_publisher
        self.consumer = event_consumer

    async def initialize(self):
        await self.broker.connect()
        await self.consumer.start_listening()

    async def shutdown(self):
        await self.consumer.stop_listening()
        await self.broker.disconnect()

messaging_manifest = MessagingManifest()

__all__ = [
    "message_broker",
    "MessageBroker",
    "event_publisher",
    "EventPublisher",
    "event_consumer",
    "EventConsumer",
    "BaseMessage",
    "EventPriority",
    "messaging_manifest"
]