## RPi-MQTT-Sprinkler
# Connect a Raspberry Pi to Home Assistant using MQTT

I use this as an irrigation controller.

Inputs and outputs are pushed to MQTT to allow the "brains" of the system to be managed by something like [Home Assistant](https://home-assistant.io). Use your home automation platform to schedule and set rules.

Output zones are connected to a relay board like the [HW-316 relay board](https://core-electronics.com.au/5v-4-channel-relay-module-10a.html).

Input zones are for things like rain sensors or flow meters.

Contributions welcome!

## Installation
Install the required Python PIP packages:
```bash
pip3 install RPi.GPIO phao-mqtt
```

# Update the input and output zone maps in main.py
Map each friendly name to each Raspberry Pi GPIO pin. 

In the example below, GPIO pin 12 is mapped to output zone 1 and GPIO pin 25 is mapped to input zone 2.

```python3
outputZoneMap = {
"1": 12,
"2": 16,
"3": 20,
"4": 21,
"5": 5,
"6": 6,
"7": 13,
"8": 19,
}

inputZoneMap = {
"1": 26,
"2": 25,
}
```

## Environment variables

Variable | Mandatory? | Default | Description
--- | :-----:|:-----:|-------
MQTT_HOST | No | mqtt |  Hostname for your MQTT broker
MQTT_PORT | No | 1883 | Port for your MQTT broker
MQTT_USER | No | | MQTT username
MQTT_PASS | No | | MQTT password

## Run
```bash
./main.py
```

## Operation
On your Home Assistant MQTT integration, new switch and binary sensor entities will look like this:

```
switch.sprinkler_output_1
switch.sprinkler_output_2
switch.sprinkler_output_3
switch.sprinkler_output_4
switch.sprinkler_output_5
switch.sprinkler_output_6
switch.sprinkler_output_7
switch.sprinkler_output_8
binary_sensor.sprinkler_input_1
binary_sensor.sprinkler_input_2
```