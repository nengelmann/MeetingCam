"""Definition of constants and types"""

from enum import Enum
from typing import NewType

import typer

# Definition of maximum image size for virtual camera.
# Higher resolutions are usually not supported on online meeting tools
# 720p:(1280, 720)  540p:(960, 540)
MAX_WIDTH = 1280
MAX_HEIGHT = 720

# Plugin types (avoid spelling errors with explicit type)
PluginType = NewType("PluginType", str)
DEPTHAI = PluginType("depthai")
WEBCAM = PluginType("webcam")

# Argument and Option types
TYPES = Enum("DevicePath", {"all": "all", WEBCAM: WEBCAM, DEPTHAI: DEPTHAI})
TypeArgument = typer.Option(default=WEBCAM, help=f"Choose camera type")
DevicePathWebcam = typer.Argument(
    default=..., help="Path to real camera device, e.g. /dev/video0."
)
DevicePathDepthai = typer.Argument(
    default=...,
    help="Path (mxid) to real camera device, e.g. 14442C1021C694D000.",
)
