import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import time
import threading
import pygame
import socket
from time import sleep
import remote_control_settings

# Rover Mission Control URL
stream_url = remote_control_settings.cam_url
# Shared data for joystick and speeds
joystick_data = {
    'dy': 0,
    'dx': 0,
    'left_speed': 0,
    'right_speed': 0
}

def draw_fps_data(frame, fps, total_data_received, avg_cam_delay):
    FONT_SCALE = 0.7  # Constant to set the font scale
    THICKNESS = 1  # boldness of the font  (1,2,3 integer)
    FONT = cv2.FONT_HERSHEY_TRIPLEX
    fps_text = f"FPS: {fps:.2f}"
    data_text = f"Data: {total_data_received / 1e6:.2f} MB"
    cam_delay_text = f"Avg frame receive time: {avg_cam_delay:.2f} ms"
    cv2.putText(frame, fps_text, (10, 30), FONT, FONT_SCALE, (0, 255, 0), THICKNESS)
    cv2.putText(frame, data_text, (10, 60), FONT, FONT_SCALE, (0, 255, 0), THICKNESS)
    cv2.putText(frame, cam_delay_text, (10, 90), FONT, FONT_SCALE, (0, 255, 0), THICKNESS)
    return frame

def draw_controls(frame, joystick_data):
    # Offset constants
    crosshair_offset_x = 100
    crosshair_offset_y = frame.shape[0] - 100

    crosshair_center = (crosshair_offset_x, crosshair_offset_y)
    crosshair_size = 50
    dx = joystick_data['dx'] / 255.0
    dy = joystick_data['dy'] / 255.0
    dot_position = (int(crosshair_center[0] + dx * crosshair_size), int(crosshair_center[1] - dy * crosshair_size))

    # Draw crosshair
    cv2.rectangle(frame, (crosshair_center[0] - crosshair_size, crosshair_center[1] - crosshair_size), 
                  (crosshair_center[0] + crosshair_size, crosshair_center[1] + crosshair_size), (255, 255, 255), 2)
    cv2.line(frame, (crosshair_center[0] - crosshair_size, crosshair_center[1]), 
             (crosshair_center[0] + crosshair_size, crosshair_center[1]), (255, 255, 255), 1)
    cv2.line(frame, (crosshair_center[0], crosshair_center[1] - crosshair_size), 
             (crosshair_center[0], crosshair_center[1] + crosshair_size), (255, 255, 255), 1)
    cv2.circle(frame, dot_position, 5, (0, 0, 255), -1)

    # Draw throttle sliders
    left_speed = joystick_data['left_speed']
    right_speed = joystick_data['right_speed']
    left_throttle_height = int(left_speed / 510.0 * crosshair_size * 2)
    right_throttle_height = int(right_speed / 510.0 * crosshair_size * 2)

    # Align zero level of throttle with the horizontal axis of the joystick crosshair
    zero_level = crosshair_center[1]
    left_throttle_start = zero_level - left_throttle_height
    right_throttle_start = zero_level - right_throttle_height

    cv2.rectangle(frame, (crosshair_center[0] - crosshair_size - 20, left_throttle_start),
                  (crosshair_center[0] - crosshair_size, zero_level), (0, 255, 0), -1)
    cv2.rectangle(frame, (crosshair_center[0] + crosshair_size, right_throttle_start),
                  (crosshair_center[0] + crosshair_size + 20, zero_level), (0, 255, 0), -1)

    # Print speed values at fixed positions
    left_speed_text = f"{left_speed}"
    right_speed_text = f"{right_speed}"

    FONT_SCALE = 0.7  # Constant to set the font scale
    THICKNESS = 1  # boldness of the font  (1,2,3 integer)
    FONT =   cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, left_speed_text, (crosshair_center[0] - crosshair_size - 40, crosshair_center[1] - crosshair_size - 10),
                FONT, FONT_SCALE, (0, 255, 0), THICKNESS)
    cv2.putText(frame, right_speed_text, (crosshair_center[0] + crosshair_size + 10, crosshair_center[1] - crosshair_size - 10),
                FONT, FONT_SCALE, (0, 255, 0), THICKNESS)

    return frame

def draw_crosshair(frame):
    center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
    crosshair_size = 20

    # Draw horizontal line
    cv2.line(frame, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), (0, 255, 0), 2)
    # Draw vertical line
    cv2.line(frame, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), (0, 255, 0), 2)

    return frame

