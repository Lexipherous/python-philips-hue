import json

import requests
import argparse
import os
from configparser import ConfigParser


class PhilipsHueLights:
    def __init__(self):
        self.room_saturation = None
        self.room_hue = None
        self.room_brightness = None
        self.room_state = None
        self.ip = None
        self.get_bridge_ip()
        self.user = None
        self.presets = {"red": {"on": True, "bri": 254, "hue": 65535, "sat": 254},
                        "warm": {"on": True, "bri": 129, "hue": 7198, "sat": 224},
                        "orange": {"on": True, "bri": 254, "hue": 7300, "sat": 235},
                        "yellow": {"on": True, "bri": 254, "hue": 12000, "sat": 185},
                        "green": {"on": True, "bri": 254, "hue": 24000, "sat": 240},
                        "turquoise": {"on": True, "bri": 254, "hue": 38600, "sat": 224},
                        "blue": {"on": True, "bri": 254, "hue": 46000, "sat": 240},
                        "purple": {"on": True, "bri": 254, "hue": 48500, "sat": 240},
                        "magenta": {"on": True, "bri": 254, "hue": 50000, "sat": 230},
                        "pink": {"on": True, "bri": 254, "hue": 55696, "sat": 220},
                        "white": {"on": True, "bri": 254, "hue": 10000, "sat": 0},
                        "on": {"on": True},
                        "off": {"on": False}}

    def generate_key(self):
        data = {"devicetype": "LightsControlScript#Python3"}
        req = requests.post(f"http://{self.ip}/api/", data=json.dumps(data))

        result = json.loads(req.content)
        if 'success' in result[0]:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lights.ini')
            config_parser = ConfigParser()

            config_parser['philips_hue_lights'] = {'key': result[0]['success']['username']}
            with open(path, 'w') as configfile:  # save
                config_parser.write(configfile)

            print(f"Successfully generated an API key to: `{path}`. Use -h to use this script :)")
        elif 'error' in result[0] and result[0]['error']['type'] == 101:
            print(f"Error {result[0]['error']['type']}: Before running again, press the button on your Hue bridge.")
        else:
            print(f"Error {result[0]['error']['type']}: {result[0]['error']['description']}")

    def get_user_key(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lights.ini')
        config_parser = ConfigParser()
        config_parser.read(path)
        try:
            self.user = config_parser.get('philips_hue_lights', 'key')
        except Exception as e:
            print("Unable to locate key. Ensure you have run this script with the -setup flag first, and that the lights.ini file is in the same directory as this script.")

    def get_bridge_ip(self):
        str_url = "https://discovery.meethue.com/"
        self.ip = requests.get(str_url).json()[0]["internalipaddress"]

    def get_room(self, group_name):
        all_rooms = requests.get(f"http://{self.ip}/api/{self.user}/groups/").json()
        for room in all_rooms:
            # print(all_rooms[room], group_name)
            if all_rooms[room]['name'] == group_name:
                self.room_state = all_rooms[room]['action']['on']
                self.room_brightness = all_rooms[room]['action']['bri']
                self.room_hue = all_rooms[room]['action']['hue']
                self.room_saturation = all_rooms[room]['action']['sat']

    def is_lights_on(self):
        # Query the local bridge and return on/off state data
        str_data = requests.get(f"http://{self.ip}/api/{self.user}/groups/1").json()
        return str_data["state"]["all_on"]

    def set_preset(self, preset: str):
        self.set_room_lights(self.presets[preset]['on'],
                             self.presets[preset]['bri'],
                             self.presets[preset]['hue'],
                             self.presets[preset]['sat'])

    def set_room_lights(self, state, brightness, hue, saturation):
        data = {"on": state, "bri": brightness, "hue": hue, "sat": saturation}
        requests.put(f"http://{self.ip}/api/{self.user}/groups/1/action", data=json.dumps(data))


parser = argparse.ArgumentParser()
state_group = parser.add_mutually_exclusive_group()
parser.add_argument('-setup', help='Generates the API key for your Hue bridge', action='store_true')
parser.add_argument('-room', type=str, help='Room name. Use quotations if spaces are in the name.')
parser.add_argument('-preset', type=str, help='Specify some presets built-in. (red, warm, orange, yellow, green, turquoise, blue, purple, magenta, pink, white)')
parser.add_argument('-bri', type=int, help='Set a rooms lights brightness (0–255)')
parser.add_argument('-hue', type=int, help='Set a rooms lights hue (0–65535)')
parser.add_argument('-sat', type=int, help='Set a rooms lights saturation (0–255)')
state_group.add_argument('-on', action='store_true')
state_group.add_argument('-off', action='store_true')

args = parser.parse_args()
args = args.__dict__

if 'setup' in args and args['setup']:
    PhilipsHueLights().generate_key()
else:
    lights = PhilipsHueLights()
    lights.get_user_key()
    if lights.user:
        lights.get_room(args['room'])

        if 'preset' in args and args['preset'] is not None:
            lights.set_preset(args['preset'])
        else:
            if args['on']:
                _status = True
            elif args['off']:
                _status = False
            else:
                _status = lights.room_state

            _bri = args['bri'] if args['bri'] else lights.room_brightness
            _hue = args['hue'] if args['hue'] else lights.room_hue
            _sat = args['sat'] if args['sat'] else lights.room_saturation

            lights.set_room_lights(_status, _bri, _hue, _sat)
