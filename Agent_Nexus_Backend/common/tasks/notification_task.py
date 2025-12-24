import dramatiq


@dramatiq.actor(queue_name="notifications")
def send_notification(event: dict) -> None:
    target = event.get("target")
    message = event.get("message")

    if not target or not message:
        raise RuntimeError("Invalid notification payload")

    print(f"[NOTIFICATION] {target}: {message}")
