# Aurora Card Tool

[![GitHub Release](https://img.shields.io/github/v/release/Nice87/aurora-card-tool?style=for-the-badge)](https://github.com/Nice87/aurora-card-tool/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://github.com/Nice87/aurora-card-tool/blob/main/LICENSE)

**Aurora Card Tool** is an enterprise-grade, high-performance custom integration for Home Assistant built to power the **Aurora Card** ecosystem. It provides a secure, lightning-fast local backend API that installs, edits, and removes card modules as isolated YAML files using an advanced **3-Tier Storage Engine** (L1 RAM cache + L2 `.storage` fast-boot snapshot + L3 atomic YAML sync).

Designed with zero event-loop blocking, SHA-256 ETag short-circuit caching, and specialized helper suites for Music Assistant, Zigbee2MQTT mesh topology, and virtual environmental sensors, Aurora Card Tool delivers unmatched responsiveness for modern wall tablets and dashboards.

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
    <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=Nice87&repository=aurora-card-tool&category=integration" target="_blank">
      <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open Aurora Card Tool on HACS">
    </a>
    <br>
    </details>

2. **Restart Home Assistant**, then navigate to **Settings → Devices & Services → Add Integration** or click the button below:
   <br><br>
   <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=aurora_card_tool" target="_blank">
     <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance to configure Aurora Card Tool">
   </a>

3. Search for **Aurora Card Tool** and complete the setup flow.
4. The integration automatically establishes your secure directory structure:
   - Base Path: `/config/aurora_card`
   - Modules: `/config/aurora_card/modules`
   - Presets: `/config/aurora_card/presets`

---

## Complete Feature Breakdown

### 1. High-Performance 3-Tier Storage Engine (`storage.py`)
- **L1 RAM Cache ($O(1)$ Lookups):** Keeps parsed module dictionaries in memory so WebSocket requests are served in under 0.2 ms without touching the disk.
- **L2 `.storage` Cold-Boot Accelerator:** Utilizes Home Assistant's C-based `orjson` serialization and file modification timestamps (`st_mtime_ns`) via LibYAML (`CSafeLoader`) for instant restarts.
- **L3 Atomic Disk Persistence:** Writes module updates to temporary files before executing an OS-level atomic swap (`os.replace`), preventing 0-byte file corruption during power loss.

### 2. Secure WebSocket CRUD API (`websocket_api.py`)
- **SHA-256 ETag Handshake:** Clients send their cached ETag hash; if unmodified, the server replies with a tiny 50-byte payload, reducing dashboard load bandwidth by 99%.
- **Surgical Delta Broadcasts:** When a module is edited, the backend broadcasts only the modified delta rather than forcing all open dashboards to re-download the entire module library.
- **Strict Security Guards:** Enforces `@websocket_api.require_admin` role locks and rigorous regex sanitization (`module_id`) to block path traversal attacks.

### 3. Advanced Music Assistant Suite (`ma_*`)
- **`ma_client.py`:** Normalizes player states, artist/title metadata, and artwork URLs across audio providers.
- **`ma_queue.py`:** Manages active playback queues and track lists.
- **`ma_favorites.py` & `ma_recommendations.py`:** Aggregates saved favorites and curated media browse nodes.
- **`ma_smart_group.py`:** Facilitates dynamic multi-room speaker grouping and provider synchronization.

### 4. Zigbee2MQTT Mesh & Topology Inspector (`z2m_topology.py`)
- Automatically scans state entities for Link Quality Indicators (LQI), counts low-signal warning nodes ($< 50$ LQI), and aggregates coordinator firmware metrics without event-loop lag.

### 5. Virtual Environmental Sensor Aggregator (`virtual_sensor.py`)
- Computes advanced comfort indices on the server side in Python—including **Thom Discomfort Index (DI)**, **Dew Point**, and **Vapor Pressure Deficit (VPD)**—saving wall-tablet CPU cycles.

### 6. Optimized Image Proxy View (`image_proxy.py`)
- Securely proxies remote or local media artwork with built-in size limits (max 10MB payload inspection) and URL scheme filters (`http://`/`https://`) to prevent server-side resource exhaustion.

### 7. Multi-Language Localization Engine (`translate.py` & `translations/`)
- Supports dynamic dot-notation string lookups with full English (`en.json`) and Polish (`pl.json`) translations for UI settings and config flows.

---

## Troubleshooting

- **Event Loop Watchdog Warnings:** Aurora Card Tool offloads 100% of file I/O to background executor threads (`hass.async_add_executor_job`), ensuring zero blocking calls on Home Assistant's main event loop.
- **Unknown Command Error:** If the UI reports an unknown command, verify that the integration is loaded, check Home Assistant logs, and confirm folder paths.
- **Support:** When requesting assistance, please include your Home Assistant version, relevant log excerpts, and steps to reproduce.