#Here is our code for Nightlight Part 1 in Python

import time
import random
import neopixel
import network
import sys
import uasyncio as asyncio
from mqtt import MQTTClient
from machine import Pin, PWM

ssid = 'Tufts_Robot'
password = ''

# ---- setting up pins ----
blueLED = PWM(Pin('GPIO0', Pin.OUT))  # Breathing LED
blueLED.freq(50)

buzzer = PWM(Pin('GPIO18', Pin.OUT))  # buzzer
neo = neopixel.NeoPixel(Pin(28), 1)   # neopixel
button = Pin('GPIO20', Pin.IN, Pin.PULL_UP)  # button

# --- Helper functions ---
async def breathe():
	for i in range(0, 65535, 500):
    	blueLED.duty_u16(i)
    	await asyncio.sleep(0.001)
	for i in range(65535, 0, -500):
    	blueLED.duty_u16(i)
    	await asyncio.sleep(0.001)

async def changeNeopixel():
	r = random.randint(0, 255)
	g = random.randint(0, 255)
	b = random.randint(0, 255)
	neo[0] = (r, g, b)
	neo.write()
	await asyncio.sleep(2)  # neopixel on for 2 seconds
	neo[0] = (0, 0, 0)
	neo.write()

# --- Define melody ---
NOTES = {
	'C4': 261, 'D4': 293, 'E4': 329, 'F4': 349,
	'G4': 392, 'A4': 440, 'B4': 493, 'C5': 523
}

melody = [
	('C4', 0.5), ('C4', 0.5), ('G4', 0.5), ('G4', 0.5),
	('A4', 0.5), ('A4', 0.5), ('G4', 1.0),
	('F4', 0.5), ('F4', 0.5), ('E4', 0.5), ('E4', 0.5),
	('D4', 0.5), ('D4', 0.5), ('C4', 1.0)
]
async def singSong(melody):
	for note, duration in melody:
    	frequency = NOTES[note]
    	buzzer.freq(frequency)
    	buzzer.duty_u16(700)
    	await asyncio.sleep(duration)
    	buzzer.duty_u16(0)
    	await asyncio.sleep(0.01)

async def handle_button():
	button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=readButtonPress)

def readButtonPress(p):
	print('Button pressed', p)
	if startCommand:
    	asyncio.create_task(changeNeopixel())
    	asyncio.create_task(singSong(melody))

async def connect_wifi():
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.connect(ssid, password)
	while not wlan.isconnected():
    	await asyncio.sleep(1)
	print('Connected to wifi')

# --- MQTT ---
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'nightlightSA'
startCommand = False

def reset():
	buzzer.duty_u16(0)
	blueLED.duty_u16(0)

def callback(topic, msg):
	global startCommand
	print((topic.decode(), msg.decode()))
	if msg.decode() == 'start':
    	startCommand = True
    	print('START!!!')
	elif msg.decode() == 'stop':
    	startCommand = False
    	reset()
    	print('STOP!!!')

async def mqtt_handler(client):
	while True:
    	client.check_msg()
    	await asyncio.sleep(0.1)

async def main_loop():
	await connect_wifi()
	client = MQTTClient('ME35_chris', mqtt_broker, port, keepalive=60)
	client.set_callback(callback)
	client.connect()
	client.subscribe(topic_sub.encode())
	print(f'Subscribed to {topic_sub}')

	asyncio.create_task(mqtt_handler(client))

	while True:
    	if startCommand:
        	print("Start command active")
        	await breathe()
        	await handle_button()
    	else:
        	print("Waiting for start command...")
    	await asyncio.sleep(1)

try:
	asyncio.run(main_loop())
except KeyboardInterrupt:
	print("Exiting...")

