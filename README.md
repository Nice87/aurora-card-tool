# Aurora Card Tool

[![GitHub Release](https://img.shields.io/github/v/release/Nice87/aurora-card-tool?style=for-the-badge)](https://github.com/Nice87/aurora-card-tool/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://github.com/Nice87/aurora-card-tool/blob/main/LICENSE)

**Aurora Card Tool** is an enterprise-grade, high-performance custom integration for Home Assistant built to power the **Aurora Card** ecosystem. It provides a secure, lightning-fast local backend API that installs, edits, and removes card modules as isolated YAML files using a **3-Tier Storage Engine** (L1 RAM cache + L2 `.storage` fast-boot snapshot + L3 atomic YAML sync).

Designed with zero event-loop blocking, SHA-256 ETag short-circuit caching, and integrated helper suites for Music Assistant, Zigbee2MQTT mesh topology, and virtual environmental sensors, Aurora Card Tool delivers unmatched responsiveness for modern wall tablets and dashboards.

---

## Requirements

- [Home Assistant](https://www.home-assistant.io/) (2024.1.0 or newer stable)
- [Aurora Card](https://github.com/Nice87/aurora-card) installed

---

## Installation and Configuration

1. Install Aurora Card Tool using **one of the methods below**:

    <details>
    <summary>Without HACS (Manual)</summary>
    <br>
    - Copy the `aurora_card_tool` folder from `custom_components/aurora_card_tool/` into your Home Assistant `/config/custom_components/` directory.
    <br>
    </details>
    
    <details>
    <summary>With HACS (Recommended)</summary>
    <br>
    - Ensure HACS is installed on your instance.<br>
    - Add `https://github.com/Nice87/aurora-card-tool` as a **Custom Repository** in HACS (Category: *Integration*).<br>
    - Click the badge below to open it directly in your HACS store:
    <br><br>
    [![Open Aurora Card Tool on Home Assistant Community Store (HACS).](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Nice87&repository=aurora-card-tool&category=integration)
    <br>
    </details>

2. **Restart Home Assistant**, then navigate to **Settings → Devices & Services → Add Integration** or click the button below:
   <br><br>
   <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=aurora_card_tool" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a>

3. Search for **Aurora Card Tool** and complete the setup flow.
4. The integration automatically establishes your secure directory structure:
   - Base Path: `/config/aurora_card`
   - Modules: `/config/aurora_card/modules`
   - Presets: `/config/aurora_card/presets`

---

## Advanced Features & Settings

Aurora Card Tool includes configurable feature suites that can be toggled at any time via **Settings → Devices & Services → Aurora Card Tool → Configure**:

- **Live File Watcher:** Automatically detects external edits made via Samba or Studio Code Server (`.yaml` file saves) and pushes live WebSocket updates instantly to open dashboards without requiring a manual refresh.
- **Music Assistant Integration Helpers:** Exposes specialized backend endpoints for dynamic multi-room speaker grouping (`ma_smart_group`), queue inspection, favorites, and recommendations.
- **Zigbee2MQTT Mesh & Topology Helpers:** Aggregates LQI health metrics, routing node quality, and warning diagnostics.
- **Virtual Sensor Aggregator:** Computes advanced environmental indices (Thom Discomfort Index, Dew Point, Vapor Pressure Deficit) on the server side to conserve wall-tablet CPU cycles.

---

## Troubleshooting

- **Event Loop Watchdog Warnings:** Aurora Card Tool uses asynchronous background executor threads (`hass.async_add_executor_job`) for all file I/O, guaranteeing zero event-loop blocking.
- **Unknown Command Error:** If the UI reports an unknown command, verify that the integration is loaded, check Home Assistant logs, and confirm folder paths.
- **Support:** When requesting assistance, please include your Home Assistant version, relevant log excerpts, and steps to reproduce.