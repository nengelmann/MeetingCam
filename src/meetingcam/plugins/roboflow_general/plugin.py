import pickle
from typing import Any, Optional

# from inference.models.utils import get_roboflow_model
import requests
import supervision as sv
import typer
from constants import WEBCAM, DevicePathWebcam
from device import device_choice
from numpy.typing import NDArray
from roboflow import Roboflow
from runner import Runner

from ..plugin_utils import PluginBase

name = "roboflow"
short_description = "General roboflow plugin"
description = """
General roboflow plugin.
\n Runs roboflow object-detection and
instance-segmentation models."""

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


class RoboflowDetection(PluginBase):
    """A plugin for running a custom roboflow model."""

    """
    def __init__(
        self,
        api_key: str | None = None,
        project_name: str | None = None,
        version: int | None = None,
        confidence: float = 0.7,
    ) -> None:
    """

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
            project_name --- your roboflow project name.
            version --- your roboflow project version.
            confidence --- confidence threshold for your model.

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

        if trigger[1]:
            numpy_data = pickle.dumps(image)

            response = requests.post(
                self.url,
                headers=self.headers,
                params=self.params,
                data=numpy_data,
            )

            res = response.json()

            detections = sv.Detections.from_roboflow(res)

            if self.detection_type == "instance-segmentation":
                image = self.annotator.annotate(
                    scene=image, detections=detections
                )
            elif self.detection_type == "object-detection":
                image = self.annotator.annotate(
                    scene=image, detections=detections, labels=self.class_list
                )

        return image


# TODO: Use env variables for api key. See https://typer.tiangolo.com/tutorial/arguments/envvar/
@plugin_app.callback(
    invoke_without_command=True, rich_help_panel="Plugin-Commands"
)
def main(
    device_path: DevicePath = DevicePathWebcam,
    api_key: Optional[str] = typer.Option(
        default=None, help="Your private roboflow API key"
    ),
    project_name: Optional[str] = typer.Option(
        default=None, help="Project name (id) you want to run"
    ),
    version: Optional[int] = typer.Option(
        default=None, help="Version of the model you want to run"
    ),
    confidence: Optional[float] = typer.Option(
        default=0.7, help="Thresholds detections"
    ),
):
    # define plugin
    if not api_key:
        api_key = typer.prompt("What's your roboflow API key?")
    if not project_name:
        project_name = typer.prompt(
            "What's the project name (id) you want to run?"
        )
    if not version:
        version = typer.prompt("What's the version you want to run?")

    plugin = RoboflowDetection(api_key, project_name, version, confidence)
    # define runner
    runner = Runner(plugin, device_path)
    print(
        "\nThe follwoing keyboard triggers and switches are available within"
        " this plugin:"
    )
    print("<ctrl>+<alt>+<l>:    Run and print in detections.")
    print("<ctrl>+<alt>+<r>:    Switch RGB to BGR color schema.")
    print("<ctrl>+<alt>+<m>:    Mirror the camera stream.")
    print("")
    # run
    runner.run()


if __name__ == "__main__":
    plugin_app()
