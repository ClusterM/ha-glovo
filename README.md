# Glovo for Home Assistant

Home Assistant custom integration for the [Glovo](https://glovoapp.com/) delivery service. It logs into your Glovo customer account and exposes live information about your current order — status, ETA, courier, progress — as Home Assistant sensors, binary sensors, and a courier `device_tracker` you can put on the map.

## Features

- **Live order tracking** — overall status, delivery stage, store, progress percent, and ETA
- **Courier on the map** — `device_tracker` with the courier's live GPS position and heading
- **Adaptive polling** — uses your configured interval (default 15 s) when idle, and automatically switches to the API-recommended interval while an order is active
- **Token auto-refresh** — you enter a refresh token once; the integration keeps the short-lived access token fresh and persists it across restarts
- **Re-authentication flow** — if the token is ever rejected, Home Assistant prompts you for a new one
- **Options flow** — change the update interval (and refresh token) without removing the integration
- **Localized** — English and Russian translations

## Installation

### HACS

> **Note:** This integration is not in the [default HACS repository](https://github.com/hacs/integration) yet. Until it is included, add this repo as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: **Integration**), then install **Glovo** and restart Home Assistant.

1. HACS → ⋮ → **Custom repositories**
2. Repository: `https://github.com/ClusterM/ha-glovo`, category: **Integration**
3. Install **Glovo**, then restart Home Assistant

### Manual

Copy `custom_components/glovo` into your Home Assistant `config/custom_components/` directory and restart Home Assistant.

## Getting the refresh token

The integration authenticates with a **refresh token** taken from your browser session on [glovoapp.com](https://glovoapp.com/):

1. Open [glovoapp.com](https://glovoapp.com/) and log in to your account.
2. Open the browser DevTools (F12) → **Application** (Chrome) / **Storage** (Firefox) → **Local Storage** → `https://glovoapp.com`.
3. Copy the value of the key **`glovo_refresh_token`**.

This long-lived token is exchanged for a short-lived access token by the integration; you only need to provide it once.

## Configuration

1. Settings → **Devices & Services** → **Add Integration** → **Glovo**
2. Paste the **refresh token** and set the **update interval** (seconds, default `15`)
3. Submit — the token is validated immediately. An invalid token is rejected right away.

Use **Configure** (Options) later to change the update interval, or to paste a new refresh token (leave the token field empty to keep the current one).

> Only a single Glovo account (one integration entry) is supported.

## Entities

All entities are grouped under one **Glovo** device. When there is no active order, sensors report empty/idle values rather than becoming unavailable.

### Sensors

| Entity | Description |
|--------|-------------|
| Order status | Combined high-level status (`PREPARING`, `ON_THE_WAY`, `ARRIVING`, `DELIVERED`, …). The full summary is available in its attributes. |
| Stage | Raw lifecycle step (`IN_PROGRESS`, `DELIVERED`, `CANCELED`, …) |
| Store | Store / restaurant name |
| Active orders | Number of currently active orders |
| Courier | Courier name |
| Courier status | `ASSIGNED`, `WAITING`, `ON_THE_WAY`, `ARRIVING` |
| Store status | `PREPARING`, `READY` |
| Progress | Delivery progress, % |
| ETA minutes left | Minutes until arrival (countdown mode) |
| ETA | Human-readable ETA text |
| ETA window | Estimated arrival time range (e.g. `16:05 – 16:25`) |
| Recommended poll interval | API-suggested polling interval (diagnostic, disabled by default) |

### Binary sensors

| Entity | Description |
|--------|-------------|
| Active order | On when at least one order is active |
| Late | On when the delivery is running late |
| Chat available | On when courier chat is available (diagnostic) |

### Device tracker

| Entity | Description |
|--------|-------------|
| Courier location | Courier's live GPS position. Extra attributes: `heading`, `courier_name`, `courier_count`. |

## How polling works

The integration calls the Glovo customer API and builds a flat summary of the most recent active order. While an order is active, the API returns a recommended polling interval (`pollingIntervalMillis`), and the integration follows it for near-real-time courier updates. When no order is active, it falls back to the interval you configured.

## Requirements

- Home Assistant `2024.12.0` or newer
- A Glovo account and its `glovo_refresh_token` (see above)
- Outbound internet access to `api.glovoapp.com`

## Disclaimer

This is an unofficial integration that uses Glovo's private customer API and is not affiliated with, endorsed by, or supported by Glovo. The API may change at any time and break this integration. Use at your own risk, and only with your own account.

## License

GPLv3 License

## Support the Developer and the Project

* [GitHub Sponsors](https://github.com/sponsors/ClusterM)

* [Patreon](https://www.patreon.com/c/ClusterMeerkat)

* [Buy Me A Coffee](https://www.buymeacoffee.com/cluster)

* [Sber](https://messenger.online.sberbank.ru/sl/Lnb2OLE4JsyiEhQgC)

* [Donation Alerts](https://www.donationalerts.com/r/clustermeerkat)

* [Boosty](https://boosty.to/cluster)
