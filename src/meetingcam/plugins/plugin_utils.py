from abc import ABC, abstractmethod
from typing import Any

import cv2
import depthai
from constants import DEPTHAI, WEBCAM
from numpy.typing import NDArray


class PluginBase(ABC):
    """PluginBase class acts as a base class for plugins with image processing capabilities.

    This class is intended to be subclassed, with subclasses implementing the abstract
    `process` method to perform specific image processing tasks.

    Attributes:
        model_dir --- directory where models are stored. Defaults to "./src/meetingcam/models".
    """

    @abstractmethod
    def __init__(self, *args: tuple[Any], **kwargs: tuple[Any]) -> None:
        """Initialize the PluginBase instance with the default model directory.

        Args:
            *args --- Variable length argument list.
            **kwargs --- Arbitrary keyword arguments.

            With this custom arguments can be passed to plugins, e.g. --name YourName
        """
        self.model_dir = "./src/meetingcam/models"
        self.type = WEBCAM

    @abstractmethod
    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        trigger: tuple[bool, bool, bool],
    ) -> NDArray[Any]:
        """Process an image through the plugin's image processing method.

        This method is abstract and should be overridden in subclasses to implement
        specific image processing functionality.

        Args:
            image --- the image to be processed.

        Returns:
            The processed image.
        """
        pass


class PluginDepthai(PluginBase):
    """PluginBase class for Depthai plugins with on device compute."""

    @abstractmethod
    def __init__(self, *args: tuple[Any], **kwargs: tuple[Any]) -> None:
        """Initialize the PluginBase instance with the default model directory.

        Args:
            *args --- Variable length argument list.
            **kwargs --- Arbitrary keyword arguments.

            With this custom arguments can be passed to plugins, e.g. --name YourName
        """
        super().__init__()
        self.type = DEPTHAI

    @abstractmethod
    def device_setup(self, device) -> None:
        """Setup of device before image acquisition loop, e.g. for get queue definition etc.

        Args:
            device --- depthai device
        """
        pass

    @abstractmethod
    def acquisition(
        self, device
    ) -> tuple[NDArray[Any], list[depthai.ImgDetection]]:
        """Acquire an image and optionally detections from camera queue and return them.

        Args:
            device --- depthai device
        """
        pass
