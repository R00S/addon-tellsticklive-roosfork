## 3.4.2.0.20261127010238

Dev-channel build from `main`.

### New

- The TellStick can now be used as a radio frequency transmitter by other
  integrations. Until now it only controlled its own 433 MHz devices; it can
  now send whatever another integration asks it to send — for example a Novy
  cooker hood or a set of Honeywell string lights added through Home
  Assistant's own device integrations. Pick the TellStick as the transmitter
  when that integration asks, and its commands go out through your TellStick.
  Works on a TellStick Duo and on the original TellStick Net (v1).
- Long pulses and gaps are split into several shorter ones, so signals with a
  long start or end pulse can be sent too. A mirror reinforces these commands
  exactly like your own devices' commands.

### After updating

- Requires Home Assistant 2026.5 or later.
- Nothing to reconfigure: devices, codes and automations are untouched. No
  new device or entity appears unless another integration asks for a
  transmitter.
