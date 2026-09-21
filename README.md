# GitHub Challenge

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey there!

Your challenge is ready.
Follow the instructions provided for this challenge and complete the required tasks in this repository.

Make sure your work is committed and pushed to your repository before submission.

Good luck!

Part 1 --------------------------------------------------->

## Operational Data Analysis

The repository contains a small synthetic dataset for a single service, stored in service_data.json  . Each record represents one observation at a point in time.

### 1. Metrics fields
The numeric telemetry values are the metrics:
 response_time_ms: latency of the service request in milliseconds.
cpu_percent: percentage of CPU utilization.
memory_percent: percentage of memory utilization.
service: identifies the service producing the observation, but it is not a metric itself.

### 2. Log information fields
The log-related fields are:
log_level: severity such as 'INFO'or 'ERROR'.
message: a free-text log message describing what happened.
These fields provide operational context and indicate the outcome or state of the service at that timestamp.

### 3. How timestamps are used
The timestamp field is an ISO-8601 datetime string in the form 'YYYY-MM-DDTHH:MM:SS'. The records are sampled once per minute across a 10-minute window, starting at '2026-09-20T10:00:00' and extending through '2026-09-20T10:09:00'. This sequence allows trend analysis over time and helps identify if latency or resource usage spikes at specific times.

### 4. Normal behaviour
The observations that appear normal are the first, second, third, fourth, fifth, seventh, eighth, ninth, and tenth records (with the exception of the two clear anomaly events). These records have:
response_time_ms between roughly 120 and 150 ms,
cpu_percent between about 42% and 58%,
memory_percen between about 51% and 57%,
log_level of 'INFO', and
- messages indicating successful payment processing.
This pattern suggests stable service health and expected capacity use.

### 5. Unusual behaviour
The unusual observations are the 6th and 7th records, around `2026-09-20T10:05:00` and 2026-09-20T10:06:00:
- response_time_ms jumps to 610 ms and 640 ms,
- cpu_percent rises to 75% and 94%,
- memory_percent rises to 70% and 91%,
- log_level becomes ERROR, and
- the messages mention timeouts ("Payment service timeout" and "Database connection timeout").
These are strong indicators of degraded service performance and possible resource saturation or backend dependency failure. They clearly deviate from the otherwise healthy baseline.

Overall, the dataset shows stable operation for most of the observed period and a short burst of abnormal behavior associated with high latency, elevated CPU and memory, and error-level logs.

Part 4 --------------------------------------------------->

## AIOps Event Flow Verification

The event-processing workflow uses the following components:

- **Event:** an anomaly record created by `AnomalyDetector.detect()` when a service record exceeds a threshold or has an `ERROR` log level. It contains the timestamp, service, anomaly type, reasons, and source record.
- **Producer:** `EventProducer`, which accepts a detected event and publishes it to its configured topic.
- **Topic:** the in-memory `EventTopic` named `anomaly-events`. It stores published events in message order.
- **Consumer:** `EventConsumer`, which reads the messages from the same topic.
- **Downstream AIOps component:** the consumer-side processing represented by `consumer.consume()` in `run_pipeline()`. The returned `events_consumed` collection is the processed output available to downstream handling and reporting.

### Execution result

Command executed:

```text
python -m src.aiops_pipeline
```

Observed output:

```text
Records processed: 10
Anomalies detected: 2
Events consumed: 2
```

The two events were produced for `2026-09-20T10:05:00` and `2026-09-20T10:06:00`. The first event contained `High response time` and `Error log detected`. The second contained `High response time`, `High CPU utilization`, `High memory utilization`, and `Error log detected`.

This verifies the complete flow: the detector identifies an anomaly, `EventProducer` receives it, the producer publishes it to the `anomaly-events` topic, `EventConsumer` reads it from that same topic, and the consumed event is returned by the pipeline as downstream AIOps output. The automated verification also passed with `9 passed` using `pytest -q`.


