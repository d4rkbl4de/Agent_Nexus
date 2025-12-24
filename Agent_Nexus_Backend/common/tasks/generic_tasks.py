import dramatiq


@dramatiq.actor(queue_name="system")
def health_check(payload: dict) -> dict:
    return {
        "status": "ok",
        "payload": payload,
    }


@dramatiq.actor(queue_name="system")
def echo(payload: dict) -> dict:
    return payload
