#!/usr/bin/env python3

"""This script facilitates the management and utilization of virtual and real camera devices."""

import re
import signal
import sys
from pathlib import Path
from types import FrameType
from typing import Any

import depthai
from constants import DEPTHAI, WEBCAM
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from utils import DepthaiCapture, VideoCapture
from v4l2ctl import V4l2Capabilities, V4l2Device


class V4l2Capture(V4l2Device):
    """Handle real camera devices.

    Inherits from v4l2ctl.V4l2Device and extends functionalities with
    methods to safely enter and exit.
    """

    def __enter__(self) -> V4l2Device:
        """Enter method for context management, returning self."""
        return self

    def __exit__(self, *args: tuple[Any]) -> None:
        """Exit method for context management, releasing the devices."""
        self.flush()
        self.close()


class DeviceHandler:
    """Base class for management and mapping of real and virtual devices."""

    def __init__(self) -> None:
        """Initialize the WebcamDevice by setting up necessary mappings and signal handler."""
        signal.signal(signal.SIGINT, self._interrupt)

        self.mapping = self.device_mapping()
        self.pprint = DevicePrinter()

    def _interrupt(self, signal: int, frame: FrameType | None) -> None:
        """Handle SIGINT signal by stopping the device and exiting the program."""
        self.pprint.device_stopped()
        sys.exit(0)

    def init_device(self, device_path: str | None) -> tuple[str, str]:
        """Initialize the device by analyzing the device path and mapping it to a real or virtual device.

        Args:
            device_path -- the path of the device to initialize, None if not specified

        Returns:
            A tuple containing paths to the real and virtual devices.
        """
        device_map = {
            device["path_real"]: device["path_virtual"]
            for device in self.mapping.values()
        }
        if device_path:
            # device is specified as argument in command line
            if device_path in device_map.keys():
                # check if specified device is available in real devices and has virtual counterpart
                self.real_path = device_path
                virtual_path = device_map[device_path]
                return virtual_path
            else:
                # if not print that the specified device needs to have a virtual counterpart and how to do it
                self.pprint.device_not_available(device_path)
                self.pprint.available_devices(
                    self.mapping, self.available_devices_real
                )
                self.pprint.add_virtual_devices(
                    self.available_devices_real, self.type
                )
                self.pprint.run_main_command(self.mapping)
                sys.exit()
        else:
            # device is not specified
            if device_map:
                # no device is specified, but a real device with virtual counterpart is available
                # print in the available devices and point out that the first available device with virtual counterpart will be used
                device = list(device_map.items())[0]
                self.real_path = device[0]
                virtual_path = device[1]
                self.pprint.available_devices(
                    self.mapping, self.available_devices_real
                )
                self.pprint.run_main_command(self.mapping)
                sys.exit()
            else:
                # no device is specified and no real device with virtual counterpart is available
                self.pprint.device_not_available(device_path)
                self.pprint.available_devices(
                    self.mapping, self.available_devices_real
                )
                self.pprint.add_virtual_devices(
                    self.available_devices_real, self.type
                )
                self.pprint.run_main_command(self.mapping)
                sys.exit()

    def get_device(self):
        if self.real_path:
            return VideoCapture(self.real_path)
        else:
            raise LookupError(
                "self.real_path is {self.real_path}. Device initialization"
                " 'self.init_device(device_path)' is needed before a device"
                " instance is created."
            )

    def device_mapping(self) -> dict[int, dict[str, str]]:
        """Create a mapping from real camera devices to virtual camera devices.

        Returns:
            A dictionary that contains information about real and virtual devices.
        """

        device_map = {}

        (paths_real, labels_real) = self.available_devices_real
        (paths_virtual, labels_virtual) = self.available_devices_virtual

        # extract the IDs (first number in virtual camera label) of available virtual cameras for mapping it to real cameras
        # the mapping index is same as real cameras path id. e.g. /dev/video_n_ with n as id
        if self.type == WEBCAM:
            mapping_ids = [
                int(re.findall(r"\d+", label)[0]) for label in labels_virtual
            ]
            ids_real = [
                int(path.replace("/dev/video", "")) for path in paths_real
            ]
            try:
                mapping_indices = [ids_real.index(id) for id in mapping_ids]
            except:
                print(
                    "The virtual cameras are not matching with attached real"
                    " cameras. Has a camera be unplugged?\n"
                )
                print(
                    "The specified virtual label is"
                    f" {str(labels_virtual)[1:-1]}."
                )
                print(
                    "May you wanted to run MeetingCam with --depthai argument?"
                )
                sys.exit(0)

        elif self.type == DEPTHAI:
            mapping_indices = []
            for i, mxid in enumerate(paths_real):
                for j, label in enumerate(labels_virtual):
                    if mxid in label:
                        mapping_indices.append(j)
        else:
            raise NotImplementedError(
                "Device type needs to be either 'webcam' or 'depthai'."
            )

        for i, j in enumerate(mapping_indices):
            device_map[i] = {
                "path_real": paths_real[j],
                "label_real": labels_real[j],
                "path_virtual": paths_virtual[i],
                "label_virtual": labels_virtual[i],
            }

        return device_map

    def get_available(self, real: bool) -> tuple[list[str], list[str]]:
        """Return a list of available real or virtual camera devices based on the input flag.

        Args:
            real --- a flag to determine whether to return real or virtual devices.

        Returns:
            A tuple containing lists of device paths and labels.
        """

        device_paths = []
        labels = []

        with V4l2Capture() as v4l2:
            for device in v4l2.iter_devices(skip_links=True):
                if (
                    real
                    and not self._is_virtual_device(device)
                    and V4l2Capabilities.VIDEO_CAPTURE in device.capabilities
                ):
                    device_path, label = self._get_device_info(device)
                elif (
                    not real
                    and self._is_virtual_device(device)
                    and V4l2Capabilities.VIDEO_OUTPUT in device.capabilities
                ):
                    device_path, label = self._get_device_info(device)
                else:
                    continue

                labels.append(label)
                device_paths.append(device_path)

        return device_paths, labels

    def device_running(self) -> None:
        """Print the running devices."""
        self.pprint.device_running()

    def _is_virtual_device(self, device: V4l2Device) -> bool:
        """Check if the device is a virtual device.

        Args:
            device (V4l2Device) --- the device to check.

        Returns:
            True if the device is virtual, False otherwise.
        """
        virtual = True if "platform:v4l2loopback" in str(device.bus) else False
        return virtual

    def _get_device_info(self, device: V4l2Device) -> tuple[str, str]:
        """Extract and return device information including path and label.

        Args:
            device (V4l2Device) --- the device to extract information from.

        Returns:
            A tuple containing the device path (str) and label (str).

        Raises:
            AssertionError: If the device path does not follow the expected format or does not exist.
        """
        device_path = str(device.device)
        card_label = str(device.name)

        assert device_path.__contains__(
            "/dev/video"
        ), "Device name '{device_name}' should be of format '/dev/video_n_'."
        assert Path(
            device_path
        ).exists(), "Device path '{device_name}' does not exist."
        return device_path, card_label


