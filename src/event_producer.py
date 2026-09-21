try:
    from .event_topic import EventTopic
except ImportError:  # pragma: no cover - support direct script execution
    from event_topic import EventTopic


class EventProducer:
    """Publishes anomaly events to an in-memory topic."""

    def __init__(self, topic: EventTopic):
        self.topic = topic

    def publish(self, event):
        if not event:
            return False

        self.topic.publish(event)
        return True
