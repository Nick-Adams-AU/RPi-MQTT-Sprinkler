#!/usr/bin/python3

import sys
import os
import json
import re
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# Map the friendly zone name to the Raspberry PI GPIO pin.
# Note that the pin number is the BCM pin number and not the Pi pin numbr

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

# Map what value the relay needs to correspond to ON and OFF
ON = 0
OFF = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(list(outputZoneMap.values()), GPIO.OUT)
GPIO.output(list(outputZoneMap.values()), OFF)
GPIO.setup(list(inputZoneMap.values()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

def input_change(channel):

  # The RPi.GPIO library doesn't pass the detect edge to the callback. This
  # is less than ideal as we then need to re-check the input state which may
  # have changed since the event happend. RPi.GPIO bug 96.

  state = "ON" if GPIO.input(channel) else "OFF"
  print("Input " + str(inputZoneMap[channel]) + ": " + state)
  client.publish(inputRootTopic + "_input_" + inputZone[channel] + "/state", state)

def getMAC(interface='wlan0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[9:17].replace(':', '')

# Home Assistant needs a unique identifier for this device so use the
# MAC address of the wlan0 interface
MAC = getMAC()

# Set the root MQTT topic for the input and output channels
outputRootTopic = "homeassistant/switch/sprinkler_" + MAC
inputRootTopic = "homeassistant/binary_sensor/sprinkler_" + MAC

def on_connect(client, userdata, flags, rc):

    # Check if we've failed to connect and if so, exit
    if rc > 0:
      exit("Cannot connect to MQTT: " + mqtt.connack_string(rc))

    print("Connected to MQTT: " + "OK" if not rc else str(rc))

    print("Sending discovery messages for each output zone...", end =" ")
    for zone in outputZoneMap:

      configPayload = {
        "name": "Sprinkler output " + zone,
        "command_topic": outputRootTopic + "_" + zone + "/set",
        "state_topic": outputRootTopic + "_" + zone + "/state",
        "unique_id": "sprinkler" + MAC + "_output_zone" + zone,
        "value_template": "{{value_json.zone" + zone + "}}",
        "device": {
          "name": "Sprinkler board",
          "identifiers": [ "sprinkler" + MAC ],
        }
      }

      client.subscribe(configPayload['command_topic'])

      client.publish(outputRootTopic + "_" + zone + "/config", json.dumps(configPayload))

      print(zone, end =" ")

    print("")

    print("Sending discovery messages for each input zone...", end =" ")
    for zone in inputZoneMap:

      configPayload = {
        "name": "Sprinkler input " + zone,
        "state_topic": inputRootTopic + "_input_" + zone + "/state",
        "unique_id": "sprinkler" + MAC + "_input_zone" + zone,
        "value_template": "{{value_json.zone" + zone + "}}",
        "device": {
          "name": "Sprinkler board",
          "identifiers": [ "sprinkler" + MAC ],
        }
      }

      GPIO.add_event_detect(inputZoneMap[zone], GPIO.BOTH, callback=input_change, bouncetime=200)

      client.publish(inputRootTopic + "_" + zone + "/config", json.dumps(configPayload))

      print(zone, end =" ")

    print("")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

  zone = re.findall(outputRootTopic + "_(\d+)/set", msg.topic)
  payload = str(msg.payload, 'utf-8')
  if re.search("^(ON|OFF)$", payload) and outputZoneMap.get(zone[0]):
    print("Zone " + zone[0] + ": " + payload)
    GPIO.output(outputZoneMap.get(zone[0]), ON if payload == "ON" else OFF)
    client.publish(outputRootTopic + "_" + zone[0] + "/state", payload)
  else:
    print("Invalid payload: " + payload)

try:

  # Setup MQTT and register our callback functions
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message

  # If an MQTT username and password environment variable is set, send the credentials
  if os.environ.get('MQTT_USER') and os.environ.get('MQTT_PASS'): client.username_pw_set(os.environ.get('MQTT_USER'), os.environ.get('MQTT_PASS'))

  # Connect to MQTT
  client.connect(os.environ.get('MQTT_HOST') or 'mqtt', os.environ.get('MQTT_PORT') or 1883, 60)

  client.loop_forever()

finally:
  # Reset the GPIO pins to the normal state
  GPIO.cleanup()