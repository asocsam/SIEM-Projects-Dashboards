# Runbook: RDP Brute Force Campaign

**Detection source:** Splunk `RDP Brute Force Campaign` / Elastic `RDP Brute Force Spike`

## 1. Trigger Conditions
- 15+ failed RDP logons within 10 minutes
- Optional successful logon from the same source following the burst

## 2. Validation Steps
1. Check Windows Event Logs on the targeted host for Event IDs 4625 and 4624.
2. Identify the source IP ownership using WHOIS or internal CMDB.
3. Review firewall logs to confirm network access attempts.
4. Ask the system owner whether there was any legitimate testing.

## 3. Containment
- Block the source IP at the perimeter firewall.
- If success occurred, disable the compromised account and force password reset.
- Isolate the host if lateral movement is suspected.

## 4. Eradication & Recovery
- Investigate for malware persistence (AV scan, Sysmon analysis).
- Enable Network Level Authentication and enforce MFA where possible.
- Review remote access policies and restrict to VPN segments.

## 5. Lessons Learned
- Deploy Account Lockout policies to rate-limit failed logins.
- Enable alerting for RDP service start events (Event ID 1149).
