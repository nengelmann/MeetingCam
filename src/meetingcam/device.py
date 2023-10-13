"""This file facilitates the management and utilization of virtual and real camera devices."""

import re
import signal
import sys
from pathlib import Path
from types import FrameType
from typing import Any

import depthai
from constants import DEPTHAI, WEBCAM
from print import Printer
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
        """Initialize the DeviceHandler by setting up necessary mappings and signal handler."""
        signal.signal(signal.SIGINT, self._interrupt)

        self.mapping = self.device_mapping()
        self.pprint = Printer()

    def _interrupt(self, signal: int, frame: FrameType | None) -> None:
        """Handle SIGINT signal by stopping the device and exiting the program."""
        self.pprint.device_stopped()
        sys.exit(0)

    def init_device(self, device_path: str | None) -> str:
        """Initialize the device by analyzing the device path and mapping it a virtual device.

        Args:
            device_path -- the path of the device to initialize, None if not specified

        Returns:
            A a string containing the path to the virtual device.
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
                self.pprint.run_main_command(self.mapping, self.type)
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
                self.pprint.run_main_command(self.mapping, self.type)
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
                self.pprint.run_main_command(self.mapping, self.type)
                sys.exit()

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
                mapping_indices = {}

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
        """Print the running device."""
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

    def get_device(self) -> VideoCapture:
        """Get a VideoCapture class instance can be used for webcam image acquisition.

        Raises:
            LookupError in case the device path is incorrect.

        Returns:
            A VideoCapture class instance.
        """
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
        """Initialize the DepthaiDevice class."""

        self.type = DEPTHAI
        self.real_path = None
        self.available_devices_real = None
        self.available_devices_virtual = None

        self.update_available()
        super().__init__()

        self.usb_speed = depthai.UsbSpeed.SUPER_PLUS
        self.device_info = None
        self.pipeline = pipeline

    def get_device(self) -> DepthaiCapture:
        """Get a DepthaiCapture class instance can be used for depthai image acquisition.

        Raises:
            LookupError in case the device path is incorrect.

        Returns:
            A DepthaiCapture class instance.
        """
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

    def get_available_depthai(self) -> tuple[list[str], list[str],]:
        """Get available depthai camera devices.

        Returns:
            Device paths and labels.
        """
        device_paths = []
        labels = []

        device_info = depthai.Device.getAllAvailableDevices()

        for device in device_info:
            labels.append(f"OAK Device on port {device.name}")
            device_paths.append(device.mxid)

        return device_paths, labels

