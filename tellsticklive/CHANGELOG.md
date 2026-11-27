## 3.4.2.2.20261127023941

Dev-channel build from `main`.

### New

- A diagnostic action, `tellstick_local.poc_rf_command`, that sends raw
  433 MHz timings through the TellStick the same way another integration
  does. It exists so a transmitter can be tested without installing a
  consumer integration first. Nothing is stored and nothing changes for
  your own devices.

### After updating

- Requires Home Assistant 2026.5 or later. Safe to ignore unless you are
  testing.
- This is the first stable release since 3.3.3.0: everything from 3.4.0.x and
  3.4.1.x is included, and the sections below describe those changes.
