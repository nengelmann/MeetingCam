#!/usr/bin/env python3

"""This script is the entry point of MeetingCam.
MeetingCam allows to manage and modify video streams and route them to web meeting tools like Teams, Meets or Zoom.
"""

import sys

import typer
from constants import DEPTHAI, TYPES, WEBCAM, TypeArgument
from device import DepthaiDevice, WebcamDevice
from plugins.plugin_utils import PluginRegistry
from print import Printer

# define typer main app and tools
app = typer.Typer(add_completion=False)
registry = PluginRegistry()
printer = Printer()

# register plugins
for name in registry.plugins:
    plugin_app = registry.import_plugin(f"plugins.{name}.main", "plugin_app")
    help = plugin_app.info.help if type(plugin_app.info.help) is str else None
    short_help = (
        plugin_app.info.short_help
        if type(plugin_app.info.short_help) is str
        else None
    )
    plugin_name = (
        plugin_app.info.name if type(plugin_app.info.help) is str else name
    )
    app.add_typer(
        plugin_app, name=plugin_name, help=help, short_help=short_help
    )


# app entry point (main typer app)
@app.callback(
    invoke_without_command=True,
    epilog=Printer.epilog(),
    no_args_is_help=False,
    help=(
        "AI and CV webcam utility for online meetings.\n\nRun your artificial"
        " intelligence and computer vision algorithems in online meetings such"
        " as Zoom, Meets or Teams! 🪄"
    ),
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
def main(ctx: typer.Context):
    """
    Typer app entry point.
    Print title, subtitle or help, depending on context.
    """
    for plugin in app.registered_groups:
        if ctx.invoked_subcommand == plugin.name:
            Printer.subtitle(plugin.name)

    if ctx.invoked_subcommand is None:
        Printer.title()
        ctx.get_help()


# General-Commands
@app.command(
    help="List all camera devices",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def list_devices(type: TYPES = TypeArgument):
    """List all camera devices, camera paths and their virtual counter part."""

    type = str(type.value)
    if type == DEPTHAI or type == "all":
        depthai_handler = DepthaiDevice(pipeline=None)
        printer.console.print(
            "\nAvailable depthai devices:", style="bold underline"
        )
        printer.available_devices(
            depthai_handler.mapping, depthai_handler.available_devices_real
        )
    if type == WEBCAM or type == "all":
        webcam_handler = WebcamDevice()
        printer.console.print(
            "\nAvailable webcam devices:", style="bold underline"
        )
        printer.available_devices(
            webcam_handler.mapping, webcam_handler.available_devices_real
        )


@app.command(
    help="List commands to add camera devices",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def add_devices(type: TYPES = TypeArgument):
    """List commands on how to add camera devices to be used with MeetingCam."""

    type = str(type.value)
    depthai_handler = DepthaiDevice(pipeline=None)
    webcam_handler = WebcamDevice()

    if depthai_handler.mapping or webcam_handler.mapping:
        printer.console.print("\nThere are already virtual devices available!")
        reset_devices()
        sys.exit(0)

    if type == DEPTHAI or type == "all":
        if len(depthai_handler.available_devices_real[0]) > 0:
            printer.console.print(
                "\nAdd depthai devices:", style="bold underline"
            )
            printer.add_virtual_devices(
                depthai_handler.available_devices_real, DEPTHAI
            )
        else:
            printer.console.print(
                "\nNo depthai device available. Make sure to connect a depthai"
                " device to your PC.\n",
                style=printer.warning_style,
            )
            sys.exit(0)

    if type == WEBCAM or type == "all":
        if len(webcam_handler.available_devices_real[0]) > 0:
            printer.console.print(
                "\nAdd webcam devices:", style="bold underline"
            )
            printer.add_virtual_devices(
                webcam_handler.available_devices_real, WEBCAM
            )
        else:
            printer.console.print(
                "\nNo webcam device available. Make sure to connect a webcam"
                " device to your PC.\n",
                style=printer.warning_style,
            )
            sys.exit(0)
    if type == DEPTHAI or type == WEBCAM or type == "all":
        printer.console.print(
            "\nYou can [bold]reset[/bold] the added [bold]virtual"
            " devices[/bold] running:\n[bold][cyan]sudo modprobe -r"
            " v4l2loopback[/cyan][/bold]\nIf you want to run a reset, please"
            " close all applications which might access a camera device (e.g."
            " your browser) before running this command.\nIf you previously"
            " added devices, a reset is necessary before adding a new camera"
            " device.\n"
        )


@app.command(
    help="List reset command to reset virtual camera devices",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def reset_devices():
    """List command on how to reset the added (virtual) camera devices."""
    printer.reset_devices()


@app.command(
    help="Create new plugin",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
    hidden=True,
)
def create_plugin():
    """Create a new plugin"""
    # TODO: Add a plugin creation template, to get started quickly.
    raise NotImplementedError


if __name__ == "__main__":
    app()
