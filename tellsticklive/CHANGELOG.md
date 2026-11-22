## 3.4.1.4.20261122202308

Dev-channel build from `main`.

### Fixed

- Pressing **Confirm** in the add-device dialog no longer freezes or restarts
  Home Assistant Core. Building the house/unit sliders for self-learning
  devices (Nexa, Proove, Anslut and similar) prepared a list of every possible
  house code — over 67 million numbers — needing gigabytes of memory and a
  multi-second stall. The first free code is now found without that list.
- This was the real cause of the Core restarts reported while pairing on a
  TellStick Net v2 / ZNet (issue #131).

### After updating

- Adding a device works as before: pick a brand, confirm, and the sliders
  start on the first code no stored device uses.
- Devices already added need no change.
