# Runbook: SMB Lateral Movement Anomaly

**Detection source:** Splunk `SMB Lateral Movement Anomaly` / Elastic `Suspicious SMB Lateral Movement`

## 1. Trigger Conditions
- Sysmon Event ID 3 network connections to TCP/445 across multiple destinations
- Baseline deviation greater than 10 connections within 5 minutes

## 2. Validation Steps
1. Confirm the initiating host is not a legitimate admin jump box.
2. Review Sysmon Event ID 1 process creation on the source for tools like `wmic`, `psexec`, or `powershell`.
3. Check for scheduled tasks or services created on destination systems.
4. Correlate with authentication logs for pass-the-hash or credential theft indicators.

## 3. Containment
- Quarantine the source workstation from the network.
- Disable compromised credentials.
- Block SMB traffic from the host at internal firewalls until root cause identified.

## 4. Eradication & Recovery
- Remove unauthorized services or scheduled tasks on affected systems.
- Patch systems and enforce SMB signing where possible.
- Deploy endpoint detection policies to monitor remote service creation.

## 5. Lessons Learned
- Harden lateral movement paths with host-based firewalls.
- Implement segmentation between workstation and server tiers.
