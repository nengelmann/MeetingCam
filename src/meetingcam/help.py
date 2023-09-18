#!/usr/bin/env python3

import sys

import typer
from device import DeviceHandler


def main() -> None:
    """Initialize the device handler and print information on how to setup and use this tool."""
    device_handler = DeviceHandler()
    device_handler.pprint.available_devices(
        device_handler.mapping, device_handler.available_devices_real
    )
    device_handler.pprint.add_virtual_devices(
        device_handler.available_devices_real
    )
    device_handler.pprint.run_main_command(device_handler.mapping)
    sys.exit(0)


if __name__ == "__main__":
    typer.run(main)
