# Home Assistant Add-on: TellStick with Telldus Live

![Project Stage][project-stage-shield]

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[![Github Actions][github-actions-shield]][github-actions]
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

A modified version of the official TellStick add-on with Telldus Live cloud integration.

## About

This add-on enables TellStick and TellStick Duo hardware to work with Home Assistant, with the added ability to publish your devices and sensors to Telldus Live cloud service.

> **Note**: The official Home Assistant TellStick add-on was deprecated in December 2024 because the underlying Telldus library is no longer maintained by its original manufacturer. This fork continues to provide TellStick support for those who need it.

### Features

- **Local Control**: Control TellStick devices directly from Home Assistant
- **Telldus Live Integration**: Publish devices and sensors to Telldus Live for remote access
- **Flexible Operation Modes**: Run in local-only, live-only, or combined mode
- **Sensor Support**: Automatic discovery and publishing of wireless sensors
- **Service Calls**: Control devices using Home Assistant service calls

## Quick Start

### 1. Install the Add-on

1. Add this repository to your Home Assistant add-on store
2. Find "TellStick with Telldus Live" and click Install
3. Configure your devices (see Configuration section below)

### 2. Configure Devices

Edit the add-on configuration with your TellStick devices. The configuration follows the same format as the original [TellStick configuration][conf]:

```yaml
enable_local: true
enable_live: false
devices:
  - id: 1
    name: Living Room Light
    protocol: arctech
    model: selflearning-switch
    house: "12345678"
    unit: "1"
  - id: 2
    name: Kitchen Dimmer
    protocol: arctech
    model: selflearning-dimmer
    house: "12345678"
    unit: "2"
```

### 3. Connect to Home Assistant (Local Mode)

Add the following to your `configuration.yaml`:

> **Important**: The hostname is unique to each add-on installation. To find your correct hostname:
> 1. Start the add-on and check the logs
> 2. Look for the message showing your exact `tellstick:` configuration
> 3. Copy the hostname shown in the logs to your `configuration.yaml`

```yaml
# TellStick core integration
# Replace YOUR_ADDON_HOSTNAME with the hostname shown in the add-on logs
tellstick:
  host: YOUR_ADDON_HOSTNAME
  port: [50800, 50801]

# Enable TellStick switches
switch:
  - platform: tellstick

# Enable TellStick lights/dimmers
light:
  - platform: tellstick

# Enable TellStick sensors
sensor:
  - platform: tellstick
    temperature_scale: "°C"
    only_named:
      - id: 135
        name: Outside Temperature
      - id: 136
        name: Kitchen Humidity
```

Restart Home Assistant after making these changes.

### 4. Enable Telldus Live (Optional)

1. Set `enable_live: true` in the add-on configuration
2. Restart the add-on
3. Check the add-on logs for a registration URL
4. Visit the URL and log in to Telldus Live
5. Copy the UUID from the URL (the part after `uuid=`)
6. Add `live_uuid: your-uuid-here` to the configuration
7. Restart the add-on

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_local` | bool | `true` | Enable local Home Assistant integration via TCP ports |
| `enable_live` | bool | `false` | Enable Telldus Live cloud connection |
| `live_uuid` | string | - | UUID obtained during Telldus Live registration |
| `live_delay` | int | `10` | Seconds to wait before connecting to Telldus Live (increase for new sensor discovery) |
| `devices` | list | - | List of TellStick devices to control |
| `sensors` | list | - | List of sensors to publish to Telldus Live |

### Device Configuration

Each device requires:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique numeric identifier (1 or higher) |
| `name` | Yes | Human-readable name |
| `protocol` | Yes | Device protocol (see [protocol list][protocol-list]) |
| `model` | No | Device model (selflearning-switch, selflearning-dimmer, codeswitch, bell) |
| `house` | Varies | House code (protocol-specific) |
| `unit` | Varies | Unit code (protocol-specific) |
| `code` | Varies | Device code (for some protocols) |
| `fade` | No | Enable fade for dimmers |

**Supported Protocols**: arctech, brateck, comen, everflourish, fineoffset, fuhaote, hasta, ikea, kangtai, mandolyn, oregon, risingsun, sartano, silvanchip, upm, waveman, x10, yidong

### Sensor Configuration (for Telldus Live)

Each sensor requires:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Sensor ID (found via service call) |
| `name` | Yes | Display name for Telldus Live |
| `protocol` | Yes | Sensor protocol (fineoffset, oregon, etc.) |
| `model` | Yes | Sensor model (temperature, temperaturehumidity) |

## Service Calls

You can control TellStick devices using the `hassio.addon_stdin` service. This is useful for automation and debugging.

### Available Commands

```yaml
# Turn on a device
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "on"
    device: 1

# Turn off a device
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "off"
    device: 1

# Set dimmer level (0-255)
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "dim"
    device: 2
    level: 128

# Ring a bell device
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "bell"
    device: 3

# List all devices
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "list"

# List all sensors (to find sensor IDs)
service: hassio.addon_stdin
data:
  addon: 32b8266a_tellsticklive
  input:
    function: "list-sensors"
