# Home Assistant TellStick with Telldus Live

TellStick and TellStick Duo service with a possibility to export devices
to Telldus Live!

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## About

This add-on is a modification of the official TellStick addon.
It adds the ability to have your devices and sensors published Telldus Live.
See the official addon documentation for details on device setup.

## Installation

Follow these steps to get the add-on installed on your system:

Add the repository `https://github.com/erik73/hassio-addons`.
Find the "TellStick with Telldus Live" add-on and click it.
Click on the "INSTALL" button.

## How to use

### Starting the add-on

After installation you are presented with an example configuration.

Adjust the add-on configuration to match your devices. See the official add-on
configuration options for details.
Save the add-on configuration by clicking the "SAVE" button.
Start the add-on.

### Home Assistant integration

You have two options for integrating with Home Assistant:

#### Option 1: Telldus Live Integration (Cloud-based)

If you want to use the Telldus Live cloud service for all device control:

1. Set `enable_local: false` in the add-on configuration
2. Set `enable_live: true` and configure your `live_uuid`
3. In Home Assistant, add the **Telldus Live** integration via Settings → Devices & Services

This method does NOT require any `configuration.yaml` entries.

#### Option 2: Local TellStick Integration (Direct connection)

If you want to run in local mode (the same way the official addon runs), you will
need to add internal communication details to the `configuration.yaml`
file to enable the integration with the add-on:

```yaml
# Example configuration.yaml entry
# Replace YOUR_ADDON_HOSTNAME with the hostname shown in the add-on logs
tellstick:
  host: YOUR_ADDON_HOSTNAME
  port: [50800, 50801]
```

**Finding Your Hostname**: Start the add-on and check the logs. When local mode is
enabled, the logs will display the exact configuration you need to add to your
`configuration.yaml`, including the correct hostname.

**IMPORTANT - Restart Sequence**: The add-on must be fully started BEFORE Home
Assistant tries to connect. If you see errors like "Could not connect to the
Telldus Service (-6)", follow these steps:

1. Start the add-on and wait for the logs to show:
   `TellStick service is ready for Home Assistant!`
2. Only then, restart Home Assistant (Settings → System → Restart)
3. Check that the tellstick integration loads without errors

## Configuration

For device configuration, refer to the official addon instructions.

All devices configured and working will be visible in your Telldus Live account when
you have completed the configuration steps below.

Example sensor configuration:

```yaml
enablelive: false
sensors:
  - id: 199
    name: Example sensor
    protocol: fineoffset
    model: temperature
  - id: 215
    name: Example sensor two
    protocol: fineoffset
    model: temperaturehumidity
```

Please note: After any changes have been made to the configuration,
you need to restart the add-on for the changes to take effect.

### Option: `sensors` (required)

Add one or more sensors entries to the add-on configuration for each
sensor you'd like to add to Telldus Live.

#### Option: `sensors.id` (required)

This is the id of the sensor. To find out what id to use you have to use the
service call hassio.addon_stdin with the following data:
`{"addon":"32b8266a_tellsticklive","input":{"function":"list-sensors"}}`
Look in the addon log, and you should be able to find the id, protocol and model
for your sensors.

#### Option: `sensors.name` (required)

A name for your sensor, that will be displayed in Telldus Live.

#### Option: `sensors.protocol` (required)

This is the protocol the sensor uses. See above regarding service call to find
this information.

#### Option: `sensors.model` (optional)

The model of the sensor. See above regarding the service call to find this information.

## Service calls

See the official addon instructions.

## How to enable the Telldus Live connection

Once you are happy with the devices and sensors configuration it is time to establish
the connection to Telldus Live, and generate an UUID that will be used to connect.

Set the config option:

```yaml
enable_live: true
```

Restart the addon and look in the addon log.
You will get a URL to visit in your browser to establish the connection
between your Live account and this addon.
That URL take you to Telldus Live, and you will be asked to login or create an account
if you don´t have one.

Also make sure you copy the string after uuid= in the URL, and create the following
config entry:

```yaml
live_uuid: de1333b5-154c-5342-87dc-6b7e0b2096ab
```

The above is an example. Yours will look different.

Finally, if you want to disable the local connection to HA, and get all of
your devices from Telldus Live through the Telldus Live integration
you have the set the following config option to false. In that case, you
can remove all tellstick configuration from configuration.yaml.

```yaml
enable_local: false
```

Once all this is complete, you can restart the addon, and your devices and
sensors will appear in Telldus Live!

```yaml
live_delay: 10
```

The above config options is by default set to 10 seconds. It is used
to control how long to wait before establishing the connection to Telldus.
This is important to set this to a higher value when new sensors has been
added, because the sensors has to be found by your Telldus device before
connecting.
So in short, if new sensors has been added to your configuration, set it
to for example 600 seconds. Once the sensors are found, and have been
assigned the correct name in the Telldus Live system, it can be reduced
to 10 seconds again.

## Troubleshooting

### Error: "Could not connect to the Telldus Service (-6)"

This error occurs when Home Assistant starts before the add-on is ready. The add-on
needs to create its TCP bridges on ports 50800 and 50801 before Home Assistant can
connect.

**Solution:**

1. Go to the add-on logs and wait until you see:
   `TellStick service is ready for Home Assistant!`
2. Restart Home Assistant: Settings → System → Restart
3. The tellstick integration should now connect successfully

**Tip:** This typically happens after a system reboot. In the future, after a reboot,
wait 30-60 seconds for the add-on to fully start before restarting Home Assistant.

### No entities appearing in Home Assistant

If you can control devices through Telldus Live but no entities appear in HA:

1. **Check your integration type:**
   - Using `enable_local: true`? You need the `tellstick:` config in `configuration.yaml`
   - Using `enable_local: false`? Use the Telldus Live integration instead

2. **For local mode:** Make sure you have platform configurations:
   ```yaml
   switch:
     - platform: tellstick
   
   light:
     - platform: tellstick
   
   sensor:
     - platform: tellstick
   ```

3. **For Telldus Live mode:** Add the Telldus Live integration via
   Settings → Devices & Services → Add Integration → Telldus Live

### Devices not syncing to Telldus Live

If devices are configured but not appearing in your Telldus Live account:

1. Check that `enable_live: true` is set
2. Verify your `live_uuid` is correctly configured
3. Check the add-on logs for connection messages to Telldus Live
4. If you recently added sensors, increase `live_delay` to 600 seconds to allow
   sensor discovery before the Live connection is established

### Device configuration format

When configuring devices, note the following format rules:

- **protocol**: Must be one of the supported protocols (e.g., `arctech`, `everflourish`)
- **model**: Can include a brand suffix (e.g., `selflearning-switch:proove`, `selflearning-switch:nexa`)

**Common mistake**: Do NOT put the model in the protocol field.

❌ Wrong:
```yaml
protocol: arctech:selflearning-switch
```

✓ Correct:
```yaml
protocol: arctech
model: selflearning-switch
```

## Support

Got questions?

You could [open an issue here][issue] GitHub.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[conf]: http://developer.telldus.com/wiki/TellStick_conf
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[issue]: https://github.com/erik73/addon-tellsticklive/issues
[protocol-list]: http://developer.telldus.com/wiki/TellStick_conf
[repository]: https://github.com/erik73/hassio-addons