# Function to display the Rover Mission Control
def display_mjpeg_stream(stream_url):
    last_frame = None
    total_data_received = 0
    frame_times = []

    def resize_frame_with_aspect_ratio(frame, window_size):
        h, w = frame.shape[:2]
        win_w, win_h = window_size
        aspect_ratio = w / h

        if win_w / win_h > aspect_ratio:
            new_h = win_h
            new_w = int(aspect_ratio * win_h)
        else:
            new_w = win_w
            new_h = int(win_w / aspect_ratio)

        resized_frame = cv2.resize(frame, (new_w, new_h))
        top_padding = (win_h - new_h) // 2
        bottom_padding = win_h - new_h - top_padding
        left_padding = (win_w - new_w) // 2
        right_padding = win_w - new_w - left_padding

        padded_frame = cv2.copyMakeBorder(resized_frame, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT)
        return padded_frame

    cv2.namedWindow(f"Rover Mission Control {stream_url}", cv2.WINDOW_NORMAL)  # Make the window resizable

    while True:
        try:
            # Open a connection to the Rover Mission Control with a timeout of 0.5 seconds
            stream = requests.get(stream_url, stream=True, timeout=1)
            if stream.status_code != 200:
                print(f"Error: Unable to open stream (status code: {stream.status_code})")
                # Display restoring connection message
                if last_frame is not None:
                    cv2.putText(last_frame, "Restoring connection...", (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(f"Rover Mission Control {stream_url}", last_frame)
                    cv2.waitKey(1)
                continue

            bytes_data = bytes()
            frame_count = 0
            start_time = time.time()

            for chunk in stream.iter_content(chunk_size=1024):
                chunk_start_time = time.time()
                bytes_data += chunk
                total_data_received += len(chunk)  # Track data received
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]

                    img = Image.open(BytesIO(jpg))
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    frame_count += 1
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time

                    # Measure the end-to-end delay
                    frame_receive_time = time.time() - chunk_start_time
                    frame_times.append(frame_receive_time)
                    if len(frame_times) > 10:
                        frame_times.pop(0)
                    avg_cam_delay = np.mean(frame_times) * 1000
                    
                    # Resize the frame to fit the window size while maintaining aspect ratio
                    window_size = cv2.getWindowImageRect(f"Rover Mission Control {stream_url}")[-2:]  # Get the current window size
                    frame = resize_frame_with_aspect_ratio(frame, window_size)

                    # Draw FPS and data on frame
                    frame = draw_fps_data(frame, fps, total_data_received, avg_cam_delay)

                    # Draw controls on frame
                    frame = draw_controls(frame, joystick_data)
                    
                    # Draw crosshair on frame
                    frame = draw_crosshair(frame)

                    # Update the last frame
                    last_frame = frame.copy()
                    
                    cv2.imshow(f"Rover Mission Control {stream_url}", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except (requests.exceptions.RequestException, cv2.error) as e:
            print(f"Stream error: {e}")
            # Display restoring connection message
            if last_frame is not None:
                cv2.putText(last_frame, "Restoring connection...", (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
                cv2.imshow(f"Rover Mission Control {stream_url}", last_frame)
                cv2.waitKey(1)

    cv2.destroyAllWindows()

def inverted_power_response_signed(A_stick, power=0.5):
        sign = np.sign(A_stick)  # Capture the sign of A_stick
        A = abs(A_stick) * 255  # Work with the absolute value of A_stick
        dA = (A / 255) ** power * 255  # Apply the power function
        return int(sign * dA)  # Restore the original sign

def speed_calculation(joystick):
        
        # Configurable dead zone
        dead_zone = 0.04  # Adjust dead zone sensitivity as needed

        def apply_dead_zone(value):
            if -dead_zone < value < dead_zone:
                return 0
            return value
        def limit_speed(value):
            return max(-255,(min(255, value)))

        x_stick_raw =  joystick.get_axis(0)   #   horizontal axis of left stick    + is right, - is left.
        y_stick_raw = -joystick.get_axis(3)  #   Vertical axis of right stick.   + is forward, - is backward
       
        x_stick = round(apply_dead_zone(x_stick_raw), 2)
        y_stick = round(apply_dead_zone(y_stick_raw), 2)

        
        dx = inverted_power_response_signed(x_stick,power=0.7)
        dy = inverted_power_response_signed(y_stick,power=0.4)                       

        left_speed  = limit_speed ( dy+dx)
        right_speed = limit_speed ( dy-dx)
      
        return  dx,dy, left_speed, right_speed

# Function to control the RC car
def control_rc_car():
    # Initialize Pygame and joystick
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Initialized joystick: {joystick.get_name()}", flush=True)

    # UDP setup
    udp_ip = remote_control_settings.control_ip
    udp_port = remote_control_settings.control_port

    print(udp_ip, flush=True)
    print(udp_port, flush=True)
    seq = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_udp_message(message):
        sock.sendto(message.encode(), (udp_ip, udp_port))

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
                print("Recording started.", flush=True)
        else:
            if recording:
                recording = False
                print("Recording stopped.", flush=True)

        # Start or stop replaying
        if replay_button_pressed:
            if not replaying:
                replaying = True
                playback_index = 0  # Reset index for new replay
                print("Replay started.", flush=True)
        else:
            if replaying:
                replaying = False
                print("Replay stopped.", flush=True)

        # Read joystick axes and apply dead zone
        dx,dy,left_speed,right_speed = speed_calculation(joystick)

       # print(f"{dx}:{dy} {left_speed}:{right_speed} ", flush=True)
        seq += 1

        # Update shared joystick data
        joystick_data['dy'] = dy
        joystick_data['dx'] = dx
        joystick_data['left_speed'] = left_speed
        joystick_data['right_speed'] = right_speed

        # Manage recording and replaying
        if replaying:
            if playback_index < len(recorded_movements):
                left_speed, right_speed = recorded_movements[playback_index]
                send_udp_message(f"{left_speed} {right_speed}")
                playback_index += 1
            else:
                print("Playback completed.", flush=True)
                replaying = False  # Automatically stop when done
        else:
            send_udp_message(f"{left_speed} {right_speed} {seq}")
            if recording:
                recorded_movements.append((left_speed, right_speed))

        sleep(0.01)  # Adjust for smoother or faster response

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":

    # Create threads for each function
    stream_thread = threading.Thread(target=display_mjpeg_stream, args=(stream_url,))
    control_thread = threading.Thread(target=control_rc_car)

    # Start threads
    stream_thread.start()
    control_thread.start()

    # Wait for threads to complete
    stream_thread.join()
    control_thread.join()
