# roboflow general

[<img src="https://2486075003-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-M6S9nPJhEX9FYH6clfW%2Fuploads%2FVW4FMckhfS5GGlUcpuY2%2F642746dba53a59a614a64b35_roboflow-open-graph.png?alt=media&token=d120c000-46a4-411b-aba3-db055d48a904" height="250">](src/meetingcam/plugins/roboflow_general/)

Runs roboflow object-detection and instance-segmentation models.

## Additional installation

None.

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

1. Currently it is needed to run a roboflow inference server **in a separate terminal**.
To do so, simply run the following to start an inference server (CPU).
   ```
   docker run --net=host roboflow/roboflow-inference-server-cpu:latest
   ```
   See [here](https://github.com/roboflow/inference) for more options.

2. Run the plugin with replacements for `api-key`, `project-name`, `version` and `device_path` with your camera path which has a virtual counterpart.
   ```bash
   python src/meetingcam/main.py roboflow --api-key YOUR_API_KEY --project-name meetingcam-roboflow-example-objectdetection --version 1 --device-path /dev/video0
   ```
   As an alternative you can run the following and you'll be ask to enter the above replacements by terminal prompt.
   ```bash
   python src/meetingcam/main.py roboflow /dev/video0
   ```

You can hide the label imprints by pressing **<Ctrl+Alt+l>**.


### Get help
Options and usage for the plugin are documented in the plugins help function.
```bash
python src/meetingcam/main.py roboflow
```

## Showcase

### Example - Object Detection

This is a custom roboflow project which runs on MeetingCam like below.

<img src="/assets/example_roboflow_object_detection.png" height=350>

Roboflow project page [here](https://universe.roboflow.com/nengelmann-phzsv/meetingcam-roboflow-example-objectdetection).

### Example - Instance Segmentation

This is a custom roboflow project which runs on MeetingCam like below.

<img src="/assets/example_roboflow_instance_segmentation.png" height=350>

Roboflow project page [here](https://universe.roboflow.com/nengelmann-phzsv/meetingcam-roboflow-example-instancesegmentation).

## Implementation details

Currently just object-detection and instance-segmentation models are supported.