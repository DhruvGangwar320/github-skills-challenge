# GitHub Challenge

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey there!

Your challenge is ready.
Follow the instructions provided for this challenge and complete the required tasks in this repository.

Make sure your work is committed and pushed to your repository before submission.

Good luck!

Part 1 --------------------------------------------------->
## Scenario Overview

### Service Being Monitored
The assessment monitors a synthetic **payment-service**, a backend service responsible for
processing payment requests. Each record in `data/service_data.json` represents a snapshot of
the service's telemetry at a given minute, including response time, CPU utilization, memory
utilization, and an accompanying log entry (level and message).

### Operational Problem Being Addressed
The scenario simulates a service degradation event: for most of the observed period the service
behaves normally (fast response times, moderate CPU/memory, `INFO` logs), but at two points in
time (`10:05:00` and `10:06:00`) the service experiences a spike in response time, CPU, and
memory usage, alongside `ERROR`-level logs (a timeout and a database connection failure). This
represents the kind of transient performance incident that operations teams need to detect and
respond to quickly, before it escalates or impacts users.

### Purpose of AIOps in This Assessment
AIOps (AI for IT Operations) aims to reduce the manual effort involved in monitoring, detecting,
and responding to operational issues by automating the analysis of metrics and logs. In this
assessment, the AIOps workflow automatically inspects each telemetry record, flags anomalous
behaviour based on defined thresholds (response time, CPU, memory) and log severity, and
streams the resulting anomaly events through a simulated producer/topic/consumer pipeline to a
downstream AIOps component. This demonstrates, end to end, how raw operational data can be
turned into actionable, explainable alerts without manual log review.

TASK 2----------------------------------------------------->
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


## Task 3: Anomaly Detection

### Detection Mechanism Used
Anomaly detection is performed by the provided `AnomalyDetector` class
(`src/anomaly_detector.py`), configured with the following thresholds:
- `response_time_threshold = 500` ms
- `cpu_threshold = 80` %
- `memory_threshold = 80` %

For each record, `detect()` checks response time, CPU, and memory against these thresholds, and
also flags any record with `log_level == "ERROR"`. A record is returned as an anomaly event if
one or more of these conditions is true; otherwise `detect()` returns `None`. This mechanism was
used as provided, without modification, and run against all 10 records via
`python src/aiops_pipeline.py`.

### Anomalies Detected
The detector correctly identified 2 anomalies out of 10 records:

| Timestamp           | Reasons                                                                 |
|----------------------|--------------------------------------------------------------------------|
| 2026-09-20T10:05:00 | High response time, Error log detected                                   |
| 2026-09-20T10:06:00 | High response time, High CPU utilization, High memory utilization, Error log detected |

