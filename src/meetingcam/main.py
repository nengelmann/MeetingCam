#!/usr/bin/env python3

"""This script is a camera processing pipeline that allows for real-time manipulation of video streams,
so that a modified video stream can be used in web meeting tools like Teams, Meets or Zoom.

The script utilizes is processing of video frames from a real camera device, and output the modified frames to a virtual camera device. 
A command line interface is provided for user interaction, with keyboard listeners enabling real-time adjustments 
like color space conversion, image flipping, and face detection functionalities.
"""

import cv2
import pyvirtualcam
import typer
from constants import DEPTHAI, WEBCAM
from device import DepthaiDevice, WebcamDevice
from plugins.depthai_yolov5_coco.plugin import Yolov5
from plugins.openvino_face_detection.plugin import FaceDetection
from plugins.plugin_utils import PluginBase
from plugins.roboflow_general.plugin import RoboflowDetection
from utils import ArgumentHandler, InvalidArgumentError, KeyHandler

app = typer.Typer()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def main(
    ctx: typer.Context,
    device_path: str | None = None,
    depthai: bool = False,
    roboflow: bool = False,
) -> None:
    """Initialize the several handlers, real and virtual camera devices for video frame capture and processing and run the whole pipeline.
    It integrates keyboard listeners for real-time user inputs to manipulate video streams.

    Args:
        ctx (typer.Context): Context information from the command line.
        device_path (str | None): The device path for the real camera. Defaults to None.
    """

    # preprocess extra arguments, e.g. for custom plugin
    extra_args = ArgumentHandler(ctx.args)
    extra_args.print(ctx.args)

    if depthai:
        # define plugin
        plugin = Yolov5()

        # initialize camera device handler with OAK as input device
        device_handler = DepthaiDevice(plugin.pipeline)
        virtual_path = device_handler.init_device(device_path)

    elif roboflow:
        # handle extra argument --name, if defined
        roboflow_api_key = extra_args.get("--roboflow-api-key", ctx.args)
        project_name = extra_args.get("--project-name", ctx.args)
        version = extra_args.get("--version", ctx.args)
        # define plugin
        plugin = RoboflowDetection(roboflow_api_key, project_name, version)
        # initialize camera device handler with webcam as input device
        device_handler = WebcamDevice()
        virtual_path = device_handler.init_device(device_path)

    else:
        # handle extra argument --name, if defined
        name = extra_args.get("--name", ctx.args)
        # define plugin
        plugin = FaceDetection(name=name)
        # initialize camera device handler with webcam as input device
        device_handler = WebcamDevice()
        virtual_path = device_handler.init_device(device_path)

    # perform some checks on given configuration before camera is started
    if plugin.type is None:
        raise NotImplementedError(
            "Your plugin needs to have a plugin type assigned. plugin.type"
            " WEBCAM | DEPTHAI"
        )
    if depthai and plugin.type == WEBCAM:
        raise InvalidArgumentError(
            "The cli flag 'depthai' is set but the plugin you run is meant for"
            " webcam usage."
        )

    if not depthai and plugin.type == DEPTHAI:
        raise InvalidArgumentError(
            "The cli flag 'depthai' is not set but the plugin you run is meant"
            " for depthai usage."
        )

    # initialize real camera, to get frames
    with device_handler.get_device() as r_cam:
        # custom setup for depthai (on device handling)
        if depthai:
            r_cam.setup(plugin.device_setup, plugin.acquisition)

        # initialize a virtual camera where the modified frames will be sent to
        with pyvirtualcam.Camera(
            width=r_cam.width,
            height=r_cam.height,
            fps=24,
            device=virtual_path,
        ) as v_cam:
            # initialize a keyboard listener to get and use keystroke during runtime as trigger or switch
            with KeyHandler() as listener:
                listener.start()

                # print in command line that the pipeline is running
                device_handler.device_running()

                # get frames from real camera, process it and sent it out via virtual camera
                while True:
                    # get a frame and optionally some on camera detections
                    frame, detection = r_cam.get_frame()

                    # convert bgr to rgb if <Ctrl+Alt+r> keys are pressed
                    if listener.bgr2rgb_sw:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # pass trigger <Ctrl+Alt+f>, <Ctrl+Alt+l> and <Ctrl+Alt+n> for usage in plugin
                    trigger = (
                        listener.f_trig,
                        listener.l_trig,
                        listener.n_trig,
                    )
                    frame = plugin.process(frame, detection, trigger)

                    # flip image if <Ctrl+Alt+m> keys are pressed
                    if listener.mirror_sw:
                        frame = cv2.flip(frame, 1)

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # sent out the modified frame to the virtual camera
                    v_cam.send(frame)
                    v_cam.sleep_until_next_frame()


if __name__ == "__main__":
    app()
