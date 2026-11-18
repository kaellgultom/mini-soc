
import re
import json
from datetime import datetime
from collections import defaultdict

LOG_FILE = "logs/auth.log"
REPORT_FILE = "report.json"

THRESHOLD = 5
TIME_WINDOW = 300


def analyze_logs():
    failed_attempts = defaultdict(list)
    events = []

    try:
        with open(LOG_FILE, "r") as file:
            for line in file:
                if "sshd[" not in line or "Failed password" not in line:
                    continue

                try:
                    timestamp = datetime.fromisoformat(line.split()[0])

                    match = re.search(
                        r"from (\d+\.\d+\.\d+\.\d+)", line
                    )

                    if match:
                        ip = match.group(1)
                        failed_attempts[ip].append(timestamp)

                        events.append({
                            "timestamp": timestamp.isoformat(),
                            "ip_address": ip,
                            "event": "Failed SSH Login"
                        })

                except (ValueError, IndexError):
                    continue

    except FileNotFoundError:
        print("File log tidak ditemukan:", LOG_FILE)
        return

    print("\n===== MINI SOC - SSH LOGIN DETECTOR =====")
    print("Metode: 5 percobaan dalam 5 menit\n")

    results = []

    if not failed_attempts:
        print("Tidak ditemukan percobaan login gagal.")

    for ip, timestamps in failed_attempts.items():
        timestamps.sort()
        max_attempts = 0
        left = 0

        for right in range(len(timestamps)):
            while (
                timestamps[right] - timestamps[left]
            ).total_seconds() > TIME_WINDOW:
                left += 1

            current = right - left + 1
            max_attempts = max(max_attempts, current)

        if max_attempts >= THRESHOLD:
            status = "SUSPICIOUS"
        else:
            status = "NORMAL"

        print("IP Address:", ip)
        print("Total Failed Attempts:", len(timestamps))
        print("Max Attempts in 5 Minutes:", max_attempts)
        print("STATUS:", status)
        print("---------------------------------------")

        results.append({
            "ip_address": ip,
            "total_failed_attempts": len(timestamps),
            "max_attempts_in_5_minutes": max_attempts,
            "status": status
        })

    report = {
        "project": "MINI SOC - SSH LOGIN DETECTOR",
        "generated_at": datetime.now().astimezone().isoformat(),
        "threshold": THRESHOLD,
        "time_window_seconds": TIME_WINDOW,
        "results": results,
        "events": events
    }

    with open(REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    print("\nLaporan berhasil disimpan ke:", REPORT_FILE)


if __name__ == "__main__":
    analyze_logs()
