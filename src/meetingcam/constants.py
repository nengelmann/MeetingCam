"""Definition of constants and types"""

from typing import NewType

# Definition of maximum image size for virtual camera.
# Higher resolutions are usually not supported on online meeting tools
# 720p:(1280, 720)  540p:(960, 540)
MAX_WIDTH = 1280
MAX_HEIGHT = 720

# Definition of plugin types (avoid spelling errors with explicit type)
PluginType = NewType("PluginType", str)
DEPTHAI = PluginType("depthai")
WEBCAM = PluginType("webcam")