class WebcamDevice(DeviceHandler):
    """Handles the management and mapping of real and virtual webcam devices."""

    def __init__(self) -> None:
        """Initialize the WebcamDevice class."""

        self.type = WEBCAM
        self.real_path = None
        self.available_devices_real = None
        self.available_devices_virtual = None

        self.update_available()
        super().__init__()

    def get_device(self):
        if self.real_path:
            return VideoCapture(self.real_path)
        else:
            raise LookupError(
                "self.real_path is {self.real_path}. Device initialization"
                " 'self.init_device(device_path)' is needed before a device"
                " instance is created."
            )

    def update_available(self) -> None:
        """Update the list of available real and virtual devices."""
        self.available_devices_real = self.get_available(real=True)
        self.available_devices_virtual = self.get_available(real=False)


class DepthaiDevice(DeviceHandler):
    """Handles the management and mapping of depthai and virtual devices."""

    def __init__(self, pipeline) -> None:
        """Initialize the WebcamDevice class."""

        self.type = DEPTHAI
        self.real_path = None
        self.available_devices_real = None
        self.available_devices_virtual = None

        self.update_available()
        super().__init__()

        self.usb_speed = depthai.UsbSpeed.SUPER_PLUS
        self.device_info = None
        self.pipeline = pipeline

    def get_device(self):
        if self.real_path:
            self.device_info = depthai.DeviceInfo(self.real_path)
            return DepthaiCapture(
                pipeline=self.pipeline,
                deviceInfo=self.device_info,
                maxUsbSpeed=self.usb_speed,
            )
        else:
            raise LookupError(
                "self.real_path is {self.real_path}. Device initialization"
                " 'self.init_device(device_path)' is needed before a device"
                " instance is created."
            )

    def update_available(self) -> None:
        """Update the list of available real and virtual devices."""
        self.available_devices_real = self.get_available_depthai()
        self.available_devices_virtual = self.get_available(real=False)

    def get_available_depthai(self) -> dict:
        """Get available depthai camera devices.

        Returns:
            dict: _description_
        """
        device_paths = []
        labels = []

        device_info = depthai.Device.getAllAvailableDevices()

        for device in device_info:
            labels.append(f"OAK Device on port {device.name}")
            device_paths.append(device.mxid)

        return device_paths, labels


