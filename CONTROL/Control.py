import pygame
import socket
from time import sleep

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Initialized joystick: {joystick.get_name()}")

# UDP setup
udp_ip = "192.168.0.167"
udp_port = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_message(message):
    sock.sendto(message.encode(), (udp_ip, udp_port))

# Configurable dead zone
dead_zone = 0.1  # Adjust dead zone sensitivity as needed

def apply_dead_zone(value):
    if -dead_zone < value < dead_zone:
        return 0
    return value

# Main loop
running = True
while running:
    pygame.event.pump()
    # Read joystick axes and apply dead zone
    left_stick_raw = -joystick.get_axis(1)   # Vertical axis of left stick
    right_stick_raw = joystick.get_axis(3)  # Vertical axis of right stick
    left_stick = round(apply_dead_zone(left_stick_raw), 2)
    right_stick = round(apply_dead_zone(right_stick_raw), 2)
    
    # Convert to integer for speed settings
    left_speed = int(left_stick * 255)
    right_speed = int(right_stick * 255)

    print(f"{left_stick} : {right_stick}    {left_speed} : {right_speed}")
    send_udp_message(f"{left_speed} {right_speed}")

    sleep(0.01)  # Adjust for smoother or faster response

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
