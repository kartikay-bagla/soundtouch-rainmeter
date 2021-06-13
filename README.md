# Server for Bose SoundTouch Speakers

A small lightweight Flask server which provides endpoints for easy control of the Bose SoundTouch series speakers.

Combined with [Rainmeter](https://www.rainmeter.net/) you can quickly and easily control it from your desktop without the bulky SoundTouch Utility provided by Bose.

Currently it only supports Aux and Bluetooth sources over a single speaker only (since I use them only).

Example `settings.txt` file:
```
DEVICE_IP=192.168.1.100
DEVICE_NAME=SoundTouch
VOLUME=70
BASS=-2
STATUS=BLUETOOTH
```