
# first-person face detection

https://github.com/nengelmann/MeetingCam/assets/120744129/ec2e608d-e785-4179-ba33-c692da05a95b

Prints your face detection and name in your webcam stream. Possibility to hide the bounding box and name imprint.

## Additional installation

1. Make sure your in the MeetingCam root directory

2. Download and convert a face detection model, then opt out from sending usage data
   ```bash
   omz_downloader --name ultra-lightweight-face-detection-rfb-320 --output_dir src/meetingcam/models
   omz_converter --name ultra-lightweight-face-detection-rfb-320 --download_dir src/meetingcam/models --output_dir src/meetingcam/models --precision=FP16
   opt_in_out --opt_out
   ```
   More about the used face detection model can be found [here](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/ultra-lightweight-face-detection-rfb-320/README.md).
   This is a very light weight model, which will just work fine due to the easy task of face detection of a person in front of a webcam.

## Usage

### First add a camera device to MeetingCam

To show a modified camera stream in online meetings it is necessary to create a virtual camera for each real camera you want to use.

1. Activate the virtual environment
   ```bash
   source .venv/bin/activate
   ```
2. Get command to add a camera device
   ```bash
   python src/meetingcam/main.py add-devices
   ```
   Then **copy and execute** the **command of the camera you want to use**.
3. You can now see that the camera of your choice has a virtual counterpart.
   ```bash
   python src/meetingcam/main.py list-devices
   ```

### Run a plugin
Replace `yourname` and `device_path` with your name of choice and your camera path which has a virtual counterpart.
```bash
python src/meetingcam/main.py face-detector --name yourname /dev/video0
```


### Get help
Options and usage for the plugin are documented in the plugins help function.
```bash
python src/meetingcam/main.py face-detector
```

## Showcase
By default the bounding box and name imprint are shown. \
<img src="/assets/example_face_detection_n_+_f_trigger.png" height=350>

You can hide the name imprint by pressing **<Ctrl+Alt+n>**. \
<img src="/assets/example_face_detection_face_f_trigger.png" height=350>

Also the bounding box can be hidden **<Ctrl+Alt+f>**. \
<img src="/assets/example_face_detection_no_trigger.png" height=350>



## Implementation details

The model itself is a general face detector, which means that it is meant to detect all faces in the webcam stream. To avoid additional bounding boxes on other faces the following assumption is made.

_Assumption_: \
You as user are nearest to the camera and hence the detected bounding box of your face covers a bigger area then from faces detected in the background.

So this plugin is is just printing a bounding box on the face detection which covers the biggest area in the video stream. That means if a person passes through behind you, the bounding box will be still shown on your face because you are nearer to the camera and hence your face detection covers the biggest area. 
Just be aware that the **implementation fails if the above assumption is not valid** in your case/setup.