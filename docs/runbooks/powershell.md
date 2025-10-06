# Runbook: Encoded PowerShell Download Cradle

**Detection source:** Splunk `Encoded PowerShell Download Cradle` / Elastic `Encoded PowerShell Execution`

## 1. Trigger Conditions
- PowerShell command line contains `-encodedCommand`
- Base64 decoded payload includes `IEX` or `Invoke-WebRequest`

## 2. Validation Steps
1. Decode the captured command and review the remote URL/domain.
2. Check browser history or EDR telemetry for the initiating process.
3. Inspect the downloaded file via sandbox or malware analysis tools.
4. Determine whether the user executed the script intentionally.

## 3. Containment
- Terminate the PowerShell process on the affected endpoint.
- Block the malicious domain/IP at the proxy or firewall.
- Remove any dropped payloads or scheduled tasks.

## 4. Eradication & Recovery
- Run endpoint scans for persistence (registry run keys, services).
- Update allow lists to prevent similar encoded commands if legitimate automation is impacted.
- Educate the user on phishing indicators if social engineering involved.

## 5. Lessons Learned
- Enable PowerShell Constrained Language Mode for high-risk users.
- Deploy AMSI-integrated security tooling to inspect scripts in memory.
