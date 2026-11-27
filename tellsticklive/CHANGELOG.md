## 3.4.2.1.20261127011202

Dev-channel build from `main`.

### Fixed

- The transmitter entity added in 3.4.2.0 never appeared. Home Assistant
  registered it as disabled — a preference stored on the integration entry —
  so it was hidden and could not be chosen as a sender. It is now registered
  enabled, whatever that preference says. If you already installed 3.4.2.0,
  update and restart: the entity switches itself back on.

### After updating

- Requires Home Assistant 2026.5 or later.
- Nothing to reconfigure; your own devices, codes and automations are
  untouched.
