import sys
from math import ceil
from pathlib import Path
from typing import Any

import cv2
import depthai
from numpy.typing import NDArray

from ..plugin_utils import PluginDepthai
from .pipeline import PipelineHandler
from .utils import displayFrame


class Yolov5(PluginDepthai):
    """A plugin for running a pretrained yolov5 model (COCO dataset) on a depthai device (OAK)."""

    def __init__(self) -> None:
        """Initialize the base class and create depthai pipeline."""
        super().__init__()
        self.pipeline_handler = PipelineHandler(self.model_dir)
        self.pipeline = self.pipeline_handler.create()

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
        trigger: tuple[bool, bool, bool],
    ) -> NDArray[Any]:
        """Process the input image and return the image with detected face annotations.

        Args:
            image --- the input image to be processed.
            detections --- detections from depthai device
            trigger --- a tuple containing boolean values indicating whether to draw bounding boxes and name annotations.

        Returns:
            The processed image with face and name annotations.
        """
        if trigger[1]:
            image = displayFrame(
                image, detection, self.pipeline_handler.labels
            )

        # do more host processing here..

        return image
