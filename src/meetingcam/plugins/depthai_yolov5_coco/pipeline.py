import json
from pathlib import Path
from typing import Any

import blobconverter
import depthai
from numpy.typing import NDArray

from .utils import *


class PipelineHandler:
    """
    This class defines the depthai pipeline and the on device processing.

    Attributes:
        model --- a compiled neural network model used for face detection.
        confidence_thr --- the confidence threshold for filtering detections.
        overlap_thr --- the overlap threshold for non-maximum suppression.
    Note:
        Code partly from:
        https://github.com/luxonis/depthai-experiments/blob/master/gen2-yolo/device-decoding/main_api.py
    """

    def __init__(self, model_dir: str) -> None:
        """
        Initialize the FaceDetector instance.

        Args:
            model_path --- the path to the neural network model file.

        Raises:
            Various exceptions can be raised by openvino runtime methods if the model file is not found or has errors.
        """

        self.model = "yolov5n_coco_416x416"
        self.config = "yolov5_config.json"
        self.model_dir = model_dir

        # parse config
        configPath = Path(__file__).resolve().parent / Path(self.config)
        if not configPath.exists():
            raise ValueError("Path {} does not exist!".format(configPath))

        self.nnPath = str(
            blobconverter.from_zoo(
                name=self.model,
                shaves=6,
                zoo_type="depthai",
                use_cache=True,
                output_dir=self.model_dir,
            )
        )

        with configPath.open() as f:
            config = json.load(f)
        nnConfig = config.get("nn_config", {})

        # parse input shape
        if "input_size" in nnConfig:
            self.width, self.height = tuple(
                map(int, nnConfig.get("input_size").split("x"))
            )

        # parse labels
        nnMappings = config.get("mappings", {})
        self.labels = nnMappings.get("labels", {})

        # extract metadata
        metadata = nnConfig.get("NN_specific_metadata", {})
        self.classes = metadata.get("classes", {})
        self.coordinates = metadata.get("coordinates", {})
        self.anchors = metadata.get("anchors", {})
        self.anchorMasks = metadata.get("anchor_masks", {})
        self.iouThreshold = metadata.get("iou_threshold", {})
        self.confidenceThreshold = metadata.get("confidence_threshold", {})

    def create(self):
        # Create pipeline
        pipeline = depthai.Pipeline()

        # Define sources and outputs
        camRgb = pipeline.create(depthai.node.ColorCamera)
        detectionNetwork = pipeline.create(depthai.node.YoloDetectionNetwork)
        xoutRgb = pipeline.create(depthai.node.XLinkOut)
        nnOut = pipeline.create(depthai.node.XLinkOut)

        xoutRgb.setStreamName("rgb")
        nnOut.setStreamName("nn")

        # Properties
        camRgb.setPreviewSize(self.width, self.height)
        camRgb.setResolution(
            depthai.ColorCameraProperties.SensorResolution.THE_1080_P
        )
        camRgb.setInterleaved(False)
        camRgb.setColorOrder(depthai.ColorCameraProperties.ColorOrder.BGR)
        camRgb.setFps(40)
        camRgb.setPreviewKeepAspectRatio(False)

        # Network specific settings
        detectionNetwork.setConfidenceThreshold(self.confidenceThreshold)
        detectionNetwork.setNumClasses(self.classes)
        detectionNetwork.setCoordinateSize(self.coordinates)
        detectionNetwork.setAnchors(self.anchors)
        detectionNetwork.setAnchorMasks(self.anchorMasks)
        detectionNetwork.setIouThreshold(self.iouThreshold)
        detectionNetwork.setBlobPath(self.nnPath)
        detectionNetwork.setNumInferenceThreads(2)
        detectionNetwork.input.setBlocking(False)

        # Linking
        camRgb.preview.link(detectionNetwork.input)
        camRgb.video.link(xoutRgb.input)
        detectionNetwork.out.link(nnOut.input)

        return pipeline
