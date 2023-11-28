from math import ceil
from typing import Any, Type

import depthai
import typer
from constants import DEPTHAI, DevicePathDepthai
from device import device_choice
from numpy.typing import NDArray
from runner import Runner
from utils import Hotkey, KeyHandler

from ..plugin_utils import PluginDepthai
from .pipeline import PipelineHandler
from .utils import displayFrame

name = "depthai-yolov5"
short_description = "Yolov5 (COCO) on depthai camera"
description = """
Yolov5 (COCO) on depthai camera.
\nRuns a Yolov5 model trained on COCO. Computation on a depthai device."""

TYPE = DEPTHAI
DevicePath = device_choice(TYPE)

plugin_txt = f"\n\n\n\nPlugin type: {TYPE}"

plugin_app = typer.Typer(
    name=name,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    short_help=short_description,
    help=str(description + plugin_txt),
    invoke_without_command=True,
)
plugin_app.type = TYPE


class Yolov5(PluginDepthai):
    """A plugin for running a pretrained yolov5 model (COCO dataset) on a depthai device (OAK)."""

    def __init__(self) -> None:
        """Initialize the base class and create depthai pipeline."""
        super().__init__()
        self.type = TYPE
        self.pipeline_handler = PipelineHandler(self.model_dir)
        self.pipeline = self.pipeline_handler.create()

        self.hotkeys = [
            Hotkey(
                "<ctrl>+<alt>+l", "l_trigger", True, "Print in the detections."
            ),
        ]
        self.verbose = True

    def device_setup(self, device):
        """Setup of device before image acquisition loop, e.g. for get queue definition etc.

        Args:
            device --- depthai device
        """
        device.qRgb = device.getOutputQueue(
            name="rgb", maxSize=1, blocking=False
        )
        device.qDet = device.getOutputQueue(
            name="nn", maxSize=1, blocking=False
        )

        # Overwrite image height and width if needed, otherwise MAX_HEIGHT and MAX_WIDTH are used
        # device.height = MAX_HEIGHT
        # device.width = MAX_WIDTH

    def acquisition(
        self, device
    ) -> tuple[NDArray[Any], list[depthai.ImgDetection]]:
        """Acquire an image and optionally detections from camera queue and return them.

        Args:
            device --- depthai device
        """
        inRgb = device.qRgb.get()
        inDet = device.qDet.get()

        if inRgb is not None:
            image = inRgb.getCvFrame()

            if inDet is not None:
                detections = inDet.detections

        return image, detections

    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        keyhandler: Type[KeyHandler],
    ) -> NDArray[Any]:
        """Process the input image and return the image with detected face annotations.

        Args:
            image --- the input image to be processed.
            detections --- detections from depthai device
            keyhandler --- keyhandler instance to enable/disable functionality by hotkey trigger.

        Returns:
            The processed image with face and name annotations.
        """
        if keyhandler.l_trigger:
            image = displayFrame(
                image, detection, self.pipeline_handler.labels
            )

        # do more host processing here..

        return image


@plugin_app.callback(
    invoke_without_command=True, rich_help_panel="Plugin-Commands"
)
def main(device_path: DevicePath = DevicePathDepthai):
    # define plugin
    plugin = Yolov5()
    # define runner
    runner = Runner(plugin, device_path)
    # run
    runner.run()
