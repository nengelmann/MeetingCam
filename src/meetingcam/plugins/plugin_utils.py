from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import depthai
import typer
from constants import DEPTHAI, WEBCAM
from numpy.typing import NDArray
from utils import KeyHandler


class PluginBase(ABC):
    """PluginBase class acts as a base class for plugins with image processing capabilities.

    This class is intended to be subclassed, with subclasses implementing the abstract
    `__init__` and `process` method to perform image processing tasks.

    Args:
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
        self.type = WEBCAM  # defaults to webcam
        self.hotkeys = {}
        self.verbose = False

    @abstractmethod
    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        trigger: tuple[bool, bool, bool],
    ) -> NDArray[Any]:
        """Process an image through the plugin's image processing method.

        This method is abstract and should be overwritten in subclasses to implement
        specific image processing functionality.

        Args:
            image --- the image to be processed.

        Returns:
            The processed image.
        """
        pass

    def keyhandler(self) -> KeyHandler:
        """Return the keyhandler for this plugin."""
        return KeyHandler(self.hotkeys, self.verbose)


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


class PluginRegistry:
    """PluginRegistry class acts as registry for default and newly added plugins."""

    def register_plugins(
        self, main_app: typer.main.Typer, plugin_list: list
    ) -> None:
        """Register plugins in typer main app"""
        for name in plugin_list:
            plugin_app = self._import_plugin(
                f"plugins.{name}.plugin", "plugin_app"
            )
            help = (
                plugin_app.info.help
                if type(plugin_app.info.help) is str
                else None
            )
            short_help = (
                plugin_app.info.short_help
                if type(plugin_app.info.short_help) is str
                else None
            )
            plugin_name = (
                plugin_app.info.name
                if type(plugin_app.info.help) is str
                else name
            )
            main_app.add_typer(
                plugin_app, name=plugin_name, help=help, short_help=short_help
            )

    def search_plugins(self, path: str = "src/meetingcam/plugins") -> list:
        """Check plugin directory for plugins and return list with found and valid plugins."""
        dirs = [d for d in Path(path).iterdir() if d.is_dir()]
        dirs = self._sortout(dirs)
        plugins = []

        for dir in dirs:
            plugin_name = dir.name
            valid = self._check_plugin(dir)

            if valid:
                plugins.append(plugin_name)
            else:
                print(
                    f"Plugin {plugin_name} is not valid. Continue without"
                    " registering this plugin."
                )

        return plugins

    def _check_plugin(self, path: str) -> bool:
        # TODO: Implement checks to validate plugin
        return True

    def _sortout(self, dirs: list) -> list:
        """Sort out directories which start with dot or underscores."""
        for d in dirs:
            if str(d.name).startswith(".") or str(d.name).startswith("__"):
                dirs.remove(d)
        return dirs

    def _import_plugin(self, modulename, name):
        """Import a named object from a module in the context of this function.
        Code adapted from: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch15s04.html
        """
        try:
            module = __import__(modulename, globals(), locals(), [name])
        except ImportError:
            return None
        return vars(module)[name]
