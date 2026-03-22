# Airodor WiFi – Home Assistant Integration

> 🇬🇧 An English version of this README is available [below](#airodor-wifi--home-assistant-integration-1).

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![GitHub Release](https://img.shields.io/github/v/release/BenniWi/airodor_home_assistant_integration)](https://github.com/BenniWi/airodor_home_assistant_integration/releases)
[![License](https://img.shields.io/github/license/BenniWi/airodor_home_assistant_integration)](LICENSE)

Eine Home Assistant Custom Integration für **Limodor Airodor WiFi** Lüftungsgeräte. Sie ermöglicht die lokale Steuerung und Überwachung des Geräts direkt aus Home Assistant heraus – ohne Cloud, ohne externe Dienste.

> **Hinweis:** Dieses Projekt wurde mit Unterstützung von [GitHub Copilot](https://github.com/features/copilot) umgesetzt.

---

## Funktionen

- Lüftungsmodus für **Gruppe A und Gruppe B** anzeigen und setzen
- Timer-Status beider Gruppen als Sensor
- Manuelle **Datenaktualisierung** per Button
- Konfigurierbares **Abfrageintervall** (Standard: 30 Minuten)
- Frei wählbare **Namen** für Gruppe A und Gruppe B
- Vollständige Unterstützung für **HACS**

---

## Zugrundeliegende API

Die Integration basiert auf der Python-Bibliothek [airodor-wifi-api](https://github.com/BenniWi/airodor-wifi), die das lokale HTTP-Protokoll des Airodor WiFi Moduls implementiert. Das Gerät wird direkt über seine **IP-Adresse** im lokalen Netzwerk angesprochen – es ist keine Internetverbindung erforderlich.

Die API stellt folgende Operationen bereit:

| Operation | Beschreibung |
|---|---|
| `get_mode(group)` | Aktuellen Lüftungsmodus abfragen |
| `set_mode(group, mode)` | Lüftungsmodus setzen |
| `get_timer(group)` | Timer-Status abfragen |

---

## Installation

### Via HACS (empfohlen)

1. HACS in Home Assistant öffnen
2. **Benutzerdefinierte Repositories** → URL `https://github.com/BenniWi/airodor_home_assistant_integration` mit Kategorie *Integration* hinzufügen
3. Integration suchen und installieren
4. Home Assistant neu starten

### Manuell

1. Den Ordner `custom_components/airodor_integration` in das Verzeichnis `custom_components` deiner Home Assistant Installation kopieren
2. Home Assistant neu starten

---

## Konfiguration

1. In Home Assistant: **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach „Airodor" suchen und auswählen
3. Folgende Werte eingeben:

| Feld | Beschreibung |
|---|---|
| IP-Adresse | IP-Adresse des Airodor WiFi Geräts im lokalen Netzwerk |
| Aktualisierungsintervall | Abfrageintervall in Minuten (Standard: 30) |
| Name Gruppe A | Anzeigename für Lüftungsgruppe A |
| Name Gruppe B | Anzeigename für Lüftungsgruppe B |

---

## Projektstruktur

| Datei/Ordner | Zweck |
|---|---|
| `custom_components/airodor_integration/` | Integrationscode |
| `custom_components/airodor_integration/manifest.json` | Integrations-Metadaten |
| `custom_components/airodor_integration/translations/` | Übersetzungen (de, en) |
| `CONTRIBUTING.md` | Hinweise für Beitragende |
| `requirements.txt` | Python-Abhängigkeiten für Entwicklung |

---

## Entwicklung

Das Projekt nutzt einen VS Code Dev Container. Zum Starten:

```bash
scripts/develop   # startet Home Assistant lokal
scripts/lint      # führt ruff-Linter aus
```

---

## Lizenz

[MIT](LICENSE) – © BenniWi

---
---

# Airodor WiFi – Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![GitHub Release](https://img.shields.io/github/v/release/BenniWi/airodor_home_assistant_integration)](https://github.com/BenniWi/airodor_home_assistant_integration/releases)
[![License](https://img.shields.io/github/license/BenniWi/airodor_home_assistant_integration)](LICENSE)

A Home Assistant custom integration for **Limodor Airodor WiFi** ventilation devices. It enables local control and monitoring of the device directly from Home Assistant – no cloud, no external services required.

> **Note:** This project was built with the assistance of [GitHub Copilot](https://github.com/features/copilot).

---

## Features

- Display and set the ventilation mode for **Group A and Group B**
- Timer status of both groups as sensors
- Manual **data refresh** via button
- Configurable **polling interval** (default: 30 minutes)
- Freely customizable **names** for Group A and Group B
- Full **HACS** support

---

## Underlying API

The integration is based on the Python library [airodor-wifi-api](https://github.com/BenniWi/airodor-wifi), which implements the local HTTP protocol of the Airodor WiFi module. The device is accessed directly via its **IP address** on the local network – no internet connection is required.

The API provides the following operations:

| Operation | Description |
|---|---|
| `get_mode(group)` | Query the current ventilation mode |
| `set_mode(group, mode)` | Set the ventilation mode |
| `get_timer(group)` | Query the timer status |

---

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. **Custom Repositories** → Add URL `https://github.com/BenniWi/airodor_home_assistant_integration` with category *Integration*
3. Search for the integration and install it
4. Restart Home Assistant

### Manual

1. Copy the folder `custom_components/airodor_integration` into the `custom_components` directory of your Home Assistant installation
2. Restart Home Assistant

---

## Configuration

1. In Home Assistant: **Settings → Devices & Services → Add Integration**
2. Search for "Airodor" and select it
3. Enter the following values:

| Field | Description |
|---|---|
| IP Address | IP address of the Airodor WiFi device on the local network |
| Update Interval | Polling interval in minutes (default: 30) |
| Group A Name | Display name for ventilation group A |
| Group B Name | Display name for ventilation group B |

---

## Project Structure

| File/Folder | Purpose |
|---|---|
| `custom_components/airodor_integration/` | Integration code |
| `custom_components/airodor_integration/manifest.json` | Integration metadata |
| `custom_components/airodor_integration/translations/` | Translations (de, en) |
| `CONTRIBUTING.md` | Contribution guidelines |
| `requirements.txt` | Python dependencies for development |

---

## Development

The project uses a VS Code Dev Container. To get started:

```bash
scripts/develop   # starts Home Assistant locally
scripts/lint      # runs the ruff linter
```

---

## License

[MIT](LICENSE) – © BenniWi
