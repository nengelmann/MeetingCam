# FAQs

## Errors

### modprobe: FATAL: Module v4l2loopback is in use.

```bash
$ sudo modprobe -r v4l2loopback
modprobe: FATAL: Module v4l2loopback is in use.
```
_Background:_ \
The command 'sudo modprobe -r v4l2loopback' tries to reset all virtual devices. \
It fails with 'modprobe: FATAL: Module v4l2loopback is in use.' if any application is still accessing the camera devices. **Also if** a **browser is** still **open**, the camera might be accessed and hence the command fails.

_Solution:_ \
Close any application which might have or had access to camera devices and try again. If this is still not working, restart your system.


## Good to know

### Judder or stuck video stream

_Background:_ \
Poor internet connection or bandwidth limitation can make the video stream in meeting calls get stuck or judder.

_Solution:_ \
Adjust the the maximum video stream size from 720p to 540p in the [constants.py](src/meetingcam/constants.py) file.

### Black image instead of video stream

_Background:_ \
Some meeting tools restrict the video stream resolution and shape.

_Solution:_ \
If you have changed the video stream resolution or shape, this is likely to cause the problem. The default of 720p to 540p should just work fine.
