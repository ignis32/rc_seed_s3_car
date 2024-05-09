import tkinter as tk
from tkinter import ttk
import socket

import udp_settings

class JoystickEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Joystick Emulator')
        self.geometry('600x600')
        # UDP setup

        self.udp_ip = udp_settings.ip
        self.udp_port = udp_settings.port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Joystick canvas
        self.canvas = tk.Canvas(self, width=600, height=600, bg='white')
        self.canvas.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
        self.center_x = 300
        self.center_y = 300
        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)

        self.draw_axes()

        # Buttons
        self.record_button = ttk.Button(self, text='Start Recording', command=self.toggle_recording)
        self.record_button.grid(column=0, row=1, padx=10, pady=10)
        self.replay_button = ttk.Button(self, text='Start Replay', command=self.toggle_replay)
        self.replay_button.grid(column=1, row=1, padx=10, pady=10)

        # Recording data
        self.recording = False
        self.replaying = False
        self.recorded_movements = []
        self.playback_index = 0

        # Motor speeds
        self.last_left_speed = 0
        self.last_right_speed = 0

        # Start periodic UDP updates
        self.periodic_udp_update()

    def send_udp_message(self, left_speed, right_speed):
        message = f"{left_speed} {right_speed}"
        self.sock.sendto(message.encode(), (self.udp_ip, self.udp_port))
        self.last_left_speed = left_speed
        self.last_right_speed = right_speed
        print(f"Left: {left_speed}, Right: {right_speed}, Recorded Movements: {len(self.recorded_movements)}")

    def periodic_udp_update(self):
        self.send_udp_message(self.last_left_speed, self.last_right_speed)
        self.after(10, self.periodic_udp_update)  # Schedule next update after 10 ms

    def start_move(self, event):
        self.update_motor_speeds(event.x, event.y)

    def on_move(self, event):
        self.update_motor_speeds(event.x, event.y)

    def stop_move(self, event):
        self.send_udp_message(0, 0)  # Stop both motors when the mouse is released

    def update_motor_speeds(self, x, y):
        dy = x - self.center_x
        dx = self.center_y - y  # Positive dy should mean forward
        left_speed = max(-255, min(255, dy + dx))
        right_speed = max(-255, min(255, dy - dx))

        if self.replaying:
            if self.playback_index < len(self.recorded_movements):
                left_speed, right_speed = self.recorded_movements[self.playback_index]
                self.playback_index += 1
            else:
                self.replaying = False
                self.replay_button.config(text="Start Replay")
                print("Replay completed.")

        self.send_udp_message(left_speed, right_speed)
        if self.recording:
            self.recorded_movements.append((left_speed, right_speed))

       

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.recorded_movements = []  # Reset the list at start
            print("Recording started.")
        else:
            self.recording = False
            self.record_button.config(text="Start Recording")
            print("Recording stopped.")

    def toggle_replay(self):
        if not self.replaying:
            self.replaying = True
            self.replay_button.config(text="Stop Replay")
            self.playback_index = 0  # Reset the index for a new replay
            print("Replay started.")
        else:
            self.replaying = False
            self.replay_button.config(text="Start Replay")
            print("Replay stopped.")

    def draw_axes(self):
        self.canvas.create_line(0, self.center_y, 600, self.center_y, fill="black")
        self.canvas.create_line(self.center_x, 0, self.center_x, 600, fill="black")

if __name__ == "__main__":
    app = JoystickEmulator()
    app.mainloop()
