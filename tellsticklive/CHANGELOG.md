## 3.4.1.2.20261121220411

Dev-channel build from `main`.

### Fixed

- Pairing a self-learning switch (Nexa, Proove, Anslut and similar) through a
  TellStick Net v2 / ZNet now sends the normal ON code instead of a dedicated
  learn frame. Receivers store the ON code, which is what their own remotes
  send, so pairing completes.
- This also stops the learn step from asking the Net v2 / ZNet firmware for a
  frame it cannot build properly, which is the suspected cause of Home
  Assistant Core restarting while pairing (issue #131).
- TellStick Net v1 is unchanged: it still sends its raw learn pulse train,
  which is confirmed on hardware.

### After updating

- Put the receiver in learn mode, then press **Send learn signal** (or add the
  device again) to pair it.
- Devices that already work need no change.
