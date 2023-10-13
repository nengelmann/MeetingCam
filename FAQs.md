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
