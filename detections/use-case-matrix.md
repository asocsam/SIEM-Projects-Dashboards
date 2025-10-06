# Detection Use-Case Matrix

| Detection | Data Source | MITRE ATT&CK Tactic | MITRE Technique | Runbook |
|-----------|-------------|---------------------|-----------------|---------|
| Crypto Mining on Fresh Instance | AWS CloudTrail, VPC Flow Logs | Impact | T1496 Resource Hijacking | [docs/runbooks/crypto-mining.md](../docs/runbooks/crypto-mining.md) |
| RDP Brute Force Campaign | Windows Security Event Log | Credential Access | T1110 Brute Force | [docs/runbooks/rdp-brute-force.md](../docs/runbooks/rdp-brute-force.md) |
| SMB Lateral Movement Anomaly | Sysmon Event ID 3 | Lateral Movement | T1021.002 SMB/Windows Admin Shares | [docs/runbooks/smb-lateral.md](../docs/runbooks/smb-lateral.md) |
| Encoded PowerShell Download Cradle | PowerShell Operational Log, Sysmon | Execution | T1059.001 PowerShell | [docs/runbooks/powershell.md](../docs/runbooks/powershell.md) |
| High Entropy DNS Queries | BIND DNS Query Logs | Command & Control | T1071.004 DNS | [docs/runbooks/dns-tunnel.md](../docs/runbooks/dns-tunnel.md) |
