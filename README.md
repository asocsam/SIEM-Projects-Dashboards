
# Enterprise SIEM Detection Pipeline 📊

This repository contains a full end-to-end **Security Information and Event Management (SIEM)** pipeline that can be run locally with Docker Compose or deployed piecemeal into an existing lab. The project mirrors a realistic enterprise environment by simulating attack traffic, forwarding telemetry to Splunk and the Elastic Stack, and surfacing detections in dashboards backed by correlation rules and automation playbooks.

> **Goal:** provide a complete, ready-to-run reference that detection engineers can use to practice building, tuning, and validating SOC-quality detections.

---

## 📦 Repository Layout

```
.
├── README.md                         # This guide
├── infrastructure/
│   ├── docker-compose.yml            # Spin up Splunk, Elastic, Kafka, and Logstash
│   ├── logstash/pipeline/logstash.conf
│   └── splunk/                       # Splunk configuration bootstrap
├── detections/
│   ├── elastic/rules.ndjson          # Elastic Security detection content
│   ├── splunk/savedsearches.conf     # Splunk Enterprise Security correlation searches
│   └── use-case-matrix.md            # MITRE ATT&CK coverage map
├── dashboards/
│   ├── elastic/                      # Kibana dashboards and Lens visualisations
│   └── splunk/                       # Splunk Simple XML dashboards
├── scripts/
│   └── simulations/generate_events.py# Adversary simulation & log generator
└── docs/
    ├── data-flow.md                  # Architectural deep dive
    └── runbooks/                     # Incident response guidance per detection
```

Each folder includes accompanying documentation so the project can double as a training lab or a template for production-ready pipelines.

---

## 🧱 Architecture Overview

The lab emulates an enterprise that streams telemetry from cloud and on-prem sources, normalises it, and pushes it into Splunk and Elastic for detection and visualisation.

1. **Data Generation** – The `generate_events.py` script emits realistic logs for the following attack scenarios:
   - EC2 crypto-mining (AWS CloudTrail, VPC Flow, CloudWatch)
   - RDP brute force (Windows Security Event Log)
   - SMB lateral movement (Windows Sysmon)
   - Suspicious PowerShell (PowerShell ScriptBlock & Sysmon)
   - DNS tunneling (Bind query logs)
2. **Transport** – Events are written to a Kafka topic (`telemetry-bus`) via the script or by dropping CSV/JSON files in `./data/incoming`. Kafka provides buffering and replay capabilities.
3. **Ingestion & Normalisation** – Logstash subscribes to Kafka, applies ECS/Splunk CIM mappings, enriches IPs with open-source threat intelligence, and outputs to Elasticsearch and the Splunk HTTP Event Collector (HEC).
4. **Storage & Analytics** – Splunk and Elasticsearch store the events. Splunk correlation searches and Elastic detection rules fire on malicious patterns.
5. **Visualisation** – Kibana Lens dashboards and Splunk Simple XML dashboards give SOC analysts fast situational awareness. Runbooks describe how to respond when detections fire.

The [docs/data-flow.md](docs/data-flow.md) file contains a detailed component-by-component explanation with diagrams and data schemas.

---

## 🚀 Quick Start

> **Prerequisites:** Docker Engine >= 24, Docker Compose Plugin >= 2, and at least 16 GB RAM for the full lab.

```bash
git clone https://github.com/<your-org>/SIEM-Projects-Dashboards.git
cd SIEM-Projects-Dashboards
docker compose -f infrastructure/docker-compose.yml up -d

# Once services are up, seed simulated telemetry
python3 scripts/simulations/generate_events.py --burst rdp --burst crypto --burst smb --burst powershell --burst dns

# Optional: continuously stream mixed events
python3 scripts/simulations/generate_events.py --continuous 300
```

After the stack starts:

- Splunk Web: http://localhost:8000 (admin / changeme)
- Splunk HEC: http://localhost:8088 (token in `infrastructure/splunk/hec-token.txt`)
- Kibana: http://localhost:5601 (elastic / changeme)
- Elasticsearch: http://localhost:9200
- Kafka UI (Redpanda Console): http://localhost:8080

