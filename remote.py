import asyncio
import time
import pygame.mixer
import serial
import signal
import sys
from evdev import InputDevice, categorize, ecodes

def signal_handler(signal, frame):
    print('CTRL-C caught, exiting.')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

pygame.mixer.init(48000, -16, 1, 1024)

lights = serial.Serial('/dev/ttyUSB0')
lights.write(b'QWERT')

race_start = pygame.mixer.Sound("mario_kart_race_start.mp3")
race_end = pygame.mixer.Sound("race_end.mp3")
first_call = pygame.mixer.Sound("first_call.mp3")

soundChannelCountdown = pygame.mixer.Channel(1)
soundChannelStart = pygame.mixer.Channel(2)
soundChannelEnd = pygame.mixer.Channel(3)
soundChannelFirst = pygame.mixer.Channel(4)

dev = InputDevice('/dev/input/event2')

last_pressed = {}
codes = {"play": 458778, "pause": 458777, "stop": 458776, "record":12124185}

millis_interval = 1000


def debounce(code):
	now_millis = int( time.time_ns() / 1000 / 1000)
	if code not in last_pressed:
		last_pressed[code] = now_millis
		print("new code")
		return True
	else:
		diff = now_millis - last_pressed[code]
		if diff > millis_interval:
			last_pressed[code] = now_millis
			print("updated code")
			return True
		else:
			return False

playing = False

def start_race():
	print("starting countdown")
	soundChannelCountdown.play(race_start)
	time.sleep(0.25)
	lights.write(b'QW3RT')
	print("3...")
	time.sleep(1)
	lights.write(b'Q234T')
	print("2...")
	time.sleep(1)
	lights.write(b'12345')
	print("1...")
	time.sleep(1)
	lights.write(b'QWERT')
	print("Go!")

async def main(dev):
	global playing
	async for ev in dev.async_read_loop():
		if ev.code == 4:
			if debounce(ev.value) is True and pygame.mixer.get_busy() is False:
				if ev.value == codes["play"]:
					start_race()
				if ev.value == codes["stop"]:
					soundChannelEnd.play(race_end)
					print("Race end!")
				if ev.value == codes["record"]:
					soundChannelFirst.play(first_call)
					print("First call!")


asyncio.run(main(dev))
