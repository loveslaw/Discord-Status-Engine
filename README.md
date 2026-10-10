# 🚀 Discord-Status-Engine

<div align="center">

```
  ███████╗████████╗ █████╗ ████████╗██╗   ██╗███████╗
  ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║   ██║██╔════╝
  ███████╗   ██║   ███████║   ██║   ██║   ██║███████╗
  ╚════██║   ██║   ██╔══██║   ██║   ██║   ██║╚════██║
  ███████║   ██║   ██║  ██║   ██║   ╚██████╔╝███████║
  ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
```

**Real-Time Hardware Telemetry & Dynamic Rich Presence (RPC) Synchronizer in Python**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests: 4 Passed](https://img.shields.io/badge/tests-4%20passed-brightgreen.svg)]()

</div>

---

## ⚡ Overview

**Discord-Status-Engine** is a lightweight background daemon that bridges live system performance metrics directly into Discord's native Rich Presence (RPC) activity status.

Operating via direct local IPC named pipe sockets (`\\.\pipe\discord-ipc-0` on Windows and Unix domain sockets on Linux/macOS), the engine communicates straight to your Discord desktop client with **zero bot tokens** required. It dynamically tracks hardware performance, system uptime, and active window processes, rotating between customizable profiles at configurable intervals.

---

## ✨ Features

- 💻 **Real-Time Hardware Telemetry**: Hooks into low-level CPU percentage, core counts, RAM usage (GB used/total), system uptime, and battery state via `psutil`.
- 🔄 **Multi-Profile Dynamic Rotation**: Seamlessly cycles between customized activity displays (e.g., *Dev Mode*, *Gaming Telemetry*, *Minimalist Stats*) every 15–30 seconds.
- 🔌 **Pure Native IPC Protocol**: Direct socket communication using binary struct packing — no external bot tokens or cloud dependencies needed.
- 🔗 **Interactive Profile Buttons**: Embed custom clickable buttons directly into your Discord activity linking to your GitHub profile, portfolio, or community.
- 📊 **Rich Terminal Dashboard**: Live terminal readout visualizing current presence states, CPU load, and memory usage.

---

## 🚀 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/loveslaw/Discord-Status-Engine.git
cd Discord-Status-Engine

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration (`config/profiles.json`)

Configure your Discord Application ID, rotation intervals, and status templates:

```json
{
  "client_id": "1200000000000000000",
  "rotation_seconds": 15,
  "profiles": [
    {
      "name": "Live Telemetry",
      "details_template": "💻 CPU: {cpu} | RAM: {ram}",
      "state_template": "⚡ RAM: {ram_gb} | Up: {uptime}",
      "large_image": "cpu_chip",
      "large_text": "Discord-Status-Engine",
      "small_image": "python_icon",
      "small_text": "Python 3.12 Engine",
      "buttons": [
        {
          "label": "GitHub Profile",
          "url": "https://github.com/loveslaw"
        }
      ]
    }
  ]
}
```

### Available Template Variables
| Variable | Description | Example Output |
| :--- | :--- | :--- |
| `{cpu}` | Total CPU load percentage | `18.4%` |
| `{cores}` | Logical CPU cores | `16` |
| `{ram}` | RAM utilization percentage | `54.2%` |
| `{ram_gb}` | Used vs total memory in GB | `8.65 / 15.96 GB` |
| `{uptime}` | System uptime string | `4h 12m` |
| `{top_proc}` | Highest CPU consumer process | `Code.exe` |
| `{battery}` | Battery percentage | `92%` or `AC Power` |

---

## 📖 Usage

### Start Daemon
Make sure Discord Desktop is running, then launch:
```bash
python main.py
```

### Dry-Run / Preview Mode
Inspect local metrics and presence formatting without connecting to Discord:
```bash
python main.py --dry-run
```

---

## 🧪 Testing

Run the automated test suite verifying metric extraction and profile rotation:
```bash
python -m pytest tests/ -v
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).
Author: **loveslaw**