class DevicePrinter:
    """Handles printing functions for device handling."""

    def __init__(self) -> None:
        """
        Initialize the DevicePrinter instance.

        Instantiates a Console object and initializes styles for different types of messages (danger, warning, ok).
        """
        self.console = Console()
        self.danger_style = Style(color="red", blink=True, bold=True)
        self.warning_style = Style(color="yellow", blink=True, bold=True)
        self.ok_style = Style(color="green", blink=True, bold=True)

    def available_devices(
        self,
        device_map: dict[int, dict[str, Any]],
        available_devices_real: tuple[
            list[str], list[str], list[int], list[str]
        ],
    ) -> None:
        """
        Print available real and virtual devices to the console.

        Args:
            device_map --- a mapping of device ids to device properties including paths and labels.
            available_devices_real --- a tuple containing lists of paths, labels, ids, and another attribute of real devices.

        The method extracts real and mapped device information and formats them for console printing.
        """

        (paths_real, labels_real) = available_devices_real

        devices_real = [
            "|" + label + "|" + str(path) + "|"
            for label, path in zip(labels_real, paths_real)
        ]
        devices_real = (
            str(devices_real).replace("'", "").replace(", ", "\n")[1:-1]
        )

        devices_mapped = [
            "|"
            + v["label_real"]
            + "|"
            + v["path_real"]
            + " -> |"
            + v["label_virtual"]
            + "|"
            + v["path_virtual"]
            + "|"
            for v in device_map.values()
        ]
        devices_mapped = (
            str(devices_mapped).replace("'", "").replace(", ", "\n")[1:-1]
        )

        text = f"""
        # Available devices
        
        | Device      | Path       |
        |-------------|------------|
        {devices_real}
        
        # Available devices with virtual counterpart
        
        | Device      | Path       | Virtual Device | Virtual Path |
        |-------------|------------|----------------|--------------|
        {devices_mapped}

        """
        self._print(text)

    def add_virtual_devices(
        self,
        available_devices_real: tuple[list[str], list[str]],
        type: str | int,
    ) -> None:
        """
        Print instructions to add virtual devices to the console.

        Args:
            available_devices_real --- a tuple containing lists of paths, labels, ids, and another attribute of real devices.

        The method extracts device labels and ids to create instructions for adding virtual devices and prints them to the console.
        """
        (device_paths, labels) = available_devices_real

        cli_cmd_single = []
        labels_str = []

        if type == WEBCAM:
            ids = [
                int(path.replace("/dev/video", "")) for path in device_paths
            ]
            vd_nrs = ids
            for idx, label in zip(ids, labels):
                cli_cmd_single.append(
                    "`sudo modprobe v4l2loopback devices=1"
                    f" video_nr={idx} card_label='MeetingCam{idx} {label}'`"
                )
                labels_str.append(f"MeetingCam{idx} {label}")

            labels_str = str(labels_str).replace(", ", ",")[1:-1]
            vd_nrs = str(vd_nrs).replace(" ", "")[1:-1]
            cli_cmd_multi = (
                "`sudo modprobe v4l2loopback"
                f" devices={len(ids)} video_nr={str(vd_nrs)} card_label='{labels_str[1:-1]}'`"
            )
        elif type == DEPTHAI:
            ids = device_paths
            for idx, label in zip(ids, labels):
                cli_cmd_single.append(
                    "`sudo modprobe v4l2loopback devices=1"
                    f" card_label='MeetingCam{idx} {label}'`"
                )
                labels_str.append(f"MeetingCam{idx} {label}")

            labels_str = str(labels_str).replace(", ", ",")[1:-1]
            cli_cmd_multi = (
                "`sudo modprobe v4l2loopback"
                f" devices={len(ids)} card_label='{labels_str[1:-1]}'`"
            )

        else:
            raise NotImplementedError(
                "Device type needs to be either 'webcam' or 'depthai'."
            )

        cli_cmd_single = (
            str(cli_cmd_single).replace(", ", "\n\n").replace('"', "")[1:-1]
        )

        self.console.print(
            "Follow the instruction below! :arrow_down:", style=self.ok_style
        )

        text = f"""
        # Add virtual devices

        The following describes on how to add virtual devices. A virtual device is needed to publish a modified camera stream.
        You can add a single device or multiple devices.
        
        ## Add a singel device
        Add a single device by running **one** of the following commands.
        
        {cli_cmd_single}
        
        ## Add multiple devices
        Add all your devices by running
        
        {cli_cmd_multi}
        
        You can **reset** the **virtual devices** running **`sudo modprobe -r v4l2loopback`**.
        If this isn't working you need to restart your system.
        """

        self._print(text)

    def device_not_available(self, device: V4l2Device) -> None:
        """Print a warning message indicating the specified device is not available.

        Args:
            device (V4l2Device) --- the device that is not available.
        """
        text = f"""
        **Device not available** 
        The specified device '{device}' is not available or does not have a virtual counterpart.
        
        """
        self.console.print("Warning! :warning:", style=self.warning_style)
        self._print(text)

    def used_device(self, real_path: str) -> None:
        self.console.print("Device ready! :ok_hand:", style=self.ok_style)
        self.console.print(
            f"Using device on {real_path}.", style=Style(bold=True)
        )
        self.console.print(
            "To use another device, specify it via command line and the"
            " devices real path, e.g. '/dev/video0'."
        )

    def run_main_command(self, device_map: dict[int, dict[str, str]]) -> None:
        """Print a message guiding the user to run the main command depending on the device map status.

        Args:
            device_map --- a dictionary containing the device map information.
        """
        if not device_map:
            self.console.print(
                "\nAdd a device with one of the above commands now.\n",
                style=Style(bold=True),
            )
            return

        elif len(device_map) == 1:
            self.console.print(
                "\nAlright, a device has been added. :white_check_mark:"
            )

        else:
            ticks = (
                str([":white_check_mark:" for i in range(len(device_map))])
                .replace("'", "")
                .replace(", ", " ")[1:-1]
            )
            self.console.print(
                f"\nAlright, multiple devices have been added. {ticks}"
            )

        self.console.print("Now it's time to run MeetingCam!\n")

        for key, device in device_map.items():
            self.console.print(
                f"For {device['label_real']} run:", style=Style(bold=True)
            )
            self.console.print(
                "python src/meetingcam/main.py --device-path"
                f" {device['path_real']} --name YourName",
                style="bold cyan on black",
            )

    def device_running(self) -> None:
        """Print a message indicating that the device is currently running and how to access the stream."""
        self.console.print(
            "Device running! :arrow_forward:", style=self.ok_style
        )
        self.console.print(
            "You can now access the modified camera stream in Meets, Teams or"
            " Zoom. :rocket:",
            style=Style(bold=True),
        )
        self.console.print(
            "Press `Ctrl+C` to stop the running stream and access your device"
            " normally."
        )

    def device_stopped(self) -> None:
        """Print a message indicating that the device has stopped and can now be accessed normally."""
        self.console.print(
            "Device stopped. :raised_hand:", style=self.danger_style
        )
        self.console.print(
            "You can access your device now as usual. MeetingCam has stopped.",
            style=Style(bold=True),
        )

    def _print(self, text: str) -> None:
        """Format text to markdown and print formatted text to the console.

        Args:
            text --- text to be formatted and displayed on the console.
        """
        text = self._reformat(text)
        md = Markdown(text)
        self.console.print(md)

    def _reformat(self, text: str) -> str:
        """Removes the indent spaces from indented multiline text, necessary for compatibility with the rich library's markdown format.

        Args:
            text --- the text to be reformatted.

        Returns:
            The reformatted text with removed indent spaces.
        """
        return text.replace("      ", "")


if __name__ == "__main__":
    pass
