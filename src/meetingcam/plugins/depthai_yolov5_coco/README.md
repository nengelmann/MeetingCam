


## Depthai Yolov5 Example

The default and current only depthai AI-Plugin is a yolov5 model trained on the COCO dataset.

You'll run it with main.py as described under the usage section. \
`python src/meetingcam/main.py --device-path /dev/videoX --depthai`

It will make an depthai OKA device as virtual camera available in your meeting tools. You join a meeting, select the virtual camera.
By default it will show an unmodified camera stream of your real camera.

<p align="center">
<img src="./assets/example_depthai_yolov5_coco.jpg" width=40% height=40%>
</p>

Let's press **<Ctrl+Alt+l>** for unhiding the camera detections!

<p align="center">
<img src="./assets/example_depthai_yolov5_coco_with_detection.jpg" width=40% height=40%>
</p>

In this example, the neural network runs directly on the OAK camera, not on your PC.


