# Runbook: High Entropy DNS Queries

**Detection source:** Splunk `High Entropy DNS Queries` / Elastic `High Entropy DNS Traffic`

## 1. Trigger Conditions
- Average query entropy > 35 with more than 50 requests per 15 minutes
- Long subdomain labels resembling encoded data

## 2. Validation Steps
1. Resolve the queried domains and review WHOIS registration.
2. Check whether the client IP belongs to a server running legitimate tunneling (e.g., VPN, security tools).
3. Inspect packet captures or Zeek logs for DNS TXT/NULL records.
4. Contact the endpoint owner to validate intended use.

## 3. Containment
- Block the suspicious domain at DNS resolver or firewall.
- If the host is compromised, disconnect from the network.
- Rotate credentials used by the affected system.

## 4. Eradication & Recovery
- Remove unauthorized tunneling software or malware.
- Apply endpoint hardening (disable local admin rights, enforce EDR policies).
- Monitor for recurrence with tuned entropy thresholds.

## 5. Lessons Learned
- Implement DNS filtering with policy-based access.
- Baseline legitimate DNS tunnels (e.g., M365) to reduce false positives.