> **Tip:** If you have limited hardware, launch only the components you need by editing the compose file.

---

## 🔍 Detection Content

| Use Case | Splunk Search | Elastic Rule | MITRE ATT&CK |
|----------|---------------|--------------|---------------|
| EC2 crypto-mining | `detections/splunk/savedsearches.conf` (`Crypto Mining on Fresh Instance`) | `detections/elastic/rules.ndjson` (`EC2 Crypto Mining Spike`) | T1496, T1106 |
| RDP brute force | `RDP Brute Force Campaign` | `RDP Brute Force Spike` | T1110 |
| Lateral movement via SMB | `SMB Lateral Movement Anomaly` | `Suspicious SMB Lateral Movement` | T1021 |
| Suspicious PowerShell | `Encoded PowerShell Download Cradle` | `Encoded PowerShell Execution` | T1059.001 |
| DNS tunneling | `High Entropy DNS Queries` | `High Entropy DNS Traffic` | T1071.004 |

Splunk searches reference the Common Information Model (CIM) data models and assume the Logstash transformations provided in `infrastructure/logstash/pipeline/logstash.conf`. Elastic rules use the Elastic Common Schema (ECS) fields produced by the same pipeline.

### Dashboards

- **Splunk** dashboards live under `dashboards/splunk/` and can be imported via Splunk Web (`Settings → Knowledge → Dashboards`).
- **Elastic/Kibana** dashboard exports live under `dashboards/elastic/` and can be imported via `Stack Management → Saved Objects`.

Each dashboard is annotated and links directly to the corresponding runbook in `docs/runbooks/`.

---

## 🧪 Validation Workflow

1. **Generate attack traffic** using the simulation script or your own dataset.
2. **Verify ingestion** by checking the Kafka topic (`telemetry-bus`) and the Logstash logs (`docker compose logs logstash`).
3. **Confirm field mappings** using the Kibana Data View (`telemetry-*`) or Splunk's `| tstats` commands.
4. **Run detection rules** manually or wait for scheduled executions to fire alerts.
5. **Review dashboards & runbooks** to understand impact and recommended response steps.
6. **Record metrics** (true positives, false positives, time-to-detect) in the `docs/runbooks/metrics-template.md` sheet.

Automation scripts under `scripts/` can replay logs, adjust noise levels, or fuzz timestamps to test detection resiliency.

---

## 🧰 Extending the Lab

- Add additional data sources (e.g., Okta, Azure AD) by creating new Logstash pipelines and mapping them to CIM/ECS.
- Build new detections by duplicating the existing rule templates in `detections/`.
- Integrate SOAR tooling by enabling the Splunk App for Phantom or Elastic webhooks.
- Convert the infrastructure to Kubernetes manifests using the docker-compose file as the basis.

Please see [`docs/contributing.md`](docs/contributing.md) for guidelines on submitting new detection content.

---

## 📚 Learning Path

To make the lab useful for training, the documentation is structured as a progressive curriculum:

1. **Foundation:** Read `docs/data-flow.md` for the architecture and telemetry mapping.
2. **Hands-on:** Execute `scripts/simulations/generate_events.py` and observe data arriving in Splunk/Kibana.
3. **Detection Engineering:** Study the Splunk saved searches and Elastic rules, then adjust thresholds to explore detection tuning.
4. **Incident Response:** Follow the runbooks when alerts fire to practice triage and containment.
5. **Purple Teaming:** Modify the simulator to introduce novel techniques and iterate on detection coverage.

Whether you are preparing for an on-call rotation or conducting a purple team exercise, this project provides an opinionated yet extensible baseline.

---

## 🙌 Acknowledgements

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) for inspiration on atomic tests.
- [MITRE ATT&CK](https://attack.mitre.org/) for the adversary tactics mapping.
- Splunk, Elastic, and the open-source security community for providing tooling and rule templates.

Contributions and improvements are welcome via issues or pull requests!
