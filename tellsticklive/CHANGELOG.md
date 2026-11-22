## 3.4.1.5.20261122204111

Dev-channel build from `main`.

### Changed behaviour

- None — this is housekeeping on top of 3.4.1.4, with nothing new to see or
  do. After removing the huge house-code list from the add-device dialog, the
  same review was run over the rest of the integration, starting with the
  unit slider in that dialog. No other place builds a list of every possible
  code, and the unit slider now walks its range instead of copying it, so a
  wide widget can never freeze Core this way again.

### After updating

- Nothing to reconfigure. Devices, codes and automations are untouched.
