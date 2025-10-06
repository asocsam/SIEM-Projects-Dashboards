# Runbook: Crypto Mining on Fresh Instance

**Detection source:** Splunk saved search `Crypto Mining on Fresh Instance` / Elastic rule `EC2 Crypto Mining Spike`

## 1. Trigger Conditions
- CloudTrail `RunInstances` events tagged with `miner`
- Instance launched less than 30 minutes ago
- Optional enrichment indicates known crypto-mining pools or threat intel matches

## 2. Validation Steps
1. Confirm the event is not part of approved load testing (check CMDB / ticketing).
2. Review associated IAM user in AWS console for anomalies (last login, access keys).
3. Inspect VPC Flow Logs for outbound connections to mining pools or TOR nodes.
4. Terminate the instance if confirmed malicious.

## 3. Containment
- Disable IAM credentials used to launch the instance.
- Snapshot the instance for forensics if required.
- Update security groups and Service Control Policies to block similar launches.

## 4. Eradication & Recovery
- Rotate IAM keys or roles involved.
- Audit recent CloudTrail logs for additional suspicious launches.
- Restore affected workloads from trusted AMIs.

## 5. Lessons Learned
- Add guardrails to prevent unapproved AMI usage.
- Implement SCPs restricting instance tagging to approved values.
