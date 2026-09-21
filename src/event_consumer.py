try:
    from .event_topic import EventTopic
except ImportError:  # pragma: no cover - support direct script execution
    from event_topic import EventTopic


class EventConsumer:
    """Consumes events from an in-memory topic."""

    def __init__(self, topic: EventTopic):
        self.topic = topic

    def consume(self):
        return self.topic.get_messages()
