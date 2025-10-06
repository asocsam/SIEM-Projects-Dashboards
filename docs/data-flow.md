# Data Flow & Architecture

The SIEM pipeline mirrors a hybrid enterprise environment with both cloud and on-prem systems. The components communicate as shown below:

```text
[Simulator] --> [Kafka] --> [Logstash] --> [Elasticsearch]
        \                       \--> [Splunk HEC]
         \--> [JSON drop folder]
```

## 1. Data Generation

The simulator (`scripts/simulations/generate_events.py`) produces JSON documents that represent the most common telemetry families used in detections:

- **AWS CloudTrail** – instance creation, IAM activity, and VPC flow snippets.
- **Windows Security & Sysmon** – authentication events, process creations, and network connections.
- **PowerShell Operational** – script block logging for encoded commands.
- **DNS Resolver Logs** – high-entropy queries that resemble tunneling.

Each event contains metadata such as `log_type`, `@timestamp`, and fields aligned to ECS/CIM. Files are dropped to `data/incoming` and optionally published to Kafka if the `kafka-python` client is installed.

## 2. Kafka Transport

Kafka acts as the durable message bus. The `telemetry-bus` topic receives events from the simulator and any additional producers (e.g., Filebeat, custom scripts). Using Kafka allows replaying scenarios, load-testing ingestion, and decoupling producers from consumers.

## 3. Logstash Normalisation

Logstash performs the following transformations (see `infrastructure/logstash/pipeline/logstash.conf`):

1. **Parsing** – CloudTrail JSON, Windows XML/JSON, Sysmon XML, and DNS CSVs are parsed into structured fields.
2. **Enrichment** – GeoIP lookup on `source_ip` plus timestamp normalization into `event.created`/`event.ingested`.
3. **Fingerprinting** – Deterministic hash stored in `event.hash` prevents duplicate alerts and allows correlation across SIEMs.
4. **Dual Output** – Events are sent simultaneously to Elasticsearch (`telemetry-*` index) and Splunk via HEC.

## 4. SIEM Platforms

- **Elastic Stack** – Elasticsearch stores the ECS-aligned documents. Kibana dashboards and detection rules (via Detection Engine) query `telemetry-*`. Alerts are written back as `event.kind: alert` documents and displayed in the Security app.
- **Splunk Enterprise** – HEC ingests events into the `telemetry` index. Saved searches in `detections/splunk/savedsearches.conf` trigger correlation alerts. Dashboards in `dashboards/splunk/` provide operational views.

## 5. Analyst Experience

1. Analysts monitor the Splunk dashboard (`SIEM Operations Overview`) or the Kibana dashboard to watch for spikes.
2. When a detection fires, automation (not included) could push to Jira/Slack, but the runbooks in `docs/runbooks/` guide manual triage.
3. Metrics for detection fidelity are captured using `docs/runbooks/metrics-template.md`.

## Component Ports

| Component      | Port | Purpose                      |
|----------------|------|------------------------------|
| Splunk Web     | 8000 | Analyst UI                   |
| Splunk HEC     | 8088 | Event ingestion              |
| Elasticsearch  | 9200 | REST / API access            |
| Kibana         | 5601 | Visualisation & Security App |
| Kafka Broker   | 9092 | Telemetry bus                |
| Redpanda UI    | 8080 | Kafka topic monitoring       |

## Scaling Considerations

- Increase Logstash JVM heap (`LS_JAVA_OPTS`) for higher throughput.
- Run multiple Logstash instances by adding workers to the compose file and enabling Kafka consumer groups.
- Externalise storage by mounting dedicated volumes for Elasticsearch and Splunk.
- Replace Kafka with managed services (e.g., MSK) for cloud deployments.

This architecture balances realism with manageability, making it suitable for laptop labs or cloud-hosted training ranges.
