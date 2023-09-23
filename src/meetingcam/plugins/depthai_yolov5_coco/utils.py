"""
Utility functions for depthai yolov5

Note:
    Code adapted from: https://github.com/luxonis/depthai-experiments/blob/master/gen2-yolo/device-decoding/main_api.py
"""

import argparse
import json
import sys
import time
from pathlib import Path

import blobconverter
import cv2
import depthai as dai
import numpy as np


# nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
def _frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def displayFrame(frame, detections, labels):
    color = (255, 0, 0)
    for detection in detections:
        bbox = _frameNorm(
            frame,
            (detection.xmin, detection.ymin, detection.xmax, detection.ymax),
        )
        cv2.putText(
            frame,
            labels[detection.label],
            (bbox[0] + 10, bbox[1] + 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            255,
            3,
            0,
        )
        cv2.putText(
            frame,
            f"{int(detection.confidence * 100)}%",
            (bbox[0] + 10, bbox[1] + 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            255,
            2,
            0,
        )
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 3)
    return frame
