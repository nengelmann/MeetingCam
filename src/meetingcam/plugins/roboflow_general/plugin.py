import pickle
from typing import Any

# from inference.models.utils import get_roboflow_model
import requests
import supervision as sv
from constants import WEBCAM
from numpy.typing import NDArray
from roboflow import Roboflow

from ..plugin_utils import PluginBase


class RoboflowDetection(PluginBase):
    """A plugin for running a custom roboflow model."""

    def __init__(
        self,
        api_key: str | None = None,
        project_name: str | None = None,
        version: int | None = None,
        confidence: float = 0.7,
    ) -> None:
        """Initialize the roboflow plugin.

        Args:
            api_key --- your roboflow API key.

        Raises:
            SystemExit: If no API key is given.
        """
        super().__init__()

        if not api_key:
            raise ValueError(
                "You need to provide a Roboflow API key via cli argument:"
                " --roboflow-api-key"
            )
        if not project_name:
            raise ValueError(
                "You need to provide a Roboflow project name via cli argument:"
                " --project-name"
            )
        if not api_key:
            raise ValueError(
                "You need to provide a Roboflow project version cli argument:"
                " --version"
            )

        try:
            rf = Roboflow(api_key=api_key)
        except:
            raise ConnectionError(
                "Can't initialize Roboflow connection. Is your Roboflow API"
                " key correct?"
            )
        try:
            project = rf.workspace().project(project_name)
        except:
            raise ConnectionError(
                "Can't initialize Roboflow project. Is your Roboflow project"
                " name correct?"
            )
        try:
            model = project.version(version).model
        except:
            raise ConnectionError(
                "Can't initialize Roboflow project version. Is your Roboflow"
                " project version correct?"
            )

        self.class_list = [c for c in project.classes.keys()]
        self.url = (
            f"http://localhost:9001/{project_name}/{version}?image_type=numpy"
        )
        self.headers = {"Content-Type": "application/json"}
        self.params = {
            "api_key": api_key,
            "confidence": confidence,
        }
        self.detection_type = project.type

        if self.detection_type == "instance-segmentation":
            self.annotator = sv.MaskAnnotator()
        elif self.detection_type == "object-detection":
            self.annotator = sv.BoxAnnotator()
        else:
            raise NotImplemented(
                f"Roboflow projects of type {self.detection_type} are not yet"
                " supported. Supported types are 'object-detection' and"
                " 'instance-segmentation' projects. \n Pull requests for this"
                " are welcome!"
            )

        # TODO: Rewrite for roboflow local inference with pip install (remove API/http inference)
        # See: https://github.com/roboflow/inference/issues/60

        # self.model = get_roboflow_model(
        #    model_id="{}/{}".format(project_name, version),
        #    api_key=api_key,
        # )

        self.type = WEBCAM

    def process(
        self,
        image: NDArray[Any],
        detection: Any,
        trigger: tuple[bool, bool, bool],
    ) -> NDArray[Any]:
        """Process the input image and return the image with detected face annotations.

        This method takes an image and a trigger tuple as inputs, performs face detection, and returns the image with annotations such as bounding boxes and names.

        Args:
            image --- the input image to be processed.
            trigger --- a tuple containing boolean values indicating whether to draw bounding boxes and name annotations.

        Returns:
            The processed image with face and name annotations.
        """

        numpy_data = pickle.dumps(image)

        response = requests.post(
            self.url, headers=self.headers, params=self.params, data=numpy_data
        )

        res = response.json()

        detections = sv.Detections.from_roboflow(res, self.class_list)

        if self.detection_type == "instance-segmentation":
            image = self.annotator.annotate(scene=image, detections=detections)
        elif self.detection_type == "object-detection":
            image = self.annotator.annotate(
                scene=image, detections=detections, labels=self.class_list
            )

        return image
