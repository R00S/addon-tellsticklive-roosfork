#!/usr/bin/env python3
"""
Telldus Live Cloud Sync - Sync devices from Telldus Live cloud to local config.

This script polls the Telldus Live API for devices and updates the local
tellstick.conf file when changes are detected.
"""

import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import random
import string
import subprocess
import time
import urllib.parse
import urllib.request
from collections import OrderedDict

API_BASE_URL = "https://api.telldus.com"


def generate_nonce(length=32):
    """Generate a random nonce for OAuth."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_timestamp():
    """Generate current Unix timestamp."""
    return str(int(time.time()))


def percent_encode(value):
    """Percent encode a value according to OAuth spec."""
    return urllib.parse.quote(str(value), safe="")


def create_signature_base_string(method, url, params):
    """Create the OAuth signature base string."""
    # Sort parameters by key
    sorted_params = OrderedDict(sorted(params.items()))
    # Create parameter string
    param_string = "&".join(
        f"{percent_encode(k)}={percent_encode(v)}" for k, v in sorted_params.items()
    )
    # Create base string
    return f"{method}&{percent_encode(url)}&{percent_encode(param_string)}"


def create_signature(base_string, consumer_secret, token_secret=""):
    """Create HMAC-SHA1 signature."""
    key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    signature = hmac.new(
        key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1
    )
    return base64.b64encode(signature.digest()).decode("utf-8")


def make_oauth_request(
    url, public_key, private_key, token, token_secret, method="GET", params=None
):
    """Make an OAuth 1.0a authenticated request to Telldus Live API."""
    if params is None:
        params = {}

    # OAuth parameters
    oauth_params = {
        "oauth_consumer_key": public_key,
        "oauth_nonce": generate_nonce(),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": generate_timestamp(),
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    # Combine all parameters for signature
    all_params = {**oauth_params, **params}

    # Create signature
    base_string = create_signature_base_string(method, url, all_params)
    signature = create_signature(base_string, private_key, token_secret)
    oauth_params["oauth_signature"] = signature

    # Create Authorization header
    auth_header = "OAuth " + ", ".join(
        f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in oauth_params.items()
    )

    # Build request URL with query parameters
    if params:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
    else:
        full_url = url

    # Make request
    req = urllib.request.Request(full_url, method=method)
    req.add_header("Authorization", auth_header)
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        logging.error("HTTP Error %d: %s", e.code, e.reason)
        try:
            error_body = e.read().decode("utf-8")
            logging.error("Response: %s", error_body)
        except Exception:
            pass
        raise
    except urllib.error.URLError as e:
        logging.error("URL Error: %s", e.reason)
        raise


def get_devices_from_cloud(public_key, private_key, token, token_secret):
    """Fetch devices from Telldus Live cloud."""
    url = f"{API_BASE_URL}/json/devices/list"
    params = {"supportedMethods": 23, "extras": "parameters"}

    response = make_oauth_request(
        url, public_key, private_key, token, token_secret, params=params
    )

    devices = []
    if "device" in response:
        for dev in response["device"]:
            device = {
                "id": dev.get("id"),
                "name": dev.get("name", ""),
                "protocol": dev.get("protocol", ""),
                "model": dev.get("model", ""),
            }

            # Extract parameters
            if "parameter" in dev:
                for param in dev["parameter"]:
                    param_name = param.get("name", "").lower()
                    param_value = param.get("value", "")
                    if param_name in ["house", "code", "unit", "fade"]:
                        device[param_name] = param_value

            devices.append(device)

    return devices


def normalize_device(device):
    """Normalize device data for comparison."""
    normalized = {
        "id": device.get("id"),
        "name": device.get("name", ""),
        "protocol": device.get("protocol", "").lower(),
        "model": device.get("model", ""),
    }
    for param in ["house", "code", "unit", "fade"]:
        if param in device and device[param]:
            normalized[param] = str(device[param])
    return normalized


def devices_equal(dev1, dev2):
    """Compare two devices for equality."""
    n1 = normalize_device(dev1)
    n2 = normalize_device(dev2)
    return n1 == n2


def generate_tellstick_conf(devices, output_path):
    """Generate tellstick.conf from device list."""
    lines = [
        'user = "root"',
        'group = "plugdev"',
        'ignoreControllerConfirmation = "false"',
    ]

    for device in devices:
        lines.append("")
        lines.append("device {")
        lines.append(f"  id = {device['id']}")
        lines.append(f'  name = "{device["name"]}"')
        lines.append(f'  protocol = "{device["protocol"]}"')

        if device.get("model"):
            lines.append(f'  model = "{device["model"]}"')

        # Check if we have any parameters
        params = []
        for param in ["house", "code", "unit", "fade"]:
            if device.get(param):
                params.append((param, device[param]))

        if params:
            lines.append("  parameters {")
            for name, value in params:
                lines.append(f'    {name} = "{value}"')
            lines.append("  }")

        lines.append("}")

    content = "\n".join(lines) + "\n"

    with open(output_path, "w") as f:
        f.write(content)

    logging.info("Generated %s with %d devices", output_path, len(devices))


def read_current_config(config_path):
    """Read current tellstick.conf and extract device info (simplified parser)."""
    if not os.path.exists(config_path):
        return []

    devices = []
    current_device = None
    in_parameters = False
    brace_depth = 0

    try:
        with open(config_path) as f:
            for line in f:
                line = line.strip()

                if line.startswith("device {"):
                    current_device = {}
                    brace_depth = 1
                elif current_device is not None:
                    if line == "parameters {":
                        in_parameters = True
                        brace_depth += 1
                    elif line == "}":
                        brace_depth -= 1
                        if brace_depth == 1:
                            # Closing parameters block
                            in_parameters = False
                        elif brace_depth == 0:
                            # Closing device block
                            if "id" in current_device and "name" in current_device:
                                devices.append(current_device)
                            current_device = None
                    elif "=" in line:
                        # Parse key = value lines
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        if key == "id":
                            value = int(value)
                        current_device[key] = value
    except Exception as e:
        logging.error("Error reading config: %s", e)
        return []

    return devices


def restart_telldusd():
    """Restart telldusd service by sending SIGTERM to trigger S6 restart."""
    logging.info("Signaling telldusd restart...")
    try:
        # Find telldusd process and send SIGTERM
        result = subprocess.run(
            ["pkill", "-TERM", "telldusd"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logging.info("Signaled telldusd to restart")
            return True
        else:
            logging.warning("Could not signal telldusd: %s", result.stderr)
            return False
    except Exception as e:
        logging.error("Error signaling telldusd: %s", e)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync devices from Telldus Live cloud to local config"
    )
    parser.add_argument(
        "--public-key",
        required=True,
        help="Telldus Live API public key",
    )
    parser.add_argument(
        "--private-key",
        required=True,
        help="Telldus Live API private key",
    )
    parser.add_argument(
        "--token",
        required=True,
        help="OAuth access token",
    )
    parser.add_argument(
        "--token-secret",
        required=True,
        help="OAuth token secret",
    )
    parser.add_argument(
        "--config",
        default="/etc/tellstick.conf",
        help="Path to tellstick.conf (default: /etc/tellstick.conf)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Sync interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit instead of continuous polling",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=level,
    )

    logging.info("Starting Telldus Live cloud sync")
    logging.info("Config path: %s", args.config)
    logging.info("Sync interval: %d seconds", args.interval)

    while True:
        try:
            # Fetch devices from cloud
            logging.info("Fetching devices from Telldus Live...")
            cloud_devices = get_devices_from_cloud(
                args.public_key,
                args.private_key,
                args.token,
                args.token_secret,
            )
            logging.info("Found %d devices in cloud", len(cloud_devices))

            # Compare with current config
            current_devices = read_current_config(args.config)
            logging.debug("Current config has %d devices", len(current_devices))

            # Check if anything changed
            needs_update = False
            if len(cloud_devices) != len(current_devices):
                needs_update = True
                logging.info(
                    "Device count changed: %d -> %d",
                    len(current_devices),
                    len(cloud_devices),
                )
            else:
                # Compare each device
                cloud_by_id = {d["id"]: d for d in cloud_devices}
                current_by_id = {d["id"]: d for d in current_devices}

                if set(cloud_by_id.keys()) != set(current_by_id.keys()):
                    needs_update = True
                    logging.info("Device IDs changed")
                else:
                    for dev_id in cloud_by_id:
                        if not devices_equal(cloud_by_id[dev_id], current_by_id[dev_id]):
                            needs_update = True
                            logging.info("Device %d changed", dev_id)
                            break

            if needs_update:
                logging.info("Updating tellstick.conf...")
                generate_tellstick_conf(cloud_devices, args.config)

                # Restart telldusd to apply changes
                restart_telldusd()
            else:
                logging.debug("No changes detected")

        except KeyboardInterrupt:
            logging.info("Interrupted, exiting...")
            break
        except Exception as e:
            logging.error("Error during sync: %s", e)

        if args.once:
            break

        # Wait before next sync
        logging.debug("Sleeping for %d seconds...", args.interval)
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            logging.info("Interrupted, exiting...")
            break

    logging.info("Cloud sync stopped")


if __name__ == "__main__":
    main()
