# libinput-gestures

```bash
$ python3 setup.py install --user
$ chmod a+rw /dev/input/<trackpad>
$ libinput-gestures -e /dev/input/<trackpad> -d dispatcher.sh
```

Determine the correct `/dev/input` event file from `cat /proc/bus/input/devices`.