### Relevant Metric/Log Information
- `10:05:00`: response time 610ms (threshold 500ms) and an `ERROR` log ("Payment service
  timeout"). CPU (75%) and memory (70%) stayed just under their thresholds, so those weren't
  flagged as individual reasons.
- `10:06:00`: response time 640ms, CPU 94%, memory 91% — all three metric thresholds breached,
  plus an `ERROR` log ("Database connection timeout"). This was the more severe of the two
  anomalies, flagged on all four possible reasons.

### Expected Anomalies Missed
None. Both records that visually stood out as abnormal in the raw data (Task 2) were
successfully detected.

### Normal Events Incorrectly Flagged
None. All 8 `INFO`-level records with baseline metric values were correctly left unflagged
(`detect()` returned `None`).

### Limitation / Possible Improvement
The detector uses fixed, static thresholds (e.g. 500ms response time, 80% CPU/memory) applied
uniformly regardless of the service's normal operating range. This works well for this dataset,
where the anomaly is a large, obvious spike, but it wouldn't catch more subtle degradations
(e.g. a sustained rise to 70% CPU that's still abnormal for a service that normally runs at
45%), and it could produce false positives for services whose normal baseline is naturally
closer to the thresholds. A possible improvement would be to use adaptive or statistical
thresholds (e.g. based on a rolling mean/standard deviation per service) rather than fixed
global values.

## Task 4: Event Streaming Workflow

### Components and Their Roles
- **Producer** (`src/event_producer.py` — `EventProducer`): receives an anomaly event from the
  detector and publishes it to a topic. If given an empty/falsy event, it returns `False` and
  publishes nothing; otherwise it calls `topic.publish(event)` and returns `True`.
- **Topic** (`src/event_topic.py` — `EventTopic`): an in-memory simulation of a streaming topic.
  It holds a `name` and a list of `messages`. `publish()` appends an event to the list,
  `get_messages()` returns a copy of all messages, and `clear()` empties it.
- **Consumer** (`src/event_consumer.py` — `EventConsumer`): reads events from a topic via
  `consume()`, which calls `topic.get_messages()` and returns everything currently on the topic.
- **Event/message**: a dictionary produced by `AnomalyDetector.detect()`, containing
  `timestamp`, `service`, `type` ("ANOMALY"), `reasons` (list of triggered conditions), and
  `source` (the original record).

### How the Flow Was Verified
In `src/aiops_pipeline.py::run_pipeline()`:
1. A single `EventTopic("anomaly-events")` is created.
2. An `EventProducer` and `EventConsumer` are both wired to that **same** topic instance.
3. Each record is passed to `detector.detect()`. If an anomaly is returned, it's immediately
   published via `producer.publish(event)`.
4. After all records are processed, `consumer.consume()` is called once to retrieve every
   published event from the topic.

This was confirmed with:
```bash
python -m pytest tests/test_aiops_pipeline.py::test_producer_publishes_event tests/test_aiops_pipeline.py::test_consumer_receives_event -v
```
Both tests passed — `test_producer_publishes_event` confirms a published event appears on the
topic (`len(topic.get_messages()) == 1`), and `test_consumer_receives_event` confirms the
consumer can retrieve an event that was published to its topic.

### End-to-End Confirmation
Running the full pipeline (`python src/aiops_pipeline.py`) confirmed that both anomaly events
detected in Task 3 successfully travelled through the entire flow: **detector → producer →
topic → consumer**, with `events_consumed` matching `anomalies_detected` exactly (2 events, same
timestamps and reasons in both).


TASK 5 --------------------------------------------->

**Re-execution and verification:** After the fix, the module imports cleanly and the pipeline
runs end to end:

```bash
python src/aiops_pipeline.py
```
Output confirmed 10 records processed, 2 anomalies detected, and 2 events consumed — matching
the results in Task 3 and Task 4.

The fix was also verified against the full test suite:
```bash
python -m pytest -v
```
Result: **9 passed** (previously only the 4 tests in `calculations_test.py` could run; all 5
tests in `test_aiops_pipeline.py` failed at collection due to the syntax error).

### Scope of Changes
Only `src/aiops_pipeline.py` was modified (a single line). No other files, and no part of the
provided detection, producer, consumer, or topic architecture, were changed — the correction
worked entirely within the existing design as required.



TASK 7 ------------------------->
@DhruvGangwar320 ➜ /workspaces/github-skills-challenge (main) $ python src/aiops_pipeline.py
==================================================
AIOps Pipeline Result
==================================================
Records processed: 10
Anomalies detected: 2
Events consumed: 2

Detected Events:

Service: payment-service
Timestamp: 2026-09-20T10:05:00
Type: ANOMALY
Reasons: High response time, Error log detected

Service: payment-service
Timestamp: 2026-09-20T10:06:00
Type: ANOMALY
Reasons: High response time, High CPU utilization, High memory utilization, Error log detected
@DhruvGangwar320 ➜ /workspaces/github-skills-challenge (main) $ 


### Verification Against Required Steps
1. **Operational data processed** — all 10 records from `data/service_data.json` were read and
   passed through the detector (`records_processed: 10`).
2. **Anomalous behaviour detected** — 2 of the 10 records were flagged by `AnomalyDetector`.
3. **Anomaly event generated** — each flagged record produced a structured event dict
   (`timestamp`, `service`, `type`, `reasons`, `source`).
4. **Event published** — each event was passed to `EventProducer.publish()` and added to the
   shared `EventTopic`.
5. **Event consumed** — `EventConsumer.consume()` retrieved all messages from the topic.
6. **Event processed successfully** — the pipeline output formats each consumed event with
   service, timestamp, type, and reasons, matching what was detected and published.
7. **Final output represents the detected operational issue** — the two reported anomalies
   correspond exactly to the two abnormal records identified during manual inspection in Task 2
   (the `10:05:00` and `10:06:00` timeout/error records).

This confirms the complete flow — **Operational Data → Anomaly Detection → Event → Producer →
Topic → Consumer → AIOps Output** — executes correctly with the fix from Task 5 applied.
   pip install -r requirements.txt
