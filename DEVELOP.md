# Developers and maintainers readme

## Installation

```bash
virtualenv -p /usr/bin/python3.10 .venv && source .venv/bin/activate
```

```bash
python -m pip install pip-tools
python -m pip install black
python -m pip install isort
python -m pip install mkdocs
python -m pip install debugpy
```

## Development

### Update the requirements

```bash
python -m piptools compile
```

### Formatting

```bash
black --line-length 79 --target-version py310 --experimental-string-processing .
isort --virtual-env .venv --python-version 310 --profile black --gitignore .
```

### Useful tools and commands

**Search for available cameras.**

```bash
v4l2-ctl --list-devices
```

**Add a single camera device.**

```bash
sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="webcam-0"
```

**Add a multiple camera device.**

```bash
sudo modprobe v4l2loopback devices=3 video_nr=8,9,10 card_label="webcam-1,webcam-2,webcam-3"
```

**Debug with CLI arguments**
```bash
python -m debugpy --listen 5678 --wait-for-client src/meetingcam/main.py 
```
Then attach with this VSCode configuration:
```json
{
    "name": "Python: Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    }
}
```
See also: https://code.visualstudio.com/docs/python/debugging

## Todos

- [x] Support for depthai
- [x] Support for roboflow
- [ ] Use roboflow api key from env variable if available  
- [x] Make KeyHandler available/adjustable within plugins
- [x] Add Template on how to run custom models
- [ ] Add documentation with MkDocs (https://www.mkdocs.org/) and MkDocstrings.
- [ ] Add one more example (e.g. [Matrix-Cam](https://github.com/joschuck/matrix-webcam/blob/main/matrix_webcam)).
- [x] Add custom plugin instructions and template.
- [ ] Check if new and custom plugins are valid, see '_check_plugin' function in [plugin_utils.py](src/meetingcam/plugins/plugin_utils.py)
- [ ] Add CI formatting (black, isort) checks.
- [ ] How to run on Windows and Mac?
- [ ] How to get rid of manual effort in creating virtual cameras?
- [ ] Extend face detection example to perform similarity. Example [here](https://github.com/luxonis/depthai-experiments/tree/master/gen2-face-recognition).
- [ ] 'for device in v4l2.iter_devices(skip_links=True):' with 'exclusive_caps=1' is likely to fail with 'IndexError: list index out of range'. Seems to be a problem with the 'v4l2' library.
