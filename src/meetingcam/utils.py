from types import MethodType
from typing import Any, Callable

import cv2
import depthai
from constants import MAX_HEIGHT, MAX_WIDTH
from numpy.typing import NDArray
from pynput import keyboard
from typing_extensions import Self


class VideoCapture(cv2.VideoCapture):
    """Handle video capture functionalities with OpenCV.

    Inherits from cv2.VideoCapture and extends functionalities with
    methods to safely enter, exit, get frames and frame rates from
    a video capture.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the VideoCapture object with width and height properties."""
        super().__init__(*args, **kwargs)
        cam_width = int(self.get(cv2.CAP_PROP_FRAME_WIDTH))
        cam_height = int(self.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = min(cam_width, MAX_WIDTH)
        self.height = min(cam_height, MAX_HEIGHT)

        self.img_handler = ImageHandler()

    def __enter__(self) -> Self:
        """Enter method for context management, returning self."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit method for context management, releasing the video capture object."""
        self.release()

    def get_frame(self) -> NDArray[Any]:
        """Capture a frame from the video stream.

        Raises:
            RuntimeError: If image acquisition fails.

        Returns:
            A frame which has been captured by the camera.
        """
        (grabbed, frame) = self.read()

        if not grabbed:
            raise RuntimeError(
                "Image acquisition failed. Make sure the specified camera is"
                " not running in another application."
            )

        # high image resolution is usually not supported by online meeting tools
        frame = self.img_handler.correct_img_size(frame)

        # return the frame and None, there is no detection available from a webcam
        return frame, None

    def get_fps(self) -> int:
        """Retrieve the frames per second (FPS) of the video capture.

        Prints the total FPS and returns the FPS as an integer.
        """
        fps = self.get(cv2.CAP_PROP_FPS)
        print(f"total FPS: {int(fps)}")
        return int(fps)


class DepthaiCapture(depthai.Device):
    """Handle video capture functionalities with depthai.

    Inherits from depthai.Device and extends functionalities with
    methods to safely enter, exit, get frames and frame rates from
    a depthai device.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the depthai.Device object and assign width and height properties."""
        super().__init__(*args, **kwargs)
        self.width = MAX_WIDTH
        self.height = MAX_HEIGHT
        self.img_handler = ImageHandler()

    def __enter__(self) -> Self:
        """Enter method for context management, returning self."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit method for context management, releasing the video capture object."""
        self.close()

    def get_frame(self) -> NDArray[Any]:
        """
        Capture a frame from the video stream.

        Returns:
            A frame and potentially detections which has been captured by the camera.
        """
        # get image and detections from depthai plugin (image acquisition function)
        img, det = self.acquisition()

        # high image resolution is usually not supported by online meeting tools
        img = self.img_handler.correct_img_size(img)

        return img, det

    def setup(self, setup_func: Callable, acquisition_func: Callable):
        """Setup initializations defined in the plugins setup function and create an acquisition function also based on plugin specification.

        Args:
            setup_func --- initialization function of plugin
            acquisition_func --- handling function for image acquisition of plugin
        """
        setup_func(self)
        self.acquisition = MethodType(acquisition_func, self)

    def get_fps(self) -> int:
        """Retrieve the frames per second (FPS) of the video capture.

        Prints the total FPS and returns the FPS as an integer.
        """

        # fps =
        # print(f"total FPS: {int(fps)}")
        # return int(fps)
        raise NotImplementedError


class KeyHandler(keyboard.GlobalHotKeys):
    """A class to handle global hotkeys and their functionalities.

    Inherits from keyboard.GlobalHotKeys and defines hotkey triggers.
    """

    def __init__(
        self, plugin_hotkeys: dict[str, str] = {}, verbose=False
    ) -> None:
        """Initialize the KeyHandler with hotkeys and their respective states.

        Args:
            hotkeys: A dictionary of hotkeys and their respective variable name.
        """

        self.hotkeys = {}
        self.verbose = verbose

        self.default_hotkeys = [
            Hotkey(
                "<ctrl>+<alt>+r",
                "bgr2rgb",
                False,
                "Switch RGB to BGR color schema.",
            ),
            Hotkey(
                "<ctrl>+<alt>+m", "mirror", True, "Mirror the camera stream."
            ),
        ]

        for h in self.default_hotkeys:
            self.add_trigger(h.hotkey, h.variable, h.enabled)

        for h in plugin_hotkeys:
            self.add_trigger(h.hotkey, h.variable, h.enabled)

        super().__init__(self.hotkeys)

    def __enter__(self) -> Self:
        """Enter method for context management, returning self."""
        return self

    def __exit__(self, *args: tuple[Any]) -> None:
        """Exit method for context management, stopping the KeyHandler."""
        self.stop()

    def add_trigger(
        self, hotkey: str, variable: str, enabled: bool = True
    ) -> None:
        """Add a new trigger function for a specific hotkey.

        Args:
            hotkey: The hotkey string.
            variable: The name of the variable to toggle.
        """
        self.validate(hotkey, variable)
        setattr(self, variable, enabled)

        def trigger_func():
            setattr(self, variable, not getattr(self, variable))
            if self.verbose:
                print(
                    "Triggered: ",
                    hotkey,
                    " ",
                    variable,
                    " ",
                    getattr(self, variable),
                )

        self.hotkeys[hotkey] = trigger_func

    def validate(self, hotkey: str, variable: str) -> None:
        """Check if a hotkey and variable names are valid and not existing.

        Args:
            hotkey: The hotkey string.
            variable: The name of the variable to toggle."""
        if not isinstance(hotkey, str):
            raise ValueError(
                "Hotkey must be a string. For example: '<Ctrl>+<Alt>+z'"
            )
        if not isinstance(variable, str):
            raise ValueError(
                "Variable must be a string. For example: 'trig_var'"
            )
        if variable in self.hotkeys.values():
            raise ValueError(f"Variable name '{variable}' already exists.")
        if hotkey in self.hotkeys.keys():
            raise ValueError(f"Hotkey '{hotkey}' already exists.")


class Hotkey:
    """Hotkey data structure."""

    def __init__(
        self,
        hotkey: str,
        variable: str,
        enabled: bool = True,
        description: str = None,
    ) -> None:
        """Initialize the Hotkey object with a hotkey string, a variable name and a boolean value indicating whether the hotkey is enabled or not.

        Args:
            hotkey: The hotkey string.
            variable: The name of the variable to toggle.
            enabled: A boolean value indicating whether the hotkey is enabled or not.
            description: A description of the hotkey.
        """
        self.hotkey = hotkey
        self.variable = variable
        self.enabled = enabled
        self.description = description


class InvalidArgumentError(ValueError):
    """Custom exception for invalid arguments, inherits from ValueError."""

    def __init__(self, message: str = "Invalid argument") -> None:
        """Initialize the exception with a custom or default message."""
        super().__init__(message)


class ArgumentHandler:
    """A class to handle and validate command-line arguments."""

    def __init__(self, ctx_args: list[str]) -> None:
        """Initialize the ArgumentHandler and check the provided arguments."""
        self.check(ctx_args)

    def check(self, ctx_args: list[str]) -> None:
        """Check the validity of the command-line arguments.

        Raises:
            InvalidArgumentError: If the arguments are not correctly formatted.
        """
        if len(ctx_args) < 2 and len(ctx_args) != 0:
            raise InvalidArgumentError(
                "You need to provide extra arguments in the form '--name'"
                " 'argument'. "
            )

        if bool(len(ctx_args) % 2):
            raise InvalidArgumentError(
                "You need to provide extra arguments in the form '--name'"
                " 'argument'. Multiple arguments per parameter are not"
                " allowed. The following is invalid: '--your_param argument1"
                " argument2', while '--your_param argument1argument2' or"
                " '--your_param1 argument1 --your_param2 argument2' are valid."
            )

    def print(self, ctx_args: list[str]) -> None:
        """Print the list of provided command-line arguments or a message if none were provided."""
        if len(ctx_args) > 0:
            print("\nProvided extra arguments are:")
            for param, arg in zip(ctx_args[0::2], ctx_args[1::2]):
                print(param, ": ", arg)
        else:
            print("\nNo extra arguments provided.\n")

    def get(self, pram_name: str, ctx_args: list[str]) -> str | None:
        """Retrieve the value of a specific parameter from the command-line arguments.

        Args:
            pram_name --- the name of the parameter to retrieve.
            ctx_args --- a list of command-line arguments.

        Returns:
            The value of the parameter if found, otherwise None.
        """
        if pram_name in ctx_args:
            idx = ctx_args.index(pram_name) + 1
            arg = ctx_args[idx]
            return arg
        else:
            return None


class ImageHandler:
    """A class to handle image processing functions."""

    def __init__(self) -> None:
        """Initialize placeholder."""
        pass

    def correct_img_size(self, image: NDArray[Any]) -> NDArray[Any]:
        """Check image for maximum image size and resize if exceeded.
        The resizing will just be applied on the exceeding dimension (width, height or both) without taking the aspect ratio into account.

        Args:
            image --- the image to be processed.

        Returns:
            The processed image.
        """
        if image.shape[0] > MAX_HEIGHT or image.shape[1] > MAX_WIDTH:
            h = min(image.shape[0], MAX_HEIGHT)
            w = min(image.shape[1], MAX_WIDTH)
            image = cv2.resize(image, (w, h))
        return image
