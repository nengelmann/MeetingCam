from typing import Any

import cv2
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
        self.width = int(self.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

        return frame

    def get_fps(self) -> int:
        """Retrieve the frames per second (FPS) of the video capture.

        Prints the total FPS and returns the FPS as an integer.
        """
        fps = self.get(cv2.CAP_PROP_FPS)
        print(f"total FPS: {int(fps)}")
        return int(fps)


class KeyHandler(keyboard.GlobalHotKeys):
    """A class to handle global hotkeys and their functionalities.

    Inherits from keyboard.GlobalHotKeys and defines hotkey triggers and switches.
    """

    def __init__(self) -> None:
        """Initialize the KeyHandler with hotkeys and their respective states."""
        self.hotkeys = {
            "<ctrl>+<alt>+f": self.f_trigger,
            "<ctrl>+<alt>+n": self.n_trigger,
            # '<ctrl>+<alt>+x':self.your_hotkey_x,
            "<ctrl>+<alt>+r": self.bgr2rgb_switch,
            "<ctrl>+<alt>+m": self.mirror_switch,
        }
        super().__init__(self.hotkeys)

        self.f_trig: bool = False
        self.n_trig: bool = False
        # self.x_trig: bool = False
        self.bgr2rgb_sw: bool = False
        self.mirror_sw: bool = True

    def __enter__(self) -> Self:
        """Enter method for context management, returning self."""
        return self

    def __exit__(self, *args: tuple[Any]) -> None:
        """Exit method for context management, stopping the KeyHandler."""
        self.stop()

    def f_trigger(self) -> None:
        """Toggle the state of f_trigger and print its status."""
        self.f_trig = not self.f_trig
        print("Keyboard trigger 1: ", str(self.f_trig))

    def n_trigger(self) -> None:
        """Toggle the state of n_trigger and print its status."""
        self.n_trig = not self.n_trig
        print("Keyboard trigger 2: ", str(self.n_trig))

    # def your_trigger_x(self) -> None:
    #    """Toggle the state of custom_trigger and print its status."""
    #    print('your hotkey is pressed')
    #    self.x_trig = not self.x_trig

    def bgr2rgb_switch(self) -> None:
        """Toggle the state of bgr2rgb_switch and print its status."""
        self.bgr2rgb_sw = not self.bgr2rgb_sw
        print("Keyboard switch BGR2RGB: ", str(self.bgr2rgb_sw))

    def mirror_switch(self) -> None:
        """Toggle the state of mirror_switch and print its status."""
        self.mirror_sw = not self.mirror_sw
        print("Keyboard switch Mirror Camera: ", str(self.mirror_sw))


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