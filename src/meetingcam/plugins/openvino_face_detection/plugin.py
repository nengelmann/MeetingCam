import sys
from math import ceil
from pathlib import Path
from typing import Any, Optional, Type

import cv2
import typer
from constants import WEBCAM, DevicePathWebcam
from device import device_choice
from numpy.typing import NDArray
from runner import Runner
from utils import Hotkey, KeyHandler

from ..plugin_utils import PluginBase
from .model import FaceDetector
from .utils import box_area, draw_bbox

name = "face-detector"
short_description = "First person face detector"
description = """
First person face detector.
\nDetects the face which appears largest on the webcam (usually the users face)
and allows to print in a bounding box as well as the name, which can be specified
as command line argument."""

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


class FaceDetection(PluginBase):
    """A plugin for detecting faces in an image.

    This plugin extends the PluginBase class and is used to detect faces in an image using a pretrained face detection model.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize the FaceDetection plugin with a specified name.

        This method initializes the FaceDetection plugin and sets up the necessary parameters including model paths, and name.

        Args:
            name --- the name of the user. If not provided, a default name is assigned.

        Raises:
            SystemExit: If the model files are not found in the specified directory.
        """
        super().__init__()
        self.type = TYPE

        self.fn_scale = 3e-3  # Adjust for larger font size in all images
        self.th_scale = 6e-3  # relative thickness in all images
        self.off_scale = (
            3e-2  # Adjust for larger Y-offset of text and bounding box
        )

        model_path = (
            Path(self.model_dir)
            / "public/ultra-lightweight-face-detection-rfb-320/FP16/ultra-lightweight-face-detection-rfb-320.xml"
        )

        if not model_path.exists():
            print(
                "\nModel files are not downloaded or converted.\nDownload and"
                " convert the model with the following commands."
            )
            print(
                "\n`omz_downloader --name"
                " ultra-lightweight-face-detection-rfb-320 --output_dir"
                " src/meetingcam/models\nomz_converter --name"
                " ultra-lightweight-face-detection-rfb-320 --download_dir"
                " src/meetingcam/models --output_dir src/meetingcam/models"
                " --precision=FP16\nopt_in_out --opt_out`"
            )
            sys.exit(0)

        if name == "Code Ninja":
            self.name = "Code Ninja"
            print("\nYou have not specified your name ('--name' YourName).")
            print(f"I simply name you {self.name}\n")
        else:
            self.name = name

        self.detector = FaceDetector(
            model_path=model_path, confidence_thr=0.9, overlap_thr=0.7
        )

        self.hotkeys = [
            Hotkey(
                "<ctrl>+<alt>+f",
                "f_trigger",
                True,
                "Print in the face detection.",
            ),
            Hotkey(
                "<ctrl>+<alt>+n",
                "n_trigger",
                True,
                "Print in the name above the face detection.",
            ),
        ]
        self.verbose = True

    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        keyhandler: Type[KeyHandler],
    ) -> NDArray[Any]:
        """Process the input image and return the image with detected face annotations.

        This method takes an image and a keyhandler as inputs, performs face detection, and returns the image with annotations such as bounding boxes and names.

        Args:
            image --- the input image to be processed.
            keyhandler --- keyhandler instance to enable/disable functionality by hotkey trigger.

        Returns:
            The processed image with face and name annotations.
        """
        bboxes, scores = self.detector.inference(image)

        if len(bboxes) > 0:
            # Assumption: The persons face in front of the web cam is the one which is closest to the camera and hence the biggest.
            # So we get the detection result with the biggest bbox area.
            box_areas = [box_area(box) for box in bboxes]
            idx = box_areas.index(max(box_areas))
            h, w = image.shape[0:2]

            # If f_trigger <Ctrl+Alt+f> is True, print in the face bbox
            if keyhandler.f_trigger:
                image = draw_bbox(
                    image,
                    bboxes[idx][:2],
                    bboxes[idx][2:],
                    color=(0, 255, 0),
                    thickness=ceil(h * self.th_scale),
                    radius=ceil(h * self.th_scale * 4),
                    corner_len=ceil(h * self.th_scale * 8),
                )
            # If n_trigger <Ctrl+Alt+n> is True, print in the name above the bbox
            if keyhandler.n_trigger and self.name:
                x1, y1 = bboxes[idx][:2]
                image = cv2.putText(
                    image,
                    self.name,
                    (x1, y1 - int(h * self.off_scale)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=h * self.fn_scale,
                    color=(0, 255, 0),
                    thickness=ceil(h * self.th_scale),
                )
        return image


@plugin_app.callback(rich_help_panel="Plugin-Commands")
def main(
    device_path: DevicePath = DevicePathWebcam,
    name: Optional[str] = typer.Option(
        default="", help="Name imprinted above the face detection."
    ),
):
    # define plugin
    if not name:
        name = typer.prompt(
            "A name will be imprinted above the face detection.\nWhat's your"
            " name?"
        )
    plugin = FaceDetection(name)

    # define runner
    runner = Runner(plugin, device_path)

    # run
    runner.run()
