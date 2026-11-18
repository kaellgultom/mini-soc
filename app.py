import json
import subprocess

from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Mini SOC Dashboard</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 30px;
            background: #0b1120;
            color: #e2e8f0;
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 1250px;
            margin: auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }

        h1 {
            color: #38bdf8;
            margin: 0 0 10px;
            font-size: 30px;
       }

        .subtitle, .info {
            color: #94a3b8;
        }

        button {
            background: #0284c7;
            color: white;
            border: none;
            padding: 13px 22px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #0369a1;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 25px;
        }

        .card, .panel {
            background: #172235;
            border: 1px solid #26364d;
            border-radius: 12px;
            padding: 22px;
        }

        .card p {
            color: #94a3b8;
            margin: 0 0 14px;
        }

        .number {
            font-size: 32px;
            font-weight: bold;
        }

        .blue { color: #38bdf8; }
        .red { color: #fb7185; }
        .green { color: #34d399; }

        .charts {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }

        h2 {
            font-size: 19px;
            margin-top: 0;
            margin-bottom: 25px;
        }

        .bar-row {
            margin-bottom: 20px;
        }

        .bar-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }

        .bar-bg {
            height: 12px;
            background: #26364d;
            border-radius: 20px;
            overflow: hidden;
        }

        .bar {
            height: 100%;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            border-radius: 20px;
        }

        .donut-area {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 25px;
            flex-wrap: wrap;
        }

        .donut {
            width: 155px;
            height: 155px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .donut-center {
            width: 105px;
            height: 105px;
            background: #172235;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #94a3b8;
        }

        .donut-center strong {
            color: white;
            font-size: 25px;
        }

        .legend p {
            margin: 12px 0;
            font-size: 14px;
        }

        .dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .table-panel {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 600px;
        }

        th, td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #26364d;
        }

        th {
            color: #38bdf8;
            background: #1e293b;
        }

        .status {
            font-weight: bold;
        }

        
.timeline-panel {
    margin-top: 25px;
}

.timeline {
    margin-top: 20px;
    border-left: 2px solid #26364d;
    padding-left: 22px;
}

.timeline-item {
    position: relative;
    padding-bottom: 22px;
}

.timeline-item:last-child {
    padding-bottom: 0;
}

.timeline-marker {
    position: absolute;
    left: -30px;
    top: 4px;
    width: 14px;
    height: 14px;
    background: #fb7185;
    border: 3px solid #172235;
    border-radius: 50%;
}

.timeline-content {
    display: flex;
    flex-direction: column;
    gap: 7px;
}

.timeline-content strong {
    color: #fb7185;
    font-size: 14px;
}

.timeline-content span {
    color: #e2e8f0;
    font-size: 13px;
}

.timeline-content small {
    color: #94a3b8;
    font-size: 12px;
}

.footer {
            margin-top: 25px;
            color: #64748b;
            font-size: 13px;
            text-align: center;
        }

        @media (max-width: 850px) {
            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .charts {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 500px) {
            body {
                padding: 15px;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 24px;
            }
        }
    </style>
</head>

<body>
<div class="container">

    <header>
        <div>
            <h1>MINI SOC DASHBOARD</h1>
            <div class="subtitle">
                SSH Login Attack Detection & Security Monitoring
            </div>
        </div>

        <form action="/run-analysis" method="POST">
            <button type="submit">RUN ANALYSIS</button>
        </form>
    </header>

    <section class="stats">
        <div class="card">
            <p>Total Failed Attempts</p>
            <div class="number blue">{{ total_failed }}</div>
        </div>

        <div class="card">
            <p>Monitored IP Addresses</p>
            <div class="number">{{ total_ips }}</div>
        </div>

        <div class="card">
            <p>Suspicious IP Addresses</p>
            <div class="number red">{{ suspicious_ips }}</div>
        </div>

        <div class="card">
            <p>Normal IP Addresses</p>
            <div class="number green">{{ normal_ips }}</div>
        </div>
    </section>

    <section class="charts">

        <div class="panel">
            <h2>Failed Login Attempts by IP</h2>

            {% if results %}
               {% for item in results %}
                <div class="bar-row">
                    <div class="bar-label">
                        <span>{{ item.ip_address }}</span>
                        <strong>{{ item.total_failed_attempts }}</strong>
                    </div>

                    <div class="bar-bg">
                        <div class="bar"
                             style="width: {{ (item.total_failed_attempts / max_failed * 100) if max_failed else 0 }}%">
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p class="info">No login activity data available.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h2>Security Status Distribution</h2>

            <div class="donut-area">
                <div class="donut"
                     style="background: conic-gradient(
                     #fb7185 0 {{ suspicious_percent }}%,
                     #34d399 {{ suspicious_percent }}% 100%
                     );">

                    <div class="donut-center">
                        <strong>{{ total_ips }}</strong>
                        IP Addresses
                    </div>
                </div>

                <div class="legend">
                    <p>
                        <span class="dot" style="background:#fb7185"></span>
                        Suspicious: {{ suspicious_ips }}
                    </p>
                    <p>
                        <span class="dot" style="background:#34d399"></span>
                        Normal: {{ normal_ips }}
                    </p>
                </div>
            </div>
        </div>

    </section>

    <section class="panel table-panel">
        <h2>SSH Login Detection Results</h2>

        <table>
            <thead>
                <tr>
                    <th>IP Address</th>
                    <th>Total Failed Attempts</th>
                    <th>Max Attempts / 5 Minutes</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                {% for item in results %}
                <tr>
                    <td>{{ item.ip_address }}</td>
                    <td>{{ item.total_failed_attempts }}</td>
                    <td>{{ item.max_attempts_in_5_minutes }}</td>
                    <td class="status"
                        style="color: {{ '#fb7185' if item.status == 'SUSPICIOUS' else '#34d399' }}">
                        {{ item.status }}
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4">No detection results available.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
<section class="panel timeline-panel">
    <h2>SSH Activity Timeline</h2>

    {% if events %}
        <div class="timeline">
            {% for event in events %}
            <div class="timeline-item">
                <div class="timeline-marker"></div>

                <div class="timeline-content">
                    <strong>{{ event.event }}</strong>
                    <span>IP Address: {{ event.ip_address }}</span>
                    <small>{{ event.timestamp }}</small>
                </div>
            </div>
            {% endfor %}
        </div>
    {% else %}
        <p class="info">No SSH activity events available.</p>
    {% endif %}
</section>
    <div class="footer">
        <p>Last Report: {{ generated_at }}</p>
        <p>Dashboard automatically refreshes every 30 seconds.</p>
        <p>MINI SOC - SSH LOGIN ATTACK DETECTOR | Educational Security Project</p>
    </div>

</div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    try:
        with open("report.json", "r") as file:
            report = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        report = {
            "results": [],
            "generated_at": "Belum tersedia"
        }

    results = report.get("results", [])

    from datetime import datetime
    from zoneinfo import ZoneInfo

    events = sorted(
        report.get("events", []),
        key=lambda item: item.get("timestamp", ""),
        reverse=True
    )[:10]

    for event in events:
        try:
            timestamp = datetime.fromisoformat(event["timestamp"])
            timestamp_wib = timestamp.astimezone(
                ZoneInfo("Asia/Jakarta")
            )
            event["timestamp"] = timestamp_wib.strftime(
                "%d-%m-%Y %H:%M:%S WIB"
            )
        except (ValueError, KeyError):
            pass

    total_failed = sum(
        item.get("total_failed_attempts", 0)
        for item in results
    )

    suspicious_ips = sum(
        1 for item in results
        if item.get("status") == "SUSPICIOUS"
    )

    normal_ips = len(results) - suspicious_ips

    max_failed = max(
        (item.get("total_failed_attempts", 0) for item in results),
        default=0
    )

    suspicious_percent = (
        suspicious_ips / len(results) * 100
        if results else 0
    )

    return render_template_string(
        HTML,
        results=results,
        total_failed=total_failed,
        total_ips=len(results),
        suspicious_ips=suspicious_ips,
        normal_ips=normal_ips,
        max_failed=max_failed,
        suspicious_percent=suspicious_percent,
        generated_at=report.get("generated_at", "-"),
    events=events
    )


@app.route("/run-analysis", methods=["POST"])
def run_analysis():
    result = subprocess.run(
        ["python3", "detector.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "Analysis failed: " + result.stderr, 500

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
