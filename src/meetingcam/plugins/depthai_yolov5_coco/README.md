# depthai yolov5

<img src="/assets/example_depthai_yolov5_coco_with_detection.jpg" height=500>

This depthai plugin is a yolov5 model trained on the COCO dataset. The model computation takes place on the depthai device.

## Additional installation

Make sure your udev rules are set according to depthai needs. If they are set already, skip this step.
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Usage

### First add a camera device to MeetingCam

To show a modified camera stream in online meetings it is necessary to create a virtual camera for each real camera you want to use.

1. Activate the virtual environment
   ```bash
   source .venv/bin/activate
   ```
2. Get command to add a camera device
   ```bash
   python src/meetingcam/main.py add-devices --type depthai
   ```
   Then **copy and execute** the **command of the camera you want to use**.
3. You can now see that the camera of your choice has a virtual counterpart.
   ```bash
   python src/meetingcam/main.py list-devices --type depthai
   ```

### Run a plugin
Replace the `device_path` with your cameras path which is the cameras **mxid** in the depthai case.
```bash
python src/meetingcam/main.py depthai-yolov5 device_path
```


### Get help
Options and usage for the plugin are documented in the plugins help function.
```bash
python src/meetingcam/main.py depthai-yolov5
```

## Showcase
By default the bounding box and name imprint are shown. \
<img src="/assets/example_depthai_yolov5_coco_with_detection.jpg" height=350>

You can hide the label imprints by pressing **<Ctrl+Alt+l>**. \
<img src="/assets/example_depthai_yolov5_coco.jpg" height=350>


## Implementation details

The depthai plugins are running the models computation on device, which means that the detection takes place on the cameras hardware. 
