from typing import Any, Optional, Type

import cv2
import typer
from constants import WEBCAM, DevicePathWebcam
from device import device_choice
from numpy.typing import NDArray
from runner import Runner
from utils import Hotkey, KeyHandler

from ..plugin_utils import PluginBase

name = "{{name}}"  # modifiable
short_description = "{{short_description}}"  # modifiable
description = """
{{description}}"""  # modifiable

TYPE = WEBCAM
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


class CustomPlugin(PluginBase):
    """A custom plugin.

    This class is based on a template and meant for modification to make it your custom plugin.
    """

    def __init__(
        self, arg1: str | None = None, arg2: str | None = None
    ) -> None:
        """Initialize the plugin wit custom arguments, variables and classes.

        Args:
            arg1 --- argument you define.
            arg2 --- argument you define.

        """
        super().__init__()
        self.type = TYPE

        # modify arguments and
        # initialize additional variables or classes (e.g. your AI model)
        # e.g.:
        # self.arg1 = arg1

        # you can use the model path to save and load your model weights
        # e.g.:
        # self.model_path = (Path(self.model_dir) / "your_model.pth")

        # define custom triggers (hotkeys, which you can trigger and enable/disable functionality)
        # e.g.:
        # self.hotkeys = {
        #    "<Ctrl>+<Alt>+z", "z_trigger", True, "toggle text",
        #    "<ctrl>+<alt>+p", "p_trigger", False, "toggle text",
        #    key_combination, variable_name, is_enabled, description
        # }
        # this will get you two triggers (keyhandler.z_trigger, keyhandler.p_trigger), set to be True, False respectively
        # you can use them to enable/disable functionality based on the trigger state
        self.hotkeys = [
            Hotkey("<Ctrl>+<Alt>+z", "z_trigger", True, "toggle text"),
        ]
        # set verbose to True to print additional information like available hotkeys and hotkey changes
        self.verbose = True

    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        keyhandler: Type[KeyHandler],
    ) -> NDArray[Any]:
        """Process the webcam image and return a modified image.

        Args:
            image --- the input image (real camera frames) to be processed.
            detection --- the on camera detection (just in case of depthai camera).
            keyhandler --- keyhandler instance to enable/disable functionality by hotkey trigger.

        Returns:
            The processed image which will be sent to the virtual camera (video meeting stream)
        """

        # implement your custom image processing here
        # e.g. run opencv functions on the image or your AI model

        image = cv2.putText(
            image,
            "Your custom plugin",
            (50, 75),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 255, 0),
            thickness=2,
        )

        # If z_trigger <Ctrl>+<Alt>+z is True, print in additional text
        if keyhandler.z_trigger:
            image = cv2.putText(
                image,
                "Toggle this text with <Ctrl>+<Alt>+z",
                (50, 200),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 0),
                thickness=1,
            )

        # If not z_trigger <Ctrl>+<Alt>+z, print next steps
        if not keyhandler.z_trigger:
            image = cv2.putText(
                image,
                "Great! Now you can start to modify this plugin. ;)",
                (50, 300),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 0),
                thickness=1,
            )

        return image


@plugin_app.callback(rich_help_panel="Plugin-Commands")
def main(
    device_path: DevicePath = DevicePathWebcam,
    arg1: Optional[str] = typer.Option(
        default="", help="Your custom argument 1."
    ),
    arg2: Optional[str] = typer.Option(
        default="", help="Your custom argument 2."
    ),
):
    # define plugin
    plugin = CustomPlugin(arg1, arg2)
    # define runner
    runner = Runner(plugin, device_path)
    # run
    runner.run()
