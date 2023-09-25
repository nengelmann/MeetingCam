from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
from openvino.runtime import Core

from .utils import non_max_suppression


class FaceDetector:
    """
    This class utilizes a pre-trained model for detecting faces in images.

    Attributes:
        model --- a compiled neural network model used for face detection.
        confidence_thr --- the confidence threshold for filtering detections.
        overlap_thr --- the overlap threshold for non-maximum suppression.
    Note:
        Check this documentation for more detail:
        https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/ultra-lightweight-face-detection-rfb-320/README.md

        Code partly from:
        https://github.com/Gabriellgpc/ultra-lightweight-face-detection
    """

    model = None

    def __init__(
        self,
        model_path: str,
        confidence_thr: float = 0.5,
        overlap_thr: float = 0.7,
    ) -> None:
        """
        Initialize the FaceDetector instance.

        Args:
            model_path --- the path to the neural network model file.
            confidence_thr --- the confidence threshold for filtering detections (default is 0.5).
            overlap_thr --- the overlap threshold for non-maximum suppression (default is 0.7).

        Raises:
            Various exceptions can be raised by openvino runtime methods if the model file is not found or has errors.
        """
        core = Core()
        model = core.read_model(str(model_path))
        self.model = core.compile_model(model)
        self.confidence_thr = confidence_thr
        self.overlap_thr = overlap_thr

    def preprocess(self, image: NDArray[Any]) -> NDArray[Any]:
        """
        Resize and prepare BGR image for neural network.

        Args:
            image --- the input image array.

        Returns:
            The processed image array ready to be fed into the neural network.
        """
        input_image = cv2.resize(image, dsize=[320, 240])
        input_image = np.expand_dims(input_image.transpose(2, 0, 1), axis=0)
        return input_image

    def postprocess(
        self,
        pred_scores: NDArray[Any],
        pred_boxes: NDArray[Any],
        image_shape: tuple[int, int],
    ):
        """
        Processes the neural network's predictions to obtain usable results.

        This method filters detections below a confidence threshold, applies non-maximum suppression
        on bounding boxes, and returns bounding boxes in absolute pixel values.

        Args:
            pred_scores --- the predicted scores from the neural network.
            pred_boxes --- the predicted bounding boxes from the neural network.
            image_shape --- the shape of the input image.

        Returns:
            A tuple containing two lists: one for bounding boxes and another for scores.
        """

        # filter
        filtered_indexes = np.argwhere(
            pred_scores[0, :, 1] > self.confidence_thr
        ).tolist()
        filtered_boxes = pred_boxes[0, filtered_indexes, :]
        filtered_scores = pred_scores[0, filtered_indexes, 1]

        if len(filtered_scores) == 0:
            return [], []

        # convert all boxes to image coordinates
        h, w = image_shape

        def _convert_bbox_format(*args: list[int]):
            bbox = args[0]
            x_min, y_min, x_max, y_max = bbox
            x_min = int(w * x_min)
            y_min = int(h * y_min)
            x_max = int(w * x_max)
            y_max = int(h * y_max)
            return x_min, y_min, x_max, y_max

        bboxes_image_coord = np.apply_along_axis(
            _convert_bbox_format, axis=2, arr=filtered_boxes
        )

        # apply non-maximum supressions
        bboxes_image_coord, indexes = non_max_suppression(
            bboxes_image_coord.reshape([-1, 4]), threshold=self.overlap_thr
        )
        filtered_scores = filtered_scores[indexes]
        return bboxes_image_coord, filtered_scores

    def inference(
        self, image: NDArray[Any]
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        """
        Run the entire inference pipeline on an input image.

        This method preprocesses the input image, performs inference using the neural network,
        and postprocesses the predictions to obtain final results.

        Args:
            image --- the input image array.

        Returns:
            A tuple containing two arrays: one for faces and another for scores.
        """
        input_image = self.preprocess(image)

        pred = self.model([input_image])
        pred_scores = pred[self.model.output(0)]
        pred_boxes = pred[self.model.output(1)]

        image_shape = image.shape[:2]
        faces, scores = self.postprocess(pred_scores, pred_boxes, image_shape)
        return faces, scores
