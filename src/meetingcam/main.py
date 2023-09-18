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
from device import DeviceHandler
from plugins.face_detection.plugin import FaceDetection
from utils import ArgumentHandler, KeyHandler, VideoCapture

app = typer.Typer()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def main(ctx: typer.Context, device_path: str | None = None) -> None:
    """Initialize the several handlers, real and virtual camera devices for video frame capture and processing and run the whole pipeline.
    It integrates keyboard listeners for real-time user inputs to manipulate video streams.

    Args:
        ctx (typer.Context): Context information from the command line.
        device_path (str | None): The device path for the real camera. Defaults to None.
    """
    # preprocess extra arguments, e.g. for custom plugin
    extra_args = ArgumentHandler(ctx.args)
    extra_args.print(ctx.args)

    # initialize camera device handler
    device_handler = DeviceHandler()
    device_path_real, device_path_virtual = device_handler.init_device(
        device_path
    )

    # setup plugin with extra argument --name
    name = extra_args.get("--name", ctx.args)
    img_processor = FaceDetection(name=name)

    # initialize real camera, to get frames
    with VideoCapture(device_path_real) as r_cam:
        # initialize a virtual camera where the modified frames will be sent to
        with pyvirtualcam.Camera(
            width=r_cam.width,
            height=r_cam.height,
            fps=60,
            device=device_path_virtual,
        ) as v_cam:
            # initialize a keyboard listener to get and use keystroke during runtime as trigger or switch
            with KeyHandler() as listener:
                listener.start()

                # print in command line that the pipeline is running
                device_handler.device_running()

                # get frames from real camera, process it and sent it out via virtual camera
                while True:
                    frame = r_cam.get_frame()

                    # convert bgr to rgb if <Ctrl+Alt+r> keys are pressed
                    if listener.bgr2rgb_sw:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # pass trigger <Ctrl+Alt+f> and <Ctrl+Alt+n> for face detection and name in prints to face detector plugin
                    trigger = (listener.f_trig, listener.n_trig)
                    frame = img_processor.process(frame, trigger)

                    # flip image if <Ctrl+Alt+m> keys are pressed
                    if listener.mirror_sw:
                        frame = cv2.flip(frame, 1)

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # sent out the modified frame to the virtual camera
                    v_cam.send(frame)
                    v_cam.sleep_until_next_frame()


if __name__ == "__main__":
    app()
