from typing import Any, Optional

import cv2
import typer
from constants import WEBCAM, DevicePathWebcam
from device import device_choice
from numpy.typing import NDArray
from runner import Runner

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

        # you can use the model path to save and load your model weights
        # self.model_path = (Path(self.model_dir) / "your_model.pth")

    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        trigger: tuple[bool, bool, bool],
    ) -> NDArray[Any]:
        """Process the webcam image and return a modified image.

        Args:
            image --- the input image (real camera frames) to be processed.
            trigger --- a tuple containing boolean values serving as triggers to enable/disable functionality.

        Returns:
            The processed image which will be sent to the virtual camera (video meeting stream)
        """

        # implement your custom image processing here
        # e.g. run opencv functions on the image or your AI model

        image = cv2.putText(
            image,
            "Your custom plugin",
            (100, 100),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 255, 0),
            thickness=2,
        )

        # If f_trigger <Ctrl+Alt+f> is True, print in the face bbox
        if trigger[0]:
            image = cv2.putText(
                image,
                "",
                (100, 600),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(0, 255, 0),
                thickness=2,
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
