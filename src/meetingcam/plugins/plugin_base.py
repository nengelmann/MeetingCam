from abc import ABC, abstractmethod
from typing import Any

from numpy.typing import NDArray


class PluginBase(ABC):
    """PluginBase class acts as a base class for plugins with image processing capabilities.

    This class is intended to be subclassed, with subclasses implementing the abstract
    `process` method to perform specific image processing tasks.

    Attributes:
        model_dir --- directory where models are stored. Defaults to "./src/meetingcam/models".
    """

    def __init__(self, *args: tuple[Any], **kwargs: tuple[Any]) -> None:
        """Initialize the PluginBase instance with the default model directory.

        Args:
            *args --- Variable length argument list.
            **kwargs --- Arbitrary keyword arguments.

            With this custom arguments can be passed to plugins, e.g. --name YourName
        """
        self.model_dir = "./src/meetingcam/models"

    @abstractmethod
    def process(self, image: NDArray[Any]) -> NDArray[Any]:
        """Process an image through the plugin's image processing method.

        This method is abstract and should be overridden in subclasses to implement
        specific image processing functionality.

        Args:
            image --- the image to be processed.

        Returns:
            The processed image.
        """
        pass
