### python-philips-hue
A simple Python3 script that allows you to change Rooms in your Philips Hue Lights setup  

#### Setup
+ Press the button on the Philips Hue Bridge  
+ Run the script with the `-setup` flag. e.g. `python3 philips_hue_lights.py -setup`  

#### Usage
philips_hue_lights uses the following flags:  
`-h`, `--help`: Shows a help message  
`-setup`:  Generates the API key for your Hue bridge  
`-room ROOM`: Room name. Use quotations if spaces are in the name.  
`-preset PRESET`: Specify some presets built-in. (red, warm, orange, yellow, green, turquoise, blue, purple, magenta, pink, white)  
`-bri 0–255`: Set a rooms lights brightness (0–255)  
`-hue 0–65535`: Set a rooms lights hue (0–65535)  
`-sat 0–255`: Set a Rooms lights saturation (0–255)  
`-on` or `-off`: Turns a Room on or off  
