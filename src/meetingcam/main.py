#!/usr/bin/env python3

"""This script is the entry point of MeetingCam.
MeetingCam allows to manage and modify video streams and route them to web meeting tools like Teams, Meets or Zoom.
"""

import shutil
import sys
from pathlib import Path

import typer
from constants import DEPTHAI, TYPES, WEBCAM, TypeArgument
from device import DepthaiDevice, WebcamDevice
from jinja2 import Environment, FileSystemLoader
from plugins.plugin_utils import PluginRegistry
from print import Printer

app = typer.Typer(add_completion=False)

registry = PluginRegistry()
plugin_list = registry.search_plugins()
registry.register_plugins(app, plugin_list)

printer = Printer()


# app entry point of typer main app
@app.callback(
    invoke_without_command=True,
    epilog=printer.epilog(),
    no_args_is_help=False,
    help=(
        "AI and CV webcam utility for online meetings.\n\nRun your artificial"
        " intelligence and computer vision algorithms in online meetings such"
        " as Zoom, Meets or Teams! 🪄"
    ),
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
def main(ctx: typer.Context) -> None:
    """
    Typer app entry point.
    Print title, subtitle or help, depending on context.
    """
    for plugin in app.registered_groups:
        if ctx.invoked_subcommand == plugin.name:
            printer.subtitle(plugin.name)

    if ctx.invoked_subcommand is None:
        printer.title()
        ctx.get_help()


# General-Commands
@app.command(
    help="List all camera devices",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def list_devices(type: TYPES = TypeArgument) -> None:
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
def add_devices(type: TYPES = TypeArgument) -> None:
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
def reset_devices() -> None:
    """List command on how to reset the added (virtual) camera devices."""
    printer.reset_devices()


@app.command(
    help="Create new plugin",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def create_plugin(
    name: str = typer.Option(default=None, help="Name of new plugin"),
    short_description: str = typer.Option(
        default=None, help="Short one line description of new plugin"
    ),
    description: str = typer.Option(
        default=None, help="Description of new plugin"
    ),
) -> None:
    """Create a new plugin"""
    # check if plugin already exists
    if name in plugin_list:
        typer.echo(f"Plugin {name} already exists.")
        sys.exit(0)

    # if arguments are not provided, ask for them
    if not name:
        name = typer.prompt("Name of new plugin")
    if not short_description:
        short_description = typer.prompt(
            "Short one line description of new plugin"
        )
    if not description:
        description = typer.prompt("Description of new plugin")

    # create new directory for plugin
    path = Path(f"src/meetingcam/plugins/{name}")
    path.mkdir(parents=True, exist_ok=True)

    # Corrected path to the template
    template_path = Path("src/meetingcam/plugins/plugin_template.py")

    env = Environment(loader=FileSystemLoader(template_path.parent.as_posix()))
    template = env.get_template(template_path.name)
    output = template.render(
        name=name, short_description=short_description, description=description
    )

    with open(f"{path}/plugin.py", "w") as f:
        f.write(output)

    with open(f"{path}/__init__.py", "w") as f:
        f.write("")

    typer.echo(f"Plugin {name} created successfully.")


@app.command(
    help="Delete plugin",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_help_panel="General-Commands",
)
def delete_plugin(
    name: str = typer.Option(default=None, help="Name of plugin to delete")
) -> None:
    """Delete a plugin"""

    # check if plugin exists
    if name not in plugin_list:
        typer.echo(f"Plugin {name} does not exist.")
        sys.exit(0)

    # ensure user wants to delete plugin
    confirm = typer.confirm(f"Are you sure you want to delete plugin {name}?")
    if not confirm:
        typer.echo(f"Plugin {name} not deleted.")
        sys.exit(0)
    else:
        # delete plugin
        path = Path(f"src/meetingcam/plugins/{name}")
        shutil.rmtree(Path(f"src/meetingcam/plugins/{name}"))
        typer.echo(f"Plugin {name} deleted successfully.")


if __name__ == "__main__":
    app()
