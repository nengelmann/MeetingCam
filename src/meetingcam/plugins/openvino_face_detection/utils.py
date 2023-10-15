from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray


def non_max_suppression(
    boxes: NDArray[Any], threshold: float
) -> tuple[list[Any]]:
    """Apply fast non-maximum suppression on bounding boxes.

    This function takes a set of bounding boxes and a threshold as input, and returns
    a tuple containing a list of suppressed bounding boxes and their respective indexes.

    Args:
        boxes --- a numpy array of bounding boxes.
        threshold --- the overlap threshold for suppression.

    Returns:
        A tuple containing a list of suppressed bounding boxes and their indexes.

    Note:
        Code adapted from: https://github.com/Gabriellgpc/ultra-lightweight-face-detection and
    """

    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # compute the area of the bounding boxes and sort the boxes by
    # their bottom-right y-coordinate
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the index
        # value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of the
        # bounding box and the smallest (x, y) coordinates for the
        # end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap between the bounding box and
        # other bounding boxes
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have overlap
        # greater than the provided overlap threshold
        idxs = np.delete(
            idxs,
            np.concatenate(([last], np.where(overlap > threshold)[0])),
        )

    # return only the bounding boxes that were picked
    return boxes[pick], pick


def draw_bbox(
    img: NDArray[Any],
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int,
    radius: int,
    corner_len: int,
    connected: bool = True,
    c_thickness: int = 1,
) -> NDArray[Any]:
    """Draw a bounding box with rounded corners onto an image.

    This function draws a bounding box with rounded corners onto a given image,
    according to the specified parameters such as the coordinates of the corners,
    the color, and the thickness of the lines.

    Args:
        img --- the input image as a numpy array.
        pt1 --- the coordinates of the first point (top left corner).
        pt2 --- the coordinates of the second point (bottom right corner).
        color --- the color of the bounding box as a tuple of RGB values.
        thickness --- the thickness of the lines forming the bounding box.
        radius --- the radius of the rounded corners.
        corner_len --- the length of the corners.
        connected --- Flag to indicate if corners are connected. Defaults to True.
        c_thickness --- the thickness of the connecting lines. Defaults to 1.

    Returns:
        The image with the bounding box drawn on it.

    Note:
        Code adapted from: https://stackoverflow.com/questions/46036477/drawing-fancy-rectangle-around-face
    """
    x1, y1 = pt1
    x2, y2 = pt2
    r = radius
    d = corner_len

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

    if connected:
        # Top left to top right
        cv2.line(img, (x1 + r + d, y1), (x2 - r, y1), color, c_thickness)
        # Bottom left to Bottom right
        cv2.line(img, (x1 + r + d, y2), (x2 - r, y2), color, c_thickness)
        # Bottom left to top left
        cv2.line(img, (x1, y2 - r - d), (x1, y1 + r + d), color, c_thickness)
        # Bottom right to top right
        cv2.line(img, (x2, y2 - r - d), (x2, y1 + r + d), color, c_thickness)

    return img


def box_area(box: list[int]) -> int:
    """Calculate the area of a bounding box.

    Args:
        box --- a list of integers representing the bounding box in the format [x_min, y_min, x_max, y_max].

    Returns:
       The area of the bounding box.
    """
    area = int(box[2] - box[0]) * (box[3] - box[1])
    return area
