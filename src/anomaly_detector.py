class AnomalyDetector:
    """Detects basic anomalies in service telemetry."""

    def __init__(
        self,
        response_time_threshold=500,
        cpu_threshold=80,
        memory_threshold=80
    ):
        self.response_time_threshold = response_time_threshold
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def detect(self, record):
        reasons = []

        if record["response_time_ms"] > self.response_time_threshold:
            reasons.append("High response time")

        if record["cpu_percent"] > self.cpu_threshold:
            reasons.append("High CPU utilization")

        if record["memory_percent"] > self.memory_threshold:
            reasons.append("High memory utilization")

        if record["log_level"] == "ERROR":
            reasons.append("Error log detected")

        if not reasons:
            return None

        return {
            "timestamp": record["timestamp"],
            "service": record["service"],
            "type": "ANOMALY",
            "reasons": reasons,
            "source": record
        }
