import sys
from math import ceil
from pathlib import Path
from typing import Any

import cv2
from numpy.typing import NDArray

from ..plugin_base import PluginBase
from .model import FaceDetector
from .utils import box_area, draw_bbox


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
                "\nModel files are not downloaded or converted.\n Download and"
                " convert the model with the following commands."
            )
            print(
                "\n`omz_downloader --name"
                " ultra-lightweight-face-detection-rfb-320 --output_dir"
                " src/meetingcam/models`"
            )
            sys.exit()

        if name is not None:
            self.name = name
        else:
            self.name = "Code Ninja"
            print("\nYou have not specified your name ('--name' YourName).")
            print(f"I simply name you {self.name}")

        self.detector = FaceDetector(
            model_path=model_path, confidence_thr=0.9, overlap_thr=0.7
        )

    def process(
        self, image: NDArray[Any], trigger: tuple[bool, bool]
    ) -> NDArray[Any]:
        """Process the input image and return the image with detected face annotations.

        This method takes an image and a trigger tuple as inputs, performs face detection, and returns the image with annotations such as bounding boxes and names.

        Args:
            image --- the input image to be processed.
            trigger --- a tuple containing two boolean values indicating whether to draw bounding boxes and name annotations.

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
            if trigger[0]:
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
            if trigger[1] and self.name:
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
