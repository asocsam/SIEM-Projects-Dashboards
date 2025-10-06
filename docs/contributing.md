# Contributing Detection Content

1. **Create a Branch** – Use descriptive names (e.g., `feature/okta-detections`).
2. **Add Telemetry Mapping** – Update `docs/data-flow.md` if new data sources are introduced.
3. **Provide Detections** – Place Splunk content under `detections/splunk/` and Elastic content under `detections/elastic/`. Include ATT&CK tags and references.
4. **Document Dashboards** – Export updated dashboards into the respective folder.
5. **Write Runbooks** – Every detection must link to a runbook with validation and containment steps.
6. **Testing** – Run the simulator to generate sample alerts and capture metrics in `docs/runbooks/metrics-template.md`.
7. **Pull Request** – Describe the new coverage area, testing performed, and false-positive considerations.

By following these steps the project remains a reliable training ground for detection engineers.
