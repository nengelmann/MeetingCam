"""This file contains a printing class which is used for common terminal prints."""

from typing import Any

import pyfiglet
import rich
from constants import DEPTHAI, WEBCAM
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text
from v4l2ctl import V4l2Device


class Printer:
    """Handles printing functions for common terminal prints"""

    def __init__(self) -> None:
        """
        Initialize the DevicePrinter.

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

        table = Table()
        table.add_column(
            "Camera name", justify="right", style="cyan", no_wrap=True
        )
        table.add_column("Camera path", style="magenta", no_wrap=True)
        table.add_column(
            "Virtual camera name", justify="right", style="cyan", no_wrap=True
        )

        for rp, rn in zip(
            available_devices_real[0], available_devices_real[1]
        ):
            cam = {"label_real": rn, "path_real": rp, "label_virtual": None}
            for d in device_map.values():
                if d["path_real"] == rp:
                    cam["label_virtual"] = d["label_virtual"]

            table.add_row(
                str(cam["label_real"]),
                str(cam["path_real"]),
                str(cam["label_virtual"]),
            )

        self.console.print(table)

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

        cli_cmd_single = {}
        labels_str = []

        if type == WEBCAM:
            ids = [
                int(path.replace("/dev/video", "")) for path in device_paths
            ]
            vd_nrs = ids
            for idx, label in zip(ids, labels):
                cli_cmd_single[label] = (
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
                cli_cmd_single[label] = (
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

        if len(device_paths) > 0:
            self.console.print(
                "\n[bold]Add[/bold] a [bold]single device[/bold] with one of"
                " the following commands:"
            )
            for label, cmd in cli_cmd_single.items():
                cmd = Text(cmd[1:-1])
                self.console.print(f"\n{label}:")
                self.console.print(cmd, style="cyan bold")
            self.console.print(
                "\n\n[bold]Add all devices[/bold] with the following command:"
            )
            cmd = Text("\n" + cli_cmd_multi[1:-1])
            self.console.print(cmd, style="cyan bold")

    def device_not_available(self, device: V4l2Device) -> None:
        """Print a warning message indicating the specified device is not available.

        Args:
            device (V4l2Device) --- the device that is not available.
        """
        self.console.print("\nWarning! :warning:", style=self.warning_style)
        text = (
            "[bold]Device not available.[/bold]\nThe specified device"
            f" '{device}' is not available or does not have a virtual"
            " counterpart."
        )
        self.console.print(text)

    def add_device_first(self) -> None:
        """Print a message guiding the user to run add devices first."""
        self.console.print(
            "\nYou'll need to add a device first. Run [cyan"
            " bold]add-devices[/cyan bold] command to see how to add a"
            " virtual counterpart to a camera device.\n"
        )

    def reset_devices(self) -> None:
        """Print instructions on how to reset virtual devices."""
        self.console.print(
            "\n1. [bold]Close[/bold] all [bold]applications which access"
            " camera[/bold] devices, including browser."
            "\n2. Run: [bold][cyan]sudo modprobe -r v4l2loopback[/cyan][/bold]"
            "\n\nA reset is necessary if you want to access your real camera"
            " device normally or if you want to add another device to be used"
            " with MeetingCam.\nIf the reset command is isn't working make"
            " sure all applications which might access cameras are closed. If"
            " this still isn't working, restart your system.\n"
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

    def title(self) -> None:
        """Print MeeingCam title."""
        title = pyfiglet.figlet_format("MeetingCam", font="big")
        title = Text(title)
        title.stylize("bold green", 0, 234)
        title.stylize("bold magenta", 235)
        rich.print(title)

    def subtitle(self, name: str) -> None:
        """Print Plugin title."""
        title = pyfiglet.figlet_format(name, font="big")
        title = Text(title)
        rich.print(title)

    def epilog(self) -> str:
        """Get epilog text to be printed underneath help."""
        text = (
            "Submit feedback, issues and questions via"
            " https://github.com/nengelmann/MeetingCam/issues.\nPlease"
            " consider to star https://github.com/nengelmann/MeetingCam if you"
            " find it helpful. ⭐"
        )
        return text
