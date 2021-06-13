# import win32gui
# import win32.lib.win32con as win32con

from libsoundtouch import soundtouch_device
from flask import Flask, jsonify

SETTINGS_FILE = "settings.txt"

app = Flask(__name__)

class SoundTouchDevice(object):
    def __init__(self) -> None:
        try:
            with open(SETTINGS_FILE) as f:
                data = {x: y for x, y in map(lambda x: x.strip().split("="), f.read().strip().split("\n"))}
            self.device_ip = data.get("DEVICE_IP")
            self.device_name = data.get("DEVICE_NAME")
        except Exception as e:
            print(e)
            print("Settings File is Missing or Corrupted. Creating New File.")
            self.device_ip = input("Enter IP of device: ")
            self.device_name = input("Enter Name of device: ")
        
        self.device = None
        self.volume = int(data.get("VOLUME", 70))
        self.bass = int(data.get("BASS", 0))
        self.status = data.get("STATUS", "STANDBY")

        self.get_device()

    def update_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            f.writelines([
                f"DEVICE_IP={self.device_ip}\n",
                f"DEVICE_NAME={self.device_name}\n",
                f"VOLUME={self.volume if self.volume is not None else 70}\n",
                f"BASS={self.bass if self.bass is not None else 0}\n",
                f"STATUS={self.status.source if self.status is not None else 'STANDBY'}\n",
            ])

    def volume_updater(self, volume):
        self.volume = volume.actual
        self.update_settings()
    
    def bass_updater(self, bass):
        self.bass = bass.actual
        self.update_settings()

    def status_updater(self, status):
        self.status = status
        self.update_settings()

    def change_volume_by(self, increment):
        self.volume += increment
        self.device.set_volume(self.volume)
    
    def set_volume(self, volume):
        self.device.set_volume(volume)

    def increase_bass(self):
        self.bass = min(0, self.bass+1)
        self.set_bass(self.bass)
    
    def decrease_bass(self):
        self.bass = max(-5, self.bass-1)
        self.set_bass(self.bass)

    def set_bass(self, bass):
        self.device.set_bass(bass)
    
    def set_power_on(self):
        self.device.power_on()
        self.device.set_volume(self.volume)
        self.device.set_bass(self.bass)

    def set_device_state(self, state):
        if state == "aux" or state == "AUX":
            self.device.select_source_aux()
        elif state == "bluetooth" or state == "BLUETOOTH":
            self.device.select_source_bluetooth()
        elif state == "off" or state == "STANDBY":
            self.device.power_off()
        elif state == "on":
            self.set_power_on()
        else:
            raise ValueError("State not supported")

    def toggle_device_state(self):
        if self.status.source == "STANDBY":
            self.set_power_on()
        else:
            self.device.power_off()

    def get_device(self):
        while self.device is None:
            try:
                self.device = soundtouch_device(self.device_ip)
                
                self.device.set_volume(self.volume)
                self.device.set_bass(self.bass)
                self.set_device_state(self.status)
                self.status = self.device.status()

                self.device.add_volume_listener(self.volume_updater)
                self.device.add_bass_listener(self.bass_updater)
                self.device.add_status_listener(self.status_updater)
                self.device.start_notification()
            except Exception as e:
                print(e)
                self.device = None

soundTouchDevice = SoundTouchDevice()
soundTouchDevice.get_device()

@app.route("/status")
def get_status():
    if soundTouchDevice.device is None:
        return jsonify({"device": None})
    else:
        return jsonify({"device": {
            "name": soundTouchDevice.device_name,
            "ip": soundTouchDevice.device_ip,
            "status": soundTouchDevice.status.source,
            "volume": str(soundTouchDevice.volume),
            "bass": str(soundTouchDevice.bass)
        }})

@app.route("/increase-vol", methods=["POST"])
def increase_device_volume():
    soundTouchDevice.change_volume_by(5)
    return "OK", 200

@app.route("/decrease-vol", methods=["POST"])
def decrease_device_volume():
    soundTouchDevice.change_volume_by(-5)
    return "OK", 200

@app.route("/increase-bass", methods=["POST"])
def increase_device_bass():
    soundTouchDevice.increase_bass()
    return "OK", 200

@app.route("/decrease-bass", methods=["POST"])
def decrease_device_bass():
    soundTouchDevice.decrease_bass()
    return "OK", 200

@app.route("/set-volume-<amount>", methods=["POST"])
def set_device_volume(amount):
    try:
        amount = int(amount)
    except ValueError as e:
        return "amount is not an integer", 400
    
    if amount < 0 or amount > 100:
        return "amount is not in range [0, 100]", 400

    soundTouchDevice.set_volume(amount)
    return "OK", 200

@app.route("/set-<state>", methods=["POST"])
def set_device_state(state):
    try:
        soundTouchDevice.set_device_state(state)
        return "OK", 200
    except Exception as e:
        print(e)
        return "Unrecognized state", 400


@app.route("/toggle-state", methods=["POST"])
def toggle_device_state():
    soundTouchDevice.toggle_device_state()
    return "OK", 200

if __name__ == "__main__":
    # my_program = win32gui.GetForegroundWindow()
    # win32gui.ShowWindow(my_program , win32con.SW_HIDE)
    app.run(port= 9999)