```

Check the add-on logs to see the output of these commands.

## Troubleshooting

### "Could not connect to the Telldus Service (-6)"

This error indicates Home Assistant cannot reach the TellStick service. Solutions:

1. **Ensure the add-on is running** - Check the add-on status in Supervisor
2. **Verify configuration** - Check that `enable_local: true` is set
3. **Wait for startup** - The add-on needs time to initialize sockets. Wait 30-60 seconds after starting the add-on before restarting Home Assistant
4. **Check host and ports** - Verify your `configuration.yaml` has the correct host (`32b8266a-tellsticklive`) and ports (`[50800, 50801]`)
5. **Restart sequence** - Stop the add-on, wait 10 seconds, start it again, wait 30 seconds, then restart Home Assistant

### Telldus Live Not Connecting After Restart

If the add-on shows registration instructions instead of connecting:

1. Ensure `live_uuid` is correctly set in the configuration
2. The UUID format must be: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (lowercase hexadecimal)
3. Check for typos - the UUID is case-sensitive
4. Verify the UUID by checking your Telldus Live account

### Sensors Not Appearing in Telldus Live

1. **Increase delay** - Set `live_delay` to 300-600 seconds for initial sensor discovery
2. **Check sensor transmission** - Ensure sensors are actively transmitting (check batteries, range)
3. **Verify configuration** - Check that sensor protocol and model match your actual sensor
4. **Check IDs** - Use the `list-sensors` service call to find the correct sensor ID

### Devices Not Responding

1. **Check USB connection** - Ensure TellStick hardware is properly connected
2. **Verify device configuration** - Protocol, model, house code, and unit must match your remote
3. **Test with tdtool** - Use the service calls to test device control directly
4. **Check logs** - Look at the add-on logs for error messages

### Sensors Appearing as Switches

This can happen due to protocol mismatches. Verify:
- The sensor ID matches your actual sensor
- The protocol and model are correctly specified
- You're using `only_named` in your sensor configuration to avoid auto-discovery issues

## Migrating from Official Add-on

If you're migrating from the deprecated official TellStick add-on:

1. **Export your device configuration** - Save your current device IDs, protocols, and settings
2. **Install this add-on** - Add the repository and install
3. **Copy device configuration** - Transfer your device settings to this add-on's configuration
4. **Update configuration.yaml** - Change the host from `core-tellstick` to `32b8266a-tellsticklive`
5. **Restart** - Restart the add-on and Home Assistant

## Support

Got questions or issues?

- [Open an issue on GitHub][issue]
- Check existing issues for solutions

## License

GNU General Public License v3.0 or later

Copyright (c) 2019-2024 Erik Hilton  
Copyright (c) 2024-2025 R00S (roosfork modifications)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

See the [LICENSE.md](LICENSE.md) file for the complete license text.

**Note**: This project was originally licensed under MIT by Erik Hilton, but
has been relicensed to GPL v3 to comply with the licensing requirements of
included GPL-licensed components (tellive-py, tellcore-py, telldus-core).
See the [NOTICE](NOTICE) file for detailed attribution and licensing
information for all incorporated components.

## Acknowledgments

This add-on would not be possible without the contributions of many individuals
and organizations:

### Core Contributors

- **Erik Hilton (erik73)** - Original author and maintainer of the
  addon-tellsticklive fork. Erik created this add-on and continues to maintain
  a fork of the telldus-core library, ensuring TellStick hardware remains
  usable after the manufacturer discontinued support.
  - Repository: https://github.com/erik73/addon-tellsticklive
  - Telldus fork: https://github.com/erik73/telldus

- **Erik Johansson (erijo)** - Author and maintainer of the Python libraries
  that power this add-on's functionality:
  - **tellive-py** - Python wrapper for Telldus Live cloud service
  - **tellcore-py** - Python bindings for TellStick Core library
  - Repositories: https://github.com/erijo/tellive-py and https://github.com/erijo/tellcore-py

### Upstream Projects

- **Telldus Technologies AB** - Original creators of TellStick hardware and
  the telldus-core daemon software (licensed under LGPL 2.1)

- **Home Assistant Team** - Creators of the Home Assistant platform and the
  original TellStick add-on (now deprecated) that inspired this work
  - Original add-on: https://github.com/home-assistant/addons

### Community

- All contributors who have reported issues, provided feedback, and helped
  improve this add-on

- The open source community for creating and maintaining the tools and
  libraries that make this project possible

For detailed licensing and attribution information, see the [NOTICE](NOTICE) file.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/R00S/addon-tellsticklive-roosfork.svg
[commits]: https://github.com/R00S/addon-tellsticklive-roosfork/commits/main
[conf]: http://developer.telldus.com/wiki/TellStick_conf
[github-actions-shield]: https://github.com/R00S/addon-tellsticklive-roosfork/workflows/CI/badge.svg
[github-actions]: https://github.com/R00S/addon-tellsticklive-roosfork/actions
[issue]: https://github.com/R00S/addon-tellsticklive-roosfork/issues
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[protocol-list]: http://developer.telldus.com/wiki/TellStick_conf
