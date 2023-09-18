<h1>MeetingCam</h1>
  <p align="center">&#x2728 Special effects for not so special meetings. &#x1F440</p>
</p>
<hr />
<p align="center">
    AI webcam utility for online meetings. Make your introduction fun! &#x1FA84;
    </br> This repo is <i>work in progess</i>. The current version is a command line tool for Linux.
</p>
<hr />

## Installation

1. Install [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html)

2. Create a virtual python3.10 environment
   ```bash
   virtualenv -p /usr/bin/python3.10 .venv && source .venv/bin/activate
   ```
3. Install the dependencies
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Setup [pyvirtualcam](https://github.com/letmaik/pyvirtualcam)
   ```bash
   sudo apt install v4l2loopback-dkms
   sudo apt install v4l-utils
   ```
5. Download model, convert model and opt out from sending usage data
   ```bash
   omz_downloader --name ultra-lightweight-face-detection-rfb-320 --output_dir src/meetingcam/models
   omz_converter --name ultra-lightweight-face-detection-rfb-320 --download_dir src/meetingcam/models --output_dir src/meetingcam/models --precision=FP16
   opt_in_out --opt_out
   ```
   More about the used face detection model can be found [here](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/ultra-lightweight-face-detection-rfb-320/README.md).
   A very light weight model will just work fine, due to the easy task of face detection of a person in front of a webcam.

## Usage

1. Make sure your web cam is connected.

2. Activate the virtual environment
   ```bash
   source .venv/bin/activate
   ```
3. Run the help.py file to get custom instructions on how to create virtual cameras with your web cam. \
   A virtual camera is needed to stream the modified camera images to your meeting tools like teams, zoom or meets.

   ```bash
   python ./src/meetingcam/help.py
   ```

   Don't be confused, you'll need to add your camera with another (sudo) bash command like `sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="MeetingCam0"`. \
   The help.py file will provide more info on how this command needs to be for your system/camera.

4. You should be all set now. Let's run help.py again to see which and how you can run main.py with your camera.
   ```bash
   python ./src/meetingcam/help.py
   ```
5. In the terminal you see which command you need to run for your specific camera setup. \
   It should look like:

   _For YOUR CAMERA DEVICE run:_ \
   _'python src/meetingcam/main.py --device-path /dev/videoX --name YourName'_

   **Enter your** camera **command** and start MeetingCam

If you **restart** your system, it **will** unload the module and **undo the above device setup** \
You can also run `sudo modprobe -r v4l2loopback` to undo the device setup.

## Face Detection Example

The default and current only AI-Plugin is the Face Detection example.

You'll run it with main.py as described under the usage section. \
`python src/meetingcam/main.py --device-path /dev/videoX --name YourName`

It will make a virtual camera available in your meeting tools. You join a meeting, select the virtual camera e.g. 'MeetingCamX CameraName'.
By default it will show an unmodified camera stream of your real camera.
![Just you ...](./assets/example_face_detection_no_trigger.png)

Let's press **<Ctrl+Alt+f>** for detection of your face!
![Face Detection](./assets/example_face_detection_face_f_trigger.png)

You can now show your name with **<Ctrl+Alt+n>**.
![Face Detection](./assets/example_face_detection_n_+_f_trigger.png)

_Actually your face is already detected the hotkey command just enables the print in of the detection._

## Further information

### Camera setup info

More information on how to setup virtual cameras can be found [here](https://wiki.archlinux.org/title/V4l2loopback)

### Development and modifications

You can customize this repo for your needs, you can also write your own AI-Plugin for running your models on Zoom, Teams or Meets. \
More information about that in [DEVELOP.md](DEVELOP.md)

### Usage with depthai camera

#### Install additional dependencies

```bash
 source .venv/bin/activate
 pip install depthai
```

#### Run OAK devices as uvc

Run OAK devices as uvc before normal usage of MeetingCam.

```bash
 source .venv/bin/activate
 python ./tools/oak_as_uvc.py
```
