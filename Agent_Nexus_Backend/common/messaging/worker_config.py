import dramatiq
from dramatiq.middleware import Retries, TimeLimit, ShutdownNotifications


def configure_workers(
    max_retries: int = 3,
    time_limit_ms: int = 300_000,
) -> None:
    broker = dramatiq.get_broker()
    broker.add_middleware(Retries(max_retries=max_retries))
    broker.add_middleware(TimeLimit(time_limit=time_limit_ms))
    broker.add_middleware(ShutdownNotifications())
