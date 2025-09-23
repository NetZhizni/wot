# World of Tanks Reserves Integration for Home Assistant

This integration allows you to track your **World of Tanks reserves** in Home Assistant.

## Installation via HACS

1. Add this repository to HACS (Custom Repositories → Category: Integration).
2. Install the integration.
3. Restart Home Assistant.

## Configuration

Add to your `configuration.yaml`:

```yaml
wot:
  name: "My WOT Reserves"
  api_key: "ВАШ_API_KEY"
  account_id: "ВАШ_ACCOUNT_ID"
