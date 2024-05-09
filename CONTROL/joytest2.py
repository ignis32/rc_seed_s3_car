import pygame
import requests
from time import sleep

# Script to control RC car via wifi, using logitech f310 joystick buttons

# Initialize Pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Initialized joystick: {joystick.get_name()}")
except pygame.error:
    print("No joystick found.")

# URL setup
base_url = "http://192.168.0.167/gpio{}"
gpio_states = {'0': 'low', '1': 'low'}

def set_gpio(gpio, state):
    full_url = f"{base_url.format(gpio)}/{state}"
    try:
        response = requests.get(full_url, timeout=5)  # Set a timeout for the request
        print(f"GPIO {gpio} set to {state}, Response: {response.status_code}  {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to set GPIO {gpio} to {state}. Error: {e}")
        # Optionally, retry or handle differently based on the error.

# Main loop to read joystick input
running = True
while running:
    for event in pygame.event.get():
        print("\n")
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 4:  # Button 4 press
                set_gpio('1', 'low')
                set_gpio('0', 'high')
                gpio_states['0'] = 'high'
                gpio_states['1'] = 'low'
            elif event.button == 6:  # Button 6 press
                set_gpio('0', 'low')
                set_gpio('1', 'high')
                gpio_states['0'] = 'low'
                gpio_states['1'] = 'high'

        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 4 or event.button == 6:  # If either button is released
                # Check if both buttons are released
                if not joystick.get_button(4) and not joystick.get_button(6):
                    set_gpio('0', 'low')
                    set_gpio('1', 'low')
                    gpio_states['0'] = 'low'
                    gpio_states['1'] = 'low'

        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 5:  # Button 4 press
                set_gpio('2', 'low')
                set_gpio('3', 'high')
                gpio_states['2'] = 'high'
                gpio_states['3'] = 'low'
            elif event.button == 7:  # Button 6 press
                set_gpio('3', 'low')
                set_gpio('2', 'high')
                gpio_states['3'] = 'low'
                gpio_states['2'] = 'high'
        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 5 or event.button == 7:  # If either button is released
                # Check if both buttons are released
                if not joystick.get_button(4) and not joystick.get_button(6):
                    set_gpio('2', 'low')
                    set_gpio('3', 'low')
                    gpio_states['2'] = 'low'
                    gpio_states['3'] = 'low'

# Quit Pygame
pygame.quit()