"""This file contains a runner class which is initializing and running the main loop within MeetingCam."""

import cv2
import pyvirtualcam
from constants import DEPTHAI, WEBCAM
from device import DepthaiDevice, WebcamDevice
from plugins.plugin_utils import PluginBase, PluginDepthai
from utils import KeyHandler


class Runner:
    def __init__(
        self,
        plugin: PluginBase | PluginDepthai,
        device_path: str | None = None,
    ) -> None:
        """Initialize the device handler, real and virtual camera devices.

        Args:
            plugin --- Plugin which should be run.
            device_path --- The device path for the real camera. Defaults to None.
        """

        if type(device_path) is not str and type(device_path) is not None:
            device_path = device_path.value

        self.plugin = plugin

        if self.plugin.type == DEPTHAI:
            # initialize camera device handler with depthai as input device
            self.device_handler = DepthaiDevice(plugin.pipeline)
            self.virtual_path = self.device_handler.init_device(device_path)
        elif self.plugin.type == WEBCAM:
            # initialize camera device handler with webcam as input device
            self.device_handler = WebcamDevice()
            self.virtual_path = self.device_handler.init_device(device_path)
        else:
            raise ValueError(
                "Your plugin needs to have a plugin type assigned."
                " plugin.type: WEBCAM | DEPTHAI"
            )

    def run(self) -> None:
        """Main loop for video frame capture and processing within MeetingCam."""
        # initialize real camera, to get frames
        with self.device_handler.get_device() as r_cam:
            # custom setup for depthai (on device handling)
            if self.plugin.type == DEPTHAI:
                r_cam.setup(self.plugin.device_setup, self.plugin.acquisition)

            # initialize a virtual camera where the modified frames will be sent to
            with pyvirtualcam.Camera(
                width=r_cam.width,
                height=r_cam.height,
                fps=24,
                device=self.virtual_path,
            ) as v_cam:
                # initialize a keyboard listener to get and use keystroke during runtime as trigger or switch
                with KeyHandler() as listener:
                    listener.start()

                    # print in command line that the pipeline is running
                    self.device_handler.device_running()

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
                        frame = self.plugin.process(frame, detection, trigger)

                        # flip image if <Ctrl+Alt+m> keys are pressed
                        if listener.mirror_sw:
                            frame = cv2.flip(frame, 1)

                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # sent out the modified frame to the virtual camera
                        v_cam.send(frame)
                        v_cam.sleep_until_next_frame()
