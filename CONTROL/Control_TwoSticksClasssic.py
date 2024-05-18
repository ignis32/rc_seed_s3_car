import pygame
import socket
from time import sleep
import math
import numpy as np
import udp_settings

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Initialized joystick: {joystick.get_name()}")
 
# UDP setup
udp_ip = udp_settings.ip
udp_port = udp_settings.port

print(udp_ip)  
print(udp_port)



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_message(message):
    sock.sendto(message.encode(), (udp_ip, udp_port))

# Configurable dead zone
dead_zone = 0.05  # Adjust dead zone sensitivity as needed

def apply_dead_zone(value):
    if -dead_zone < value < dead_zone:
        return 0
    return value

def inverted_power_response_signed(A_stick, power=0.5):
    sign = np.sign(A_stick)  # Capture the sign of A_stick
    A = abs(A_stick) * 255  # Work with the absolute value of A_stick
    dA = (A / 255) ** power * 255  # Apply the power function
    return int(sign * dA)  # Restore the original sign



# Recording and playback mechanisms
recording = False
replaying = False
recorded_movements = []
playback_index = 0

# Main loop
running = True
while running:
    pygame.event.pump()

    # Button states
    record_button_pressed = joystick.get_button(4)
    replay_button_pressed = joystick.get_button(5)

    # Start or stop recording
    if record_button_pressed:
        if not recording:
            recorded_movements = []  # Reset movements when starting new recording
            recording = True
            print("Recording started.")
    else:
        if recording:
            recording = False
            print("Recording stopped.")

    # Start or stop replaying
    if replay_button_pressed:
        if not replaying:
            replaying = True
            playback_index = 0  # Reset index for new replay
            print("Replay started.")
    else:
        if replaying:
            replaying = False
            print("Replay stopped.")

    # Read joystick axes and apply dead zone
    y_stick_raw = joystick.get_axis(0)   # horizontal axis of left stick  
    x_stick_raw = -joystick.get_axis(3)  # Vertical axis of right stick
    
    y_stick = round(apply_dead_zone(y_stick_raw), 2)
    x_stick = round(apply_dead_zone(x_stick_raw), 2)
 
    # dy = int(y_stick * 255 ) 
    #dx = int(x_stick * 255 ) 

    dy = inverted_power_response_signed(y_stick)
    dx = inverted_power_response_signed(x_stick)
    

    left_speed = max(-255, min(255, dy + dx))
    right_speed = max(-255, min(255, dy - dx))

    #  -255 +255   | -255 +255


    print(f"{dy }:{dx}        {left_speed}:{right_speed}")

    # Manage recording and replaying
    if replaying:
        if playback_index < len(recorded_movements):
            left_speed, right_speed = recorded_movements[playback_index]
            send_udp_message(f"{left_speed} {right_speed}")
            playback_index += 1
        else:
            print("Playback completed.")
            replaying = False  # Automatically stop when done
    else:
        send_udp_message(f"{left_speed} {right_speed}")
        if recording:
            recorded_movements.append((left_speed, right_speed))
            

   # print(f"{left_stick} : {right_stick}    {left_speed} : {right_speed}    {len(recorded_movements)} ")

    sleep(0.01)  # Adjust for smoother or faster response

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
