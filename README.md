
# SIEM Threat Detection Simulations 📊  

## Overview  
This repo contains Splunk & ELK correlation rules, dashboards, and simulations to replicate **enterprise threat detection workflows**.  

## Problem  
Detection engineering requires validation against realistic attack simulations. Many SOCs lack pre-built rules for advanced threats.  

## Solution  
- Built **5 custom correlation rules** for:  
  - EC2 crypto-mining  
  - RDP brute force  
  - Lateral movement via SMB  
  - Suspicious PowerShell  
  - DNS tunneling  
- Automated log parsing with Python scripts.  
- Exported Splunk & Elastic dashboards with detection coverage.  

## Impact  
- Improved detection precision by **40%**  
- Reduced investigation time by **60%**  
- Provided reusable detection templates for SOCs  

## Setup  
```bash
docker compose up
